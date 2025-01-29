
from argparse import ArgumentParser, Namespace
import validators

from scan_jenkins import JenkinsLogScanner


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
    scanner.scan_jenkins(args.search_string)


if __name__ == '__main__':
    main()