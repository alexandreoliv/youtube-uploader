# Engineering Decisions

## Single-file design

The app is contained in one `app.py` file. Chosen for simplicity: no imports between modules, easy to run, and minimal surface area for maintenance.

---

## Unlisted privacy

Videos are uploaded as `unlisted` rather than private or public. Unlisted videos are viewable only via direct link, suited for personal concert recordings without public exposure.

---

## Trash instead of hard delete

Files are moved with `gio trash` rather than permanently deleted. Reduces risk of data loss if an upload was mistaken or the user wants to recover files.

---

## Ubuntu/GNOME trash only

`move_to_trash()` uses `gio trash`, which is standard on Ubuntu/GNOME. Not portable to macOS (`trash` command) or Windows (Recycle Bin) without changes.

---

## Resumable upload

`MediaFileUpload(..., resumable=True)` is used so large uploads can resume after network interruption. Chunk progress is printed to the terminal.

---

## OAuth scope

Only `https://www.googleapis.com/auth/youtube.upload` is requested. Minimal scope for the upload-only use case.

---

## File discovery strictness

Only files matching `YYYY-MM-DD HH.MM.SS.mp4` are processed. Other MP4s are skipped with a log message. This avoids uploading arbitrary files and keeps titles consistent.

---

## Multi-band uploads (one folder)

For festivals with several acts, drop **all** timestamp-named MP4s into Downloads once. The script uploads in **sorted filename order** (typically chronological). You enter band **A** and how many files belong to **A** from the start of that order, then band **B** and its count, and so on; press **Enter** on a blank band name when there are no more acts. The sum of those counts must equal the number of matching files.

Single-band nights are the same flow: one band name and a count equal to the number of videos.

Optional **festival name** (first prompt): when set, each title prefixes the band with ` @ ` and that name (e.g. `Empyrium @ Walpurgisnacht | …`).

---

## No config file (beyond optional `.env`)

Bands (names + counts per segment), city, and optional preset cities are prompted each run. Optional `.env` only supplies `PRESET_CITIES` for the menu; there are no CLI flags. Keeps setup simple.

---

## Preset cities in the prompt

Common cities are offered as numbered quick-picks via the `PRESET_CITIES` variable in a local `.env` file (template: `.env.example`) so the public repo does not embed personal defaults; any other city can still be entered as free text. `.env` is gitignored.
