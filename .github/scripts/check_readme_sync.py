#!/usr/bin/env python3
import re, sys, subprocess, pathlib, difflib

README = pathlib.Path('README.md')
GEN = pathlib.Path('.github/scripts/generate_readme.py')
START='<!-- START:RESOURCES -->'
END='<!-- END:RESOURCES -->'

def extract_block(txt:str):
    m=re.search(re.escape(START)+r'(.*)'+re.escape(END), txt, flags=re.S)
    return m.group(1).strip('\n') if m else None

def main():
    if not README.exists() or not GEN.exists():
        print('Required files missing', file=sys.stderr)
        return 2
    original = README.read_text()
    before_block = extract_block(original)
    if before_block is None:
        print('Markers not found in README', file=sys.stderr)
        return 2
    subprocess.run([sys.executable, str(GEN)], check=False)
    updated = README.read_text()
    after_block = extract_block(updated)
    if after_block is None:
        print('Markers missing after generation', file=sys.stderr)
        return 1
    if before_block == after_block:
        print('README resources block in sync')
        return 0
    print('README resources block OUT OF SYNC:')
    diff = difflib.unified_diff(before_block.splitlines(), after_block.splitlines(), 'current','generated', lineterm='')
    for line in diff:
        print(line)
    README.write_text(original)
    return 1

if __name__ == '__main__':
    sys.exit(main())
