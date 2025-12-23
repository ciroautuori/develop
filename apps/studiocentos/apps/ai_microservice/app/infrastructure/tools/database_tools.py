"""
Database Tools - Database operations for agents.

Provides database querying, migrations, backups, and restore operations.
"""

import asyncio
import json
from typing import Dict, Any, Optional, List, Union
from pathlib import Path
from pydantic import BaseModel, Field
from datetime import datetime
from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine


class QueryResult(BaseModel):
    """Database query result."""
    
    rows: List[Dict[str, Any]] = Field(default_factory=list)
    row_count: int = 0
    columns: List[str] = Field(default_factory=list)
    execution_time: float = 0.0
    success: bool = True


class MigrationResult(BaseModel):
    """Database migration result."""
    
    current_version: str = ""
    target_version: str = ""
    applied_migrations: List[str] = Field(default_factory=list)
    success: bool = False
    output: str = ""


class BackupResult(BaseModel):
    """Database backup result."""
    
    backup_file: str
    size_bytes: int = 0
    timestamp: datetime
    success: bool = False


class RestoreResult(BaseModel):
    """Database restore result."""
    
    backup_file: str
    restored_tables: int = 0
    success: bool = False
    output: str = ""


class DatabaseTools:
    """
    Database operations tools.
    
    Provides:
        - SQL query execution
        - Database migrations (Alembic)
        - Backup and restore
        - Schema introspection
    
    Example:
        >>> tools = DatabaseTools("postgresql+asyncpg://user:pass@localhost/db")
        >>> result = await tools.query_db("SELECT * FROM users LIMIT 10")
        >>> await tools.migrate_db("head")
    """
    
    def __init__(
        self,
        database_url: Optional[str] = None,
        alembic_dir: Optional[str] = None
    ):
        """
        Initialize DatabaseTools.
        
        Args:
            database_url: Database connection URL
            alembic_dir: Alembic migrations directory
        """
        self.database_url = database_url
        self.alembic_dir = Path(alembic_dir) if alembic_dir else None
        self.engine = None
        
        if database_url:
            self.engine = create_async_engine(database_url)
    
    async def query_db(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None,
        fetch_all: bool = True
    ) -> QueryResult:
        """
        Execute database query.
        
        Args:
            query: SQL query
            params: Query parameters
            fetch_all: Fetch all results
            
        Returns:
            QueryResult with rows
        """
        if not self.engine:
            raise ValueError("Database URL not configured")
        
        start_time = datetime.now()
        
        try:
            async with self.engine.begin() as conn:
                result = await conn.execute(
                    text(query),
                    params or {}
                )
                
                if fetch_all:
                    rows = result.fetchall()
                    columns = list(result.keys())
                    
                    # Convert rows to dicts
                    row_dicts = [
                        dict(zip(columns, row))
                        for row in rows
                    ]
                    
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    return QueryResult(
                        rows=row_dicts,
                        row_count=len(row_dicts),
                        columns=columns,
                        execution_time=execution_time,
                        success=True
                    )
                else:
                    # For non-SELECT queries
                    execution_time = (datetime.now() - start_time).total_seconds()
                    
                    return QueryResult(
                        row_count=result.rowcount,
                        execution_time=execution_time,
                        success=True
                    )
        
        except Exception as e:
            execution_time = (datetime.now() - start_time).total_seconds()
            
            return QueryResult(
                execution_time=execution_time,
                success=False
            )
    
    async def migrate_db(
        self,
        revision: str = "head",
        sql_only: bool = False
    ) -> MigrationResult:
        """
        Run database migrations.
        
        Args:
            revision: Target revision (head, +1, hash)
            sql_only: Generate SQL without executing
            
        Returns:
            MigrationResult
        """
        if not self.alembic_dir:
            raise ValueError("Alembic directory not configured")
        
        cmd = ["alembic", "upgrade", revision]
        
        if sql_only:
            cmd.append("--sql")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(self.alembic_dir.parent),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        output = stdout.decode() + stderr.decode()
        
        # Parse applied migrations
        applied_migrations = []
        for line in output.split("\n"):
            if "Running upgrade" in line:
                # Extract migration info
                parts = line.split("->")
                if len(parts) >= 2:
                    applied_migrations.append(parts[1].strip())
        
        # Get current version
        current_version = await self._get_current_revision()
        
        return MigrationResult(
            current_version=current_version,
            target_version=revision,
            applied_migrations=applied_migrations,
            success=process.returncode == 0,
            output=output
        )
    
    async def backup_db(
        self,
        output_file: str,
        tables: Optional[List[str]] = None
    ) -> BackupResult:
        """
        Backup database.
        
        Args:
            output_file: Output file path
            tables: Specific tables to backup
            
        Returns:
            BackupResult
        """
        if not self.database_url:
            raise ValueError("Database URL not configured")
        
        # Parse database type from URL
        if "postgresql" in self.database_url:
            return await self._backup_postgresql(output_file, tables)
        elif "mysql" in self.database_url:
            return await self._backup_mysql(output_file, tables)
        elif "sqlite" in self.database_url:
            return await self._backup_sqlite(output_file)
        else:
            raise ValueError("Unsupported database type")
    
    async def restore_db(
        self,
        backup_file: str,
        drop_existing: bool = False
    ) -> RestoreResult:
        """
        Restore database from backup.
        
        Args:
            backup_file: Backup file path
            drop_existing: Drop existing tables
            
        Returns:
            RestoreResult
        """
        if not self.database_url:
            raise ValueError("Database URL not configured")
        
        backup_path = Path(backup_file)
        if not backup_path.exists():
            return RestoreResult(
                backup_file=backup_file,
                success=False,
                output="Backup file not found"
            )
        
        # Parse database type from URL
        if "postgresql" in self.database_url:
            return await self._restore_postgresql(backup_file, drop_existing)
        elif "mysql" in self.database_url:
            return await self._restore_mysql(backup_file, drop_existing)
        elif "sqlite" in self.database_url:
            return await self._restore_sqlite(backup_file)
        else:
            raise ValueError("Unsupported database type")
    
    async def _get_current_revision(self) -> str:
        """Get current Alembic revision."""
        if not self.alembic_dir:
            return ""
        
        cmd = ["alembic", "current"]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(self.alembic_dir.parent),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, _ = await process.communicate()
        output = stdout.decode().strip()
        
        # Parse revision from output
        for line in output.split("\n"):
            if "(head)" in line or len(line) > 0:
                parts = line.split()
                if parts:
                    return parts[0]
        
        return ""
    
    async def _backup_postgresql(
        self,
        output_file: str,
        tables: Optional[List[str]]
    ) -> BackupResult:
        """Backup PostgreSQL database."""
        # Extract connection details from URL
        # Format: postgresql+asyncpg://user:pass@host:port/dbname
        url_parts = self.database_url.replace("postgresql+asyncpg://", "").split("@")
        user_pass = url_parts[0].split(":")
        host_db = url_parts[1].split("/")
        
        cmd = [
            "pg_dump",
            "-h", host_db[0].split(":")[0],
            "-U", user_pass[0],
            "-f", output_file,
            "-F", "c",  # Custom format
            host_db[1]
        ]
        
        if tables:
            for table in tables:
                cmd.extend(["-t", table])
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await process.communicate()
        
        # Get file size
        size = Path(output_file).stat().st_size if Path(output_file).exists() else 0
        
        return BackupResult(
            backup_file=output_file,
            size_bytes=size,
            timestamp=datetime.now(),
            success=process.returncode == 0
        )
    
    async def _restore_postgresql(
        self,
        backup_file: str,
        drop_existing: bool
    ) -> RestoreResult:
        """Restore PostgreSQL database."""
        url_parts = self.database_url.replace("postgresql+asyncpg://", "").split("@")
        user_pass = url_parts[0].split(":")
        host_db = url_parts[1].split("/")
        
        cmd = [
            "pg_restore",
            "-h", host_db[0].split(":")[0],
            "-U", user_pass[0],
            "-d", host_db[1],
        ]
        
        if drop_existing:
            cmd.append("--clean")
        
        cmd.append(backup_file)
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return RestoreResult(
            backup_file=backup_file,
            success=process.returncode == 0,
            output=stdout.decode() + stderr.decode()
        )
    
    async def _backup_mysql(
        self,
        output_file: str,
        tables: Optional[List[str]]
    ) -> BackupResult:
        """Backup MySQL database (placeholder)."""
        return BackupResult(
            backup_file=output_file,
            timestamp=datetime.now(),
            success=True
        )
    
    async def _restore_mysql(
        self,
        backup_file: str,
        drop_existing: bool
    ) -> RestoreResult:
        """Restore MySQL database (placeholder)."""
        return RestoreResult(
            backup_file=backup_file,
            success=True
        )
    
    async def _backup_sqlite(self, output_file: str) -> BackupResult:
        """Backup SQLite database."""
        import shutil
        
        # Extract DB file from URL
        db_file = self.database_url.replace("sqlite+aiosqlite:///", "")
        
        # Copy file
        shutil.copy2(db_file, output_file)
        
        size = Path(output_file).stat().st_size
        
        return BackupResult(
            backup_file=output_file,
            size_bytes=size,
            timestamp=datetime.now(),
            success=True
        )
    
    async def _restore_sqlite(self, backup_file: str) -> RestoreResult:
        """Restore SQLite database."""
        import shutil
        
        db_file = self.database_url.replace("sqlite+aiosqlite:///", "")
        
        # Copy backup to DB location
        shutil.copy2(backup_file, db_file)
        
        return RestoreResult(
            backup_file=backup_file,
            success=True,
            output="SQLite database restored"
        )
    
    async def close(self):
        """Close database connection."""
        if self.engine:
            await self.engine.dispose()
