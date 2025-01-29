
from argparse import ArgumentParser, Namespace
import requests
import validators

from scan_jenkins import JenkinsLogScanner, Operation

from log_operations import head, tail


def collect_input() -> Namespace:
    parser = ArgumentParser()
    
    parser.add_argument('jenkins_url')
    parser.add_argument('search_string')

    args = parser.parse_args()

    if not ('localhost:' in args.jenkins_url or validators.url(args.jenkins_url)): #skip localhost validation for local development
        raise ValueError(f'The provided url {args.jenkins_url} is invalid')
    
    return args


def main():

    args = collect_input()
    
    scanner = JenkinsLogScanner(args.jenkins_url)
    ops = [
        Operation("head", head),
        Operation("tail", tail)
    ]
    try:
        scans = scanner.scan_jenkins(ops)
    except requests.exceptions.RequestException as e:
        print(f'scan_jenkins failed with the following response status code: {e.response.status_code}')
        raise e

    for scan in scans:
        print(scan)


if __name__ == '__main__':
    main()