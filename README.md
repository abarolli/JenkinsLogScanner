# JenkinsLogScanner - A fast utility for scanning Jenkins logs efficiently.

JenkinsLogScanner is a utility for recursively scanning every build log within a Jenkins project (whether it is top level org or a single job).
Its power is in its ability to scan many build logs in parallel, but it can be used just as well to scan individual builds.

## Environment Setup

The library only expects two environment variables to be defined: `JENKINS_USER` and `JENKINS_PASSWORD`.
Make sure these credentials are set in these environment variables and this user has access to the target Jenkins projects.

## Installation

Install with pip:

```
pip install jenkins-log-scanner
```

## Basic Usage:

```
from jenkins_log_scanner.scan_jenkins import JenkinsLogScanner, Operation
import jenkins_log_scanner.log_operations as logops

url = 'http://localhost:8081/jenkins/job/testfolder1/job/testjob2/'
scanner = JenkinsLogScanner(url)
ops = [
    Operation('head', logops.head),
    Operation('tail', logops.tail),
]

for s in scanner.scan_jenkins(ops):
    print(s)
```

Output:

```
{'jobUrl': 'http://localhost:8081/jenkins/job/testfolder1/job/testjob2', 'buildNumber': 3, 'head': 'Started by user Adeiron Barolli\n', 'tail': 'Finished: FAILURE\n'}
{'jobUrl': 'http://localhost:8081/jenkins/job/testfolder1/job/testjob2', 'buildNumber': 2, 'head': 'Started by user Adeiron Barolli\n', 'tail': 'Finished: SUCCESS\n'}
{'jobUrl': 'http://localhost:8081/jenkins/job/testfolder1/job/testjob2', 'buildNumber': 1, 'head': 'Started by user Adeiron Barolli\n', 'tail': 'Finished: SUCCESS\n'}
...
```

To scan a single build, simply give the url to that build:

```
url = 'http://localhost:8081/jenkins/job/testfolder1/job/testjob2/1'
# or
url = 'http://localhost:8081/jenkins/job/testfolder1/job/testjob2/2'
# or
url = 'http://localhost:8081/jenkins/job/testfolder1/job/testjob2/3'
# etc...
```

## The Operation Class

`Operation` represents a callable that's not expected to be called until some unknown time. At initialization, optional `kwargs` can be
provided and these will be passed to the callable when the `call` method is invoked at a later time.

This allows the user to bind certain arguments to the callable in advance. In the example above, the `head` and `tail` log operations
both take optional `lineCount` parameters. So if the user was interested in seeing the last 2 lines instead of the default of 1, `ops` in
the snippet above can be changed to the following:

```
ops = [
    Operation('head', logops.head),
    Operation('tail', logops.tail, lineCount = 2),
]
```

Output:

```
{'jobUrl': 'http://localhost:8081/jenkins/job/testfolder1/job/testjob2', 'buildNumber': 3, 'head': 'Started by user Adeiron Barolli\n', 'tail': 'Build step "Execute shell" marked build\nFinished: FAILURE\n'}
{'jobUrl': 'http://localhost:8081/jenkins/job/testfolder1/job/testjob2', 'buildNumber': 2, 'head': 'Started by user Adeiron Barolli\n', 'tail': 'Build step "Execute shell" marked build\nFinished: SUCCESS\n'}
{'jobUrl': 'http://localhost:8081/jenkins/job/testfolder1/job/testjob2', 'buildNumber': 1, 'head': 'Started by user Adeiron Barolli\n', 'tail': 'Build step "Execute shell" marked build\nFinished: SUCCESS\n'}
...
```
