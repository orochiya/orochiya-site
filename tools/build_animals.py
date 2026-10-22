#!/usr/bin/env python3
"""tools/animals.json から、トップの生体コーナー（カテゴリ入口）と
カテゴリ別ページ animals-<id>.html を生成する。

使い方: リポジトリ直下で  python3 tools/build_animals.py
"""
import html, json, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
INDEX = os.path.join(ROOT, 'index.html')
DATA = json.load(open(os.path.join(ROOT, 'tools', 'animals.json'), encoding='utf-8'))
CATS = DATA['categories']
IMG = 'img/animals/'
esc = html.escape

ANIMAL_CSS = '''.animals{display:grid;grid-template-columns:repeat(auto-fill,minmax(220px,1fr));gap:16px;list-style:none;margin:0;padding:0}
.animal{background:var(--card);border:1px solid var(--line);border-radius:8px;overflow:hidden;display:flex;flex-direction:column}
.animal .ph{position:relative;margin:0;padding:0;border:0;background:#000;cursor:pointer;display:block;width:100%}
.animal .main{aspect-ratio:1/1;width:100%;object-fit:cover}
.animal .count{position:absolute;top:8px;right:8px;background:rgba(0,0,0,.6);color:#fff;font-size:11px;font-weight:600;padding:2px 7px;border-radius:10px;font-variant-numeric:tabular-nums}
.animal .body{padding:12px 14px 14px;display:flex;flex-direction:column;gap:6px;flex:1}
.animal .name{font-size:15px;font-weight:600;line-height:1.5}
.animal .name small{display:block;color:var(--muted);font-size:12px;font-weight:500}
.animal .price{margin-top:auto;font-weight:700;font-size:17px;font-variant-numeric:tabular-nums}
.animal .price span{display:block;font-size:13px;font-weight:600}
.animal.hold{opacity:.75}
.animal .tag{display:inline-block;align-self:flex-start;font-size:11px;font-weight:700;letter-spacing:.06em;padding:2px 8px;border-radius:3px;background:var(--accent-dark);color:var(--text)}
.cats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;list-style:none;margin:0;padding:0}
.cat{display:block;position:relative;border:1px solid var(--line);border-radius:8px;overflow:hidden;background:var(--card);color:var(--text);text-decoration:none}
.cat .cv{aspect-ratio:4/3;width:100%;object-fit:cover;background:#000}
.cat .cv-none{aspect-ratio:4/3;display:flex;align-items:center;justify-content:center;color:var(--muted);font-size:13px;background:linear-gradient(135deg,#141918,#0c0f0f)}
.cat .cb{display:flex;align-items:baseline;justify-content:space-between;gap:8px;padding:12px 14px}
.cat .cn{font-size:17px;font-weight:700}
.cat .cc{font-size:13px;color:var(--muted);white-space:nowrap}
.cat .cc b{color:var(--accent);font-size:15px;margin-right:2px}
.cat:hover{border-color:var(--accent)}
.cat-switch{display:flex;gap:6px;margin:0 0 24px;flex-wrap:wrap}
.cat-switch a{flex:1;min-width:0;text-align:center;padding:9px 4px;border:1px solid var(--line);border-radius:6px;color:var(--muted);text-decoration:none;font-size:14px;font-weight:600;white-space:nowrap}
.cat-switch a small{font-size:11px;font-weight:500;margin-left:2px;opacity:.8}
.cat-switch a[aria-current="page"]{background:var(--accent);border-color:var(--accent);color:#06211e}
.crumb{font-size:12px;color:var(--muted);margin:0 0 18px}
.crumb a{color:var(--muted)}
.page-head{padding-top:40px;padding-bottom:8px}
.page-head h1{font-size:clamp(24px,5vw,34px);margin:0 0 8px}
@media (max-width:760px){.cats{grid-template-columns:repeat(2,1fr);gap:10px}.cat .cb{padding:10px 12px}.cat .cn{font-size:15px}}
@media (max-width:640px){
  .animals{grid-template-columns:repeat(2,1fr);gap:10px}
  .animal .body{padding:10px}.animal .name{font-size:13px}.animal .price{font-size:15px}
  .cat-switch a{font-size:13px}
}
'''

PHOTO_JS = '''<script>
document.querySelectorAll('.animal .ph').forEach(function(b){
  var l=b.dataset.srcs.split(','),i=0,m=b.querySelector('.main'),c=b.querySelector('.count');
  if(l.length<2){c.remove();return}
  b.addEventListener('click',function(){i=(i+1)%l.length;m.src=l[i];c.textContent=(i+1)+'/'+l.length});
});
</script>'''


def page_url(c):
    return f"animals-{c['id']}.html"


def card(a):
    name, sub = esc(a['name']), esc(a.get('sub', ''))
    alt = f"{name} {sub}".strip()
    subh = f'<small>{sub}</small>' if sub else ''
    price = a['price']
    priceh = ''.join(f'<span>{esc(p)}</span>' for p in price) if isinstance(price, list) else esc(price)
    hold = a.get('status') == 'hold'
    tag = '<span class="tag">商談中</span>' if hold else ''
    ph = ''
    if a['photos']:
        srcs = [IMG + p for p in a['photos']]
        ph = (f'<button type="button" class="ph" data-srcs="{",".join(srcs)}" aria-label="{alt}の次の写真">'
              f'<img class="main" src="{srcs[0]}" alt="{alt}" loading="lazy" width="600" height="600">'
              f'<span class="count">1/{len(srcs)}</span></button>')
    cls = 'animal hold' if hold else 'animal'
    return (f'        <li class="{cls}">\n          {ph}\n'
            f'          <div class="body">{tag}<div class="name">{name}{subh}</div><div class="price">{priceh}</div></div>\n'
            f'        </li>')


