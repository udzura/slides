#!/usr/bin/env python3
"""Draw two matched C/Wasm diagrams for the initial and resumed SjLj paths."""
from html import escape
from pathlib import Path

ROOT = Path(__file__).resolve().parent
CODE_TOP = 54
LINE_HEIGHT = 24
CODE = [
    'static jmp_buf env;',
    '',
    'static void jump(void) {',
    '  longjmp(env, 42);   // ③',
    '}',
    '',
    'int probe(void) {',
    '  switch (setjmp(env)) { // ①',
    '    case 0: jump(); return -1; // ②',
    '    case 42: return 42; // ④',
    '    default: return -1;',
    '  }',
    '}',
]
STEPS = [
    (7, 32, 62, '① 再開地点を env に記録', [('判定用の値 = 0', 80, 'code')]),
    (8, 114, 74, '② 呼び出しを捕捉対象にする', [('try_table …', 158, 'code'), ('  call jump', 180, 'code')]),
    (3, 208, 62, '③ longjmp(env, 42) の実行', [('__wasm_longjmp → throw', 256, 'code')]),
    (9, 290, 76, '④ 捕捉し、env の戻り先を照合', [('判定用の値 = 42', 336, 'code'), ('switch を再判定 → case 42', 358, 'detail')]),
]

STYLE = '''
svg.sjlj-flow { display:block; width:100%; max-width:100%; height:auto; overflow:visible; }
.sjlj-flow text { fill:#252924; font-family:-apple-system,BlinkMacSystemFont,'Segoe UI','Hiragino Kaku Gothic ProN','Noto Sans JP',sans-serif; letter-spacing:0; pointer-events:none; }
.sjlj-flow .column-label { font-size:17px; fill:#686c63; }
.sjlj-flow .c-panel,.sjlj-flow .node-bg { fill:#eeeee4; stroke:#d5d7cd; stroke-width:1; transition:fill 120ms ease,stroke 120ms ease; }
.sjlj-flow .code { font-family:Menlo,monospace; font-size:19px; white-space:pre; }
.sjlj-flow .node-heading { font-size:18px; fill:#686c63; }
.sjlj-flow .detail { font-size:18px; }
.sjlj-flow .takeaway { font-size:20px; }
.sjlj-flow .c-highlight { fill:transparent; transition:fill 120ms ease; }
.sjlj-flow .line-mark { fill:#b53d27; opacity:0; transition:opacity 120ms ease; pointer-events:none; }
.sjlj-flow .flow-node { outline:none; }
.sjlj-flow .phase-active .node-bg,.sjlj-flow .phase-active .c-highlight { fill:#fffdf9; }
.sjlj-flow .phase-active .node-bg { stroke:#b53d27; }
.sjlj-flow .phase-active .line-mark { opacity:1; }
.sjlj-flow .edge { fill:none; stroke:#686c63; stroke-width:2; }
.sjlj-flow .edge.unwind { stroke:#b53d27; stroke-dasharray:4 3; }
.sjlj-flow:has(.flow-node:focus-visible) .c-panel,.sjlj-flow:has(.flow-node:focus-visible) .node-bg { fill:#d3d5c9; stroke:#d5d7cd; }
.sjlj-flow:has(.flow-node:focus-visible) .c-highlight { fill:transparent; }
.sjlj-flow:has(.flow-node:focus-visible) .line-mark { opacity:0; }
.sjlj-flow:has(.flow-node:focus-visible) .flow-node:focus-visible .node-bg,.sjlj-flow:has(.flow-node:focus-visible) .flow-node:focus-visible .c-highlight { fill:#fffdf9; }
.sjlj-flow:has(.flow-node:focus-visible) .flow-node:focus-visible .node-bg { stroke:#b53d27; stroke-width:2; }
.sjlj-flow:has(.flow-node:focus-visible) .flow-node:focus-visible .line-mark { opacity:1; }
@media (hover:hover) {
  .sjlj-flow:has(.flow-node:hover) .c-panel,.sjlj-flow:has(.flow-node:hover) .node-bg { fill:#d3d5c9; stroke:#d5d7cd; }
  .sjlj-flow:has(.flow-node:hover) .c-highlight { fill:transparent; }
  .sjlj-flow:has(.flow-node:hover) .line-mark { opacity:0; }
  .sjlj-flow:has(.flow-node:hover) .flow-node:hover .node-bg,.sjlj-flow:has(.flow-node:hover) .flow-node:hover .c-highlight { fill:#fffdf9; }
  .sjlj-flow:has(.flow-node:hover) .flow-node:hover .node-bg { stroke:#b53d27; stroke-width:2; }
  .sjlj-flow:has(.flow-node:hover) .flow-node:hover .line-mark { opacity:1; }
}
@media (prefers-reduced-motion:reduce) { .sjlj-flow rect { transition:none; } }
@media print {
  .sjlj-flow .c-panel,.sjlj-flow .flow-node .node-bg { fill:#eeeee4 !important; stroke:#d5d7cd !important; stroke-width:1 !important; }
  .sjlj-flow .flow-node .c-highlight { fill:transparent !important; }
  .sjlj-flow .flow-node .line-mark { opacity:0 !important; }
  .sjlj-flow .phase-active .node-bg,.sjlj-flow .phase-active .c-highlight { fill:#fffdf9 !important; }
  .sjlj-flow .phase-active .node-bg { stroke:#b53d27 !important; }
  .sjlj-flow .phase-active .line-mark { opacity:1 !important; }
}
'''


