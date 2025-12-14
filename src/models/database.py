"""Database management for SQLite storage."""

import sqlite3
from datetime import datetime
from pathlib import Path
from typing import Dict, List, Optional, Tuple

from ..models.media_file import MediaFile, MediaType


class Database:
    """SQLite database manager for media files."""

    def __init__(self, db_path: str = "data/videoteka.db"):
        """Initialize database connection.

        Args:
            db_path: Path to SQLite database file
        """
        self.db_path = Path(db_path)
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn: Optional[sqlite3.Connection] = None
        self.init_database()

    def _get_connection(self) -> sqlite3.Connection:
        """Get database connection, creating if necessary.

        Returns:
            SQLite connection object
        """
        if self.conn is None:
            self.conn = sqlite3.connect(
                str(self.db_path), check_same_thread=False
            )
            self.conn.row_factory = sqlite3.Row
        return self.conn

    def init_database(self) -> None:
        """Initialize database schema if it doesn't exist."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Create media_files table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS media_files (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                file_path TEXT UNIQUE NOT NULL,
                file_name TEXT NOT NULL,
                file_type TEXT NOT NULL,
                file_size INTEGER,
                duration REAL,
                width INTEGER,
                height INTEGER,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                date_modified TIMESTAMP,
                folder_path TEXT NOT NULL,
                thumbnail_path TEXT,
                UNIQUE(file_path)
            )
            """
        )

        # Create folders table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS folders (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                folder_path TEXT UNIQUE NOT NULL,
                date_added TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                is_active INTEGER DEFAULT 1,
                UNIQUE(folder_path)
            )
            """
        )

        # Create metadata table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS metadata (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                media_file_id INTEGER NOT NULL,
                key TEXT NOT NULL,
                value TEXT,
                FOREIGN KEY (media_file_id) REFERENCES media_files(id) ON DELETE CASCADE,
                UNIQUE(media_file_id, key)
            )
            """
        )

        # Create preferences table
        cursor.execute(
            """
            CREATE TABLE IF NOT EXISTS preferences (
                key TEXT PRIMARY KEY,
                value TEXT
            )
            """
        )

        # Create indexes for performance
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_file_type ON media_files(file_type)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_folder_path ON media_files(folder_path)"
        )
        cursor.execute(
            "CREATE INDEX IF NOT EXISTS idx_file_name ON media_files(file_name)"
        )

        conn.commit()

    def add_media_file(self, media_file: MediaFile) -> int:
        """Add a media file to the database.

        Args:
            media_file: MediaFile instance to add

        Returns:
            ID of the inserted record
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        data = media_file.to_dict()
        cursor.execute(
            """
            INSERT OR REPLACE INTO media_files
            (file_path, file_name, file_type, file_size, duration, width, height,
             date_modified, folder_path, thumbnail_path)
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            """,
            (
                data["file_path"],
                data["file_name"],
                data["file_type"],
                data["file_size"],
                data["duration"],
                data["width"],
                data["height"],
                datetime.now().timestamp(),
                data["folder_path"],
                data["thumbnail_path"],
            ),
        )

        conn.commit()
        return cursor.lastrowid

    def get_media_files(
        self,
        file_type: Optional[str] = None,
        folder_path: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict]:
        """Get media files with optional filters.

        Args:
            file_type: Filter by media type ('video', 'audio', 'image', 'document')
            folder_path: Filter by folder path
            search_query: Search in file names
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of dictionaries with media file data
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM media_files WHERE 1=1"
        params = []

        if file_type:
            query += " AND file_type = ?"
            params.append(file_type)

        if folder_path:
            query += " AND folder_path = ?"
            params.append(folder_path)

        if search_query:
            query += " AND file_name LIKE ?"
            params.append(f"%{search_query}%")

        query += " ORDER BY file_name ASC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        if offset:
            query += " OFFSET ?"
            params.append(offset)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def get_media_file_by_path(self, file_path: str) -> Optional[Dict]:
        """Get a media file by its path.

        Args:
            file_path: Path to the file

        Returns:
            Dictionary with media file data or None
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT * FROM media_files WHERE file_path = ?", (file_path,))
        row = cursor.fetchone()

        return dict(row) if row else None

    def update_media_file(self, file_id: int, data: Dict) -> None:
        """Update a media file record.

        Args:
            file_id: ID of the media file
            data: Dictionary with fields to update
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        set_clauses = []
        params = []

        for key, value in data.items():
            if key != "id" and key != "file_path":  # Don't allow updating these
                set_clauses.append(f"{key} = ?")
                params.append(value)

        if set_clauses:
            params.append(file_id)
            query = f"UPDATE media_files SET {', '.join(set_clauses)} WHERE id = ?"
            cursor.execute(query, params)
            conn.commit()

    def delete_media_file(self, file_path: str) -> None:
        """Delete a media file from the database.

        Args:
            file_path: Path to the file to delete
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("DELETE FROM media_files WHERE file_path = ?", (file_path,))
        conn.commit()

    def add_folder(self, folder_path: str) -> int:
        """Add a folder to the database.

        Args:
            folder_path: Path to the folder

        Returns:
            ID of the inserted record
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT OR IGNORE INTO folders (folder_path) VALUES (?)",
            (folder_path,),
        )

        conn.commit()
        return cursor.lastrowid

    def get_folders(self, active_only: bool = True) -> List[Dict]:
        """Get list of folders.

        Args:
            active_only: Only return active folders

        Returns:
            List of dictionaries with folder data
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if active_only:
            cursor.execute(
                "SELECT * FROM folders WHERE is_active = 1 ORDER BY folder_path"
            )
        else:
            cursor.execute("SELECT * FROM folders ORDER BY folder_path")

        rows = cursor.fetchall()
        return [dict(row) for row in rows]

    def update_folder(self, folder_id: int, is_active: bool) -> None:
        """Update folder active status.

        Args:
            folder_id: ID of the folder
            is_active: Active status
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "UPDATE folders SET is_active = ? WHERE id = ?",
            (1 if is_active else 0, folder_id),
        )
        conn.commit()

    def get_media_count(self, file_type: Optional[str] = None) -> int:
        """Get count of media files.

        Args:
            file_type: Optional filter by type

        Returns:
            Total count of media files
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        if file_type:
            cursor.execute(
                "SELECT COUNT(*) FROM media_files WHERE file_type = ?", (file_type,)
            )
        else:
            cursor.execute("SELECT COUNT(*) FROM media_files")

        return cursor.fetchone()[0]

    def get_unique_folders(self) -> List[str]:
        """Get list of unique folder paths from media files.

        Returns:
            List of unique folder paths
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT DISTINCT folder_path FROM media_files ORDER BY folder_path")
        rows = cursor.fetchall()
        return [row[0] for row in rows]

    def get_categories(self, root_folders: List[str]) -> List[str]:
        """Extract categories (first-level subfolders) from media files.

        Args:
            root_folders: List of root folder paths that were mapped

        Returns:
            List of unique category names
        """
        # Normalize root folders to ensure consistent path comparison
        normalized_root_folders = [str(Path(r).resolve()) for r in root_folders]
        
        all_folders = self.get_unique_folders()
        categories = set()

        for folder_path in all_folders:
            # Normalize folder path for comparison
            normalized_folder = str(Path(folder_path).resolve())
            category = self._get_category_from_path(normalized_folder, normalized_root_folders)
            if category:
                categories.add(category)

        return sorted(list(categories))

    def _get_category_from_path(self, folder_path: str, root_folders: List[str]) -> Optional[str]:
        """Extract full category path from folder path relative to root folders.
        
        Returns the complete relative path from root to folder, joined with " > ".
        Example: if root is "/home/user/youtube" and folder is 
        "/home/user/youtube/investments/stocks", returns "investments > stocks".

        Args:
            folder_path: Full folder path (should be normalized/resolved)
            root_folders: List of root folder paths (should be normalized/resolved)

        Returns:
            Full category path like "investments > stocks" or None
        """
        from pathlib import Path

        folder = Path(folder_path)
        for root in root_folders:
            root_path = Path(root)
            try:
                relative = folder.relative_to(root_path)
                if len(relative.parts) > 0:
                    # Join all parts with " > "
                    return " > ".join(relative.parts)
            except ValueError:
                # Not relative to this root
                continue
        return None

    def get_media_files_by_category(
        self,
        category: str,
        root_folders: List[str],
        file_type: Optional[str] = None,
        search_query: Optional[str] = None,
        limit: Optional[int] = None,
        offset: Optional[int] = None,
    ) -> List[Dict]:
        """Get media files filtered by category.

        Args:
            category: Category name to filter by (can be full path like "investments > stocks")
            root_folders: List of root folder paths
            file_type: Optional filter by media type
            search_query: Optional search query
            limit: Maximum number of results
            offset: Offset for pagination

        Returns:
            List of media file dictionaries
        """
        # Normalize root folders to ensure consistent path comparison
        normalized_root_folders = [str(Path(r).resolve()) for r in root_folders]
        
        # Get all folders that match this category
        all_folders = self.get_unique_folders()
        matching_folders = []

        for folder_path in all_folders:
            # Normalize folder path for comparison
            normalized_folder = str(Path(folder_path).resolve())
            cat = self._get_category_from_path(normalized_folder, normalized_root_folders)
            # Match exact category (now supports full paths like "investments > stocks")
            # Only match if cat is not None and matches category
            if cat is not None and cat == category:
                matching_folders.append(folder_path)

        if not matching_folders:
            return []

        # Get media files from matching folders
        conn = self._get_connection()
        cursor = conn.cursor()

        query = "SELECT * FROM media_files WHERE folder_path IN ("
        placeholders = ",".join(["?"] * len(matching_folders))
        query += placeholders + ")"

        params = list(matching_folders)

        if file_type:
            query += " AND file_type = ?"
            params.append(file_type)

        if search_query:
            query += " AND file_name LIKE ?"
            params.append(f"%{search_query}%")

        query += " ORDER BY file_name ASC"

        if limit:
            query += " LIMIT ?"
            params.append(limit)

        if offset:
            query += " OFFSET ?"
            params.append(offset)

        cursor.execute(query, params)
        rows = cursor.fetchall()

        return [dict(row) for row in rows]

    def get_preference(self, key: str, default: Optional[str] = None) -> Optional[str]:
        """Get a preference value.

        Args:
            key: Preference key
            default: Default value if not found

        Returns:
            Preference value or default
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute("SELECT value FROM preferences WHERE key = ?", (key,))
        row = cursor.fetchone()

        return row[0] if row else default

    def set_preference(self, key: str, value: str) -> None:
        """Set a preference value.

        Args:
            key: Preference key
            value: Preference value
        """
        conn = self._get_connection()
        cursor = conn.cursor()

        cursor.execute(
            "INSERT OR REPLACE INTO preferences (key, value) VALUES (?, ?)",
            (key, value),
        )
        conn.commit()

    def clear_all_data(self) -> None:
        """Clear all data from database (media files, folders, metadata) but keep schema and preferences."""
        conn = self._get_connection()
        cursor = conn.cursor()

        # Delete all data but keep schema
        cursor.execute("DELETE FROM media_files")
        cursor.execute("DELETE FROM folders")
        cursor.execute("DELETE FROM metadata")
        # Keep preferences (user settings)

        conn.commit()

    def close(self) -> None:
        """Close database connection."""
        if self.conn:
            self.conn.close()
            self.conn = None


