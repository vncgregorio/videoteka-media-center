"""File utilities for media file detection and metadata extraction."""

import os
from pathlib import Path
from typing import Dict, List, Optional, Tuple


def get_media_extensions() -> Dict[str, List[str]]:
    """Get dictionary of media extensions by type.

    Returns:
        Dictionary mapping media types to lists of extensions
    """
    return {
        "video": [
            ".mp4",
            ".mkv",
            ".avi",
            ".mov",
            ".wmv",
            ".flv",
            ".webm",
            ".m4v",
            ".mpg",
            ".mpeg",
            ".3gp",
        ],
        "audio": [
            ".mp3",
            ".flac",
            ".wav",
            ".ogg",
            ".m4a",
            ".aac",
            ".wma",
            ".opus",
            ".amr",
        ],
        "image": [
            ".jpg",
            ".jpeg",
            ".png",
            ".gif",
            ".bmp",
            ".webp",
            ".svg",
            ".tiff",
            ".tif",
            ".ico",
        ],
        "document": [".pdf"],
    }


def is_media_file(file_path: str) -> bool:
    """Check if a file is a supported media file.

    Args:
        file_path: Path to the file

    Returns:
        True if file is a supported media type, False otherwise
    """
    path = Path(file_path)
    if not path.is_file():
        return False

    ext = path.suffix.lower()
    extensions = get_media_extensions()
    all_extensions = [
        ext for extensions_list in extensions.values() for ext in extensions_list
    ]
    return ext in all_extensions


def get_file_type(file_path: str) -> Optional[str]:
    """Detect file type from extension.

    Args:
        file_path: Path to the file

    Returns:
        Media type string ('video', 'audio', 'image', 'document') or None
    """
    ext = Path(file_path).suffix.lower()
    extensions = get_media_extensions()

    for media_type, ext_list in extensions.items():
        if ext in ext_list:
            return media_type

    return None


def get_file_metadata(file_path: str) -> Dict[str, any]:
    """Extract basic file metadata.

    Args:
        file_path: Path to the file

    Returns:
        Dictionary with file metadata (size, date_modified)
    """
    path = Path(file_path)
    if not path.exists():
        return {}

    stat = path.stat()
    return {
        "file_size": stat.st_size,
        "date_modified": stat.st_mtime,
    }


def get_file_duration(file_path: str) -> Optional[float]:
    """Get duration of video/audio file in seconds.

    Args:
        file_path: Path to the media file

    Returns:
        Duration in seconds or None if not available
    """
    file_type = get_file_type(file_path)
    if file_type not in ["video", "audio"]:
        return None

    try:
        if file_type == "audio":
            from mutagen import File as MutagenFile

            audio_file = MutagenFile(file_path)
            if audio_file is not None and hasattr(audio_file, "info"):
                return audio_file.info.length
        elif file_type == "video":
            import cv2

            cap = cv2.VideoCapture(file_path)
            if cap.isOpened():
                fps = cap.get(cv2.CAP_PROP_FPS)
                frame_count = cap.get(cv2.CAP_PROP_FRAME_COUNT)
                cap.release()
                if fps > 0:
                    return frame_count / fps
    except Exception:
        pass

    return None


def get_image_dimensions(file_path: str) -> Optional[Tuple[int, int]]:
    """Get dimensions of an image file.

    Args:
        file_path: Path to the image file

    Returns:
        Tuple of (width, height) or None if not available
    """
    file_type = get_file_type(file_path)
    if file_type != "image":
        return None

    try:
        from PIL import Image

        with Image.open(file_path) as img:
            return img.size
    except Exception:
        return None


def get_video_dimensions(file_path: str) -> Optional[Tuple[int, int]]:
    """Get dimensions of a video file.

    Args:
        file_path: Path to the video file

    Returns:
        Tuple of (width, height) or None if not available
    """
    file_type = get_file_type(file_path)
    if file_type != "video":
        return None

    try:
        import cv2

        cap = cv2.VideoCapture(file_path)
        if cap.isOpened():
            width = int(cap.get(cv2.CAP_PROP_FRAME_WIDTH))
            height = int(cap.get(cv2.CAP_PROP_FRAME_HEIGHT))
            cap.release()
            return (width, height)
    except Exception:
        pass

    return None