def text(x, y, value, kind):
    return f'<text x="{x}" y="{y}" class="{kind}" xml:space="preserve">{escape(value)}</text>'


def draw(phase, active, takeaway, filename):
    prefix = 'sjlj-' + phase
    parts = [
        f'<svg xmlns="http://www.w3.org/2000/svg" class="sjlj-flow" viewBox="0 0 1120 404" width="1120" height="404" role="group" aria-labelledby="{prefix}-title {prefix}-desc">',
        f'<title id="{prefix}-title">CとWasmの対応：{"初回は0" if phase == "initial" else "捕捉後は42"}</title>',
        f'<desc id="{prefix}-desc">左がCのコード、右がコンパイラが作る処理の模式図。同じ番号の箇所を対応づける。{escape(takeaway)}</desc>',
        '<style>' + STYLE + '</style>',
        f'<defs><marker id="{prefix}-arrow" viewBox="0 0 10 10" refX="9" refY="5" markerWidth="6" markerHeight="6" orient="auto"><path d="M1 1 L9 5 L1 9" fill="none" stroke="#686c63" stroke-width="1.5" /></marker></defs>',
        '<g aria-hidden="true">',
        text(0, 18, 'C（前の例と同じ処理・抜粋）', 'column-label'),
        text(620, 18, 'コンパイラが作る処理（模式図）', 'column-label'),
        '<rect class="c-panel" x="0" y="32" width="520" height="334" />',
        f'<path class="edge" d="M870 99 V109" marker-end="url(#{prefix}-arrow)" />',
        f'<path class="edge" d="M870 193 V203" marker-end="url(#{prefix}-arrow)" />',
        f'<path class="edge unwind" d="M870 275 V285" marker-end="url(#{prefix}-arrow)" />',
    ]
    highlighted_lines = {step[0] for step in STEPS}
    for index, line in enumerate(CODE):
        if index not in highlighted_lines:
            parts.append(text(18, CODE_TOP + LINE_HEIGHT * index, line, 'code'))
    parts.append('</g>')
    for number, (line_index, y, height, heading, lines) in enumerate(STEPS, 1):
        css_class = 'flow-node phase-active' if number in active else 'flow-node'
        parts.append(f'<g class="{css_class}" tabindex="0" role="group" aria-label="{escape(heading)}">')
        baseline = CODE_TOP + LINE_HEIGHT * line_index
        parts.extend([
            f'<rect class="c-highlight" x="3" y="{baseline - 20}" width="514" height="{LINE_HEIGHT}" />',
            f'<rect class="line-mark" x="0" y="{baseline - 20}" width="3" height="{LINE_HEIGHT}" />',
            text(18, baseline, CODE[line_index], 'code'),
            f'<rect class="node-bg" x="620" y="{y}" width="500" height="{height}" />',
            text(640, y + 22, heading, 'node-heading'),
        ])
        parts.extend(text(640, baseline_y, label, kind) for label, baseline_y, kind in lines)
        parts.append('</g>')
    parts.append(text(0, 394, takeaway, 'takeaway'))
    parts.append('</svg>')
    (ROOT / 'images' / filename).write_text('\n'.join(parts) + '\n')


draw('initial', {1, 2}, '初回は0で case 0 へ。jump() から伝播する例外を try_table で捕捉する。', 'sjlj-flow.svg')
draw('resume', {3, 4}, '捕捉した42で case 42 へ。setjmp を呼び直すのではなく、その後の経路に復帰する。', 'sjlj-return.svg')
