#!/usr/bin/env python3
"""Analyze new resource issue and emit structured outputs.
Outputs: url, manual_desc, title, description, category, appropriate
"""
import os,re,json,subprocess,textwrap

ISSUE_BODY=os.environ.get('ISSUE_BODY','')
GITHUB_OUTPUT=os.environ.get('GITHUB_OUTPUT')

def _section_regex(label: str):
    # Match '### Label' followed by any whitespace/newlines, capture everything
    # until the next heading starting with '### ' or end of string.
    # Support both \n and \r\n newlines.
    return re.compile(
        rf"###\s+{re.escape(label)}\s*\r?\n+([\s\S]*?)(?=\r?\n###\s+|\Z)",
        re.IGNORECASE
    )

def grab(label: str) -> str:
    m=_section_regex(label).search(ISSUE_BODY or '')
    if not m:
        return ''
    val=m.group(1).strip()
    # Single-line normalize; drop leading markdown artifacts like bullets and block italics
    val=re.sub(r"^[-*]\s+", "", val, flags=re.M)
    val=re.sub(r"^_+|_+$", "", val)
    # Collapse whitespace and keep it on one line for GITHUB_OUTPUT safety
    val=re.sub(r"\s+", " ", val).strip()
    return val

url=grab('URL')
manual_desc=grab('Description (Optional if using AI)')

def fetch(u):
    """Return cleaned text snippet (for prompting)."""
    if not u: return ''
    try:
        import requests
        r=requests.get(u,timeout=20,headers={"User-Agent":"awesome-fordtransit-bot/1.0"})
        txt=r.text
    except Exception:
        return ''
    txt=re.sub(r'<(script|style)[^>]*>.*?</\1>',' ',txt,flags=re.I|re.S)
    txt=re.sub(r'<[^>]+>',' ',txt)
    txt=re.sub(r'\s+',' ',txt)
    return txt[:4000]

def fetch_html(u):
    """Return raw HTML for metadata extraction."""
    if not u: return ''
    try:
        import requests
        r=requests.get(u,timeout=20,headers={"User-Agent":"awesome-fordtransit-bot/1.0"})
        return r.text
    except Exception:
        return ''

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

def _call_model_via_curl(prompt_text: str) -> str:
    """Call GitHub Models chat/completions via curl and return the content string.
    Requires GITHUB_TOKEN (or GH_TOKEN) in env. Returns empty string on failure.
    """
    token = os.environ.get('GITHUB_TOKEN') or os.environ.get('GH_TOKEN')
    if not token:
        return ''
    payload = {
        'model': 'openai/gpt-4o-mini',
        'messages': [
            {'role': 'user', 'content': prompt_text}
        ],
        # Keep responses concise and deterministic-ish
        'temperature': 0.2,
    }
    args = [
        'curl','-sS','-f',
        'https://models.github.ai/inference/chat/completions',
        '-H','Content-Type: application/json',
        '-H',f'Authorization: Bearer {token}',
        '--data-binary','@-'
    ]
    try:
        proc = subprocess.run(
            args,
            input=json.dumps(payload),
            capture_output=True,
            text=True,
            check=False
        )
        if proc.returncode != 0:
            # curl error; include stderr for local debugging
            err = (proc.stderr or '').strip()
            if err:
                print(f"curl models error: {err}")
            return ''
        body = (proc.stdout or '').strip()
        try:
            resp = json.loads(body)
        except Exception:
            return ''
        # Extract content text similar to OpenAI schema
        choices = resp.get('choices') or []
        if not choices:
            return ''
        msg = choices[0].get('message') or {}
        content = msg.get('content') or ''
        return content
    except FileNotFoundError:
        # curl not available
        return ''

raw = _call_model_via_curl(prompt)
if raw:
    # Extract first JSON object if array or extra text present
    m=re.search(r'\{.*?\}', raw, re.S)
    if m:
        try:
            model_json=json.loads(m.group(0))
        except Exception:
            pass

# Fallback if model_json is empty or missing critical fields
def safe_get(d,k,default=''):
    v=d.get(k, default) if isinstance(d, dict) else default
    return ('' if v is None else str(v)).strip()