def cat_cards():
    out = []
    for c in CATS:
        n = len(c['animals'])
        cv = (f'<img class="cv" src="{IMG}{c["cover"]}" alt="{esc(c["name"])}" loading="lazy" width="600" height="450">'
              if c['cover'] else '<div class="cv-none">写真準備中</div>')
        out.append(f'        <li><a class="cat" href="{page_url(c)}">{cv}'
                   f'<span class="cb"><span class="cn">{esc(c["name"])}</span><span class="cc"><b>{n}</b>件 →</span></span></a></li>')
    return '      <ul class="cats">\n' + '\n'.join(out) + '\n      </ul>'


def main():
    s = open(INDEX, encoding='utf-8').read()

    # 1) CSS（.animals{ 〜 .note{ の間を差し替え）
    a, b = s.index('.animals{'), s.index('.note{font-size:13px;')
    s = s[:a] + ANIMAL_CSS + s[b:]

    # 2) トップの生体コーナー
    sec_a = s.index('<section id="animals">')
    sec_b = s.index('</section>', sec_a)
    sec = s[sec_a:sec_b]
    head = re.search(r'(.*?<p class="lead">.*?</p>\n)', sec, re.S).group(1)
    tail = re.search(r'(      <p class="note">生体の状態.*)', sec, re.S).group(1)
    tail = tail.replace('style="margin-top:20px"', 'style="margin-top:20px"')
    new_sec = head + '<!--animals:start-->\n' + cat_cards() + '\n<!--animals:end-->\n\n' + tail
    s = s[:sec_a] + new_sec + s[sec_b:]

    # 3) トップのスクリプト（生体カード用）は不要なので除去
    s = re.sub(r'<script>.*?</script>\n', '', s, flags=re.S)
    open(INDEX, 'w', encoding='utf-8').write(s)

    # 4) カテゴリ別ページ
    style = re.search(r'<style>.*?</style>', s, re.S).group(0)
    fonts = re.search(r'(<link rel="preconnect".*?rel="stylesheet">)', s, re.S).group(1)
    header = re.search(r'<header>.*?</header>', s, re.S).group(0)
    header = re.sub(r'href="#(?!top)', 'href="./#', header).replace('href="#top"', 'href="./"')
    footer = re.search(r'<footer>.*?</footer>', s, re.S).group(0).replace('href="#top"', 'href="./"')
    note = re.search(r'(      <p class="note">生体の状態.*?</div>\n)', tail, re.S).group(1)

    for c in CATS:
        n = len(c['animals'])
        sw = ''.join(
            f'<a href="{page_url(x)}"{" aria-current=\"page\"" if x is c else ""}>{esc(x["name"])}<small>{len(x["animals"])}</small></a>'
            for x in CATS)
        title = f'{c["name"]}の生体一覧｜大蛇屋 San-in Reptiles（米子の爬虫類専門店）'
        desc = f'鳥取県米子市の爬虫類専門店・大蛇屋 San-in Reptilesで販売中の{c["name"]}（{n}件）。写真・価格（税込）を掲載しています。'
        cards = '\n'.join(card(a) for a in c['animals'])
        doc = f'''<!doctype html>
<html lang="ja">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{esc(title)}</title>
<meta name="description" content="{esc(desc)}">
<link rel="canonical" href="https://orochiya.jp/{page_url(c)}">
<meta property="og:title" content="{esc(title)}">
<meta property="og:description" content="{esc(desc)}">
<meta property="og:type" content="website">
<meta property="og:url" content="https://orochiya.jp/{page_url(c)}">
<meta property="og:image" content="https://orochiya.jp/{IMG + c['cover'] if c['cover'] else 'orochiya-exterior.jpeg'}">
{fonts}
{style}
</head>
<body id="top">

{header}

<main>
  <div class="wrap page-head">
    <p class="crumb"><a href="./">トップ</a> ／ <a href="./#animals">生体</a> ／ {esc(c["name"])}</p>
    <p class="eyebrow">SELECTED ANIMALS</p>
    <h1>{esc(c["name"])}の生体一覧</h1>
    <p class="lead">表示価格は税込です。写真をタップすると次の写真に切り替わります。最新の販売状況はInstagramで確認できます。</p>
  </div>
  <section style="border-top:0;padding-top:8px">
    <div class="wrap">
      <nav class="cat-switch" aria-label="生体の種類">{sw}</nav>
      <ul class="animals">
{cards}
      </ul>
{note}    </div>
  </section>
</main>

{footer}
{PHOTO_JS}
</body>
</html>
'''
        open(os.path.join(ROOT, page_url(c)), 'w', encoding='utf-8').write(doc)
        print('wrote', page_url(c), n, '件')


if __name__ == '__main__':
    main()
