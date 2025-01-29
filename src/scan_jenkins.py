import os

import requests
import requests.auth


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
                f'The URL {url} returned a bad http response',
                request=res.request,
                response=res)
        
        return res


    def __scan_jobs(self, jobs: list[dict], search_string: str):
        
        for job in jobs:
            job_api_url = job.get('url') + '/api/json'
            res = self.__request(job_api_url)

            job_data = res.json()

            if (more_jobs := job_data.get('jobs')):
                self.__scan_jobs(more_jobs, search_string)
            elif (builds := job_data.get('builds')):
                self.__scan_builds(builds, search_string)


    def __scan_builds(self, builds: list[dict], search_string: str):
        
        for build in builds:
            build_log_url = build.get('url') + 'consoleText'
            res = self.__request(build_log_url)
            build_log_contents = res.text
            if search_string in build_log_contents:
                print('Found search string')
            else:
                print('Did not find the search string')


    def scan_jenkins(self, search_string: str) -> None:
        
        res = self.__request(self.__url + '/api/json')
        
        jenkins_data = res.json()
        
        if (jobs := jenkins_data.get('jobs')):
            self.__scan_jobs(jobs, search_string)
        elif (builds := jenkins_data.get('builds')):
            self.__scan_builds(builds, search_string)