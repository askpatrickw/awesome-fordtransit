#!/usr/bin/env python3
from pathlib import Path
from utils import load_resources, category_sort_key

START='<!-- START:RESOURCES -->'
END='<!-- END:RESOURCES -->'

def render(data):
    cats=list(data.get('categories',[]))
    cats.sort(key=category_sort_key)
    out=[]
    for cat in cats:
        items=[i for i in cat.get('items',[]) if i.get('approved')]
        if not items: continue
        out.append(f"## {cat['title']}\n\n")
        for it in items:
            desc=it.get('description','').strip()
            out.append(f"- [{it['title']}]({it['url']}) {' '+desc if desc else ''}\n".rstrip()+"\n")
        out.append("\n")
    return ''.join(out).rstrip()+"\n"

def main():
    readme=Path('README.md')
    data=load_resources(Path('resources.json'))
    block=render(data)
    # If no approved items exist, skip modifying README to avoid wiping existing manual content
    if not any(i.get('approved') for c in data.get('categories',[]) for i in c.get('items',[])):
        print('No approved items; leaving README unchanged (migration likely pending).')
        return 0
    if not readme.exists():
        print('README.md missing');return 1
    txt=readme.read_text()
    if START in txt and END in txt:
        pre,rest=txt.split(START,1)
        _,post=rest.split(END,1)
        new=pre+START+'\n\n'+block+'\n'+END+post
    else:
        new=txt.rstrip()+f"\n\n{START}\n\n{block}\n{END}\n"
    if new!=txt:
        readme.write_text(new)
        print('README updated')
    else:
        print('README unchanged')

if __name__=='__main__':
    raise SystemExit(main())
