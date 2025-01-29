

import re


def build_agent(build_log: str):
    '''Finds the build agent on a simple build running on a single agent'''
    pattern = re.compile('Building remotely on (.*?) ')
    match = pattern.search(build_log)
    if not match:
        return "built-in node"
    
    return match.group(1)


def head(build_log: str, lineCount: int = 1) -> str:
    '''Grabs the first `lineCount` number of lines in the `build_log`'''
    if lineCount <= 0:
        raise ValueError('lineCount must be larger than 0')
        
    lines = build_log.splitlines(keepends=1)
    return ''.join(lines[:min(len(lines), lineCount)])


def tail(build_log: str, lineCount: int = 1) -> str:
    '''Grabs the last `lineCount` number of lines in the `build_log`'''
    if lineCount <= 0:
        raise ValueError('lineCount must be larger than 0')
        
    lines = build_log.splitlines(keepends=1)
    return ''.join(lines[-(min(len(lines), lineCount)):])