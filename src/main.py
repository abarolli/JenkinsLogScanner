
from argparse import ArgumentParser, Namespace
import os
import traceback

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


def scan_jobs(jobs: list[dict]):
    pass


def scan_builds(builds: list[dict]):
    pass


def scan_jenkins(url: str) -> None:
    
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
        scan_jobs(jobs)
    elif (builds := jenkins_data.get('builds')):
        scan_builds(builds)


def main():

    args = collect_input()
    scan_jenkins(args.jenkins_url)


if __name__ == '__main__':
    main()