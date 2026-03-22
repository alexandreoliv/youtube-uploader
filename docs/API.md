# API Reference

The application exposes functions in `app.py`. There are no HTTP endpoints.

## Constants

| Name | Value | Description |
|------|-------|-------------|
| `SCOPES` | `['https://www.googleapis.com/auth/youtube.upload']` | OAuth scope for YouTube upload |

---

## Functions

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

Entry point. Scans Downloads, prompts for artist/city, authenticates, uploads matching MP4s, and trashes them on success.

**Returns:** None

**Flow:**
1. Scan `~/Downloads` for `*.mp4`
2. Prompt: `Enter artist/band name:` and `Enter city:`
3. Call `get_authenticated_service()`
4. For each file matching `YYYY-MM-DD HH.MM.SS.mp4`:
   - Build title: `{Artist} | {City} | YYYY MM DD | HH MM SS`
   - Call `upload_video()`, then `move_to_trash()` on success
5. Print total uploaded count

**Exits early if:** No MP4s found, empty artist/city, or auth fails.
