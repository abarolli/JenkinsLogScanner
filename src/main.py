
from argparse import ArgumentParser, Namespace
import os

import requests
import requests.auth
import requests.exceptions
import validators


def collect_input() -> Namespace:
    parser = ArgumentParser()
    
    parser.add_argument('jenkins_url')
    parser.add_argument('search_string')

    args = parser.parse_args()

    if not ('localhost:' in args.jenkins_url or validators.url(args.jenkins_url)):
        raise ValueError(f'The provided url {args.jenkins_url} is invalid')
    
    return args


def scan_jobs(jobs: list[dict], search_string: str):
    
    for job in jobs:
        job_api_url = job.get('url') + '/api/json'
        res = requests.get(
            job_api_url,
            auth=requests.auth.HTTPBasicAuth(os.environ.get('JENKINS_USER'), os.environ.get('JENKINS_PASSWORD'))
        )
        
        if not res.ok:
            print('uh oh')

        job_data = res.json()

        if (more_jobs := job_data.get('jobs')):
            scan_jobs(more_jobs, search_string)
        elif (builds := job_data.get('builds')):
            scan_builds(builds, search_string)


def scan_builds(builds: list[dict], search_string: str):
    
    for build in builds:
        build_log_url = build.get('url') + 'consoleText'
        res = requests.get(
            build_log_url,
            auth=requests.auth.HTTPBasicAuth(os.environ.get('JENKINS_USER'), os.environ.get('JENKINS_PASSWORD'))
        )

        if not res.ok:
            raise requests.exceptions.RequestException(
                f'Error requesting url {build_log_url}; is this a valid Jenkins url?',
                request=res.request,
                response=res)
        
        build_log_contents = res.text
        if search_string in build_log_contents:
            print('Found search string')
        else:
            print('Did not find the search string')


def scan_jenkins(url: str, search_string: str) -> None:
    
    api_url = url + '/api/json'
    res = requests.get(
        api_url,
        auth=requests.auth.HTTPBasicAuth(os.environ.get('JENKINS_USER'), os.environ.get('JENKINS_PASSWORD'))
    )
    
    if not res.ok:
        raise requests.exceptions.RequestException(
            f'Error requesting url {api_url}; is this a valid Jenkins url?',
            request=res.request,
            response=res)
    
    jenkins_data = res.json()
    if (jobs := jenkins_data.get('jobs')):
        scan_jobs(jobs, search_string)
    elif (builds := jenkins_data.get('builds')):
        scan_builds(builds, search_string)


def main():

    args = collect_input()
    scan_jenkins(args.jenkins_url, args.search_string)


if __name__ == '__main__':
    main()