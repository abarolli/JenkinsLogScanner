

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