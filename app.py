import os
import re
from pathlib import Path
from typing import List, Tuple

from dotenv import load_dotenv
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

load_dotenv()

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']


def _preset_cities_from_env() -> Tuple[str, ...]:
    """Comma-separated PRESET_CITIES in .env (see .env.example)."""
    raw = os.getenv("PRESET_CITIES", "").strip()
    if not raw:
        return ()
    return tuple(part.strip() for part in raw.split(",") if part.strip())


PRESET_CITIES = _preset_cities_from_env()

# Filenames like "2025-10-23 21.30.24.mp4" (used for discovery and titles)
MP4_TIMESTAMP_PATTERN = re.compile(
    r"(\d{4})-(\d{2})-(\d{2})\s+(\d{2})\.(\d{2})\.(\d{2})\.mp4$"
)


def prompt_for_city() -> str:
    """Return a city from presets (1, 2, …) or a user-typed name."""
    presets = PRESET_CITIES
    if presets:
        menu = ", ".join(f"{i} for {name}" for i, name in enumerate(presets, start=1))
        print(f"City: {menu}, or type another city name.")
        field = "City (number or name): "
    else:
        print("City (copy .env.example to .env and set PRESET_CITIES for quick-picks):")
        field = "City: "
    while True:
        raw = input(field).strip()
        if not raw:
            return ""
        if raw.isdigit() and presets:
            idx = int(raw)
            if 1 <= idx <= len(presets):
                return presets[idx - 1]
            print(f"Enter 1–{len(presets)} or type a city name.")
            continue
        return raw


def discover_timestamp_mp4s(folder_path: Path) -> Tuple[List[Path], List[Path]]:
    """Split Downloads MP4s into timestamp-named (sorted) vs skipped."""
    all_mp4 = list(folder_path.glob("*.mp4"))
    matching: List[Path] = []
    skipped: List[Path] = []
    for p in all_mp4:
        if MP4_TIMESTAMP_PATTERN.match(p.name):
            matching.append(p)
        else:
            skipped.append(p)
    matching.sort(key=lambda path: path.name)
    return matching, skipped


def prompt_band_segments(total_videos: int) -> List[Tuple[str, int]]:
    """
    Collect band/artist names and how many consecutive videos belong to each,
    in upload order. Empty band name (after the first) finishes input.

    Counts must sum to total_videos; validated by caller.
    """
    print(
        f"Assign bands in upload order — counts must add up to {total_videos} "
        "timestamp-named file(s)."
    )
    segments: List[Tuple[str, int]] = []
    band_num = 1

    while True:
        if band_num == 1:
            name = input("Band 1 name: ").strip()
        else:
            name = input(
                f"Band {band_num} name (press Enter if none): "
            ).strip()

        if not name:
            if band_num == 1:
                print("Band name cannot be empty.")
                continue
            break

        while True:
            raw = input(
                f"Number of videos for \"{name}\" (1–100): "
            ).strip()
            try:
                n = int(raw)
            except ValueError:
                print("Enter an integer from 1 to 100.")
                continue
            if not (1 <= n <= 100):
                print("Enter an integer from 1 to 100.")
                continue
            segments.append((name, n))
            band_num += 1
            break

    return segments


def get_authenticated_service():
    """Authenticate with YouTube API"""
    creds = None
    
    # Token file stores the user's access and refresh tokens
    if os.path.exists('token.pickle'):
        with open('token.pickle', 'rb') as token:
            creds = pickle.load(token)
    
    # If there are no valid credentials, refresh or run OAuth
    if not creds or not creds.valid:
        if creds and creds.expired and creds.refresh_token:
            try:
                creds.refresh(Request())
            except RefreshError:
                creds = None
                if os.path.exists('token.pickle'):
                    os.remove('token.pickle')
                print(
                    "Saved token could not be refreshed (revoked or expired). "
                    "Starting browser sign-in again."
                )

        if not creds or not creds.valid:
            if not os.path.exists('client_secrets.json'):
                print("ERROR: client_secrets.json not found!")
                print("Please download it from Google Cloud Console:")
                print("https://console.cloud.google.com/apis/credentials")
                return None

            flow = InstalledAppFlow.from_client_secrets_file(
                'client_secrets.json', SCOPES)
            creds = flow.run_local_server(port=0)

        with open('token.pickle', 'wb') as token:
            pickle.dump(creds, token)
    
    return build('youtube', 'v3', credentials=creds)

