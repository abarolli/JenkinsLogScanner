# JenkinsLogScanner - A fast utility for scanning Jenkins logs efficiently.

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

job_url = 'http://localhost:8081/jenkins/job/testfolder1/job/testjob2/'
scanner = JenkinsLogScanner(job_url)
ops = [
    Operation('head', logops.head),
    Operation('tail', logops.tail),
]

for s in scanner.scan_jenkins(ops):
    print(s)
```

Output:

```
{'head': 'Jenkins job started by user...', 'tail': 'Finished: SUCCESS\n'}
{'head': 'Jenkins job started by user...', 'tail': 'Finished: FAILURE\n'}
...
```

## The Operation Class

`Operation` represents a callable that's not expected to be called until some unknown time. At initialization, optional `kwargs` can be
provided and these will be passed to the callable when the `call` method is invoked at a later time.

This allows the user to bind certain arguments to the callable in advance. In the example above, the `head` and `tail` log operations
both take optional `lineCount` parameters. So if the user was interested in seeing the last 2 lines instead of the default of 1, `ops` in
the snippet above can be changed to the following:

```
ops = [
    Operation('head', logops.head, lineCount = 2),
    Operation('tail', logops.tail),
]
```

Output:

```
{'head': 'Jenkins job started by user...', 'tail': 'Build finished with success status code\nFinished: SUCCESS\n'}
{'head': 'Jenkins job started by user...', 'tail': 'Build finished with failed status code\nFinished: FAILURE\n'}
...
```
