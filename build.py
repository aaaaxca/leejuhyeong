"""
학생용 과목 페이지 생성기

  python3 build.py

- index.html 의 DATA 를 읽어서, 수업 과정·세미나의 과목마다
  c/<id>-<key>.html 학생용 페이지를 만듭니다.
- key 가 없는 과목에는 무작위 key 를 만들어 index.html 에 적어 둡니다.
- 학생 페이지에는 그 과목 내용만 들어가고, 허브나 다른 과목으로 가는 링크는 없습니다.
"""
import html, json, os, re, secrets, string, subprocess, sys

ROOT = os.path.dirname(os.path.abspath(__file__))
HUB = os.path.join(ROOT, "index.html")
OUT = os.path.join(ROOT, "c")
STUDENT_CATS = {"course", "seminar"}

src = open(HUB, encoding="utf-8").read()

# 1) key 없는 과목에 key 부여 (index.html 에 기록)
def add_keys(text):
    def rep(m):
        line = m.group(0)
        if "key:" in line or "ppt:" in line:
            return line
        k = "".join(secrets.choice(string.ascii_lowercase + string.digits) for _ in range(5))
        return line.replace(f'{{ id:"{m.group(1)}", ', f'{{ id:"{m.group(1)}", key:"{k}", ', 1)
    return re.sub(r'^\s*\{ id:"([\w-]+)", (?!title:"[^"]*", desc:"[^"]*", icon:)[^\n]*$', rep, text, flags=re.M)

block_start = src.index("const DATA = [")
block_end = src.index("];", block_start) + 2
block = src[block_start:block_end]
cat_ids = re.findall(r'\{ id:"([\w-]+)", title:"[^"]*", desc:"[^"]*", icon:', block)
new_block = add_keys(block)
# 카테고리 줄에는 key 가 붙지 않도록 되돌림
for cid in cat_ids:
    new_block = re.sub(rf'\{{ id:"{cid}", key:"\w+", ', f'{{ id:"{cid}", ', new_block)
if new_block != block:
    src = src[:block_start] + new_block + src[block_end:]
    open(HUB, "w", encoding="utf-8").write(src)

# 2) DATA 를 JSON 으로 꺼내기 (node 사용)
js = new_block + "\nprocess.stdout.write(JSON.stringify(DATA));"
data = json.loads(subprocess.run(["node", "-e", js], capture_output=True, text=True, check=True).stdout)

css = src[src.index("<style>") + 7: src.index("</style>")]
fonts = "\n".join(re.findall(r'<link rel="stylesheet"[^>]*>', src))
e = lambda t: html.escape(str(t or ""), quote=True)

PAGE_CSS = """
  .stu header{margin-bottom:40px}
  a.pcard{cursor:pointer}
  a.pcard .ps{color:var(--sub)}
  .notice{color:var(--sub);font-size:14px;padding:32px;border:1px dashed var(--line);border-radius:8px;text-align:center}
"""

TBAR_CSS = """
  .tcrumb{display:none} .tcrumb.on{display:flex} .tcrumb.on~.back,.tcrumb.on~.back+br{display:none}
"""
def tbar(parts):
    # 허브에서 번호를 입력한 브라우저에서만 보이는 강사용 경로 (홈 / 수업 과정 / 과목)
    html_ = " ".join((f'<a href="{h}">{e(t)}</a> <span>/</span>' if h else f"<b>{e(t)}</b>") for t, h in parts)
    return (f'<nav class="crumb tcrumb" id="tbar">{html_}</nav>'
            '<script>try{if(sessionStorage.getItem("hub-ok")==="1")document.getElementById("tbar").classList.add("on")}catch(e){}</script>')