def upload_video(youtube, file_path, title):
    """Upload a video to YouTube"""
    body = {
        'snippet': {
            'title': title,
            'description': 'Concert recording',
            'categoryId': '10'  # Music category
        },
        'status': {
            'privacyStatus': 'unlisted',
            'selfDeclaredMadeForKids': False
        }
    }
    
    media = MediaFileUpload(file_path, chunksize=-1, resumable=True)
    
    request = youtube.videos().insert(
        part='snippet,status',
        body=body,
        media_body=media
    )
    
    print(f"Uploading: {title}")
    response = None
    while response is None:
        status, response = request.next_chunk()
        if status:
            print(f"Upload progress: {int(status.progress() * 100)}%")
    
    print(f"Upload complete! Video ID: {response['id']}")
    return response['id']

def move_to_trash(file_path):
    """Move file to trash (Ubuntu)"""
    try:
        # Use gio trash command (works on Ubuntu/GNOME)
        os.system(f'gio trash "{file_path}"')
        print(f"Moved to trash: {file_path.name}")
    except Exception as e:
        print(f"Error moving to trash: {e}")

def main():
    folder_path = Path.home() / "Downloads"
    mp4_files, skipped_mp4 = discover_timestamp_mp4s(folder_path)

    total_mp4 = len(mp4_files) + len(skipped_mp4)
    if total_mp4 == 0:
        print("No .mp4 files found in the folder.")
        return

    print(f"Found {total_mp4} .mp4 file(s) in Downloads.")
    if skipped_mp4:
        print(
            f"  {len(mp4_files)} match the timestamp name pattern "
            f"(YYYY-MM-DD HH.MM.SS.mp4); "
            f"{len(skipped_mp4)} skipped until renamed."
        )
    else:
        print(f"  All {len(mp4_files)} match the timestamp name pattern.")

    if not mp4_files:
        print("No timestamp-named videos to upload. Rename files or add new recordings.")
        return

    print(
        "Upload order is sorted by filename (usually chronological within one export batch)."
    )

    segments = prompt_band_segments(len(mp4_files))
    if not segments:
        print("Add at least one band and video count.")
        return

    planned = sum(count for _, count in segments)
    if planned != len(mp4_files):
        print(
            f"Video counts ({planned}) must match timestamp-named files "
            f"({len(mp4_files)}). Re-run with counts that add up."
        )
        return

    city = prompt_for_city()
    if not city:
        print("City cannot be empty.")
        return

    labels = []
    for name, count in segments:
        labels.extend([name] * count)

    print("\nReady to upload:")
    for name, count in segments:
        print(f"  • {name}: {count} video(s)")
    print(f"  • City: {city}")
    print()

    print("Authenticating with YouTube...")
    youtube = get_authenticated_service()

    if not youtube:
        print("Authentication failed. Exiting.")
        return

    uploaded_count = 0

    for file_path, artist_name in zip(mp4_files, labels):
        filename = file_path.name
        match = MP4_TIMESTAMP_PATTERN.match(filename)
        year, month, day, hour, minute, second = match.groups()

        title = (
            f"{artist_name} | {city} | {year} {month} {day} | "
            f"{hour} {minute} {second}"
        )

        try:
            upload_video(youtube, str(file_path), title)
            move_to_trash(file_path)
            uploaded_count += 1

        except Exception as e:
            print(f"Error uploading {filename}: {e}")

    print(f"\n✓ Successfully uploaded and trashed {uploaded_count} file(s).")

if __name__ == "__main__":
    main()