# Architecture

## Folder Structure

```
youtube-uploader/
├── app.py              # Main application logic
├── requirements.txt    # Python dependencies
├── README.md           # User-facing setup and usage
├── .env.example        # Template for PRESET_CITIES (copy to `.env`)
├── .gitignore          # Excludes .env, client_secrets.json, token.pickle, venv/
└── docs/               # Project documentation
```

## Core Modules

The project is a single module (`app.py`) with these responsibilities:

| Component | Responsibility |
|-----------|----------------|
| `get_authenticated_service()` | OAuth flow, token persistence, YouTube API client build |
| `upload_video()` | Resumable upload, progress reporting, video metadata |
| `move_to_trash()` | Post-upload cleanup via `gio trash` |
| `discover_timestamp_mp4s()` | Split Downloads `*.mp4` into timestamp-named (sorted) vs skipped |
| `prompt_for_festival()` | Optional festival name for `@ Festival` suffix on band names in titles |
| `artist_title_part()` | Builds `{Band}` or `{Band} @ {Festival}` for the title fragment |
| `prompt_band_segments()` | Multi-band prompts: name + count per segment until blank name |
| `prompt_for_city()` | City quick-picks from `PRESET_CITIES` in `.env` or free-text name |
| `main()` | Discovery, user input, orchestration |

## Data Flow

```mermaid
flowchart TD
    subgraph Input
        A[~/Downloads/*.mp4]
        Fest[Festival name optional]
        B[Band segments name + count]
        C[City name]
    end

    subgraph Auth
        D[token.pickle or client_secrets.json]
        E[Google OAuth]
        F[YouTube API Client]
    end

    subgraph Process
        G[Match filename YYYY-MM-DD HH.MM.SS.mp4]
        H[Sort matching files by name]
        I[Upload with title per segment order]
        J[Move to trash]
    end

    A --> G
    G --> H
    Fest --> I
    B --> I
    C --> I
    D --> E
    E --> F
    H --> I
    F --> I
    I --> J
```

## Execution Flow

1. **Discovery** — `Path.home() / "Downloads"` scanned for `*.mp4`; timestamp-named files sorted by filename
2. **User input** — `prompt_for_festival()` (optional; non-empty value suffixes every band with `@ Festival` in titles); `prompt_band_segments()` (band name + video count 1–100 per segment; blank name after the first band ends the list); counts must equal the number of matching files; city via `prompt_for_city()` (presets or custom)
3. **Auth** — `get_authenticated_service()` loads or refreshes OAuth credentials
4. **Filter** — Regex `(\d{4})-(\d{2})-(\d{2})\s+(\d{2})\.(\d{2})\.(\d{2})\.mp4` (`MP4_TIMESTAMP_PATTERN`) filters valid filenames; other MP4s are reported as skipped
5. **Upload loop** — Each matching file uploaded with `artist_title_part(band, festival)` then city and timestamp, then moved to trash on success

## Design Patterns

- **Script-style entrypoint** — `if __name__ == "__main__": main()`
- **Token persistence** — Pickled credentials in `token.pickle` for reuse
- **Resumable upload** — `MediaFileUpload(..., resumable=True)` with chunk progress

## External Integrations

| Integration | Purpose |
|-------------|---------|
| YouTube Data API v3 | Video insert (`videos().insert`) |
| Google OAuth 2.0 | `https://www.googleapis.com/auth/youtube.upload` |
| `gio trash` | Ubuntu/GNOME trash (via `os.system`) |
