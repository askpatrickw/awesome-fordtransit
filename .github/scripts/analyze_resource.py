#!/usr/bin/env python3
"""Analyze new resource issue and emit structured outputs.
Outputs: url, manual_desc, title, description, category, appropriate
"""
import os,re,json,subprocess,textwrap

ISSUE_BODY=os.environ.get('ISSUE_BODY','')
GITHUB_OUTPUT=os.environ.get('GITHUB_OUTPUT')

def grab(label):
    m=re.search(rf'### {re.escape(label)}\n+([^#\n].*)', ISSUE_BODY)
    return (m.group(1).strip() if m else '').strip()

url=grab('URL')
manual_desc=grab('Description (Optional if using AI)')

def fetch(u):
    if not u: return ''
    try:
        import requests
        r=requests.get(u,timeout=15)
        txt=r.text
    except Exception:
        return ''
    txt=re.sub(r'<(script|style)[^>]*>.*?</\1>',' ',txt,flags=re.I|re.S)
    txt=re.sub(r'<[^>]+>',' ',txt)
    txt=re.sub(r'\s+',' ',txt)
    return txt[:4000]

snippet=fetch(url)
prompt=textwrap.dedent(f"""You are a strict JSON generator for a Ford Transit resource list.
Return ONLY minified JSON with keys: title, description, category, appropriate.
Rules:
  title: concise.
  description: <=160 chars, one sentence.
  category: logical bucket (Mods, Maintenance, Electrical, Interior, Exterior, Tools, Resources, Troubleshooting, Suppliers, Suspension) or new.
  appropriate: false if spam/unrelated/malicious.
Input URL: {url}
User description: {manual_desc}
Page snippet: {snippet}
JSON only.
""")
with open('prompt.txt','w') as f:
    f.write(prompt)
model_json={}
try:
    proc=subprocess.run(['gh','models','run','openai/gpt-4o-mini','--prompt-file','prompt.txt'],capture_output=True,text=True,check=False)
    raw=proc.stdout.strip()
    m=re.search(r'\{.*?\}',raw,re.S)
    if m:
        try: model_json=json.loads(m.group(0))
        except Exception: pass
except FileNotFoundError:
    pass

def field(k):
    return str(model_json.get(k,'')).strip()

outputs={
 'url':url,
 'manual_desc':manual_desc,
 'title':field('title'),
 'description':field('description'),
 'category':field('category'),
 'appropriate':field('appropriate')
}
if GITHUB_OUTPUT:
    with open(GITHUB_OUTPUT,'a') as fh:
        for k,v in outputs.items():
            fh.write(f"{k}={v}\n")
print('Analysis outputs:', outputs)