def page(cat, it):
    where = " · ".join(x for x in ["SBS아카데미컴퓨터AIX학원"] if x)
    title = e(it["title"])
    cards = []
    for i, p in enumerate(it.get("projects") or [], 1):
        no = f"{i:02d}"
        if p.get("student"):
            cards.append(f'<a class="pcard" href="{e(p["student"])}" target="_blank" rel="noopener"><span class="pno">{no}</span>'
                         f'<h3>{e(p["title"])}</h3>{f"""<span class="ps" style="margin-top:0">{e(p.get("desc"))}</span>""" if p.get("desc") else ""}'
                         f'<span class="ps">열기 ↗</span></a>')
        else:
            cards.append(f'<div class="pcard ready"><span class="pno">{no}</span><h3>{e(p["title"])}</h3><span class="ps">준비 중</span></div>')
    body = f'<div class="pgrid">{"".join(cards)}</div>' if cards else '<div class="notice">수업 자료가 곧 올라옵니다.</div>'
    foot = " · ".join(x for x in ["SBS아카데미컴퓨터AIX학원", it["title"], it.get("subtitle")] if x)
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{e(it["title"])} · 이주형 클래스</title>
{fonts}
<style>{css}{PAGE_CSS}{TBAR_CSS}</style>
</head>
<body class="stu">
<div class="wrap">
  <header>
    {tbar([("홈","../index.html#/"),(cat["title"],"../index.html#/"+cat["id"]),(it["title"],None)])}
    <span class="d-eyebrow">{e(where)}</span>
    <h1 class="d-title">{title}</h1>
    {f'<p class="lead d-lead">{e(it["subtitle"])}</p>' if it.get("subtitle") else ""}
    {f'<p class="lead d-lead">{e(it["desc"])}</p>' if it.get("desc") else ""}
  </header>
  <main>
    <h2 class="d-sec">수업 자료</h2>
    {body}
    <div class="d-foot">{e(foot)}</div>
  </main>
