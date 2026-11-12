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

def page(cat, it):
    where = " · ".join(x for x in ["SBS아카데미AIX 안산", it.get("group")] if x)
    title = e(it["title"]) + (f' <span class="sub">·</span> {e(it["subtitle"])}' if it.get("subtitle") else "")
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
    foot = " · ".join(x for x in ["SBS아카데미AIX 안산", it["title"], it.get("subtitle")] if x)
    return f"""<!doctype html>
<html lang="ko">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<meta name="robots" content="noindex, nofollow">
<title>{e(it["title"])} · 이주형 클래스</title>
{fonts}
<style>{css}{PAGE_CSS}</style>
</head>
<body class="stu">
<div class="wrap">
  <header>
    <span class="d-eyebrow">{e(where)}</span>
    <h1 class="d-title">{title}</h1>
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
        open(os.path.join(OUT, name), "w", encoding="utf-8").write(page(cat, it))
for f in os.listdir(OUT):
    if f.endswith(".html") and f not in keep:
        os.remove(os.path.join(OUT, f))
print(f"학생 페이지 {len(keep)}개 생성")
