"""Check exported visitor content for links or references to the former site."""
from html.parser import HTMLParser
from pathlib import Path
import re
from urllib.parse import urlparse

FORBIDDEN = re.compile(r'\bWordPress\b|(?:original|previous|existing|old)\s+(?:YCP\s+)?(?:website|web\s+site)|Original YCP source|View the original source|https?://(?:www\.)?youthcouncil\.pk', re.I)


class Audit(HTMLParser):
    def __init__(self):
        super().__init__()
        self.hidden = 0
        self.text = []
        self.errors = []

    def handle_starttag(self, tag, attrs):
        if tag in ['script', 'style']:
            self.hidden += 1
        for name, value in attrs:
            if not value:
                continue
            if name in ['href', 'src', 'action']:
                url = urlparse('https:' + value if value.startswith('//') else value)
                if url.scheme in ['https', 'http'] and url.hostname in ['youthcouncil.pk', 'www.youthcouncil.pk']:
                    self.errors.append(f'{name}={value}')
            if name in ['alt', 'aria-label', 'title'] and FORBIDDEN.search(value):
                self.errors.append(f'{name}={value}')

    def handle_endtag(self, tag):
        if tag in ['script', 'style']:
            self.hidden = max(0, self.hidden - 1)

    def handle_data(self, value):
        if not self.hidden:
            self.text.append(value)


errors = []
pages = list(Path('out').rglob('*.html'))
assert pages, 'Build the static export before running this check.'
for page in pages:
    audit = Audit()
    audit.feed(page.read_text(encoding='utf-8'))
    match = FORBIDDEN.search(' '.join(audit.text))
    if match:
        audit.errors.append(f'visible text: {match.group()}')
    errors.extend(f'{page}: {error}' for error in audit.errors)
assert not errors, '\n'.join(errors)
print(f'PASS {len(pages)} exported HTML files contain no old-site links or visitor-facing references.')
