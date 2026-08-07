#!/usr/bin/env python3
"""Generate passage.txt from passage.html for machine readers.

Preserves the three-part unit (label, name, whisper) and dividers
so AI visitors arriving through fetchers see the full structure.
"""

import html as html_mod
import re
import os

HERE = os.path.dirname(os.path.abspath(__file__))
HTML_PATH = os.path.join(HERE, 'passage.html')
OUT = os.path.join(HERE, 'passage.txt')

with open(HTML_PATH, encoding='utf-8') as f:
    src = f.read()

body_m = re.search(r'<div class="passage">(.*)</div>\s*</body>', src, re.S)
if not body_m:
    raise SystemExit('Could not find passage body')

content = body_m.group(1)

def clean(s):
    s = re.sub(r'<br\s*/?>', '\n', s)
    s = re.sub(r'<[^>]+>', '', s)
    s = html_mod.unescape(s)
    s = re.sub(r'[ \t]+', ' ', s)
    s = re.sub(r' *\n *', '\n', s)
    return s.strip()

# Find each top-level element (4-space indent), then slice to next start
starts = list(re.finditer(r'^    <div\s+class="([^"]*)"', content, re.M))

lines = []

for i, m in enumerate(starts):
    cls = m.group(1)
    pos = m.start()
    end = starts[i + 1].start() if i + 1 < len(starts) else len(content)
    block = content[pos:end]

    if cls == 'air':
        lines.append(clean(block))
        lines.append('')

    elif cls == 'pause':
        lines.append('· · ·')
        lines.append('')

    elif cls.startswith('opening'):
        label_m = re.search(r'class="label"[^>]*>(.*?)</div>', block, re.S)
        link_m = re.search(r'<a\s[^>]*>(.*?)</a>', block, re.S)
        href_m = re.search(r'href="([^"]*)"', block)
        whisper_m = re.search(r'class="whisper"[^>]*>(.*?)</div>', block, re.S)
        plaque_m = re.search(r'class="plaque"[^>]*>(.*?)</div>', block, re.S)

        if label_m:
            lines.append(clean(label_m.group(1)))
        if link_m and href_m:
            lines.append(f'{clean(link_m.group(1))}  ({href_m.group(1)})')
        if whisper_m:
            lines.append(clean(whisper_m.group(1)))
        if plaque_m:
            lines.append(clean(plaque_m.group(1)))
        lines.append('')

    elif cls == 'stone':
        lines.append(clean(block))
        lines.append('')

    elif cls == 'note':
        lines.append(clean(block))
        lines.append('')

    elif cls == 'wall-piece':
        title_m = re.search(r'class="title"[^>]*>(.*?)</div>', block, re.S)
        desc_m = re.search(r'class="description"[^>]*>(.*?)</div>', block, re.S)
        link_m = re.search(r'<a\s[^>]*>(.*?)</a>', block, re.S)
        href_m = re.search(r'href="([^"]*)"', block)

        if title_m:
            lines.append(clean(title_m.group(1)))
        if desc_m:
            lines.append(clean(desc_m.group(1)))
        if link_m and href_m:
            lines.append(f'{clean(link_m.group(1))}  ({href_m.group(1)})')
        lines.append('')

    elif cls == 'threshold':
        lines.append(clean(block))
        lines.append('')

    elif cls == 'back':
        link_m = re.search(r'<a\s[^>]*>(.*?)</a>', block, re.S)
        href_m = re.search(r'href="([^"]*)"', block)
        if link_m and href_m:
            lines.append(f'{clean(link_m.group(1))}  ({href_m.group(1)})')
        lines.append('')

output = '\n'.join(lines).strip() + '\n'

with open(OUT, 'w', encoding='utf-8') as f:
    f.write(output)

print(f'Wrote {len(output)} bytes to passage.txt ({output.count(chr(10))} lines)')
