import os
from typing import List
from concurrent.futures import Future, ThreadPoolExecutor, as_completed

JLS_VERIFY_SSL = True if os.environ.get('JLS_VERIFY_SSL', 'True') == 'True' else False
if not JLS_VERIFY_SSL:
    import urllib3
    urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

import requests
import requests.auth


class BuildScan:
    def __init__(self, jobUrl: str, buildNumber: int):
        self.__jobUrl = jobUrl
        self.__buildNumber = buildNumber
        self.__results = {}


    @property
    def jobUrl(self): return self.__jobUrl


    @property
    def buildNumber(self): return self.__buildNumber


    @property
    def results(self): return self.__results


    def add_result(self, key: str, result):
        self.__results.update({key: result})


    def __str__(self):
        return str({"jobUrl": self.__jobUrl, "buildNumber": self.__buildNumber, **self.__results})


class Operation:
    '''
    Represents a callable that's not expected to be called until some unknown time. At initialization, optional `kwargs` can be provided
    and these will be passed to the callable when the `call` method is invoked at a later time.
    '''
    def __init__(self, name: str, f: callable, **kwargs):
        self.__name = name
        self.__f = f
        self.__kwargs = kwargs


    @property
    def name(self): return self.__name

    def call(self, *args, **kwargs):
        '''
        Any `kwargs` passed here will override the `kwargs` that were supplied at initialization.
        '''
        return self.__f(*args, **self.__kwargs, **kwargs)


class JenkinsLogScanner:

    def __init__(self, url: str):
        self.__url = url
        self.__auth = requests.auth.HTTPBasicAuth(os.environ.get('JENKINS_USER'), os.environ.get('JENKINS_PASSWORD'))


    @property
    def url(self): return self.__url


    def __request(self, url: str) -> requests.Response:
        res = requests.get(
            url,
            auth=self.__auth,
            verify=JLS_VERIFY_SSL
        )
    
        if not res.ok:
            raise requests.exceptions.RequestException(
                f'The URL {url} returned a bad http response {res.status_code}',
                request=res.request,
                response=res)
        
        return res
    

    def __is_build_data(self, jenkins_data: dict) -> bool:
        return 'builtOn' in jenkins_data


    def __scan_jobs(self, jobs: list[dict], operations: List[Operation]) -> List[BuildScan]:
        
        results: List[BuildScan] = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures: List[Future] = []
            for job in jobs:
                job_api_url = job.get('url') + '/api/json'
                res = self.__request(job_api_url)

                job_data = res.json()
                if (more_jobs := job_data.get('jobs')):
                    futures.append(executor.submit(self.__scan_jobs, more_jobs, operations))
                elif (builds := job_data.get('builds')):
                    futures.append(executor.submit(self.__scan_builds, builds, operations))
            
            for future in as_completed(futures):
                results.extend(future.result())
        
        return results


    def __scan_builds(self, builds: list[dict], operations: List[Operation]) -> List[BuildScan]:
        
        results: List[BuildScan] = []

        with ThreadPoolExecutor(max_workers=10) as executor:
            futures: List[Future] = []
            for build in builds:
                futures.append(
                    executor.submit(self.__scan_build, build, operations)
                )
            
            for future in as_completed(futures):
                results.append(future.result())

        return results
    

    def __scan_build(self, build: dict, operations: List[Operation]) -> BuildScan:

        build_log_url = build.get('url') + 'consoleText'
        res = self.__request(build_log_url)
        build_log_contents = res.text
        build_scan = BuildScan(build.get('url').rsplit('/', 2)[0], build.get('number'))
        for operation in operations:
            build_scan.add_result(operation.name, operation.call(build_log_contents)) #make sure each Operation has a unique name
        
        return build_scan
    

    def scan_jenkins(self, operations: List[Operation]) -> List[BuildScan]:
        '''
        Returns a list of BuildScan objects.
        '''
        res = self.__request(self.__url + '/api/json')
        
        try:
            jenkins_data = res.json()
        except requests.exceptions.JSONDecodeError as e:
            raise requests.exceptions.JSONDecodeError(
                f'Could not decode json data at {self.__url + "/api/json"}; is this a valid Jenkins url?',
                e.doc,
                e.pos
            )

        if (jobs := jenkins_data.get('jobs')):
            return self.__scan_jobs(jobs, operations)
        elif (builds := jenkins_data.get('builds')):
            return self.__scan_builds(builds, operations)
        elif (self.__is_build_data(jenkins_data)):
            return [self.__scan_build(jenkins_data, operations)]
        else:
            raise AttributeError(
                f'Could not determine the type of Jenkins data at the url {self.__url}'
            )