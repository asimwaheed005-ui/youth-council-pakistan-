# WordPress public content migration

Source: https://youthcouncil.pk/ and its paginated public WordPress REST API. Imported 23 October 2026. The original website is unchanged.

## Imported

- All 13 published page records and all 17 published posts returned by WordPress, including older articles.
- All 283 available media originals, locally stored with their titles, alt text, descriptions, captions, attachment relationships, and source URLs.
- Seven categories, seven tags, published article authors and publication dates. WordPress returned no public comments.
- All eight published FAQs and all five sections / 25 fields of the membership form, including choice labels, required flags, and field descriptions.
- Published contact email, social profile links, map location, and the existing live membership form link.
- Existing 24-event / 39-photo migration remains in place.

`src/lib/wordpress-content.json` is the imported content, `src/lib/wordpress-migration.json` records counts and missing assets. `scripts/import-wordpress.py` repeats the migration. Run it with `--refresh` to refetch the paginated API records. Source snapshots are cached in ignored `.qa/legacy-import/`.

## Page mapping

| Original WordPress page | New destination | Treatment |
| --- | --- | --- |
| `/` (`home-2`) | `/` | Original introduction, work, mission, webinars and article content integrated into the redesigned homepage. Complete source version at `/home-2/`. |
| `/home/` | `/home/` | Earlier homepage preserved. |
| `/about/` | `/about/` | Full published text, mission, photographs and FAQs. |
| `/presidents-message/` | `/leadership/president/` | Full message and original portrait; previous URL remains usable. |
| `/blogs/` | `/blog/` | All 17 real posts replace the sample articles; previous listing URL remains usable. |
| `/events/` | `/events/` | Existing domestic/international archive and event galleries retained. |
| `/contact/` | `/contact/` | Published email, social links, map location and contact form fields. The original filler paragraph stays in the source archive. |
| `/join-us/` | `/join/` | All original application fields and live external application link; previous URL remains usable. |
| `/team/` | `/team/` | Published template-looking listing preserved and explicitly marked unverified; not used as the confirmed executive directory. |
| `/young-leaders-award-ceremony-2025/` | Same URL plus existing event page | Full report preserved. |
| `/donor-dashboard/` | Same URL | Legacy plugin page notice; no donation data or functioning dashboard claimed. |
| `/donation-failed/` | Same URL | Original message retained as archived content with a notice that no payment occurred here. |
| `/donation-confirmation/` | Same URL | Legacy plugin page notice; no confirmation or receipt fabricated. |

Every imported record also has a complete readable source version at `/source-archive/<original-slug>/`, indexed by `/source-archive/`. Posts have `/blog/<original-slug>/` and `/news/<original-slug>/` routes; original root post URLs remain usable. Category and tag archives are generated from WordPress records. Former sample article URLs now open relevant published articles. Source archive and unverified/plugin pages are marked noindex. Relative canonical links identify primary pages.

`/media/` provides search, pagination and viewing for the 283 available media files. Media controls open files for viewing and do not request downloads. Links to copied pages, posts, categories, tags and available media resolve locally. Unmatched links to the former website are displayed without outbound navigation. Other external destinations, including organizational social profiles and the online membership form, retain their original URL.

Visitor-facing source credits, references to the former website, and the footer's original-website archive link have been removed. Archive pages use neutral YCP publication labels. Source URLs remain internal migration metadata only. `python scripts/check-site-references.py` audits every exported HTML file for old-site hyperlinks and visible references; browser verification also checks every media-library page.

## Known source gaps and unavailable private data

Three historical image references already return HTTP 404 on WordPress:

- `/wp-content/uploads/2021/03/bold-logo-final-png-01.png`
- `/wp-content/uploads/2021/03/bold-logo-final-png-01-1024x580.png`
- `/wp-content/uploads/2021/03/WhatsApp-Image-2021-03-23-at-6.24.37-AM-1024x547.jpeg`

These missing references are recorded rather than replaced with invented images. All 283 media records exposed by the media API were downloaded successfully.

WordPress exposes no verified executive-member or university/district-head directory. The new directory pages explain this gap. The original `/team/` contains names such as Liam Anderson and repeated Sophie Carter profiles; these are preserved only as unverified original content.

Private drafts, users/passwords, form submissions, donor records, payments, plugin settings and databases are not accessible through the public API. Migrating them requires an authorized WordPress export/backup and a backend/data-storage implementation. The local membership/contact forms remain explicit previews; no data is silently posted to WordPress. Visitors can use the published membership form link or email YCP. Staff authentication and dashboard persistence remain demonstrations. Privacy and terms remain draft notices because no published source policies were available.

## Verification

Run `npm run typecheck`, `npm run build`, then serve `out/` locally. `scripts/smoke-test.mjs` checks exported routes and existing interactions. `scripts/verify-wordpress.mjs` compares all imported content blocks against rendered source pages, checks full post pages, every copied asset, all membership fields, original FAQs/contact links, media filtering/pagination, category archives, navigation and mobile overflow. Set `QA_ORIGIN` to the local server origin.
