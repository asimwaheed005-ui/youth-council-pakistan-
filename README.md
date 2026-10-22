# Youth Council Pakistan — frontend

Responsive Next.js App Router / TypeScript frontend based on the supplied proposal. The existing WordPress website is unchanged.

## Run

Requires Node.js 20.9 or newer.

```sh
npm install
npm run dev
```

Open http://127.0.0.1:3000. Staff role preview: http://127.0.0.1:3000/admin/login/.

```sh
npm run build
npm run typecheck
```

Production static HTML is exported to `out/`. To preview the export, use `python -m http.server 3000 --bind 127.0.0.1 --directory out`. Dynamic routes are generated from `src/lib/data.ts`.

## Public pages

Home, About, Leadership, President’s message, Executive Members, University/District Representatives, Programs and details, Events and details, Event Registration, Gallery and album, News and articles, Blog and articles/category, International Conferences and details, Impact, Media Center, Join, Contact, FAQ, Search, Privacy, and Terms.

Interactions include event/article filters, search, validated application/contact previews, image lightbox, FAQs, and a deterministic FAQ helper. The helper does not use AI.

## Five staff role previews

One portal supports Super Admin, Event Manager, Blog Writer, Blog Editor, and Registration Manager. Selection changes sidebar navigation and section visibility. Explore application review, sample status changes, CSV export, content drafts, and a basic form-field builder.

There is **no authentication or secure authorization**. Roles are intentionally selectable. Selected role, sample content title/status records, and application statuses use browser localStorage. Generic module lists last until leaving the page. Public content comes from fixed fixtures: admin edits do not update public pages. Editor description/date/category fields demonstrate the UI and are not persisted. Form definitions are not connected to public application forms.

Public form entries remain in memory and are not saved, sent, or emailed. Reference numbers are demonstrations. Do not enter real applicant information.

## Content and assets

Logo and archive photographs come from the existing youthcouncil.pk website and are stored in `public/images`. The organization description, president’s name, and message excerpt are grounded in its public content. Program copy requires review. Future events/dates, conference examples, articles, applicant records, and counts are labelled samples. Unverified member profiles and statistics have not been invented. Policies are draft preview notices. Fonts are local.

## Browser verification

With the exported site running on port 3000, run `npm run test:smoke`. The test uses locally installed Chrome through Playwright. Set `CHROME_PATH` for a nonstandard Chrome location. Screenshots go into ignored `.qa/`.

## Backend remains

Database/content APIs, real authentication, server-side authorization, immutable form versions, persistent submissions, uploads, email, live analytics, approved articles, WordPress migration/redirects, backups, and production policies are later phases.

## Event structure

Events now includes dedicated `/events/domestic/` and `/events/international/` listings. International Youth Dialogue has an overview at `/events/international/international-youth-dialogue/` and a separate `/gallery/` subpage beneath it. The original conference URLs remain supported. Conference gallery images are explicitly labelled archive previews pending verified conference photography.
