# Event photographs

Place domestic / local event photos in `public/images/events/domestic/<event-name>/`.
Place international event photos in `public/images/events/international/<event-name>/`.

The International Youth Dialogue folder is already created:
`public/images/events/international/international-youth-dialogue/`.

Use a separate folder per event and simple lowercase filenames, such as `opening-session.jpg`.

## Displaying an image

Adding a file does not automatically add it to a page. Public event records and the conference gallery are configured in `src/lib/data.ts`.

For a domestic event cover, set its `image` field to:
`events/domestic/youth-leadership-dialogue/cover.jpg`.

For a conference gallery image, add or update a `conferencePhotos` record:

```ts
{
  image: "events/international/international-youth-dialogue/opening-session.jpg",
  title: "Opening session",
  description: "A description of the people and activity shown in the photograph."
}
```

Paths in these records are relative to `public/images/`. The corresponding browser URL is `/images/events/international/international-youth-dialogue/opening-session.jpg`.

Current conference photos and captions are archive previews. Once verified conference photos are supplied, also update the preview notices, captions, and conference cover images in `src/components/events-experience.tsx` to describe the actual content.

The site is a static frontend: there is no working admin upload service yet. New images and data changes need a rebuild and deployment to appear on the hosted site.
