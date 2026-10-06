# 枠付きの四角形と、その中に収まる文字を <g class="box"> にまとめ、ホバー演出の <style> を足す。
# 使い方: cd assets && python3 add_hover.py file.svg ...
#
# ■ 新しい図を足すときの手順
#   1. 日本語版の SVG（例: new-diagram.svg）を assets/ に作る
#      - 文字は <g font-family="..."> の直下に <text x= y=> で置く（x, y で四角形に入っているか判定する）
#      - ホバーさせたい四角形には stroke を付ける。stroke のない <rect>（背景や文字の下敷き）は対象外
#      - 光る色は stroke で決まる: #ceff05 → ライム / #ff58af → ピンク / それ以外 → 白
#   2. python3 add_hover.py new-diagram.svg
#      - <style> がすでにある SVG はスキップするので、何度実行しても安全
#   3. svg_en.py の対応表 T に new-diagram の訳を足して python3 svg_en.py
#      - new-diagram-en.svg ができる。英語版にもホバー演出が引き継がれる
#   4. スライドには <img> ではなく <object> で埋め込む（<img> だとホバーが効かない）
#        <object type="image/svg+xml" data="assets/new-diagram.svg" width="1100" height="460" aria-label="説明">
#        <img src="assets/new-diagram.svg" alt="説明" width="1100"></object>
#      - height は SVG の viewBox の高さに合わせる。英語版（index.md）は -en.svg を指す
#      - HTML 書き出しには --html（VS Code なら markdown.marp.enableHtml）が必要
#
# ■ 既存の図を直すとき
#   - 日本語版の SVG を直接編集し、svg_en.py で英語版を作り直す
#   - <g class="box"> の外に文字を足した場合は、ホバー時に一緒に動かないので、手で <g> の中へ移す
#   - <style> 内に日本語や「<」を書かない（svg_en.py が止まる / XML として壊れる）
import sys
import xml.etree.ElementTree as ET

NS = 'http://www.w3.org/2000/svg'
ET.register_namespace('', NS)
q = lambda tag: f'{{{NS}}}{tag}'

STYLE = """
/* Hover effect: works only when embedded as an object element in a browser. Static in PDF and images. */
.box { --glow: #ceff05; --hover-fill: #3a4422; transform-box: fill-box; transform-origin: center; transition: transform .2s ease, filter .2s ease; }
.box.gray { --glow: #ffffff; --hover-fill: #444444; }
.box.pink { --glow: #ff58af; --hover-fill: #4a2a3f; }
.box rect { transition: fill .2s ease; }
.box:hover { transform: scale(1.04); filter: drop-shadow(0 0 10px var(--glow)); }
.box:hover rect { fill: var(--hover-fill); }
@media (prefers-reduced-motion: reduce) { .box, .box rect { transition: none; } .box:hover { transform: none; } }
"""

def color_class(stroke):
    s = stroke.lower()
    if s == '#ff58af': return 'box pink'
    if s == '#ceff05': return 'box'
    return 'box gray'

def process(path):
    tree = ET.parse(path)
    root = tree.getroot()
    if root.find(q('style')) is not None:
        print(f'skip {path}: already has <style>'); return
    content = next(g for g in root.findall(q('g')) if g.get('font-family'))

    # 属性だけを持つ入れ子の <g>（rect をまとめて塗っているもの）を平らにする
    for i, child in list(enumerate(list(content))):
        if child.tag == q('g') and len(child) and all(c.tag == q('rect') for c in child):
            idx = list(content).index(child)
            content.remove(child)
            for j, r in enumerate(list(child)):
                for k, v in child.attrib.items():
                    r.attrib.setdefault(k, v)
                content.insert(idx + j, r)

    texts = [t for t in content if t.tag == q('text')]
    used = set()
    for rect in [r for r in content if r.tag == q('rect') and r.get('stroke')]:
        x, y = float(rect.get('x')), float(rect.get('y'))
        w, h = float(rect.get('width')), float(rect.get('height'))
        inner = [t for t in texts if id(t) not in used
                 and x <= float(t.get('x')) <= x + w and y <= float(t.get('y')) <= y + h]
        idx = list(content).index(rect)
        group = ET.Element(q('g'), {'class': color_class(rect.get('stroke'))})
        content.remove(rect)
        group.append(rect)
        for t in inner:
            content.remove(t)
            group.append(t)
            used.add(id(t))
        content.insert(idx, group)

    style = ET.Element(q('style'))
    style.text = STYLE
    desc_idx = list(root).index(root.find(q('desc')))
    root.insert(desc_idx + 1, style)
    tree.write(path, encoding='unicode', xml_declaration=False)
    print(f'wrote {path}: {len([g for g in content if g.get("class", "").startswith("box")])} boxes')

for p in sys.argv[1:]:
    process(p)
