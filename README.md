# oply-player
Music & video player with YouTube audio/video downloader (yt-dlp auto-updated).

<p align="center">
  <img src="docs/screenshots/oply.png" alt="Oply GUI" width="900">
</p>

Oply Player is a GTK3 multimedia suite created by **josejp2424**. It includes a music player, a video player, and a YouTube audio/video downloader in a single, consistent interface.

## Components

- **Oply**: music player (playlists, queue, basic controls).
- **Oply Video**: video player (including IPTV/TV News integration in v2.2+).
- **Oply Convert**: YouTube audio/video download + conversion (yt-dlp + FFmpeg).
- **Oply Radio**: online radio player with favorites (v2.2+).

## Note about yt-dlp

This repository **does not ship yt-dlp**.

- On first run, **Oply Convert** will offer to install it if it is missing.
- You can also use the **“Update yt-dlp”** button.

Oply Convert downloads the latest **official** `yt-dlp_linux` release and installs it to:

`/usr/local/Oply/bin/yt-dlp`

The install/update requires Internet access and will ask for admin permission (via the included GTK password prompt helper).

## Downloading music/video (Oply Convert)

1. Copy the YouTube video URL.
2. Paste it into **Oply Convert**.
3. Choose the output format (e.g. **mp3**, **wav**, **mp4**, **avi**, etc.).
4. Click **Convert** to download and convert.

Oply Convert uses **yt-dlp** for downloading and **FFmpeg** for conversion.

## Dependencies (Debian/Devuan)

Core runtime dependencies:

```bash
sudo apt update
sudo apt install -y \
  python3 python3-gi gir1.2-gtk-3.0 \
  python3-cairo python3-gi-cairo \
  gir1.2-gdkpixbuf-2.0 librsvg2-common \
  mpv ffmpeg \
  sudo ca-certificates
