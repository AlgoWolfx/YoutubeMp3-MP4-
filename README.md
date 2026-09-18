# YouTube MP3/MP4 Downloader

A desktop app for downloading YouTube videos as MP4 or extracting audio as MP3, built with a simple PyQt5 GUI.

## Features

- Download YouTube videos as MP4
- Extract and download audio as MP3
- Modern, animated user interface
- One-click access to the downloads folder
- Status updates and error notifications

## Requirements

- Python 3.6+
- PyQt5
- yt-dlp
- FFmpeg (required for MP3 conversion)

## Installation

1. Clone the repository:
   ```bash
   git clone https://github.com/AlgoWolfx/YoutubeMp3-MP4-.git
   cd YoutubeMp3-MP4-
   ```

2. Install dependencies:
   ```bash
   pip install PyQt5 yt-dlp
   ```

3. Install FFmpeg:
   - Windows: [FFmpeg downloads](https://ffmpeg.org/download.html)
   - Mac: `brew install ffmpeg`
   - Linux: `sudo apt-get install ffmpeg`

## Usage

1. Start the app:
   ```bash
   python "youtube mp3.py"
   ```
2. Paste a YouTube video URL
3. Choose MP4 (video) or MP3 (audio)
4. Click "Download"
5. Once finished, use "Open Downloads Folder" to access your files

Downloaded files are saved to a `YouTubeDownloads` folder on the desktop.

## License

Released under the MIT License. See [LICENSE](LICENSE) for details.
