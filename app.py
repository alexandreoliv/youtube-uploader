import os
import re
from pathlib import Path
from google_auth_oauthlib.flow import InstalledAppFlow
from google.auth.transport.requests import Request
from google.auth.exceptions import RefreshError
from googleapiclient.discovery import build
from googleapiclient.http import MediaFileUpload
import pickle

# YouTube API scopes
SCOPES = ['https://www.googleapis.com/auth/youtube.upload']

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
    # Set the folder path
    folder_path = Path.home() / "Downloads"
    
    # Find all .mp4 files in the folder
    mp4_files = list(folder_path.glob("*.mp4"))
    
    if not mp4_files:
        print("No .mp4 files found in the folder.")
        return
    
    print(f"Found {len(mp4_files)} .mp4 file(s)")
    
    # Ask for artist name and city
    artist_name = input("Enter artist/band name: ").strip()
    city = input("Enter city: ").strip()
    
    if not artist_name or not city:
        print("Artist name and city cannot be empty.")
        return
    
    # Authenticate with YouTube
    print("\nAuthenticating with YouTube...")
    youtube = get_authenticated_service()
    
    if not youtube:
        print("Authentication failed. Exiting.")
        return
    
    # Pattern to match filenames like "2025-10-23 21.30.24.mp4"
    pattern = r"(\d{4})-(\d{2})-(\d{2})\s+(\d{2})\.(\d{2})\.(\d{2})\.mp4"
    
    uploaded_count = 0
    
    for file_path in mp4_files:
        filename = file_path.name
        match = re.match(pattern, filename)
        
        if match:
            year, month, day, hour, minute, second = match.groups()
            
            # Create title: {Artist name} | {City} | YYYY MM DD | HH MM SS
            title = f"{artist_name} | {city} | {year} {month} {day} | {hour} {minute} {second}"
            
            try:
                # Upload the video
                upload_video(youtube, str(file_path), title)
                
                # If upload successful, move to trash
                move_to_trash(file_path)
                uploaded_count += 1
                
            except Exception as e:
                print(f"Error uploading {filename}: {e}")
        else:
            print(f"Skipped (doesn't match expected format): {filename}")
    
    print(f"\n✓ Successfully uploaded and trashed {uploaded_count} file(s).")

if __name__ == "__main__":
    main()