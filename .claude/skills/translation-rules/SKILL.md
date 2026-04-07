---
name: translation-rules
description: LV/EN/RU translation conventions, key naming, file structure, completeness validation, and locale-specific formatting. For i18n Agent.
disable-model-invocation: true
user-invocable: false
---

# Translation Rules

## Language Priority

**LV (Latvian) is the primary language.** Every translation key MUST exist in LV first.

| Priority | Language | URL prefix | Fallback |
|----------|----------|-----------|----------|
| 1 (primary) | Latvian (LV) | `/lv/` | None — LV must be complete |
| 2 | English (EN) | `/en/` | Falls back to LV |
| 3 | Russian (RU) | `/ru/` | Falls back to LV |

**NEVER show a raw translation key or blank string to the user.** If EN or RU is missing a key, display the LV version.

## File Structure

```
frontend/public/locales/
├── lv/
│   ├── common.json         # Shared UI: nav, footer, buttons, errors
│   ├── membership.json     # Join, renew, status, pricing
│   ├── training.json       # Catalog, registration, waitlist
│   ├── certification.json  # Applications, CPD, verification
│   ├── directory.json      # Search, profiles, badges
│   ├── content.json        # News, resources, events
│   ├── auth.json           # Login, register, password
│   └── admin.json          # Admin console labels
├── en/
│   └── (same files)
└── ru/
    └── (same files)
```

## Key Naming Convention

Use **dot-separated lowercase** keys organized by feature then context:

```json
{
  "membership.join.title": "Pievienoties LPA",
  "membership.join.subtitle": "Izvēlieties dalības veidu",
  "membership.join.plan.individual": "Individuālais instruktors",
  "membership.join.plan.studio": "Studija / organizācija",
  "membership.join.plan.supporter": "Atbalstītājs",
  "membership.join.cta": "PIEVIENOTIES",
  "membership.status.active": "Aktīvs",
  "membership.status.grace": "Pagarinājuma periods",
  "membership.status.lapsed": "Beidzies"
}
```

**Rules:**
- Feature first: `membership.`, `training.`, `directory.`
- Then context: `.join.`, `.catalog.`, `.filter.`
- Then element: `.title`, `.subtitle`, `.cta`, `.error`
- No camelCase, no UPPER_CASE
- Plurals: use `_one` / `_other` suffix (e.g., `training.seats_one`, `training.seats_other`)

## URL Localization

| Page | LV | EN | RU |
|------|----|----|-----|
| Home | `/lv` | `/en` | `/ru` |
| Trainings | `/lv/apmacibas` | `/en/trainings` | `/ru/treningi` |
| Directory | `/lv/katalogs` | `/en/directory` | `/ru/katalog` |
| Join | `/lv/pieteikties` | `/en/join` | `/ru/prisoedinitsa` |
| News | `/lv/jaunumi` | `/en/news` | `/ru/novosti` |
| About | `/lv/par-mums` | `/en/about` | `/ru/o-nas` |
| Contact | `/lv/kontakti` | `/en/contact` | `/ru/kontakty` |

## Date/Number Formatting

| Format | LV | EN | RU |
|--------|----|----|-----|
| Date | `dd.mm.yyyy` (07.04.2026) | `MMM d, yyyy` (Apr 7, 2026) | `dd.mm.yyyy` (07.04.2026) |
| Time | `HH:mm` (14:30) | `h:mm a` (2:30 PM) | `HH:mm` (14:30) |
| Currency | `50,00 €` | `€50.00` | `50,00 €` |
| Decimal | `1 234,56` | `1,234.56` | `1 234,56` |

Use `Intl.DateTimeFormat` and `Intl.NumberFormat` with the appropriate locale, not manual formatting.

## Completeness Validation

After any translation changes, run this check:

```bash
# Compare LV keys against EN and RU
node -e "
const fs = require('fs');
const path = require('path');
const localeDir = './frontend/public/locales';
const namespaces = fs.readdirSync(path.join(localeDir, 'lv')).filter(f => f.endsWith('.json'));

let missing = [];
for (const ns of namespaces) {
  const lv = JSON.parse(fs.readFileSync(path.join(localeDir, 'lv', ns)));
  for (const lang of ['en', 'ru']) {
    const filePath = path.join(localeDir, lang, ns);
    if (!fs.existsSync(filePath)) { missing.push(lang + '/' + ns + ' (entire file)'); continue; }
    const other = JSON.parse(fs.readFileSync(filePath));
    const lvKeys = Object.keys(lv);
    const missingKeys = lvKeys.filter(k => !(k in other));
    if (missingKeys.length) missing.push(lang + '/' + ns + ': ' + missingKeys.join(', '));
  }
}
if (missing.length) { console.log('MISSING TRANSLATIONS:'); missing.forEach(m => console.log('  ' + m)); process.exit(1); }
else { console.log('All translations complete.'); }
"
```

**Expected:** "All translations complete." Any missing keys must be added before the phase gate.

## Email Translations

Backend email templates in `backend/app/infrastructure/email/templates/` must support all three locales. The user's `preferred_language` field determines which version is sent.

Coordinate with Backend Agent via handoff for email template translation needs.
