# Data Models

The project has no internal database or custom schemas. Data is derived from filenames and YouTube API responses.

## Filename Pattern

**Regex:** `(\d{4})-(\d{2})-(\d{2})\s+(\d{2})\.(\d{2})\.(\d{2})\.mp4`

**Example:** `2025-10-23 21.30.24.mp4`

| Group | Meaning | Example |
|-------|---------|---------|
| 1 | Year (4 digits) | `2025` |
| 2 | Month (2 digits) | `10` |
| 3 | Day (2 digits) | `23` |
| 4 | Hour (2 digits) | `21` |
| 5 | Minute (2 digits) | `30` |
| 6 | Second (2 digits) | `24` |

---

## Video Title Format

`{ArtistLine} | {City} | {year} {month} {day} | {hour} {minute} {second}`

Where `{ArtistLine}` is:

- `{Band}` if no festival name was entered, or
- `{Band} @ {Festival}` when a festival name was provided at the start of the prompts.

**Examples:**

- `Metallica | Berlin | 2025 10 23 | 21 30 24`
- `Empyrium @ Walpurgisnacht | Berlin | 2026 05 02 | 23 55 51`

---

## YouTube API Request Body

Upload body passed to `videos().insert()`:

```python
{
    'snippet': {
        'title': str,        # Formatted title
        'description': 'Concert recording',
        'categoryId': '10'   # Music
    },
    'status': {
        'privacyStatus': 'unlisted',
        'selfDeclaredMadeForKids': False
    }
}
```

---

## Credential Storage

| File | Format | Content |
|------|--------|---------|
| `client_secrets.json` | JSON | OAuth 2.0 client ID/secret (from Google Cloud Console) |
| `token.pickle` | Pickle | `google.oauth2.credentials.Credentials` (access/refresh tokens) |

Both are gitignored.
