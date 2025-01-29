

from typing import List


def find_search_str(target: str, search_str: str, before: int = 0, after: int = 0, maxsearches: int = -1):

    results: List[str] = []
    lines = target.splitlines(keepends=1)
    for n in range(len(lines)):
        if maxsearches == 0: break

        line = lines[n]
        if search_str not in line:
            continue

        search_window_start = max(n - before, 0)
        search_window_end = min(n + after + 1, len(lines))
        results.append(''.join(lines[search_window_start : search_window_end]))
        maxsearches -= 1
    
    return results


def find_search_str_range(target: str, start_str: str, stop_str: str, maxsearches: int = -1):
    
    results: List[str] = []
    lines = target.splitlines(keepends=1)
    current_finding: List[str] = []
    is_collecting = False
    for line in lines:
        if maxsearches == 0: break

        if start_str in line:
            is_collecting = True
        elif stop_str in line and is_collecting:
            current_finding.append(line)
            results.append(''.join(current_finding))
            current_finding.clear()
            is_collecting = False
            maxsearches -= 1

        if is_collecting:
            current_finding.append(line)

    return results