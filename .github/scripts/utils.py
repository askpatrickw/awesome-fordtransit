#!/usr/bin/env python3
import re, json
from datetime import date
from pathlib import Path
from typing import Any, Dict

ALLOWED_TOP_LEVEL_ORDER = [
    "Car Wash","Community","Dealers","Engine Mods","Exterior Components","Bumpers","Front Hooks","Rear Shock Relocation","Skid Plates","Ski Boxes","Heating and Air Conditioning","Interior Components","Maintenance","Plumbing","Suppliers to DIY Builders","Suspension and Lifts","Seat Swivels","Van Builds","Van Automation","Van Builders","Wheels and Tires"
]

def slugify(name: str) -> str:
    return re.sub(r"[^a-z0-9-]","-",name.lower()).strip('-')

def load_resources(path: Path) -> Dict[str, Any]:
    if not path.exists():
        return {"meta":{"schemaVersion":1,"generated":None},"categories":[]}
    return json.loads(path.read_text())

def save_resources(path: Path, data: Dict[str, Any]):
    path.write_text(json.dumps(data, indent=2, ensure_ascii=False)+"\n")

def find_category(data: Dict[str, Any], title: str):
    for c in data.get("categories", []):
        if c["title"].lower()==title.lower():
            return c
    return None

def ensure_category(data: Dict[str, Any], title: str, parent: str|None=None):
    existing=find_category(data,title)
    if existing: return existing
    cat={"id":slugify(title),"title":title,"parent":parent,"items":[]}
    data.setdefault("categories", []).append(cat)
    return cat

def normalize_url(url: str) -> str:
    url=url.strip()
    if not re.match(r'^https?://',url): url='https://'+url
    if '?' in url:
        base,qs=url.split('?',1)
        kept=[p for p in qs.split('&') if not p.lower().startswith(('utm_','ref='))]
        url=base+('?'+'&'.join(kept) if kept else '')
    if url.endswith('/') and '/' in url[:-1]: url=url[:-1]
    return url

def add_resource(data: Dict[str, Any], *, title:str,url:str,description:str,category:str,source_issue:int|None,approve:bool):
    url_norm=normalize_url(url)
    for cat in data.get("categories", []):
        for item in cat.get("items", []):
            if normalize_url(item['url'])==url_norm:
                return False, f"Duplicate of existing entry in category '{cat['title']}'"
    cat_obj=ensure_category(data,category)
    cat_obj['items'].append({
        'title':title.strip(),
        'url':url_norm,
        'description':description.strip(),
        'added':str(date.today()),
        'sourceIssue':source_issue,
        'approved':approve
    })
    cat_obj['items'].sort(key=lambda x:x['title'].lower())
    return True,'Added'

def category_sort_key(cat: Dict[str, Any]):
    try: return ALLOWED_TOP_LEVEL_ORDER.index(cat['title'])
    except ValueError: return len(ALLOWED_TOP_LEVEL_ORDER)+hash(cat['title'])%1000
