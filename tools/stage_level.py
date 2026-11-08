#!/usr/bin/env python3
"""Stage one level's entry in src/levels.js for commit, and nothing else.

    python3 tools/stage_level.py "Level name"

The index gets HEAD's levels.js with only that level's entry replaced by the
working copy's. Other levels' uncommitted changes (for example a picture whose
deal is still generating) stay unstaged. Refuses a level without a deal.
"""
import os
import re
import subprocess
import sys

if len(sys.argv) != 2:
    sys.exit(__doc__.strip())
name = sys.argv[1]
os.chdir(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

head = subprocess.run(['git', 'show', 'HEAD:src/levels.js'], capture_output=True, text=True, check=True).stdout
cur = open('src/levels.js').read()


def span(src, n, where):
    m = re.search(r"^  \{\n    name: '" + re.escape(n) + r"',\n", src, re.M)
    if not m:
        sys.exit(f'no level called {n!r} in {where}')
    return m.start(), src.index('\n  },\n', m.start()) + len('\n  },\n')


a, b = span(head, name, 'HEAD')
c, d = span(cur, name, 'the working copy')
block = cur[c:d]
if 'deal:' not in block or 'solution:' not in block:
    sys.exit(f'{name} has no deal yet; generate one before committing')
staged = head[:a] + block + head[b:]
h = subprocess.run(['git', 'hash-object', '-w', '--stdin'], input=staged,
                   capture_output=True, text=True, check=True).stdout.strip()
subprocess.run(['git', 'update-index', '--cacheinfo', f'100644,{h},src/levels.js'], check=True)
rows = re.findall(r"^      '(\S+)',$", block, re.M)
print(f'staged {name}: {len(rows[0])}x{len(rows)} picture with its deal')
