# YouTube Concert Uploader

A Python script that automatically uploads MP4 concert recordings from your Downloads folder to YouTube as unlisted videos.

## Description

This script scans `~/Downloads` for MP4 files with timestamp filenames (e.g., `2025-10-23 21.30.24.mp4`), uploads them to YouTube with formatted titles including artist name, city, and timestamp, and moves successfully uploaded files to the trash.

## Features

-   Automatic detection of MP4 files in Downloads folder
-   YouTube upload with unlisted privacy setting
-   Videos marked as "not for kids"
-   Formatted video titles: `{Artist} | {City} | YYYY MM DD | HH MM SS`
-   Automatic file cleanup (moves to trash after successful upload)
-   Upload progress tracking

## Prerequisites

-   Ubuntu/Linux system
-   Python 3.6 or higher
-   Google Cloud account with YouTube Data API v3 enabled
-   OAuth 2.0 credentials from Google Cloud Console

## Setup

### 1. Clone the repository

```bash
git clone https://github.com/alexandreoliv/youtube-uploader.git
cd youtube-uploader
```

### 2. Create and activate virtual environment

```bash
python3 -m venv venv
source venv/bin/activate
```

### 3. Install dependencies

```bash
pip install -r requirements.txt
```

### 4. Get YouTube API Credentials

1. Go to [Google Cloud Console](https://console.cloud.google.com/)
2. Create a new project (or select existing one)
3. Enable **YouTube Data API v3**:
    - Navigate to "APIs & Services" > "Library"
    - Search for "YouTube Data API v3"
    - Click "Enable"
4. Create OAuth 2.0 credentials:
    - Go to "APIs & Services" > "Credentials"
    - Click "Create Credentials" > "OAuth client ID"
    - Select "Desktop app" as application type
    - Download the JSON file
5. Rename the downloaded file to `client_secrets.json`
6. Place `client_secrets.json` in the same directory as `app.py`

## Usage

1. Make sure your virtual environment is activated:

```bash
source venv/bin/activate
```

2. Run the script:

```bash
python app.py
```

3. On first run, the script will:

    - Open your browser for Google authentication
    - Ask you to authorize the application
    - Save credentials for future use (stored in `token.pickle`)

4. Follow the prompts:
    - Enter the artist/band name
    - Enter the city name
    - Wait for uploads to complete

## File Naming Convention

The script expects MP4 files with the following naming format:

```
YYYY-MM-DD HH.MM.SS.mp4
```

Example: `2025-10-23 21.30.24.mp4`

These will be uploaded with titles like:

```
Metallica | Berlin | 2025 10 23 | 21 30 24
```

## Notes

-   Videos are uploaded as **unlisted** (not public, not private)
-   Videos are marked as **not for kids**
-   Files are only deleted after successful upload
-   Deleted files go to Ubuntu's trash bin (can be recovered if needed)
-   Upload progress is displayed in the terminal

## Troubleshooting

**"client_secrets.json not found"**

-   Make sure you've downloaded OAuth credentials from Google Cloud Console
-   Verify the file is named exactly `client_secrets.json`
-   Check that the file is in the same directory as `app.py`

**Authentication issues**

-   Delete `token.pickle` and run the script again
-   Make sure YouTube Data API v3 is enabled in your Google Cloud project

**Upload fails**

-   Check your internet connection
-   Verify the video file is not corrupted
-   Ensure you have sufficient YouTube quota (default: 10,000 units/day)

## License

MIT License
