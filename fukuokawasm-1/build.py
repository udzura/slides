#!/usr/bin/env python3
"""Build Marp HTML with hoverable source code and inline SjLj diagrams."""
from collections import Counter
from html.parser import HTMLParser
from pathlib import Path
import html
import re
import subprocess

root = Path(__file__).resolve().parent
subprocess.run(['marp', '--no-stdin', 'index.md', '-o', 'index.html'], cwd=root, check=True)
output = root / 'index.html'
page = output.read_text()
# Only source-code fences are interactive. Commands (sh), output (text), and
# unlabelled fences stay as Marp-generated pre elements.
source_languages = {'c': 'C', 'cpp': 'C++', 'js': 'JavaScript', 'wat': 'WAT'}
converted = Counter()


class HighlightedCode(HTMLParser):
    """Split highlighted HTML into lines without losing text or token colors."""
    def __init__(self):
        super().__init__(convert_charrefs=True)
        self.lines = [[]]
        self.classes = []
        self.source = ''

    def handle_starttag(self, tag, attrs):
        if tag != 'span':
            raise ValueError(f'Unexpected element in highlighted code: {tag}')
        self.classes.append(dict(attrs).get('class', ''))

    def handle_endtag(self, tag):
        if tag != 'span' or not self.classes:
            raise ValueError(f'Unexpected closing element in highlighted code: {tag}')
        self.classes.pop()

    def handle_data(self, data):
        self.source += data
        for index, part in enumerate(data.split('\n')):
            if index:
                self.lines.append([])
            if part:
                classes = html.escape(' '.join(self.classes), quote=True)
                self.lines[-1].append(
                    f'<tspan class="{classes}">{html.escape(part)}</tspan>')


def highlight_wat(source):
    # Match strings/comments before atoms, so ;; or $ inside a string is literal.
    tokens = re.compile(
        r'(?P<comment>;;[^\n]*)|(?P<string>"(?:\\.|[^"\\])*")|'
        r'(?P<name>\$[^\s()";]+)|(?P<atom>[^\s()";]+)|(?P<other>.)', re.S)
    number = re.compile(
        r'[+-]?(?:0x[\da-fA-F_]+(?:\.[\da-fA-F_]*)?(?:[pP][+-]?[\d_]+)?|'
        r'\d[\d_]*(?:\.[\d_]*)?(?:[eE][+-]?[\d_]+)?|inf|nan(?::0x[\da-fA-F_]+)?)')
    classes = {'comment': 'hljs-comment', 'string': 'hljs-string',
               'name': 'wat-name', 'number': 'hljs-number'}
    highlighted = []
    for token in tokens.finditer(source):
        kind, text = token.lastgroup, token.group()
        if kind == 'atom' and number.fullmatch(text):
            kind = 'number'
        escaped = html.escape(text)
        if kind in classes:
            escaped = f'<span class="{classes[kind]}">{escaped}</span>'
        highlighted.append(escaped)
    return ''.join(highlighted)


def convert_code(match):
    language, highlighted = match.groups()
    if language not in source_languages:
        return match.group(0)
    parsed = HighlightedCode()
    parsed.feed(highlighted)
    parsed.close()
    if language == 'wat':
        highlighted = highlight_wat(parsed.source)
        parsed = HighlightedCode()
        parsed.feed(highlighted)
        parsed.close()
    # A code fence emits one final newline, which is not an extra display row.
    code = parsed.source.removesuffix('\n')
    lines = parsed.lines[:-1] if parsed.source.endswith('\n') else parsed.lines
    height = 36 + 27 * len(lines)
    rows = []
    for index, line in enumerate(lines):
        y = 18 + index * 27
        rows.append(
            f'<g class="code-line" transform="translate(0 {y})">'
            '<rect class="line-hit" x="3" width="1117" height="27" />'
            '<rect class="line-mark" width="3" height="27" />'
            f'<text x="27" y="20" xml:space="preserve">{"".join(line)}</text></g>')
    converted[language] += 1
    label = f'{source_languages[language]}のコード例（{len(lines)}行）'
    return (f'<svg xmlns="http://www.w3.org/2000/svg" class="hover-code" '
            f'data-language="{language}" '
            f'viewBox="0 0 1120 {height}" width="1120" height="{height}" '
            f'role="img" aria-label="{label}">'
            f'<title>{html.escape(code)}</title>'
            f'<rect class="code-stripe" width="3" height="{height}" />'
            '<g class="code-lines">' + ''.join(rows) + '</g></svg>')


page = re.sub(r'<pre\b[^>]*><code class="language-([^" ]+)">(.*?)</code></pre>',
              convert_code, page, flags=re.S)
expected = Counter(language for language in re.findall(
    r'^```([^\s`]+)\s*$', (root / 'index.md').read_text(), re.M)
    if language in source_languages)
if not expected or converted != expected:
    raise SystemExit(f'Expected source blocks {dict(expected)}, got {dict(converted)}')
diagram = re.compile(r'<div class="sjlj-diagram"><img\b[^>]*\bsrc="(images/sjlj-(?:flow|return)\.svg)"[^>]*></div>')
page, diagram_count = diagram.subn(
    lambda match: '<div class="sjlj-diagram">' + (root / match.group(1)).read_text() + '</div>',
    page)
if diagram_count != 2:
    raise SystemExit(f'Expected two SjLj diagrams, got {diagram_count}')
css = '''
<style id="svg-code-hover">
.sjlj-diagram { flex-shrink:0; margin:12px 0 18px; }
svg.hover-code { display:block; flex-shrink:0; width:100%; max-width:100%;
  margin:12px 0 18px; overflow:hidden; background:#eeeee4; transition:background-color 120ms ease;
  border-top:1px solid #d5d7cd; border-bottom:1px solid #d5d7cd; }
.hover-code text { font-family:Menlo,monospace; font-size:20px;
  letter-spacing:0; color:#252924; fill:#252924; white-space:pre; pointer-events:none; }
.hover-code tspan { fill:currentColor; }
.hover-code .wat-name { color:#3f627e; }
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
print(f'Converted {sum(converted.values())} source blocks to hoverable inline SVG: {dict(converted)}.')
print('Inlined two hoverable SjLj diagrams.')
