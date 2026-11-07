#!/usr/bin/env python3
"""Put drawn pictures and generated deals into src/levels.js.

  python3 tools/art/install.py picture SCRIPT SIZE "Level name" [--after "Other level"] [--png out.png]
      Runs SCRIPT's draw(SIZE) (it must also define PAL) and writes its rows
      and palette into the level called "Level name". An existing level keeps
      its place, but loses its deal and solution, because they no longer
      match the picture. A new level goes after --after, or at the end.

  python3 tools/art/install.py deal "Level name" OUTPUT_FILE
      Copies the deal: and solution: lines from test/generate.html's output
      (e.g. tools/out/gen9) into that level.

Typical loop: picture -> generate.html (see AGENTS.md) -> deal -> sim.html.
"""
import argparse
import importlib.util
import os
import re
import sys

HERE = os.path.dirname(os.path.abspath(__file__))
LEVELS = os.path.join(os.path.dirname(os.path.dirname(HERE)), 'src', 'levels.js')
sys.path.insert(0, HERE)  # so drawing scripts can `from pix import Pic`


def find_level(src, name):
    """(start, end) of the level's `  {\\n    name: '...'...  },\\n` block, or None."""
    m = re.search(r"^  \{\n    name: '" + re.escape(name) + r"',\n", src, re.M)
    if not m:
        return None
    end = src.index('\n  },\n', m.start()) + len('\n  },\n')
    return m.start(), end


def js_str(s):
    return "'" + s.replace('\\', '\\\\').replace("'", "\\'") + "'"


def picture(args):
    spec = importlib.util.spec_from_file_location('drawing', os.path.abspath(args.script))
    mod = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mod)
    pic = mod.draw(args.size)
    rows = pic.rows()
    used = sorted(set(''.join(rows)))
    missing = [k for k in used if k not in mod.PAL]
    if missing:
        sys.exit(f'palette has no colour for: {missing}')
    if len(used) > 8:
        sys.exit(f'{len(used)} colours used; the game allows at most 8')
    palette = {k: mod.PAL[k] for k in mod.PAL if k in used}
    if args.png:
        pic.png(args.png, cell=max(4, 480 // max(pic.w, pic.h)))

    pal = ', '.join(f"{k}: '{v}'" for k, v in palette.items())
    body = ''.join(f"      '{r}',\n" for r in rows)
    entry = f"  {{\n    name: {js_str(args.name)},\n    palette: {{ {pal} }},\n    rows: [\n{body}    ],\n  }},\n"

    src = open(LEVELS).read()
    at = find_level(src, args.name)
    if at:
        src = src[:at[0]] + entry + src[at[1]:]
        how = 'replaced (deal and solution removed)'
    elif args.after:
        ref = find_level(src, args.after)
        if not ref:
            sys.exit(f'no level called {args.after!r}')
        src = src[:ref[1]] + entry + src[ref[1]:]
        how = f'added after {args.after!r}'
    else:
        end = src.rindex('];')
        src = src[:end] + entry + src[end:]
        how = 'added at the end'
    open(LEVELS, 'w').write(src)
    counts = pic.counts()
    print(f'{args.name}: {pic.w}x{pic.h}, {how}')
    print('  pixels per colour: ' + ', '.join(f'{k}={counts[k]}' for k in palette))


def deal(args):
    out = open(args.output).read()
    d = re.search(r'deal: (\[.*?\]),', out)
    s = re.search(r"solution: '(\d+)'", out)
    if not d or not s:
        sys.exit(f'no deal/solution lines in {args.output} (did generation fail?)')
    src = open(LEVELS).read()
    at = find_level(src, args.name)
    if not at:
        sys.exit(f'no level called {args.name!r}')
    block = src[at[0]:at[1]]
    block = re.sub(r"    deal: \[.*?\],\n", '', block, flags=re.S)
    block = re.sub(r"    solution: '\d*',.*\n", '', block)
    i = block.index('    rows: [')
    block = block[:i] + f"    deal: {d.group(1).replace(chr(34), chr(39))},\n    solution: '{s.group(1)}',\n" + block[i:]
    open(LEVELS, 'w').write(src[:at[0]] + block + src[at[1]:])
    print(f'{args.name}: deal and solution installed ({len(s.group(1))} moves)')


p = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
sub = p.add_subparsers(dest='cmd', required=True)
a = sub.add_parser('picture')
a.add_argument('script')
a.add_argument('size', type=int)
a.add_argument('name')
a.add_argument('--after')
a.add_argument('--png')
a.set_defaults(fn=picture)
b = sub.add_parser('deal')
b.add_argument('name')
b.add_argument('output')
b.set_defaults(fn=deal)
args = p.parse_args()
args.fn(args)
