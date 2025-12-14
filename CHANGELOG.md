# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [0.1.0] - 2024-01-01

### Added
- Initial release of Videoteka Media Center
- Setup wizard for initial folder configuration
- SQLite database for media file storage
- Media scanner with recursive folder scanning
- Streaming-style interface with grid layout
- Support for videos, audio, images, and PDF documents
- Automatic thumbnail generation for all media types
- Keyboard navigation (arrows, Enter, Home/End, Esc)
- Filter panel with type filters and search
- Media preview for audio (30s), images, and PDFs
- Dark theme with modern styling
- AppImage and Flatpak packaging support
- Unit tests for core functionality

### Features
- **Media Types Supported:**
  - Videos: MP4, MKV, AVI, MOV, WMV, FLV, WebM, M4V, MPG, MPEG, 3GP
  - Audio: MP3, FLAC, WAV, OGG, M4A, AAC, WMA, Opus, AMR
  - Images: JPG, JPEG, PNG, GIF, BMP, WebP, SVG, TIFF, ICO
  - Documents: PDF

- **Interface:**
  - Netflix/streaming-style grid layout
  - Responsive card-based media display
  - Smooth keyboard navigation
  - Real-time filtering and search
  - Preview dialogs for different media types

- **Performance:**
  - Background scanning in separate thread
  - Lazy thumbnail loading
  - Thumbnail caching
  - Database indexing for fast queries


