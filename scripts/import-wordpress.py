"""Migrate public WordPress content and media; never import executable plugin markup.

Uses the paginated REST snapshots shared with import-legacy-events.py.
Run with --refresh to refresh snapshots; reruns reuse downloaded original files.
"""
import concurrent.futures
from datetime import datetime, timezone
import hashlib
import importlib.util
import json
from pathlib import Path
import re
import sys
from urllib.parse import unquote, urlparse

ROOT = Path(__file__).resolve().parents[1]
spec = importlib.util.spec_from_file_location('legacy', ROOT / 'scripts/import-legacy-events.py')
legacy = importlib.util.module_from_spec(spec)
spec.loader.exec_module(legacy)
Node, Parser, plain = legacy.Node, legacy.Parser, legacy.plain


def clean(node):
    if isinstance(node, str):
        return ' '.join(node.split())
    if node.tag in ['script', 'style', 'noscript', 'input', 'select', 'textarea', 'button']:
        return ''
    return ' '.join(filter(None, (clean(c) for c in node.children)))


def safe_url(url):
    return url if url and urlparse(url).scheme in ['https', 'http', 'mailto', 'tel'] else ''


def write_json(path, data):
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(data, ensure_ascii=False, indent=2) + '\n', encoding='utf-8')


def run():
    with concurrent.futures.ThreadPoolExecutor(max_workers=4) as pool:
        posts, pages, media, categories, authors, tags, comments = list(pool.map(legacy.api, ['posts', 'pages', 'media', 'categories', 'users', 'tags', 'comments']))
    assets, urls, failures = [], {}, []
    for record in media:
        url = record['source_url']
        filename = unquote(urlparse(url).path.rsplit('/', 1)[-1])
        filename = re.sub(r'[^a-zA-Z0-9._-]', '-', filename)
        local = f'/images/wordpress/{record["id"]}-{filename}'
        asset = dict(id=record['id'], title=plain(record['title']['rendered']), sourceUrl=url,
                     src=local, mimeType=record.get('mime_type', ''), alt=record.get('alt_text', ''),
                     caption=plain(record['caption']['rendered']), description=plain(record['description']['rendered']),
                     parent=record.get('post'), publishedAt=record.get('date_gmt'))
        assets.append(asset)
        urls[url] = local
        for size in record.get('media_details', {}).get('sizes', {}).values():
            if size.get('source_url'):
                urls[size['source_url']] = local
        original = record.get('media_details', {}).get('original_image')
        if original:
            urls[url.rsplit('/', 1)[0] + '/' + original] = local

    # Preserve upload assets referenced by content even if missing from the media API.
    for record in posts + pages:
        for match in re.findall(r'https?://youthcouncil\.pk/wp-content/uploads/[^\s"\'<>\\)]+', record['content']['rendered']):
            url = match.replace('&amp;', '&')
            if url not in urls and re.search(r'\.(jpg|jpeg|png|webp|gif|svg|pdf)(?:\?|$)', url, re.I):
                filename = re.sub(r'[^a-zA-Z0-9._-]', '-', unquote(urlparse(url).path.rsplit('/', 1)[-1]))
                local = f'/images/wordpress/linked-{hashlib.sha256(url.encode()).hexdigest()[:10]}-{filename}'
                urls[url] = local
                assets.append(dict(id=0, title=filename, sourceUrl=url, src=local, mimeType='', alt='', caption='', description='', parent=None, publishedAt=None))

    def download(asset):
        target = ROOT / 'public' / asset['src'].lstrip('/')
        target.parent.mkdir(parents=True, exist_ok=True)
        if target.exists() and target.stat().st_size:
            return
        for attempt in range(3):
            try:
                data = legacy.fetch(asset['sourceUrl'])
                target.write_bytes(data)
                return
            except Exception as error:
                if attempt == 2:
                    failures.append(dict(url=asset['sourceUrl'], error=str(error)))

    with concurrent.futures.ThreadPoolExecutor(max_workers=8) as pool:
        list(pool.map(download, assets))
    if failures:
        write_json(ROOT / '.qa/legacy-import/media-failures.json', failures)
        if any('HTTP Error 404' not in f['error'] for f in failures):
            raise RuntimeError('Media transfer failed; inspect .qa/legacy-import/media-failures.json and rerun.')
    for asset in assets:
        asset['available']=(ROOT/'public'/asset['src'].lstrip('/')).is_file()
    missing={a['sourceUrl'] for a in assets if not a['available']}

    category_map = {c['id']: plain(c['name']) for c in categories}
    author_map = {a['id']: a['name'] if '@' not in a['name'] else 'Youth Council Pakistan' for a in authors}

    def image_block(node):
        source = node.attrs.get('src', '')
        if source not in urls:
            return []
        if source in missing:
            return [dict(type='missing-image', text='This image is unavailable on the original website.', href=source)]
        return [dict(type='image', src=urls[source], alt=node.attrs.get('alt', ''), caption='')]

    def links(node):
        return [dict(text=clean(n) or n.attrs['href'], href=n.attrs['href'])
                for n in node.find(lambda n: n.tag == 'a' and safe_url(n.attrs.get('href')))]

    def blocks(node):
        if isinstance(node, str):
            text = ' '.join(node.split())
            return [dict(type='paragraph', text=text)] if text else []
        widget = node.attrs.get('data-widget_type', '')
        if node.tag in ['script', 'style', 'noscript', 'input', 'select', 'textarea', 'button', 'form', 'iframe']:
            return []
        if widget in ['form.default', 'shortcode.default', 'google_maps.default', 'social-icons.default', 'divider.default']:
            return []
        if node.tag == 'img':
            return image_block(node)
        if node.tag in ['h1','h2','h3','h4','h5','h6']:
            text = clean(node)
            return [dict(type='heading', text=text, level=int(node.tag[1]))] if text else []
        if node.tag == 'figure':
            images = [b for n in node.find(lambda n:n.tag == 'img') for b in image_block(n)]
            captions = node.find(lambda n:n.tag == 'figcaption')
            if captions and images:
                images[0]['caption'] = clean(captions[0])
            return images
        if node.tag in ['ul','ol']:
            items = [clean(n) for n in node.children if isinstance(n,Node) and n.tag=='li' and clean(n)]
            return [dict(type='list', items=items, ordered=node.tag=='ol', links=links(node))] if items else []
        if node.tag == 'table':
            rows = [[clean(c) for c in n.children if isinstance(c,Node) and c.tag in ['th','td']] for n in node.find(lambda n:n.tag=='tr')]
            return [dict(type='table', rows=rows)]
        if node.tag in ['p','blockquote']:
            result = [dict(type='quote' if node.tag=='blockquote' else 'paragraph', text=clean(node), links=links(node))] if clean(node) else []
            return result + [b for n in node.find(lambda n:n.tag=='img') for b in image_block(n)]
        if node.tag == 'a' and safe_url(node.attrs.get('href')):
            return [dict(type='link', text=clean(node) or 'Open link', href=node.attrs['href'])] + [b for n in node.find(lambda n:n.tag=='img') for b in image_block(n)]
        result=[]
        for child in node.children:
            result.extend(blocks(child))
        # Background photographs in Elementor CTA widgets.
        if widget == 'call-to-action.default':
            for n in node.find(lambda n:'background-image' in n.attrs.get('style','')):
                match=re.search(r'url\(["\x27]?([^"\x27)]+)',n.attrs['style'])
                if match and match.group(1) in urls:
                    result.insert(0,dict(type='image',src=urls[match.group(1)],alt='',caption=''))
        return result

    docs=[]
    for record in pages + posts:
        body=blocks(Parser(record['content']['rendered']).root)
        # Responsive Elementor variants repeat identical blocks. Keep first occurrence.
        seen=set(); unique=[]
        for block in body:
            signature=json.dumps(block,sort_keys=True)
            if signature not in seen:
                unique.append(block);seen.add(signature)
        is_post=record in posts
        title=plain(record['title']['rendered'])
        featured_id=record.get('featured_media')
        image=next((a['src'] for a in assets if featured_id and a['id']==featured_id and a['available']), '')
        if not image:
            image=next((b['src'] for b in unique if b['type']=='image'),'')
        cats=[category_map[c] for c in record.get('categories',[]) if c in category_map]
        excerpt=plain(record.get('excerpt',{}).get('rendered',''))
        if not excerpt:
            excerpt=next((b['text'] for b in unique if b['type']=='paragraph'),'')[:280]
        docs.append(dict(id=record['id'],slug=record['slug'],title=title,sourceUrl=record['link'],
                         kind='post' if is_post else 'page',publishedAt=record['date_gmt'],modifiedAt=record['modified_gmt'],
                         image=image,category=cats[0] if cats else 'YCP',categories=cats,excerpt=excerpt,blocks=unique,
                         author=author_map.get(record.get('author'),'Youth Council Pakistan'),tags=record.get('tags',[]),
                         comments=[dict(author=c['author_name'],date=c['date_gmt'],text=plain(c['content']['rendered'])) for c in comments if c['post']==record['id']]))

    about=Parser(next(p for p in pages if p['slug']=='about')['content']['rendered']).root
    faqs=[]
    for card in about.find(lambda n:'elementskit-card' in n.attrs.get('class','').split()):
        questions=card.find(lambda n:'ekit-accordion-title' in n.attrs.get('class','').split())
        answers=card.find(lambda n:'elementskit-card-body' in n.attrs.get('class','').split())
        if questions and answers:
            faqs.append(dict(q=clean(questions[0]),a=clean(answers[0])))
    assert len(faqs)==8, f'Unexpected FAQ extraction: {len(faqs)}'

    join=Parser(next(p for p in pages if p['slug']=='join-us')['content']['rendered']).root
    form_sections=[]
    for section in join.find(lambda n:'forminator-pagination' in n.attrs.get('class','').split()):
        headings=section.find(lambda n:n.tag in ['h2','h3','h4'])
        title=clean(headings[0]) if headings else f'Section {len(form_sections)+1}'
        fields=[]
        for field in section.find(lambda n:'forminator-field' in n.attrs.get('class','').split()):
            controls=field.find(lambda n:n.tag in ['input','select','textarea'] and n.attrs.get('type')!='hidden')
            if not controls:
                continue
            labels=field.find(lambda n:n.tag=='label' and 'forminator-label' in n.attrs.get('class','').split())
            group_labels=field.find(lambda n:n.tag=='span' and 'forminator-label' in n.attrs.get('class','').split())
            label=clean((labels or group_labels)[0]) if labels or group_labels else ''
            if not label:
                continue
            control=controls[0]; attrs=control.attrs
            kind=control.tag if control.tag!='input' else attrs.get('type','text')
            if 'datepicker' in attrs.get('class',''):kind='date'
            if attrs.get('name','').startswith('phone'):kind='tel'
            descriptions=field.find(lambda n:'forminator-description' in n.attrs.get('class','').split())
            choices=[]
            for choice in controls:
                if choice.attrs.get('type') in ['checkbox','radio']:
                    label_nodes=field.find(lambda n:n.tag=='label' and n.attrs.get('for')==choice.attrs.get('id'))
                    choices.append(dict(value=choice.attrs.get('value',''),label=clean(label_nodes[0]) if label_nodes else choice.attrs.get('value','')))
            fields.append(dict(name=attrs.get('name','').replace('[]',''),label=label.rstrip(' *'),type=kind,
                               required=attrs.get('aria-required')=='true' or attrs.get('data-required')=='true',
                               description=clean(descriptions[0]) if descriptions else '',options=choices,
                               min=attrs.get('min',''),max=attrs.get('max','')))
        form_sections.append(dict(title=title,fields=fields))
    assert sum(len(s['fields']) for s in form_sections)>=25, 'Incomplete membership form'
    contact=Parser(next(p for p in pages if p['slug']=='contact')['content']['rendered']).root
    socials=[dict(text=clean(n),href=n.attrs['href']) for n in contact.find(lambda n:n.tag=='a' and safe_url(n.attrs.get('href'))) if any(host in n.attrs['href'] for host in ['facebook.com','x.com','instagram.com','linkedin.com'])]
    home=next(p for p in pages if p['link']==legacy.BASE+'/')
    home_links=Parser(home['content']['rendered']).root.find(lambda n:n.tag=='a' and 'forms.gle' in n.attrs.get('href',''))
    config=dict(faqs=faqs,membershipSections=form_sections,socials=socials,email='info@youthcouncil.pk',
                membershipUrl=home_links[0].attrs['href'] if home_links else legacy.BASE+'/join-us/',
                mapsUrl='https://maps.google.com/maps?q=Islamabad&t=m&z=10&output=embed&iwloc=near')
    write_json(ROOT/'src/lib/wordpress-content.json',dict(documents=docs,media=assets,
                categories=[dict(id=c['id'],slug=c['slug'],name=plain(c['name']),description=c['description']) for c in categories],
                tags=[dict(id=t['id'],slug=t['slug'],name=plain(t['name']),description=t['description']) for t in tags],config=config))
    report=dict(importedAt=datetime.now(timezone.utc).isoformat(),pages=len(pages),posts=len(posts),media=len(media),
                downloadedAssets=sum(a['available'] for a in assets),assetReferences=len(assets),faqs=len(faqs),membershipFields=sum(len(s['fields']) for s in form_sections),publicComments=len(comments),failures=failures)
    write_json(ROOT/'src/lib/wordpress-migration.json',report)
    print(json.dumps(report,indent=2))


if __name__=='__main__':
    sys.stdout.reconfigure(encoding='utf-8')
    run()
