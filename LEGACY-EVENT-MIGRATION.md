# Legacy event migration

Source: the public youthcouncil.pk Events page, current and older homepages, linked reports, awards page, and WordPress media records. Imported on 22 October 2026.

24 activities, 39 photographs: 10 domestic/local and 14 international.

Published titles, reports, and captions are preserved. When no image caption exists, its published event title labels the photograph. Duplicate image sizes and byte-identical files are consolidated. Repeated Human Rights Day tiles form one event with both photographs.

Scope distinguishes local activities from international conferences and cross-border engagements, including online exchanges. Youth in Governance covers New York and Islamabad as described on the older homepage. Missing dates and locations stay unstated. Article publication and image upload dates are never substituted for event dates.

The fictional International Youth Dialogue sample is replaced by the published 9th Asia-Pacific Climate Change Adaptation Forum. The former preview URL opens the international archive.

| Event | Section | Photos | Available content | Source |
| --- | --- | ---: | --- | --- |
| Aurat Foundation of Pakistan | international | 2 | Published report/caption | [Original](https://youthcouncil.pk/aurat-foundation-of-pakistan/) |
| Delegation by Patron In Chief | international | 4 | Published report/caption | [Original](https://youthcouncil.pk/delegation-by-patron-in-chief/) |
| Diplomatic Engagements in Islamabad | domestic | 1 | Title and photograph only | [Original](https://youthcouncil.pk/events/) |
| Meeting with Thai Ambassador | domestic | 1 | Title and photograph only | [Original](https://youthcouncil.pk/events/) |
| Visit to the Embassy of the Russian Federation | domestic | 1 | Title and photograph only | [Original](https://youthcouncil.pk/events/) |
| 6th International Students Convention & Expo 2026 | international | 1 | Title and photograph only | [Original](https://youthcouncil.pk/events/) |
| Meeting of the Executive Members of The Youth Council Pakistan | domestic | 1 | Title and photograph only | [Original](https://youthcouncil.pk/events/) |
| Commemoration of UN HUMAN RIGHTS DAY 2025 | domestic | 2 | Title and photograph only | [Original](https://youthcouncil.pk/events/) |
| 9th Asia-Pacific Climate Change Adaptation Forum (APAN) | international | 3 | Published report/caption | [Original](https://youthcouncil.pk/9th-asia-pacific-climate-change-adaptation-forum-apan/) |
| International Parliamentary & Diplomatic Reception | international | 1 | Title and photograph only | [Original](https://youthcouncil.pk/events/) |
| Cyber Security Conference | domestic | 1 | Title and photograph only | [Original](https://youthcouncil.pk/events/) |
| Asia Pacific Climate Change Adaptation Forum | international | 1 | Published report/caption | [Original](https://youthcouncil.pk/asia-pacific-climate-change-adaptation-forum/) |
| ASEAN Carbon Market Sustainability Council | international | 2 | Published report/caption | [Original](https://youthcouncil.pk/asean-carbon-market-sustainability-council/) |
| Youth In Governance | international | 1 | Published report/caption | [Original](https://youthcouncil.pk/home/) |
| Diplomatic and Youth Engagement Visit to the United Kingdom | international | 3 | Published report/caption | [Original](https://youthcouncil.pk/diplomatic-and-youth-engagement-visit-to-the-united-kingdom/) |
| YCP & UNEP Unite for Climate Action | international | 1 | Published report/caption | [Original](https://youthcouncil.pk/ycp-unep-unite-for-climate-action/) |
| Youth Diplomacy on Global Issues | international | 1 | Published report/caption | [Original](https://youthcouncil.pk/youth-diplomacy-on-global-issues/) |
| Consultative Meeting on Kashmir | domestic | 1 | Published report/caption | [Original](https://youthcouncil.pk/home/) |
| SafeNet Cyber Awareness Drive | domestic | 3 | Published report/caption | [Original](https://youthcouncil.pk/safenet-cyber-awareness-drive/) |
| Youth Diplomacy for Climate Change, Kashmir & Palestine Issue | international | 3 | Published report/caption | [Original](https://youthcouncil.pk/youth-diplomacy-for-climate-change-kashmir-palestine-issue/) |
| Young Leaders Award Ceremony 2025 | domestic | 2 | Published report/caption | [Original](https://youthcouncil.pk/young-leaders-award-ceremony-2025/) |
| Building Life Skills | international | 1 | Published report/caption | [Original](https://youthcouncil.pk/) |
| Reimagining Education | domestic | 1 | Published report/caption | [Original](https://youthcouncil.pk/) |
| Climate Policy and Youth Engagement | international | 1 | Published report/caption | [Original](https://youthcouncil.pk/) |

## Importing again

Run `python scripts/import-legacy-events.py --refresh` to fetch updated public records. Raw source snapshots live under ignored `.qa/legacy-import/`. `--redownload` refreshes downloaded files. Review the explicit scope/date mapping before publishing new records. The importer generates `src/lib/legacy-events.json` and downloads images into `public/images/events/<scope>/<event-slug>/`.

Some original records have no written report or exact event date. The frontend marks these gaps. Archived event pages, including retained registration URLs, do not offer application forms.
