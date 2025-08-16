#!/usr/bin/env python3
import os,re,sys
path=sys.argv[1] if len(sys.argv)>1 else 'comment.txt'
try: text=open(path).read()
except FileNotFoundError: text=''
labels=[('URL','url'),('Proposed Title','title'),('Proposed Category','category'),('Description','description')]
found={}
for lab,key in labels:
    m=re.search(rf'{lab}: (.+)', text)
    if m: found[key]=m.group(1).strip()
out=os.environ.get('GITHUB_OUTPUT')
if out:
    with open(out,'a') as fh:
        for k,v in found.items(): fh.write(f"{k}={v}\n")
print('Extracted:',found)
