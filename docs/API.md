# API Reference

The application exposes functions in `app.py`. There are no HTTP endpoints.

## Constants

| Name | Value | Description |
|------|-------|-------------|
| `SCOPES` | `['https://www.googleapis.com/auth/youtube.upload']` | OAuth scope for YouTube upload |
| `PRESET_CITIES` | (runtime) | Parsed from env after `load_dotenv()` — comma-separated names, see `.env.example` |
| `MP4_TIMESTAMP_PATTERN` | compiled `re.Pattern` | Full-match regex for `YYYY-MM-DD HH.MM.SS.mp4` filenames |

---

## Functions

### `prompt_for_festival()`

First prompt of a run: optional festival or event name (`Festival name (press Enter if none):`).

**Returns:** `str` — trimmed input, or `""` when skipped.

**Behaviour:** Passed into `artist_title_part()` for every upload; when non-empty, titles use `{Band} @ {Festival}`.

---

### `artist_title_part(band_name, festival_name)`

Builds the artist fragment at the start of the YouTube title (before ` | {City} | …`).

**Returns:** `{Band} @ {Festival}` when `festival_name.strip()` is non-empty; otherwise `{Band}`.

---

### `discover_timestamp_mp4s(folder_path)`

Scans `folder_path` for `*.mp4`, splits into timestamp-named files (pattern below) vs others.

**Returns:** `(matching, skipped)` — each a `list[Path]`. `matching` is sorted by `path.name` (upload order).

---

### `prompt_band_segments(total_videos)`

Interactive multi-band setup for one festival/run.

**Parameters:** `total_videos` — number of timestamp-named files (used in the instruction line).

**Returns:** `list[tuple[str, int]]` — `(band_name, count)` per segment in upload order.

**Prompts:**
- Band 1: `Band 1 name:` (required; blank re-prompts)
- Bands 2+: `Band N name (press Enter if none):` — blank finishes input (no count asked)
- After each non-empty name: `Number of videos for "{name}" (1–100):` — integer validation loop

**Caller validation:** Sum of counts must equal `total_videos`.

---

### `prompt_for_city()`

Interactive city selection: if `PRESET_CITIES` is non-empty, prints a menu (`1 for …`, `2 for …`) and reads `City (number or name):`. If unset/empty, prompts for a city name only (see `.env.example`).

**Returns:** `str` — chosen preset city, or a trimmed free-text name. Empty string if the user submits blank (caller should treat as invalid).

**Behavior:**
- With presets: digits only and in range → matching preset; digits only out of range → hint and re-prompt.
- Without presets: all input is treated as the city name (including digit-only strings).
- Any non-digit-only input (when presets exist): returned as the city name as-is (after strip).

---

### `get_authenticated_service()`

Authenticates with YouTube API and returns a configured client.

**Returns:** `Resource` (YouTube API client) or `None` if auth fails

**Behavior:**
1. Loads credentials from `token.pickle` if present
2. Refreshes expired credentials if a refresh token exists
3. If refresh fails with `RefreshError` (e.g. revoked token), removes `token.pickle` and runs OAuth again
4. Otherwise runs OAuth flow via `client_secrets.json` (opens browser)
5. Saves credentials to `token.pickle` for future runs

**Raises:** None (returns `None` on failure, prints error if `client_secrets.json` missing)

---

### `upload_video(youtube, file_path, title)`

Uploads a video file to YouTube.

| Parameter | Type | Description |
|-----------|------|-------------|
| `youtube` | `Resource` | YouTube API client from `get_authenticated_service()` |
| `file_path` | `str` | Absolute path to the MP4 file |
| `title` | `str` | Video title shown on YouTube |

**Returns:** `str` — YouTube video ID

**Upload settings:**
- `privacyStatus`: `'unlisted'`
- `selfDeclaredMadeForKids`: `False`
- `categoryId`: `10` (Music)
- `description`: `'Concert recording'`

**Side effects:** Prints upload progress to stdout (e.g., `Upload progress: 45%`)

---

### `move_to_trash(file_path)`

Moves a file to the system trash (Ubuntu/GNOME).

| Parameter | Type | Description |
|-----------|------|-------------|
| `file_path` | `Path` | Path to the file to trash |

**Returns:** None

**Implementation:** Invokes `gio trash "{file_path}"` via `os.system()`

**Side effects:** Prints `Moved to trash: <filename>` or error message

---

### `main()`

Entry point. Scans Downloads, prompts for festival (optional), band segments, and city; authenticates; uploads matching MP4s in sorted filename order; trashes them on success.

**Returns:** None

**Flow:**
1. Scan `~/Downloads` for `*.mp4`; partition with `discover_timestamp_mp4s()`; print counts (matching vs skipped)
2. `prompt_for_festival()`
3. `prompt_band_segments(len(matching))`; verify sum of counts equals number of matching files
4. `prompt_for_city()` (menu + `City (number or name):` when presets exist)
5. Print summary (bands as `artist_title_part` + city), then `get_authenticated_service()`
6. Zip sorted matching files with per-file band labels derived from segments; for each file:
   - Build title: `{artist_title_part(Band, Festival)} | {City} | YYYY MM DD | HH MM SS`
   - Call `upload_video()`, then `move_to_trash()` on success
7. Print total uploaded count

**Exits early if:** No MP4s, no timestamp-named files, empty band plan, count mismatch, empty city, or auth fails.
