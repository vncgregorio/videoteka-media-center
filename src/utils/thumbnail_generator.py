"""Thumbnail generator for various media types."""

import contextlib
import hashlib
import os
import sys
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image


@contextlib.contextmanager
def suppress_stderr():
    """Temporarily suppress stderr to hide FFmpeg/AV1 error messages.
    
    Yields:
        None
    """
    with open(os.devnull, 'w') as devnull:
        old_stderr = sys.stderr
        sys.stderr = devnull
        try:
            yield
        finally:
            sys.stderr = old_stderr


class ThumbnailGenerator:
    """Generate thumbnails for media files."""

    def __init__(self, cache_dir: str = "data/thumbnails", size: Tuple[int, int] = (300, 200)):
        """Initialize thumbnail generator.

        Args:
            cache_dir: Directory to cache thumbnails
            size: Default thumbnail size (width, height)
        """
        self.cache_dir = Path(cache_dir)
        self.cache_dir.mkdir(parents=True, exist_ok=True)
        self.size = size

    def _get_cache_path(self, file_path: str) -> Path:
        """Get cache path for a file's thumbnail.

        Args:
            file_path: Path to the media file

        Returns:
            Path to cached thumbnail
        """
        # Create hash from file path for cache filename
        file_hash = hashlib.md5(file_path.encode()).hexdigest()
        return self.cache_dir / f"{file_hash}.jpg"

    def generate_thumbnail(
        self, file_path: str, file_type: str, force_regenerate: bool = False
    ) -> Optional[str]:
        """Generate thumbnail for a media file.

        Args:
            file_path: Path to the media file
            file_type: Type of media ('video', 'audio', 'image', 'document')
            force_regenerate: Force regeneration even if cached

        Returns:
            Path to thumbnail file or None if generation failed
        """
        cache_path = self._get_cache_path(file_path)

        # Return cached thumbnail if exists and not forcing regeneration
        if cache_path.exists() and not force_regenerate:
            return str(cache_path)

        try:
            if file_type == "video":
                thumbnail = self._generate_video_thumbnail(file_path)
            elif file_type == "image":
                thumbnail = self._generate_image_thumbnail(file_path)
            elif file_type == "document":
                thumbnail = self._generate_pdf_thumbnail(file_path)
            elif file_type == "audio":
                thumbnail = self._generate_audio_thumbnail(file_path)
            else:
                return None

            if thumbnail:
                # Save thumbnail
                thumbnail.thumbnail(self.size, Image.Resampling.LANCZOS)
                thumbnail.save(cache_path, "JPEG", quality=85)
                return str(cache_path)

        except Exception:
            pass

        return None

    def _generate_video_thumbnail(self, file_path: str) -> Optional[Image.Image]:
        """Generate thumbnail from video file.

        Args:
            file_path: Path to video file

        Returns:
            PIL Image or None
        """
        cap = None
        try:
            import cv2

            # Suppress OpenCV logging to hide FFmpeg/AV1 warnings
            # OpenCV uses different log levels: 0=SILENT, 1=FATAL, 2=ERROR, 3=WARN, 4=INFO, 5=DEBUG, 6=VERBOSE
            old_log_level = cv2.getLogLevel()
            cv2.setLogLevel(0)  # Set to SILENT to suppress all OpenCV/FFmpeg messages

            try:
                # Suppress stderr to hide FFmpeg/AV1 error messages (additional layer)
                with suppress_stderr():
                    # Try to open video file
                    cap = cv2.VideoCapture(file_path)
                    if not cap.isOpened():
                        return None

                    # Get total frames - handle potential AV1/codec errors
                    try:
                        total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
                    except (ValueError, OverflowError):
                        # AV1 or other codec issues may cause invalid frame counts
                        return None

                    if total_frames <= 0:
                        return None

                    # Seek to 25% of video, but try first frame if seek fails
                    target_frame = max(0, int(total_frames * 0.25))
                    try:
                        cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)
                    except Exception:
                        # If seek fails, try first frame
                        cap.set(cv2.CAP_PROP_POS_FRAMES, 0)

                    # Read frame with timeout handling
                    ret, frame = cap.read()

                    if ret and frame is not None and frame.size > 0:
                        # Convert BGR to RGB
                        try:
                            frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                            return Image.fromarray(frame_rgb)
                        except Exception:
                            # Color conversion failed
                            return None
            finally:
                # Restore original OpenCV log level
                cv2.setLogLevel(old_log_level)

        except (OSError, IOError, MemoryError) as e:
            # Handle AV1 codec errors, missing headers, or memory issues
            # These are often the cause of "AV1 missing header" errors
            pass
        except Exception:
            # Catch any other unexpected errors
            pass
        finally:
            # Always release VideoCapture to prevent memory leaks
            if cap is not None:
                try:
                    cap.release()
                except Exception:
                    pass

        return None

    def _generate_image_thumbnail(self, file_path: str) -> Optional[Image.Image]:
        """Generate thumbnail from image file.

        Args:
            file_path: Path to image file

        Returns:
            PIL Image or None
        """
        try:
            with Image.open(file_path) as img:
                # Convert to RGB if necessary (e.g., for PNG with transparency)
                if img.mode in ("RGBA", "LA", "P"):
                    rgb_img = Image.new("RGB", img.size, (255, 255, 255))
                    if img.mode == "P":
                        img = img.convert("RGBA")
                    rgb_img.paste(img, mask=img.split()[-1] if img.mode in ("RGBA", "LA") else None)
                    return rgb_img
                elif img.mode != "RGB":
                    return img.convert("RGB")
                else:
                    return img.copy()
        except Exception:
            pass

        return None

    def _generate_pdf_thumbnail(self, file_path: str) -> Optional[Image.Image]:
        """Generate thumbnail from PDF file (first page).

        Args:
            file_path: Path to PDF file

        Returns:
            PIL Image or None
        """
        try:
            import fitz  # PyMuPDF

            doc = fitz.open(file_path)
            if len(doc) == 0:
                doc.close()
                return None

            # Get first page
            page = doc[0]
            # Render page to image (zoom factor for quality)
            pix = page.get_pixmap(matrix=fitz.Matrix(2, 2))
            img_data = pix.tobytes("ppm")

            # Convert to PIL Image
            from io import BytesIO

            img = Image.open(BytesIO(img_data))
            doc.close()

            return img.convert("RGB")

        except Exception:
            pass

        return None

    def _generate_audio_thumbnail(self, file_path: str) -> Optional[Image.Image]:
        """Generate default thumbnail for audio file.

        Args:
            file_path: Path to audio file

        Returns:
            PIL Image with default audio icon/pattern
        """
        # Create a simple gradient image as placeholder
        img = Image.new("RGB", self.size, (30, 30, 40))
        return img

    def get_thumbnail_path(self, file_path: str) -> Optional[str]:
        """Get thumbnail path if it exists in cache.

        Args:
            file_path: Path to the media file

        Returns:
            Path to thumbnail or None if not found
        """
        cache_path = self._get_cache_path(file_path)
        if cache_path.exists():
            return str(cache_path)
        return None


