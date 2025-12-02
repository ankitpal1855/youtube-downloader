from yt_dlp import YoutubeDL

# -------------------------------
# Download MP3 with forced output name
# -------------------------------
def download_mp3(url, outtmpl):
    opts = {
        "format": "bestaudio/best",
        "outtmpl": outtmpl,  # <- IMPORTANT
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "mp3",
                "preferredquality": "192",
            }
        ],
    }
    with YoutubeDL(opts) as ydl:
        ydl.download([url])


# -------------------------------
# Try one video format
# -------------------------------
def try_format(url, quality, ydl_format, outtmpl):
    print(f"Trying: {quality} → {ydl_format}")
    try:
        opts = {
            "format": ydl_format,
            "outtmpl": outtmpl,  # <- forced filename
            "merge_output_format": "mp4",
            "quiet": True
        }
        with YoutubeDL(opts) as ydl:
            ydl.download([url])
        print(f"SUCCESS → downloaded {quality}\n")
        return True
    except Exception as e:
        print(f"FAILED → {quality} ({e})\n")
        return False


# -------------------------------
# Download video with fallbacks
# -------------------------------
def download_video(url, quality, outtmpl):
    format_map = {
        "360p": [
            "bestvideo[height<=360][ext=mp4]+bestaudio/best",
            "bestvideo[height<=360]+bestaudio/best",
        ],
        "720p": [
            "bestvideo[height<=720][ext=mp4]+bestaudio/best",
            "bestvideo[height<=720]+bestaudio/best",
        ],
        "1080p": [
            "bestvideo[height<=1080][ext=mp4]+bestaudio/best",
            "bestvideo[height<=1080]+bestaudio/best",
        ],
    }

    for fmt in format_map[quality]:
        if try_format(url, quality, fmt, outtmpl):
            return

    print(f"❌ All formats failed for {quality}")
