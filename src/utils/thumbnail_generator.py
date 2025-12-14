"""Thumbnail generator for various media types."""

import hashlib
from pathlib import Path
from typing import Optional, Tuple

from PIL import Image


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
        try:
            import cv2

            cap = cv2.VideoCapture(file_path)
            if not cap.isOpened():
                return None

            # Get total frames
            total_frames = int(cap.get(cv2.CAP_PROP_FRAME_COUNT))
            if total_frames == 0:
                cap.release()
                return None

            # Seek to 25% of video
            target_frame = int(total_frames * 0.25)
            cap.set(cv2.CAP_PROP_POS_FRAMES, target_frame)

            ret, frame = cap.read()
            cap.release()

            if ret and frame is not None:
                # Convert BGR to RGB
                frame_rgb = cv2.cvtColor(frame, cv2.COLOR_BGR2RGB)
                return Image.fromarray(frame_rgb)

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


