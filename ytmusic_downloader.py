import os
import re
import sys
from ytmusicapi import YTMusic
import subprocess
# 🔹 Clean up names for safe folder/file creation
def sanitize_name(name: str) -> str:
    """Make safe folder/filename by replacing illegal characters with underscores."""
    return re.sub(r'[<>:"/\\|?*]', '_', name)
# 🔹 Download a single track from a YouTube / YouTube Music link
def download_track(track_url: str, base_dir="DownloadedMusic"):
    """Download a single song from a YouTube or YouTube Music track URL."""
    print(f"\n=== Downloading track: {track_url} ===")
    os.makedirs(base_dir, exist_ok=True)
    command_download = [
        "yt-dlp",
        "-f", "bestaudio",
        "--extract-audio",
        "--audio-format", "mp3",
        "--add-metadata",
        "--embed-metadata",
        "--embed-thumbnail",
        "-o", os.path.join(base_dir, "%(title)s.%(ext)s"),
        track_url
    ]
    subprocess.run(command_download)
    print("\n✅ Track download completed!")
# 🔹 Main function to download songs from a YouTube Music playlist
def download_playlist(playlist_url: str, base_dir="DownloadedMusic"):
    """Download all songs from a YouTube Music playlist with proper titles, metadata, and high-res album art."""
    print(f"\n=== Downloading playlist: {playlist_url} ===")
    # Initialize YTMusic API (works without authentication for public playlists)
    ytmusic = YTMusic()
    # Extract playlist ID from the URL (everything after "list=")
    playlist_id = playlist_url.split("list=")[-1].split("&")[0]
    # Fetch full playlist metadata (no song limit)
    playlist = ytmusic.get_playlist(playlist_id, limit=None)
    # Create folder for the playlist
    playlist_name = sanitize_name(playlist['title'])
    playlist_folder = os.path.join(base_dir, playlist_name)
    os.makedirs(playlist_folder, exist_ok=True)
    # Extract all track info
    tracks = playlist['tracks']
    total_songs = len(tracks)
    # Counters for summary
    downloaded_count = 0
    already_present_count = 0
    no_video_count = 0
    # Loop through every song in the playlist
    for idx, track in enumerate(tracks, start=1):
        song_title = sanitize_name(track['title'])
        file_path = os.path.join(playlist_folder, f"{song_title}.mp3")
        # ✅ Skip if file already exists
        if os.path.exists(file_path):
            print(f"[{idx:3d} / {total_songs}] Already exists, skipping: {song_title}")
            already_present_count += 1
            continue
        # ❌ Skip if no videoId available (sometimes happens for unavailable tracks)
        video_id = track.get('videoId')
        if not video_id:
            print(f"[{idx:3d} / {total_songs}] ⚠️ No video found, skipping: {song_title}")
            no_video_count += 1
            continue
        # Build full YouTube URL for the track
        video_url = f"https://www.youtube.com/watch?v={video_id}"
        print(f"[{idx:3d} / {total_songs}] Downloading: {song_title}")
        # yt-dlp command → best audio, convert to MP3, embed metadata + thumbnail
        command_download = [
            "yt-dlp",
            "-f", "bestaudio",
            "--extract-audio",
            "--audio-format", "mp3",
            "--add-metadata",
            "--embed-metadata",
            "--embed-thumbnail",
            "-o", os.path.join(playlist_folder, "%(title)s.%(ext)s"),  # Save as song title
            video_url
        ]
        # Run download process
        subprocess.run(command_download)
        downloaded_count += 1
    # Summary after playlist download
    skipped_total = already_present_count + no_video_count
    print("\n✅ Playlist download completed!")
    print(f"Playlist: {playlist_name}")
    print(f"Total songs in playlist: {total_songs}")
    print(f"Downloaded this run: {downloaded_count}")
    print(f"Already in folder: {already_present_count}")
    print(f"Skipped (no video found): {no_video_count}")
    print(f"Total skipped: {skipped_total}")
# 🔹 Script entry point
def main():
    # Require a playlist link as input
    if len(sys.argv) < 2:
        print("Usage: python3 ytmusic_downloader.py <playlist-url>")
        print("       python3 ytmusic_downloader.py <track-url>")
        sys.exit(1)
    link = sys.argv[1]
    # Only supports YouTube Music playlist links
    if "playlist?list=" in link:
        download_playlist(link)
    elif "watch?v=" in link or "youtu.be/" in link or "music.youtube.com/watch" in link:
        download_track(link)
    else:
        print("❌ Unsupported link type. Provide a YouTube Music playlist URL or a track URL.")
# 🔹 Run script
if __name__ == "__main__":
    main()