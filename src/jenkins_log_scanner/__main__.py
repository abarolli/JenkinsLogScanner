
import validators
from argparse import ArgumentParser, Namespace

from scan_jenkins import JenkinsLogScanner, Operation

import string_utils


def __collect_input() -> Namespace:
    parser = ArgumentParser()
    
    parser.add_argument('jenkins_url')
    parser.add_argument('search_string')

    args = parser.parse_args()

    if not ('localhost:' in args.jenkins_url or validators.url(args.jenkins_url)): #skip localhost validation for local development
        raise ValueError(f'The provided url {args.jenkins_url} is invalid')
    
    return args


def __main():

    args = __collect_input()
    
    scanner = JenkinsLogScanner(args.jenkins_url)
    ops = [
        Operation('findings', string_utils.find_search_str, search_str=args.search_string),
    ]

    scans = scanner.scan_jenkins(ops)

    for scan in scans:
        print(scan)


if __name__ == '__main__':
    __main()