</div>
</body>
</html>
"""


CONTENT_CSS = """
  .meta-row{display:flex;flex-wrap:wrap;gap:6px 22px;margin-top:18px;font-size:13px;color:var(--sub)}
  .meta-row span::before{content:"";display:inline-block;width:4px;height:4px;border-radius:50%;background:var(--faint);margin:0 8px 2px 0;vertical-align:middle}
  .phase{display:flex;gap:8px;flex-wrap:wrap;margin:16px 0 0;font-size:12px;color:var(--sub)}
  .phase span{border:1px solid var(--line);border-radius:999px;padding:3px 12px}
  .doc{font-size:15px;line-height:1.8;word-break:keep-all}
  .doc p{margin:0 0 1em} .doc ul{margin:0 0 1em;padding-left:1.2em} .doc li{margin-bottom:.4em}
  .doc b,.doc strong{color:var(--ink);font-weight:600}
  .doc code{font-family:ui-monospace,Menlo,monospace;font-size:.86em;background:var(--panel);border:1px solid var(--line);border-radius:4px;padding:.1em .4em}
  .hub-section{margin:56px 0 0}
  .hub-section-head{margin-bottom:16px}
  .hub-section-head h2{font-family:"Noto Serif KR",serif;font-size:20px;font-weight:500;margin:0}
  .hub-section-head p{margin:6px 0 0;color:var(--sub);font-size:14px}
  .table-scroll{overflow-x:auto;margin:14px 0;border:1px solid var(--line);border-radius:8px}
  .doc table{border-collapse:collapse;width:100%;min-width:520px;font-size:14px}
  .doc th,.doc td{text-align:left;padding:10px 14px;border-bottom:1px solid var(--line);vertical-align:top}
  .doc th{background:var(--panel);font-weight:600;color:var(--sub);font-size:13px;white-space:nowrap}
  .doc tbody tr:last-child td{border-bottom:none}
  .doc .ok{color:var(--c-live);font-weight:600}
  .callout{border:1px solid var(--line);border-left:2px solid var(--sub);background:var(--panel);border-radius:6px;padding:14px 18px;margin:16px 0;font-size:14px}
  .callout p:last-child{margin-bottom:0}
  .callout-label{font-weight:600;margin-bottom:6px}
  .callout--tip{border-left-color:var(--c-wip)} .callout--tip .callout-label{color:var(--c-wip)}
  .callout--warning{border-left-color:#d08a7c}
  .goal{font-size:15px;color:var(--sub);max-width:640px;line-height:1.75;margin:14px 0 0}
  .tags{display:flex;flex-wrap:wrap;gap:6px;margin-top:16px}
  .tags .tag{font-size:12px;padding:3px 10px;border-radius:999px;border:1px solid var(--line);color:var(--sub)}
  .tags .tag.time{color:var(--c-wip);border-color:color-mix(in srgb,var(--c-wip) 40%,transparent)}
  .doc h4{font-size:13px;font-weight:600;letter-spacing:.08em;color:var(--faint);margin:0 0 10px}
  .practice-card{border:1px solid var(--line);border-radius:8px;background:var(--panel);padding:18px 20px;margin:16px 0}
  .practice-title{font-weight:600;font-size:15px;margin:0 0 8px;color:var(--ink)}
  .practice-card>p{margin:0;font-size:14px;color:var(--sub)}
  .practice-prep{border-top:1px solid var(--line);margin-top:14px;padding-top:12px;font-size:13px}
  .practice-prep .prep-label{font-weight:600;margin-bottom:4px;color:var(--sub)}
  .practice-prep ul{list-style:none;padding:0;margin:0} .practice-prep li{margin:0 0 .2em}
  .practice-prep .meta{display:inline;color:var(--faint);border:0;padding:0;margin:0;font-size:inherit}
  .adjust,.out{border-radius:6px;padding:12px 16px;margin:14px 0;font-size:14px;color:var(--sub)}
  .adjust{border:1px dashed var(--line)}
  .out{background:var(--panel);border:1px solid var(--line)}
  .snav{display:flex;justify-content:space-between;gap:12px;margin-top:48px}
  .snav a{flex:1;border:1px solid var(--line);border-radius:8px;padding:14px 16px;text-decoration:none;color:var(--ink);font-size:14px}
  .snav a:hover{border-color:var(--sub)}
  .snav small{display:block;font-size:11px;color:var(--faint);letter-spacing:.08em;margin-bottom:2px}
  .snav .nx{text-align:right}
  .back{display:inline-block;font-size:13px;color:var(--sub);text-decoration:none;margin-bottom:18px}
  .back:hover{color:var(--ink)}
"""

def shell(title, inner, back=""):
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{e(title)} · 이주형 클래스</title>
{fonts}
<style>{css}{PAGE_CSS}{CONTENT_CSS}{TBAR_CSS}</style>
</head>
<body class="stu">
<div class="wrap">
{inner}
</div>
</body>
</html>
"""

def strip_emoji(t):
    return re.sub("[\U0001F300-\U0001FAFF☀-➿⏰-⏿️]\\s?", "", t)

def course_with_content(it, folder):
    cdir = os.path.join(ROOT, "content", it["content"])
    where = " · ".join(x for x in ["SBS아카데미컴퓨터AIX학원"] if x)
    title = e(it["title"])
    meta = "".join(f"<span>{e(m)}</span>" for m in it.get("meta") or [])
    phases = "".join(f"<span>{e(m)}</span>" for m in it.get("phases") or [])
    projs = it.get("projects") or []
    cards = "".join(f'<a class="pcard" href="{folder}/{p["doc"]}.html"><span class="pno">{p["doc"]}차시</span><h3>{e(p["title"])}</h3><span class="ps">열기 →</span></a>' if p.get("doc")
                    else f'<div class="pcard ready"><span class="pno">{i:02d}</span><h3>{e(p["title"])}</h3><span class="ps">준비 중</span></div>' for i, p in enumerate(projs, 1))
    ov = open(os.path.join(cdir, "overview.html"), encoding="utf-8").read() if os.path.exists(os.path.join(cdir, "overview.html")) else ""
    inner = f"""  <header>
    {tbar([("홈","../index.html#/"),("수업 과정","../index.html#/course"),(it["title"],None)])}
    <span class="d-eyebrow">{e(where)}</span>
    <h1 class="d-title">{title}</h1>
    {f'<p class="lead d-lead">{e(it["subtitle"])}</p>' if it.get("subtitle") else ""}
    {f'<p class="lead d-lead">{e(it["desc"])}</p>' if it.get("desc") else ""}
    {f'<div class="meta-row">{meta}</div>' if meta else ""}
  </header>
  <main>
    <h2 class="d-sec">차시별 수업</h2>
    <div class="pgrid">{cards}</div>
    {f'<div class="phase">{phases}</div>' if phases else ""}
    <div class="doc">{strip_emoji(ov)}</div>
    <div class="d-foot">{e(" · ".join(x for x in ["SBS아카데미컴퓨터AIX학원", it["title"], it.get("subtitle")] if x))}</div>
  </main>"""
    return shell(it["title"], inner)

def session_page(it, idx, folder_name):
    projs = it["projects"]; p = projs[idx]
    raw = open(os.path.join(ROOT, "content", it["content"], p["doc"] + ".html"), encoding="utf-8").read()
    h3 = re.search(r"<h3>(.*?)</h3>", raw, re.S); goal = re.search(r'<p class="goal">(.*?)</p>', raw, re.S)
    tags = re.search(r'<div class="tags">(.*?)</div>', raw, re.S)
    body = re.sub(r'<div class="day-head">.*?</div>\s*', "", raw, count=1, flags=re.S)
    body = re.sub(r'<p class="goal">.*?</p>\s*', "", body, count=1, flags=re.S)
    body = re.sub(r'<div class="tags">.*?</div>\s*', "", body, count=1, flags=re.S)
    prev = projs[idx-1] if idx > 0 and projs[idx-1].get("doc") else None; nxt = projs[idx+1] if idx+1 < len(projs) and projs[idx+1].get("doc") else None
    nav = '<nav class="snav">' + (f'<a href="{prev["doc"]}.html"><small>← {prev["doc"]}차시</small>{e(prev["title"])}</a>' if prev else "<span style=flex:1></span>") \
        + (f'<a class="nx" href="{nxt["doc"]}.html"><small>{nxt["doc"]}차시 →</small>{e(nxt["title"])}</a>' if nxt else "<span style=flex:1></span>") + "</nav>"
    inner = f"""  <header>
    {tbar([("홈","../../index.html#/"),("수업 과정","../../index.html#/course"),(it["title"],f"../{folder_name}.html"),(p["doc"]+"차시",None)])}
    <a class="back" href="../{folder_name}.html">← {e(it["title"])} 전체</a><br>
    <span class="d-eyebrow">{e(it["title"])} · {p["doc"]}차시</span>
    <h1 class="d-title">{h3.group(1) if h3 else e(p["title"])}</h1>
    {f'<p class="goal">{goal.group(1)}</p>' if goal else ""}
    {f'<div class="tags">{tags.group(1)}</div>' if tags else ""}
  </header>
  <main class="doc">
    {strip_emoji(body)}
    {nav}
    <div class="d-foot">{e(it["title"])} · {p["doc"]}차시</div>
  </main>"""
    return shell(f'{p["doc"]}차시 · {p["title"]}', inner)

import shutil

os.makedirs(OUT, exist_ok=True)
keep = set()
for cat in data:
    if cat["id"] not in STUDENT_CATS:
        continue
    for it in cat["items"]:
        if not it.get("key"):
            continue
        name = f'{it["id"]}-{it["key"]}.html'
        keep.add(name)
        base = name[:-5]
        if it.get("content"):
            open(os.path.join(OUT, name), "w", encoding="utf-8").write(course_with_content(it, base))
            d = os.path.join(OUT, base); os.makedirs(d, exist_ok=True)
            for f in os.listdir(d): os.remove(os.path.join(d, f))
            for i in range(len(it["projects"])):
                if not it["projects"][i].get("doc"): continue
                open(os.path.join(d, it["projects"][i]["doc"] + ".html"), "w", encoding="utf-8").write(session_page(it, i, base))
            keep.add(base)
        else:
            open(os.path.join(OUT, name), "w", encoding="utf-8").write(page(cat, it))
for f in os.listdir(OUT):
    fp = os.path.join(OUT, f)
    if f.endswith(".html") and f not in keep: os.remove(fp)
    elif os.path.isdir(fp) and f not in keep: shutil.rmtree(fp)
print(f"학생 페이지 {len([k for k in keep if k.endswith('.html')])}개 생성")
