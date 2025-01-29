from concurrent.futures import Future, ThreadPoolExecutor, as_completed
import os
from typing import List

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
            auth=self.__auth
        )
    
        if not res.ok:
            raise requests.exceptions.RequestException(
                f'The URL {url} returned a bad http response {res.status_code}',
                request=res.request,
                response=res)
        
        return res


    def __scan_jobs(self, jobs: list[dict], operations: List[Operation]) -> List[BuildScan]:
        
        results: List[BuildScan] = []
        for job in jobs:
            job_api_url = job.get('url') + '/api/json'
            res = self.__request(job_api_url)

            job_data = res.json()

            if (more_jobs := job_data.get('jobs')):
                scanned_builds = self.__scan_jobs(more_jobs, operations)
            elif (builds := job_data.get('builds')):
                scanned_builds = self.__scan_builds(builds, operations)
            
            results.extend(scanned_builds)
        
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
        
        jenkins_data = res.json()

        if (jobs := jenkins_data.get('jobs')):
            return self.__scan_jobs(jobs, operations)
        elif (builds := jenkins_data.get('builds')):
            return self.__scan_builds(builds, operations)