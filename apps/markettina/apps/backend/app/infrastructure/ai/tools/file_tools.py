"""
File Tools - File system operations for agents.

Provides safe file operations with validation and error handling.
"""

import re
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel


class FileInfo(BaseModel):
    """File information."""

    path: str
    name: str
    size: int
    created: datetime
    modified: datetime
    is_dir: bool
    extension: str | None = None


class SearchMatch(BaseModel):
    """Search result match."""

    file: str
    line_number: int
    line_content: str
    match_start: int
    match_end: int


class FileTools:
    """
    File system operations tools.
    
    Provides safe file operations with:
        - Path validation
        - Error handling
        - Content encoding
        - Pattern matching
    
    Example:
        >>> tools = FileTools(workspace="/project")
        >>> content = await tools.read_file("app/main.py")
        >>> await tools.write_file("output.txt", "Hello")
    """

    def __init__(self, workspace: str | None = None):
        """
        Initialize FileTools.
        
        Args:
            workspace: Base workspace directory (default: cwd)
        """
        self.workspace = Path(workspace) if workspace else Path.cwd()

    async def read_file(
        self,
        path: str,
        encoding: str = "utf-8"
    ) -> str:
        """
        Read file content.
        
        Args:
            path: File path (relative to workspace)
            encoding: File encoding
            
        Returns:
            File content as string
            
        Raises:
            FileNotFoundError: If file doesn't exist
            PermissionError: If no read permission
        """
        file_path = self._resolve_path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if not file_path.is_file():
            raise ValueError(f"Not a file: {path}")

        try:
            with open(file_path, encoding=encoding) as f:
                return f.read()
        except Exception as e:
            raise OSError(f"Error reading file {path}: {e}")

    async def write_file(
        self,
        path: str,
        content: str,
        encoding: str = "utf-8",
        create_dirs: bool = True
    ) -> bool:
        """
        Write content to file.
        
        Args:
            path: File path (relative to workspace)
            content: Content to write
            encoding: File encoding
            create_dirs: Create parent directories if needed
            
        Returns:
            True if successful
            
        Raises:
            PermissionError: If no write permission
        """
        file_path = self._resolve_path(path)

        # Create parent directories
        if create_dirs:
            file_path.parent.mkdir(parents=True, exist_ok=True)

        try:
            with open(file_path, "w", encoding=encoding) as f:
                f.write(content)
            return True
        except Exception as e:
            raise OSError(f"Error writing file {path}: {e}")

    async def list_files(
        self,
        pattern: str = "*",
        recursive: bool = False
    ) -> list[str]:
        """
        List files matching pattern.
        
        Args:
            pattern: Glob pattern (e.g., "*.py", "**/*.js")
            recursive: Search recursively
            
        Returns:
            List of file paths (relative to workspace)
        """
        if recursive and "**" not in pattern:
            pattern = f"**/{pattern}"

        base_path = self.workspace
        matches = []

        for file_path in base_path.glob(pattern):
            if file_path.is_file():
                rel_path = file_path.relative_to(base_path)
                matches.append(str(rel_path))

        return sorted(matches)

    async def search_in_files(
        self,
        pattern: str,
        path: str = ".",
        file_pattern: str = "*",
        is_regex: bool = False,
        case_sensitive: bool = False
    ) -> list[SearchMatch]:
        """
        Search for pattern in files.
        
        Args:
            pattern: Search pattern
            path: Directory to search
            file_pattern: File glob pattern
            is_regex: Treat pattern as regex
            case_sensitive: Case-sensitive search
            
        Returns:
            List of search matches
        """
        search_path = self._resolve_path(path)
        matches = []

        # Compile regex if needed
        if is_regex:
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(pattern, flags)
        else:
            flags = 0 if case_sensitive else re.IGNORECASE
            regex = re.compile(re.escape(pattern), flags)

        # Get files to search
        files = await self.list_files(
            pattern=file_pattern,
            recursive=True
        )

        for file_path in files:
            try:
                content = await self.read_file(file_path)

                for line_num, line in enumerate(content.splitlines(), 1):
                    for match in regex.finditer(line):
                        matches.append(
                            SearchMatch(
                                file=file_path,
                                line_number=line_num,
                                line_content=line,
                                match_start=match.start(),
                                match_end=match.end()
                            )
                        )
            except Exception:
                # Skip files that can't be read
                continue

        return matches

    async def get_file_info(self, path: str) -> FileInfo:
        """
        Get file metadata.
        
        Args:
            path: File path
            
        Returns:
            FileInfo with metadata
        """
        file_path = self._resolve_path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        stat = file_path.stat()

        return FileInfo(
            path=str(file_path.relative_to(self.workspace)),
            name=file_path.name,
            size=stat.st_size,
            created=datetime.fromtimestamp(stat.st_ctime),
            modified=datetime.fromtimestamp(stat.st_mtime),
            is_dir=file_path.is_dir(),
            extension=file_path.suffix if file_path.is_file() else None
        )

    async def delete_file(self, path: str) -> bool:
        """
        Delete file.
        
        Args:
            path: File path
            
        Returns:
            True if successful
        """
        file_path = self._resolve_path(path)

        if not file_path.exists():
            raise FileNotFoundError(f"File not found: {path}")

        if file_path.is_dir():
            raise ValueError(f"Cannot delete directory: {path}")

        try:
            file_path.unlink()
            return True
        except Exception as e:
            raise OSError(f"Error deleting file {path}: {e}")

    async def copy_file(
        self,
        source: str,
        destination: str,
        overwrite: bool = False
    ) -> bool:
        """
        Copy file.
        
        Args:
            source: Source file path
            destination: Destination file path
            overwrite: Overwrite if exists
            
        Returns:
            True if successful
        """
        import shutil

        src_path = self._resolve_path(source)
        dst_path = self._resolve_path(destination)

        if not src_path.exists():
            raise FileNotFoundError(f"Source not found: {source}")

        if dst_path.exists() and not overwrite:
            raise FileExistsError(f"Destination exists: {destination}")

        try:
            shutil.copy2(src_path, dst_path)
            return True
        except Exception as e:
            raise OSError(f"Error copying file: {e}")

    def _resolve_path(self, path: str) -> Path:
        """Resolve path relative to workspace."""
        p = Path(path)
        if p.is_absolute():
            return p
        return (self.workspace / p).resolve()
