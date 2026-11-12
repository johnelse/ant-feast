#!/usr/bin/env python3
"""Stage one level's entry in src/levels.js for commit, and nothing else.

    python3 tools/stage_level.py "Level name"

The index gets HEAD's levels.js with only that level's entry replaced by the
working copy's. A level that isn't in HEAD yet is inserted after the nearest
level before it that is, as in the working copy. Other levels' uncommitted
changes (for example a picture whose deal is still generating) stay unstaged.
Refuses a level without a deal.
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


def span(src, n):
    """(start, end) of a level's block, or None."""
    m = re.search(r"^  \{\n    name: '" + re.escape(n) + r"',\n", src, re.M)
    if not m:
        return None
    return m.start(), src.index('\n  },\n', m.start()) + len('\n  },\n')


def names(src):
    return re.findall(r"^  \{\n    name: '((?:[^'\\]|\\.)*)',\n", src, re.M)


where = span(cur, name)
if not where:
    sys.exit(f'no level called {name!r} in the working copy')
block = cur[where[0]:where[1]]
if 'deal:' not in block or 'solution:' not in block:
    sys.exit(f'{name} has no deal yet; generate one before committing')
old = span(head, name)
if old:
    staged = head[:old[0]] + block + head[old[1]:]
    how = 'replaced'
else:
    # new level: insert after the nearest earlier level that HEAD already has
    order = names(cur)
    at = None
    for prev in reversed(order[:order.index(name)]):
        if span(head, prev):
            at = span(head, prev)[1]
            break
    if at is None:
        at = head.index('LEVELS = [\n') + len('LEVELS = [\n')
    staged = head[:at] + block + head[at:]
    how = 'added'

h = subprocess.run(['git', 'hash-object', '-w', '--stdin'], input=staged,
                   capture_output=True, text=True, check=True).stdout.strip()
subprocess.run(['git', 'update-index', '--cacheinfo', f'100644,{h},src/levels.js'], check=True)
rows = re.findall(r"^      '(\S+)',$", block, re.M)
print(f'staged {name} ({how}): {len(rows[0])}x{len(rows)} picture with its deal')
