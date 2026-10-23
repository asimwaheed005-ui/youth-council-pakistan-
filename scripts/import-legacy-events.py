"""Import public YCP event records and their original photographs. No admin access needed."""
import concurrent.futures
import html
import hashlib
from html.parser import HTMLParser
import json
from pathlib import Path
import re
import urllib.request

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / '.qa' / 'legacy-import'
CACHE.mkdir(parents=True, exist_ok=True)
BASE = 'https://youthcouncil.pk'


def fetch(url):
    with urllib.request.urlopen(url, timeout=60) as response:
        return response.read()


def api(kind):
    cached = CACHE / f'{kind}.json'
    if cached.exists() and '--refresh' not in __import__('sys').argv:
        return json.loads(cached.read_text(encoding='utf-8'))
    records = []
    page = 1
    while True:
        with urllib.request.urlopen(f'{BASE}/wp-json/wp/v2/{kind}?per_page=100&page={page}', timeout=60) as response:
            records.extend(json.loads(response.read()))
            if page >= int(response.headers.get('X-WP-TotalPages', '1')):
                break
        page += 1
    (CACHE / f'{kind}.json').write_text(json.dumps(records, ensure_ascii=False), encoding='utf-8')
    return records


class Node:
    def __init__(self, tag='', attrs=None, parent=None):
        self.tag, self.attrs, self.parent, self.children = tag, dict(attrs or []), parent, []

    def text(self):
        return ' '.join(' '.join(x.text() if isinstance(x, Node) else x for x in self.children).split())

    def find(self, predicate):
        result = [self] if predicate(self) else []
        for child in self.children:
            if isinstance(child, Node):
                result.extend(child.find(predicate))
        return result


class Parser(HTMLParser):
    def __init__(self, source):
        super().__init__(convert_charrefs=True)
        self.root = self.node = Node()
        self.feed(source)

    def handle_starttag(self, tag, attrs):
        child = Node(tag, attrs, self.node)
        self.node.children.append(child)
        if tag not in ['img', 'br', 'hr', 'input', 'meta', 'link', 'source', 'wbr', 'embed']:
            self.node = child

    def handle_endtag(self, tag):
        node = self.node
        while node.parent:
            if node.tag == tag:
                self.node = node.parent
                break
            node = node.parent

    def handle_data(self, value):
        self.node.children.append(value)


def plain(value):
    return Parser(value).root.text()


def slugify(value):
    return re.sub(r'[^a-z0-9]+', '-', value.lower()).strip('-')


def inventory():
    with concurrent.futures.ThreadPoolExecutor(max_workers=3) as pool:
        posts, pages, media = list(pool.map(api, ['posts', 'pages', 'media']))
    page = next(p for p in pages if p['slug'] == 'events')
    tree = Parser(page['content']['rendered']).root
    css = fetch(f'{BASE}/wp-content/uploads/elementor/css/post-{page["id"]}.css').decode()
    (CACHE / 'events.css').write_text(css, encoding='utf-8')
    cards = []
    for column in tree.find(lambda n: n.attrs.get('data-element_type') == 'column'):
        headings = column.find(lambda n: n.tag == 'h2')
        if len(headings) != 1:
            continue
        title = headings[0].text()
        element = column.attrs.get('data-id')
        image = re.search(r'elementor-element-' + re.escape(element) + r'[^{}]*\{[^{}]*background-image:url\(["\x27]?([^"\x27)]+)', css)
        if not image:
            continue
        links = column.find(lambda n: n.tag == 'a' and n.attrs.get('href', '').startswith(BASE + '/'))
        url = column.attrs.get('data-ra-url') or (links[0].attrs['href'] if links else page['link'])
        cards.append(dict(title=title, image=image.group(1), sourceUrl=url, element=element))
    (CACHE / 'cards.json').write_text(json.dumps(cards, ensure_ascii=False, indent=2), encoding='utf-8')
    return posts, pages, media, cards


def paragraphs(source):
    source = re.sub(r'<(script|style)\b[^>]*>.*?</\1>', '', source, flags=re.S)
    source = re.sub(r'<br\s*/?>|</(?:p|div|li|h[1-6]|blockquote)>', '\n', source)
    return [text for line in source.splitlines() if (text := plain(line))]


