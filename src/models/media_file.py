"""Media file model with type detection and validation."""

from enum import Enum
from pathlib import Path
from typing import Optional


class MediaType(Enum):
    """Enumeration of supported media types."""

    VIDEO = "video"
    AUDIO = "audio"
    IMAGE = "image"
    DOCUMENT = "document"


class MediaFile:
    """Represents a media file with its properties."""

    def __init__(
        self,
        file_path: str,
        file_name: Optional[str] = None,
        file_type: Optional[MediaType] = None,
        file_size: Optional[int] = None,
        duration: Optional[float] = None,
        width: Optional[int] = None,
        height: Optional[int] = None,
        folder_path: Optional[str] = None,
        thumbnail_path: Optional[str] = None,
    ):
        """Initialize a MediaFile instance.

        Args:
            file_path: Full path to the file
            file_name: Name of the file (extracted from path if not provided)
            file_type: Type of media (detected from extension if not provided)
            file_size: Size of file in bytes
            duration: Duration in seconds (for video/audio)
            width: Width in pixels (for video/image)
            height: Height in pixels (for video/image)
            folder_path: Path to the containing folder
            thumbnail_path: Path to thumbnail image
        """
        self.file_path = str(Path(file_path).resolve())
        self.file_name = file_name or Path(file_path).name
        self.file_type = file_type or self._detect_type(file_path)
        self.file_size = file_size
        self.duration = duration
        self.width = width
        self.height = height
        self.folder_path = folder_path or str(Path(file_path).parent)
        self.thumbnail_path = thumbnail_path

    @staticmethod
    def _detect_type(file_path: str) -> MediaType:
        """Detect media type from file extension.

        Args:
            file_path: Path to the file

        Returns:
            Detected MediaType
        """
        from pathlib import Path

        ext = Path(file_path).suffix.lower()
        extensions_map = {
            ".mp4": MediaType.VIDEO,
            ".mkv": MediaType.VIDEO,
            ".avi": MediaType.VIDEO,
            ".mov": MediaType.VIDEO,
            ".wmv": MediaType.VIDEO,
            ".flv": MediaType.VIDEO,
            ".webm": MediaType.VIDEO,
            ".m4v": MediaType.VIDEO,
            ".mp3": MediaType.AUDIO,
            ".flac": MediaType.AUDIO,
            ".wav": MediaType.AUDIO,
            ".ogg": MediaType.AUDIO,
            ".m4a": MediaType.AUDIO,
            ".aac": MediaType.AUDIO,
            ".wma": MediaType.AUDIO,
            ".jpg": MediaType.IMAGE,
            ".jpeg": MediaType.IMAGE,
            ".png": MediaType.IMAGE,
            ".gif": MediaType.IMAGE,
            ".bmp": MediaType.IMAGE,
            ".webp": MediaType.IMAGE,
            ".svg": MediaType.IMAGE,
            ".tiff": MediaType.IMAGE,
            ".pdf": MediaType.DOCUMENT,
        }

        return extensions_map.get(ext, MediaType.VIDEO)  # Default to video if unknown

    def to_dict(self) -> dict:
        """Convert MediaFile to dictionary for database storage.

        Returns:
            Dictionary representation of the media file
        """
        return {
            "file_path": self.file_path,
            "file_name": self.file_name,
            "file_type": self.file_type.value,
            "file_size": self.file_size,
            "duration": self.duration,
            "width": self.width,
            "height": self.height,
            "folder_path": self.folder_path,
            "thumbnail_path": self.thumbnail_path,
        }

    @classmethod
    def from_dict(cls, data: dict) -> "MediaFile":
        """Create MediaFile from dictionary.

        Args:
            data: Dictionary with media file data

        Returns:
            MediaFile instance
        """
        file_type = MediaType(data.get("file_type", "video"))
        return cls(
            file_path=data["file_path"],
            file_name=data.get("file_name"),
            file_type=file_type,
            file_size=data.get("file_size"),
            duration=data.get("duration"),
            width=data.get("width"),
            height=data.get("height"),
            folder_path=data.get("folder_path"),
            thumbnail_path=data.get("thumbnail_path"),
        )

    def __repr__(self) -> str:
        """String representation of MediaFile."""
        return (
            f"MediaFile(file_path={self.file_path!r}, "
            f"file_type={self.file_type.value}, "
            f"file_size={self.file_size})"
        )

