# Event photographs

Place domestic / local event photos in `public/images/events/domestic/<event-name>/`.
Place international event photos in `public/images/events/international/<event-name>/`.

Imported conference photographs are in:
`public/images/events/international/9th-asia-pacific-climate-change-adaptation-forum-apan/`.

Other imported events have their own folders under the domestic or international directory.

Use a separate folder per event and simple lowercase filenames, such as `opening-session.jpg`.

## Displaying an image

Adding a file does not automatically add it to a page. Imported event reports, captions, and photo records are stored in `src/lib/legacy-events.json` and exported through `src/lib/data.ts`. The importer is `scripts/import-legacy-events.py`; its source mapping is documented in `LEGACY-EVENT-MIGRATION.md`.

For a domestic event cover, set its `image` field to:
`events/domestic/youth-leadership-dialogue/cover.jpg`.

For an event gallery image, add or update an entry in that event?s `photos` array in `src/lib/legacy-events.json`:

```ts
{
  image: "events/international/9th-asia-pacific-climate-change-adaptation-forum-apan/opening-session.jpg",
  title: "Opening session",
  description: "A description of the people and activity shown in the photograph.",
  originalCaption: "The original caption, if supplied.",
  sourceUrl: "https://youthcouncil.pk/events/"
}
```

Paths in these records are relative to `public/images/`. The corresponding browser URL is `/images/events/international/9th-asia-pacific-climate-change-adaptation-forum-apan/opening-session.jpg`.

The event galleries now use photographs and reports imported from the original YCP website. Keep captions factual and retain the source URL for each imported photograph. The importer can overwrite manual edits to the generated JSON; keep reviewed changes in the import script if you plan to re-run it.

The site is a static frontend: there is no working admin upload service yet. New images and data changes need a rebuild and deployment to appear on the hosted site.
