#!/usr/bin/env python3
import argparse, sys
import os
from pathlib import Path
from utils import load_resources, save_resources, add_resource, ensure_category

def migrate_if_empty(data):
    if data.get('categories'):
        return
    # Attempt one-time extraction from existing README inside markers
    readme_path=Path('README.md')
    if not readme_path.exists():
        return
    txt=readme_path.read_text().splitlines()
    current=None
    import re
    link_re=re.compile(r'^- \[([^\]]+)\]\(([^)]+)\)\s*(.*)')
    from datetime import date
    for line in txt:
        if line.startswith('## ') and not line.startswith('###'):
            current=line[3:].strip()
            continue
        m=link_re.match(line)
        if m and current:
            cat=ensure_category(data,current)
            title,url,desc=m.groups()
            if not any(item['url']==url for item in cat['items']):
                cat['items'].append({'title':title.strip(),'url':url.strip(),'description':desc.strip(),'added':str(date.today()),'sourceIssue':None,'approved':True})
    for c in data.get('categories',[]):
        c['items'].sort(key=lambda x:x['title'].lower())

def main():
    p=argparse.ArgumentParser()
    p.add_argument('--url',required=True)
    p.add_argument('--title',required=True)
    p.add_argument('--description',required=True)
    p.add_argument('--category',required=True)
    p.add_argument('--issue',type=int)
    p.add_argument('--approve',action='store_true')
    p.add_argument('--resources',default='resources.json')
    a=p.parse_args()
    path=Path(a.resources)
    data=load_resources(path)
    migrate_if_empty(data)
    ok,msg=add_resource(data,title=a.title,url=a.url,description=a.description,category=a.category,source_issue=a.issue,approve=a.approve)
    if not ok:
        print(msg)
        print('::set-output name=status::duplicate')
        sys.exit(0)
    save_resources(path,data)
    print(msg)
    # New style output for GitHub Actions
    if 'GITHUB_OUTPUT' in os.environ:
        with open(os.environ['GITHUB_OUTPUT'],'a') as fh:
            fh.write('status=added\n')
    print('status=added')

if __name__=='__main__':
    main()
