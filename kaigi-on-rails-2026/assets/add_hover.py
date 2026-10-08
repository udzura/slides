# 図（SVG）にホバー演出を入れる。
#   - 枠付きの四角形と、その中に収まる文字・アイコンを <g class="box"> にまとめる（入れ子にも対応）
#   - 矢印（marker-end 付きの path）に class="flow" を付け、図にマウスを乗せると流れるようにする
# 使い方: cd assets && python3 add_hover.py file.svg ...
#   何度実行しても安全（すでに演出がある図は、足りない部分だけ補う）
#
# ■ 正本について
#   英語版（*-en.svg と index.md）が正本。英語版の SVG を直接作り・直し、このスクリプトをかける。
#   svg_en.py（日本語版から英語版を作る）は、手で直した英語版を上書きしてしまうので使わない。
#
# ■ 新しい図を足すときの手順
#   1. assets/ に SVG を作る（例: new-diagram-en.svg）
#      - 図全体を <g font-family="..."> で包み、その直下に <rect> / <text x= y=> などを置く
#      - ホバーさせたい四角形には stroke を付ける。stroke のない <rect>（背景や下敷き）は対象外
#      - 光る色は stroke で決まる: #ceff05 → ライム / #ff58af → ピンク / それ以外 → 白
#   2. python3 add_hover.py new-diagram-en.svg
#   3. スライドには <img> ではなく <object> で埋め込む（<img> だとホバーが効かない）
#        <object type="image/svg+xml" data="assets/new-diagram-en.svg" width="1100" height="460" aria-label="説明">
#        <img src="assets/new-diagram-en.svg" alt="説明" width="1100"></object>
#      - height は SVG の viewBox の高さに合わせる
#      - HTML 書き出しには --html（VS Code なら markdown.marp.enableHtml）が必要
#
# ■ 既存の図を直すとき
#   - 四角形の外に文字を足すと、ホバー時に一緒に動かない。四角形の中に収めるか、手で <g> の中へ移す
#   - <style> 内に「<」を書かない（XML として壊れる）
#   - 流したくない矢印（グラフの軸など）には class="no-flow" を付ける
import re
import sys
import xml.etree.ElementTree as ET

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
q = lambda tag: f'{{{NS}}}{tag}'

STYLE_BOX = """
/* Hover effect: works only when embedded as an object element in a browser. Static in PDF and images. */
.box { --glow: #ceff05; --hover-fill: #3a4422; transform-box: fill-box; transform-origin: center; transition: transform .2s ease, filter .2s ease; }
.box.gray { --glow: #ffffff; --hover-fill: #444444; }
.box.pink { --glow: #ff58af; --hover-fill: #4a2a3f; }
.box > rect { transition: fill .2s ease; }
.box:hover:not(:has(.box:hover)) { transform: scale(1.04); filter: drop-shadow(0 0 10px var(--glow)); }
.box:hover:not(:has(.box:hover)) > rect { fill: var(--hover-fill); }
@media (prefers-reduced-motion: reduce) { .box, .box > rect { transition: none; } .box:hover { transform: none; } }
"""
STYLE_FLOW = """
/* Flow effect: arrows march while the pointer is on the diagram. */
svg:hover .flow { stroke-dasharray: 12 6; animation: flow .8s linear infinite; }
@keyframes flow { to { stroke-dashoffset: -18; } }
@media (prefers-reduced-motion: reduce) { svg:hover .flow { animation: none; stroke-dasharray: none; } }
"""


def color_class(stroke):
    s = stroke.lower()
    if s == '#ff58af':
        return 'box pink'
    if s == '#ceff05':
        return 'box'
    return 'box gray'


def rect_box(r):
    x, y = float(r.get('x', 0)), float(r.get('y', 0))
    return x, y, x + float(r.get('width')), y + float(r.get('height'))


def path_box(d):
    # 絶対座標のコマンド（M L H V Q C Z）だけを想定した、ざっくりした外接矩形
    xs, ys, cx, cy = [], [], 0.0, 0.0
    for cmd, args in re.findall(r'([MLHVQCZ])([^MLHVQCZ]*)', d):
        n = [float(v) for v in re.findall(r'-?\d+(?:\.\d+)?', args)]
        if cmd == 'H':
            for v in n:
                cx = v; xs.append(cx); ys.append(cy)
        elif cmd == 'V':
            for v in n:
                cy = v; xs.append(cx); ys.append(cy)
        elif cmd != 'Z':
            for i in range(0, len(n) - 1, 2):
                cx, cy = n[i], n[i + 1]; xs.append(cx); ys.append(cy)
    return (min(xs), min(ys), max(xs), max(ys)) if xs else None