def build_records(posts, pages, media, cards):
    posts_by_url = {p['link']: p for p in posts}
    # Scope denotes local activity versus cross-border engagement. Missing locations stay unstated.
    info = {
        'aurat-foundation-of-pakistan': ('international', 'Leadership', 'Manchester, United Kingdom', '9 October 2026'),
        'delegation-by-patron-in-chief': ('international', 'Diplomacy', 'London, United Kingdom', '8 October 2026'),
        'diplomatic-engagements-in-islamabad': ('domestic', 'Diplomacy', 'Islamabad', ''),
        'meeting-with-thai-ambassador': ('domestic', 'Diplomacy', 'Location not stated', ''),
        'visit-to-the-embassy-of-the-russian-federation': ('domestic', 'Diplomacy', 'Location not stated', ''),
        '6th-international-students-convention-expo-2026': ('international', 'Education', 'Location not stated', '2026 — exact date not stated'),
        'meeting-of-the-executive-members-of-the-youth-council-pakistan': ('domestic', 'Leadership', 'Location not stated', ''),
        'commemoration-of-un-human-rights-day-2025': ('domestic', 'Human rights', 'Location not stated', '2025 — exact date not stated'),
        '9th-asia-pacific-climate-change-adaptation-forum-apan': ('international', 'Climate', 'Bangkok, Thailand', ''),
        'international-parliamentary-diplomatic-reception': ('international', 'Diplomacy', 'Location not stated', ''),
        'cyber-security-conference': ('domestic', 'Digital safety', 'Location not stated', ''),
        'asia-pacific-climate-change-adaptation-forum': ('international', 'Climate', 'Bangkok, Thailand', ''),
        'asean-carbon-market-sustainability-council': ('international', 'Climate', 'Bangkok, Thailand', ''),
        'youth-in-governance': ('international', 'Leadership', 'New York, United States / Islamabad, Pakistan', '15–17 April 2025'),
        'diplomatic-and-youth-engagement-visit-to-the-united-kingdom': ('international', 'Diplomacy', 'United Kingdom', 'August 2025'),
        'ycp-unep-unite-for-climate-action': ('international', 'Climate', 'Bangkok, Thailand', ''),
        'youth-diplomacy-on-global-issues': ('international', 'Diplomacy', 'United Kingdom', ''),
        'consultative-meeting-on-kashmir': ('domestic', 'Human rights', 'Location not stated', ''),
        'safenet-cyber-awareness-drive': ('domestic', 'Digital safety', 'Islamabad · NASTP', '2025 — exact date not stated'),
        'youth-diplomacy-for-climate-change-kashmir-palestine-issue': ('international', 'Diplomacy', 'Leeds, United Kingdom', 'August 2025'),
        'young-leaders-award-ceremony-2025': ('domestic', 'Leadership', 'Islamabad', 'September 2025'),
        'building-life-skills': ('international', 'Leadership', 'Online', '2025 — exact date not stated'),
        'reimagining-education': ('domestic', 'Education', 'Online', '2025 — exact date not stated'),
        'climate-policy-and-youth-engagement': ('international', 'Climate', 'Online', ''),
    }
    records = {}
    for card in cards:
        # The original page's Youth Diplomacy tile has a # link; match its published report by title.
        if card['title'].lower() == 'youth diplomacy on global issues':
            card['sourceUrl'] = BASE + '/youth-diplomacy-on-global-issues/'
        post = posts_by_url.get(card['sourceUrl'])
        slug = post['slug'] if post else slugify(card['title'])
        if slug not in records:
            records[slug] = dict(slug=slug, title=plain(post['title']['rendered']) if post else card['title'], originalTitle=card['title'], sourceUrl=card['sourceUrl'], post=post, urls=[])
        records[slug]['urls'].append(card['image'])
    for slug in ['youth-diplomacy-for-climate-change-kashmir-palestine-issue', 'young-leaders-award-ceremony-2025']:
        post = next(p for p in posts + pages if p['slug'] == slug)
        records[slug] = dict(slug=slug, title=plain(post['title']['rendered']), originalTitle=plain(post['title']['rendered']), sourceUrl=post['link'], post=post, urls=[])
    home = next(p for p in pages if p['link'] == BASE + '/')
    home_tree = Parser(home['content']['rendered']).root
    for widget in home_tree.find(lambda n: n.attrs.get('data-widget_type') == 'call-to-action.default'):
        title_nodes = widget.find(lambda n: 'elementor-cta__title' in n.attrs.get('class', '').split())
        caption_nodes = widget.find(lambda n: 'elementor-cta__description' in n.attrs.get('class', '').split())
        backgrounds = widget.find(lambda n: 'background-image' in n.attrs.get('style', ''))
        if not title_nodes or not caption_nodes or not backgrounds:
            continue
        title, caption = title_nodes[0].text(), caption_nodes[0].text()
        image = re.search(r'url\(["\x27]?([^"\x27)]+)', backgrounds[0].attrs['style']).group(1)
        slug = slugify(title)
        records[slug] = dict(slug=slug, title=title, originalTitle=title, sourceUrl=home['link'], post=None, urls=[image], body=[caption])
    older_home = next(p for p in pages if p['slug'] == 'home')
    for widget in Parser(older_home['content']['rendered']).root.find(lambda n: n.attrs.get('data-widget_type') == 'elementskit-image-box.default'):
        headings = widget.find(lambda n: n.tag in ['h2', 'h3'])
        descriptions = widget.find(lambda n: 'elementskit-box-style-content' in n.attrs.get('class', '').split())
        if not headings or not descriptions:
            continue
        slug = slugify(headings[0].text())
        if slug not in records:
            continue
        record = records[slug]
        caption = descriptions[0].text()
        record['originalPhotoCaption'] = caption
        record['captionSourceUrl'] = older_home['link']
        if not record['post']:
            record['body'] = [caption]
            record['sourceUrl'] = older_home['link']
    media_by_url = {m['source_url']: m for m in media}
    for item in media:
        for size in item.get('media_details', {}).get('sizes', {}).values():
            if size.get('source_url'):
                media_by_url[size['source_url']] = item
        original = item.get('media_details', {}).get('original_image')
        if original:
            media_by_url[item['source_url'].rsplit('/', 1)[0] + '/' + original] = item
    result = []
    download_jobs = []
    for slug, record in records.items():
        scope, category, city, event_date = info[slug]
        post = record.pop('post')
        body = paragraphs(post['content']['rendered']) if post else record.pop('body', [])
        original_caption = record.pop('originalPhotoCaption', '')
        if post:
            tree = Parser(post['content']['rendered']).root
            record['urls'].extend(n.attrs['src'] for n in tree.find(lambda n: n.tag == 'img' and n.attrs.get('src', '').startswith(BASE)))
            record['urls'].extend(m['source_url'] for m in media if m.get('post') == post['id'] and m.get('mime_type', '').startswith('image/'))
            if not record['urls']:
                css = fetch(f'{BASE}/wp-content/uploads/elementor/css/post-{post["id"]}.css').decode()
                record['urls'].extend(re.findall(r'background-image:url\(["\x27]?([^"\x27)]+)', css))
        urls = list(dict.fromkeys(media_by_url.get(url, {}).get('source_url', url) for url in record.pop('urls')))
        photos = []
        for i, url in enumerate(urls):
            if not url.startswith(BASE + '/wp-content/uploads/'):
                continue
            m = media_by_url.get(url, {})
            suffix = Path(urllib.parse.urlparse(url).path).suffix.lower()
            path = f'events/{scope}/{slug}/photo-{i+1:02d}{suffix}'
            caption = plain(m.get('caption', {}).get('rendered', '')) or (original_caption if i == 0 else '')
            # Preserve supplied captions; use the actual event title when the source has none.
            photos.append(dict(image=path, title=caption or record['originalTitle'], description=m.get('alt_text') or caption or record['originalTitle'], originalCaption=caption, sourceUrl=url))
            download_jobs.append((url, ROOT / 'public' / 'images' / path))
        if not photos:
            raise RuntimeError(f'No photograph found for {slug}')
        summary = next((p for p in body if len(p) > 90), '')
        if summary:
            summary = re.split(r'(?<=[.!?])\s+', summary)[0]
        else:
            summary = f'{record["originalTitle"]}. Photograph and title published in the Youth Council Pakistan event archive.'
        record.update(scope=scope, category=category, city=city, fullDate=event_date or 'Event date not published', date='', month='', format='Past event', image=photos[0]['image'], description=summary, paragraphs=body, photos=photos, sourcePublishedAt=post['date'][:10] if post else None, contentStatus='report' if body else 'photo-only')
        result.append(record)

    def download(job):
        url, destination = job
        destination.parent.mkdir(parents=True, exist_ok=True)
        if not destination.exists() or '--redownload' in __import__('sys').argv:
            data = fetch(url)
            if not data or data[:20].lstrip().startswith(b'<'):
                raise RuntimeError(f'Invalid image response for {url}')
            destination.write_bytes(data)
        return destination.stat().st_size

    with concurrent.futures.ThreadPoolExecutor(max_workers=5) as pool:
        sizes = list(pool.map(download, download_jobs))
    for record in result:
        unique, seen = [], set()
        for photo in record['photos']:
            digest = hashlib.sha256((ROOT / 'public' / 'images' / photo['image']).read_bytes()).hexdigest()
            if digest not in seen:
                unique.append(photo)
                seen.add(digest)
        record['photos'] = unique
    target = ROOT / 'src' / 'lib' / 'legacy-events.json'
    target.write_text(json.dumps(result, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')
    lines = ['# Legacy event migration', '', 'Source: the public youthcouncil.pk Events page, current and older homepages, linked reports, awards page, and WordPress media records. Imported on 22 October 2026.', '', f'{len(result)} activities, {sum(len(e["photos"]) for e in result)} photographs: {sum(e["scope"] == "domestic" for e in result)} domestic/local and {sum(e["scope"] == "international" for e in result)} international.', '', 'Published titles, reports, and captions are preserved. When no image caption exists, its published event title labels the photograph. Duplicate image sizes and byte-identical files are consolidated. Repeated Human Rights Day tiles form one event with both photographs.', '', 'Scope distinguishes local activities from international conferences and cross-border engagements, including online exchanges. Youth in Governance covers New York and Islamabad as described on the older homepage. Missing dates and locations stay unstated. Article publication and image upload dates are never substituted for event dates.', '', 'The fictional International Youth Dialogue sample is replaced by the published 9th Asia-Pacific Climate Change Adaptation Forum. The former preview URL opens the international archive.', '', '| Event | Section | Photos | Available content | Source |', '| --- | --- | ---: | --- | --- |']
    for event in result:
        lines.append(f'| {event["title"]} | {event["scope"]} | {len(event["photos"])} | {"Published report/caption" if event["paragraphs"] else "Title and photograph only"} | [Original]({event["sourceUrl"]}) |')
    lines += ['', '## Importing again', '', 'Run `python scripts/import-legacy-events.py --refresh` to fetch updated public records. Raw source snapshots live under ignored `.qa/legacy-import/`. `--redownload` refreshes downloaded files. Review the explicit scope/date mapping before publishing new records. The importer generates `src/lib/legacy-events.json` and downloads images into `public/images/events/<scope>/<event-slug>/`.', '', 'Some original records have no written report or exact event date. The frontend marks these gaps. Archived event pages, including retained registration URLs, do not offer application forms.']
    (ROOT / 'LEGACY-EVENT-MIGRATION.md').write_text('\n'.join(lines) + '\n', encoding='utf-8')
    print(f'Imported {len(result)} events, {sum(len(r["photos"]) for r in result)} unique event photographs.')
    return result


if __name__ == '__main__':
    import sys
    sys.stdout.reconfigure(encoding='utf-8')
    posts, pages, media, cards = inventory()
    result = build_records(posts, pages, media, cards)
    for record in result:
        print(record['scope'], record['slug'], len(record['photos']), 'photos;', len(record['paragraphs']), 'paragraphs')
