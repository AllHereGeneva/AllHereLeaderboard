#!/usr/bin/env python3
# Cache-bust leaderboard.js / leaderboard.css: hash their content and write the
# result into the two `?v=` params in index.html, so it's never bumped by hand.
# Run this before every deploy: python3 build/bump-version.py
import hashlib, os, re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
JS = os.path.join(ROOT, 'assets', 'leaderboard.js')
CSS = os.path.join(ROOT, 'assets', 'leaderboard.css')
INDEX = os.path.join(ROOT, 'index.html')

h = hashlib.sha1()
for path in (JS, CSS):
    with open(path, 'rb') as f:
        h.update(f.read())
version = h.hexdigest()[:8]

with open(INDEX, encoding='utf-8') as f:
    html = f.read()

new_html, n_css = re.subn(r'(leaderboard\.css\?v=)[^"\']+', r'\g<1>' + version, html)
new_html, n_js = re.subn(r'(leaderboard\.js\?v=)[^"\']+', r'\g<1>' + version, new_html)

if n_css != 1 or n_js != 1:
    raise SystemExit('expected exactly one `?v=` each for leaderboard.css/.js in index.html, '
                      'found css=%d js=%d -- check index.html did not change shape' % (n_css, n_js))

if new_html == html:
    print('version unchanged:', version, '(leaderboard.js/.css content is the same as last bump)')
else:
    with open(INDEX, 'w', encoding='utf-8') as f:
        f.write(new_html)
    print('version bumped ->', version)
