# Videoteka Media Center

A modern desktop media center for Linux with streaming-style interface.

## Features

- 🎬 Streaming-style interface (Netflix, Amazon Prime, etc.)
- 📁 Support for videos, audio, images, and PDF documents
- 🖼️ Automatic thumbnail generation
- ⌨️ Full keyboard navigation
- 🔊 Audio preview (30 seconds)
- 📄 First page PDF visualization
- 💾 Portable SQLite database
- 🎨 Modern dark theme

## Requirements

- Python 3.9 or higher
- Qt6 (PySide6)
- Python libraries (see requirements.txt)
- **System dependencies** (required for Qt 6.5+):
  - `libxcb-cursor0` or `libxcb-cursor1` (depending on distribution)
  - Other xcb dependencies (usually already installed)

## Installation

### Development

1. Clone the repository:
```bash
git clone https://github.com/videoteka/media-center.git
cd media-center
```

2. Install system dependencies (required for Qt 6.5+):
```bash
# Ubuntu/Debian/Linux Mint
sudo apt update
sudo apt install libxcb-cursor0 libxcb-xinerama0 libxcb-xfixes0 libxcb-render0 libxcb-shape0

# Fedora/RHEL/CentOS
sudo dnf install libxcb-cursor libxcb-xinerama libxcb-xfixes libxcb-render libxcb-shape

# Arch Linux
sudo pacman -S libxcb-cursor libxcb-xinerama libxcb-xfixes libxcb-render libxcb-shape
```

**Note**: If `libxcb-cursor0` is not available in your distribution, try `libxcb-cursor1` or just `libxcb-cursor`.

3. Create a virtual environment:
```bash
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

4. Install Python dependencies:
```bash
pip install -r requirements.txt
```

5. Run the application:
```bash
python -m src.main
```

### Packaging

#### AppImage

To create an AppImage:

```bash
cd packaging/appimage
appimage-builder --recipe AppImageBuilder.yml
```

The AppImage will be generated in the build directory.

#### Flatpak

To create a Flatpak:

```bash
cd packaging/flatpak
flatpak-builder build org.videoteka.MediaCenter.yml
flatpak-builder --run build org.videoteka.MediaCenter.yml videoteka
```

## Usage

### First Run

On first run, the application will show a setup wizard where you can:

1. Select the folders that contain your multimedia files
2. Confirm and start scanning
3. Wait for file processing

### Navigation

- **Arrow keys**: Navigate between media cards
- **Enter**: Open the selected file with the default application
- **Esc**: Close previews/dialogs
- **Home/End**: Go to first/last item
- **Filters**: Use the buttons in the sidebar to filter by type

### Filters

- **All**: Shows all files
- **Videos**: Only video files
- **Audio**: Only audio files
- **Images**: Only images
- **Documents**: Only PDFs

Use the search bar to find files by name.

## Supported Formats

### Video
- MP4, MKV, AVI, MOV, WMV, FLV, WebM, M4V, MPG, MPEG, 3GP

### Audio
- MP3, FLAC, WAV, OGG, M4A, AAC, WMA, Opus, AMR

### Image
- JPG, JPEG, PNG, GIF, BMP, WebP, SVG, TIFF, ICO

### Document
- PDF

## Project Structure

```
videoteka-media-center/
├── src/
│   ├── main.py              # Entry point
│   ├── models/              # Data models
│   ├── views/               # UI components
│   ├── controllers/         # Controllers
│   ├── utils/               # Utilities
│   └── resources/           # Resources (styles, icons)
├── tests/                   # Unit tests
├── packaging/               # Packaging configurations
├── data/                    # Application data (SQLite, thumbnails)
└── requirements.txt        # Python dependencies
```

## Development

### Run Tests

```bash
python -m pytest tests/
```

### Contributing

Contributions are welcome! Please:

1. Fork the project
2. Create a branch for your feature (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Open a Pull Request

## Versioning

This project follows [Semantic Versioning](https://semver.org/):
- **MAJOR**: Incompatible API changes
- **MINOR**: Backwards-compatible new features
- **PATCH**: Backwards-compatible bug fixes

Current version: **0.1.0**

## License

This project is licensed under the GNU General Public License v3.0 - see the [LICENSE](LICENSE) file for details.

## Roadmap

- [ ] Playlist support
- [ ] Advanced metadata (IMDB for movies, tags)
- [ ] Advanced search
- [ ] Automatic organization
- [ ] Network streaming support
- [ ] Customizable themes
- [ ] Subtitle support
- [ ] Integrated media player

## Support

To report bugs or request features, open an issue on GitHub.

## Authors

- Videoteka Team

## Acknowledgments

- PySide6 for the excellent Qt library
- Open source community
