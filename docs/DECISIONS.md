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

## No config file

Artist and city are prompted interactively each run. No config or CLI flags. Keeps setup simple; config file could be added later if needed.