def meta_from_html(html: str):
    title=''
    desc=''
    if not html:
        return title, desc
    m=re.search(r'<title[^>]*>(.*?)</title>', html, flags=re.I|re.S)
    if m:
        title=re.sub(r'\s+', ' ', m.group(1)).strip()
        # Trim common site suffixes
        for sep in [' | ', ' – ', ' — ', ' - ']:
            if sep in title and len(title) > 40:
                title=title.split(sep)[0].strip()
                break
    # Meta description in any attribute order
    m=re.search(r'<meta[^>]+name=["\"]description["\"][^>]*?content=["\"]([^"\"]+)["\"][^>]*?>', html, flags=re.I)
    if not m:
        m=re.search(r'<meta[^>]+content=["\"]([^"\"]+)["\"][^>]*?name=["\"]description["\"][^>]*?>', html, flags=re.I)
    if m:
        desc=re.sub(r'\s+', ' ', m.group(1)).strip()
    return title, desc

def categorize(url:str, title:str, text:str) -> str:
    u=(url or '').lower()
    t=(title or '').lower()
    x=(text or '').lower()
    def has(*kw):
        s=u+' '+t+' '+x
        return any(k in s for k in kw)
    if has('forum','reddit','discord','facebook','group','community'): return 'Community'
    if has('github.com','npmjs.com','pypi.org','cli','tool','library'): return 'Tools'
    if has('manual','guide','faq','spec','documentation','wiki'): return 'Resources'
    if has('error','fix','problem','diagnos','troubleshoot'): return 'Troubleshooting'
    if has('suspension','lift','shock','strut','coil','spring'): return 'Suspension'
    if has('electrical','wiring','12v','solar','battery','inverter','dc-dc','alternator'): return 'Electrical'
    if has('interior','cabinet','bed','insulation','floor','swivel','seat'): return 'Interior Components'
    if has('exterior','bumper','rack','skid','exhaust','hook'): return 'Exterior Components'
    if has('maintenance','service','oil','filter','brake','coolant','transmission'): return 'Maintenance'
    if has('supplier','store','shop','parts','outfitters','carid','amazon','ebay'): return 'Suppliers to DIY Builders'
    if has('engine','tune','turbo','intake','exhaust','ecu'): return 'Engine Mods'
    return 'Resources'

def clamp(s: str, limit: int=160) -> str:
    s=re.sub(r'\s+', ' ', s or '').strip()
    if len(s) <= limit: return s
    # Try to cut at last period before limit
    cut=s[:limit]
    p=cut.rfind('. ')
    if p>60: return cut[:p+1]
    return cut.rstrip()+'…'

def field(k):
    return safe_get(model_json, k, '')

title=field('title')
description=field('description')
category=field('category')
appropriate=field('appropriate')

if not (title and description and category):
    html=fetch_html(url)
    meta_title, meta_desc = meta_from_html(html)
    clean_snippet = snippet
    # Prefer meta
    if not title: title = meta_title or ''
    if not description:
        if manual_desc and manual_desc.lower() not in {'_no response_', 'no response'}:
            description = clamp(manual_desc, 160)
        else:
            description = clamp(meta_desc or clean_snippet, 160)
    if not category:
        category = categorize(url, title, html or clean_snippet)
    if not appropriate:
        s = (url + ' ' + title + ' ' + (html or clean_snippet)).lower()
        appropriate = 'true' if ('ford' in s and 'transit' in s) else 'true'

# Final single-line sanitize for outputs
def oneline(s: str) -> str:
    return re.sub(r'[\r\n]+', ' ', (s or '').strip())

outputs={
 'url': oneline(url),
 'manual_desc': oneline(manual_desc),
 'title': oneline(title),
 'description': oneline(description),
 'category': oneline(category),
 'appropriate': oneline(str(appropriate))
}
if GITHUB_OUTPUT:
    with open(GITHUB_OUTPUT,'a') as fh:
        for k,v in outputs.items():
            fh.write(f"{k}={v}\n")
print('Analysis outputs:', outputs)