def elem_box(e):
    tag = e.tag.split('}')[1]
    if tag == 'text':
        x, y = float(e.get('x')), float(e.get('y'))
        return x, y, x, y
    if tag == 'circle':
        cx, cy, r = float(e.get('cx')), float(e.get('cy')), float(e.get('r'))
        return cx - r, cy - r, cx + r, cy + r
    if tag == 'path' and not e.get('marker-end'):
        return path_box(e.get('d', ''))
    if tag == 'rect' and not e.get('stroke') and e.get('x') is not None:
        return rect_box(e)
    return None


def inside(inner, outer):
    return outer[0] <= inner[0] and outer[1] <= inner[1] and inner[2] <= outer[2] and inner[3] <= outer[3]


def area(b):
    return (b[2] - b[0]) * (b[3] - b[1])


def add_style(root, css):
    style = root.find(q('style'))
    if style is None:
        style = ET.Element(q('style'))
        style.text = ''
        root.insert(0, style)
    style.text = (style.text or '') + css


def process(path):
    tree = ET.parse(path)
    root = tree.getroot()
    content = next(g for g in root.iter(q('g')) if g.get('font-family'))
    css = root.find(q('style'))
    css = css.text if css is not None else ''

    # 矢印に flow を付ける
    # class="no-flow" の矢印（グラフの軸など）は流さない
    marked = {id(p) for g in root.iter(q('g')) if g.get('marker-end') for p in g.iter(q('path'))}
    arrows = [p for p in root.iter(q('path'))
              if (p.get('marker-end') or id(p) in marked) and 'no-flow' not in (p.get('class') or '')]
    for p in arrows:
        if 'flow' not in (p.get('class') or '').split():
            p.set('class', (p.get('class', '') + ' flow').strip())
    if arrows and '.flow' not in css:
        add_style(root, STYLE_FLOW)

    # すでに <style> を持つ図（演出済み、または計測グラフなど独自の演出）は、箱の演出を足さない
    if css.strip():
        tree.write(path, encoding='unicode', xml_declaration=False)
        print(f'{path}: has its own style; flow on {len(arrows)} arrows')
        return

    # 属性だけを持つ入れ子の <g>（rect をまとめて塗っているもの）を平らにする
    for child in list(content):
        if child.tag == q('g') and len(child) and all(c.tag == q('rect') for c in child):
            idx = list(content).index(child)
            content.remove(child)
            for j, r in enumerate(list(child)):
                for k, v in child.attrib.items():
                    r.attrib.setdefault(k, v)
                content.insert(idx + j, r)

    kids = list(content)
    boxes = [r for r in kids if r.tag == q('rect') and r.get('stroke') and r.get('x') is not None]
    bbox = {id(r): rect_box(r) for r in boxes}

    def smallest_container(b, exclude=None):
        cands = [r for r in boxes if r is not exclude and inside(b, bbox[id(r)])]
        return min(cands, key=lambda r: area(bbox[id(r)])) if cands else None

    parent = {id(r): smallest_container(bbox[id(r)], exclude=r) for r in boxes}
    owner = {}
    for e in kids:
        if e in boxes:
            continue
        b = elem_box(e)
        if b is not None:
            c = smallest_container(b)
            if c is not None:
                owner[id(e)] = c

    groups = {id(r): ET.Element(q('g'), {'class': color_class(r.get('stroke'))}) for r in boxes}
    for e in kids:  # 文書の順序を保ったまま、各 group に詰める
        if e in boxes:
            g = groups[id(e)]
            g.insert(0, e)
            p = parent[id(e)]
            if p is not None:
                groups[id(p)].append(g)
        elif id(e) in owner:
            groups[id(owner[id(e)])].append(e)

    new_kids = []
    for e in kids:
        if e in boxes:
            if parent[id(e)] is None:
                new_kids.append(groups[id(e)])
        elif id(e) not in owner:
            new_kids.append(e)
    for e in kids:
        content.remove(e)
    for e in new_kids:
        content.append(e)

    add_style(root, STYLE_BOX)
    tree.write(path, encoding='unicode', xml_declaration=False)
    print(f'{path}: {len(boxes)} boxes, flow on {len(arrows)} arrows')


for p in sys.argv[1:]:
    process(p)
