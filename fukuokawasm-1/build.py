#!/usr/bin/env python3
"""Build Marp HTML, then inline the flow diagram and marked WAT SVG prototype."""
from pathlib import Path
import html
import re
import subprocess

root = Path(__file__).resolve().parent
subprocess.run(['marp', '--no-stdin', 'index.md', '-o', 'index.html'], cwd=root, check=True)
output = root / 'index.html'
page = output.read_text()
converted = 0

def convert_section(match):
    global converted
    section = match.group(0)
    if not re.search(r'class="[^"]*\bsvg-hover\b', section):
        return section
    def convert_code(code_match):
        global converted
        code = html.unescape(code_match.group(1)).rstrip('\n')
        lines = code.split('\n')
        height = 36 + 27 * len(lines)
        rows = []
        for index, line in enumerate(lines):
            y = 18 + index * 27
            rows.append(
                f'<g class="code-line" transform="translate(0 {y})">'
                '<rect class="line-hit" x="3" width="1117" height="27" />'
                '<rect class="line-mark" width="3" height="27" />'
                f'<text x="27" y="20" xml:space="preserve">{html.escape(line)}</text></g>')
        converted += 1
        return (f'<svg xmlns="http://www.w3.org/2000/svg" class="hover-code" '
                f'viewBox="0 0 1120 {height}" width="1120" height="{height}" '
                'role="img" aria-label="WAT: タグ付き例外を捕捉して42を返す">'
                f'<title>{html.escape(code)}</title>'
                f'<rect class="code-stripe" width="3" height="{height}" />'
                '<g class="code-lines">' + ''.join(rows) + '</g></svg>')
    return re.sub(r'<pre\b[^>]*><code class="language-wat">(.*?)</code></pre>',
                  convert_code, section, flags=re.S)

page = re.sub(r'<section\b[^>]*>.*?</section>', convert_section, page, flags=re.S)
if converted != 1:
    raise SystemExit(f'Expected one marked WAT block, got {converted}')
diagram = re.compile(r'<div class="sjlj-diagram"><img\b[^>]*\bsrc="images/sjlj-flow\.svg"[^>]*></div>')
page, diagram_count = diagram.subn(
    lambda _: '<div class="sjlj-diagram">' + (root / 'images/sjlj-flow.svg').read_text() + '</div>',
    page)
if diagram_count != 1:
    raise SystemExit(f'Expected one SjLj diagram, got {diagram_count}')
css = '''
<style id="svg-code-hover">
.sjlj-diagram { flex-shrink:0; margin:12px 0 18px; }
svg.hover-code { display:block; flex-shrink:0; width:100%; max-width:100%;
  margin:12px 0 18px; overflow:hidden; background:#eeeee4; transition:background-color 120ms ease;
  border-top:1px solid #d5d7cd; border-bottom:1px solid #d5d7cd; }
.hover-code text { font-family:Menlo,monospace; font-size:20px;
  letter-spacing:0; fill:#252924; white-space:pre; pointer-events:none; }
.hover-code .line-hit { fill:transparent; pointer-events:all; transition:fill 120ms ease; }
.hover-code .code-stripe { fill:#b53d27; opacity:.35; pointer-events:none; }
.hover-code .line-mark { fill:#b53d27; opacity:0; pointer-events:none;
  transition:opacity 120ms ease; }
@media (hover:hover) {
  svg.hover-code:has(.code-line:hover) { background:#d3d5c9; }
  .hover-code .code-lines:has(.code-line:hover) .line-hit { fill:#d3d5c9; }
  .hover-code .code-lines .code-line:hover .line-hit { fill:#fffdf9; }
  .hover-code .code-line:hover .line-mark { opacity:1; }
}
@media (prefers-reduced-motion:reduce) {
  svg.hover-code, .hover-code text, .hover-code rect { transition:none; }
}
@media print {
  svg.hover-code { background:#eeeee4 !important; }
  .hover-code .code-line text { opacity:1 !important; }
  .hover-code .line-hit { fill:transparent !important; }
  .hover-code .line-mark { opacity:0 !important; }
}
</style>
'''
page = page.replace('</head>', css + '</head>', 1)
output.write_text(page)
print('Converted one WAT block to hoverable inline SVG.')
print('Inlined the hoverable SjLj flow diagram.')
