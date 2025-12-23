"""
Git Tools - Version control operations for agents.

Provides Git operations including status, diff, commit, push, and pull.
"""

import asyncio
from typing import Dict, Any, Optional, List
from pathlib import Path
from pydantic import BaseModel, Field
from datetime import datetime
from enum import Enum


class FileStatus(str, Enum):
    """Git file status."""
    MODIFIED = "modified"
    ADDED = "added"
    DELETED = "deleted"
    RENAMED = "renamed"
    UNTRACKED = "untracked"


class GitFileChange(BaseModel):
    """Git file change information."""
    
    path: str
    status: FileStatus
    additions: int = 0
    deletions: int = 0


class GitStatus(BaseModel):
    """Git repository status."""
    
    branch: str
    ahead: int = 0
    behind: int = 0
    staged: List[GitFileChange] = Field(default_factory=list)
    unstaged: List[GitFileChange] = Field(default_factory=list)
    untracked: List[str] = Field(default_factory=list)
    clean: bool = True


class GitDiff(BaseModel):
    """Git diff result."""
    
    files: List[GitFileChange] = Field(default_factory=list)
    total_additions: int = 0
    total_deletions: int = 0
    diff_text: str = ""


class CommitResult(BaseModel):
    """Git commit result."""
    
    commit_hash: str = ""
    message: str = ""
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0
    success: bool = False


class PushResult(BaseModel):
    """Git push result."""
    
    remote: str
    branch: str
    commits_pushed: int = 0
    success: bool = False
    output: str = ""


class PullResult(BaseModel):
    """Git pull result."""
    
    remote: str
    branch: str
    files_changed: int = 0
    insertions: int = 0
    deletions: int = 0
    success: bool = False
    output: str = ""


class GitTools:
    """
    Git version control operations.
    
    Provides:
        - Repository status
        - Diff viewing
        - Committing changes
        - Push/pull operations
        - Branch management
    
    Example:
        >>> tools = GitTools("/path/to/repo")
        >>> status = await tools.git_status()
        >>> diff = await tools.git_diff()
        >>> await tools.git_commit("Fix bug", ["file.py"])
    """
    
    def __init__(self, repo_path: Optional[str] = None):
        """
        Initialize GitTools.
        
        Args:
            repo_path: Git repository path (defaults to cwd)
        """
        self.repo_path = Path(repo_path) if repo_path else Path.cwd()
    
    async def git_status(self) -> GitStatus:
        """
        Get repository status.
        
        Returns:
            GitStatus with branch and file changes
        """
        # Get current branch
        branch_cmd = await self._run_git_command(["rev-parse", "--abbrev-ref", "HEAD"])
        branch = branch_cmd.strip()
        
        # Get status
        status_cmd = await self._run_git_command(["status", "--porcelain", "-b"])
        lines = status_cmd.split("\n")
        
        staged = []
        unstaged = []
        untracked = []
        ahead = 0
        behind = 0
        
        for line in lines:
            if not line:
                continue
            
            # Parse branch tracking info
            if line.startswith("##"):
                if "[ahead" in line:
                    ahead = int(line.split("[ahead ")[1].split("]")[0])
                if "[behind" in line:
                    behind = int(line.split("[behind ")[1].split("]")[0])
                continue
            
            # Parse file status
            status_code = line[:2]
            filepath = line[3:]
            
            if status_code == "??":
                untracked.append(filepath)
            elif status_code[0] != " ":
                # Staged
                staged.append(GitFileChange(
                    path=filepath,
                    status=self._parse_status_code(status_code[0])
                ))
            elif status_code[1] != " ":
                # Unstaged
                unstaged.append(GitFileChange(
                    path=filepath,
                    status=self._parse_status_code(status_code[1])
                ))
        
        return GitStatus(
            branch=branch,
            ahead=ahead,
            behind=behind,
            staged=staged,
            unstaged=unstaged,
            untracked=untracked,
            clean=not (staged or unstaged or untracked)
        )
    
    async def git_diff(
        self,
        paths: Optional[List[str]] = None,
        staged: bool = False
    ) -> GitDiff:
        """
        Get diff of changes.
        
        Args:
            paths: Specific paths to diff
            staged: Show staged changes
            
        Returns:
            GitDiff with changes
        """
        cmd = ["diff", "--numstat"]
        
        if staged:
            cmd.append("--cached")
        
        if paths:
            cmd.extend(paths)
        
        output = await self._run_git_command(cmd)
        
        files = []
        total_additions = 0
        total_deletions = 0
        
        for line in output.split("\n"):
            if not line:
                continue
            
            parts = line.split("\t")
            if len(parts) >= 3:
                additions = int(parts[0]) if parts[0] != "-" else 0
                deletions = int(parts[1]) if parts[1] != "-" else 0
                filepath = parts[2]
                
                files.append(GitFileChange(
                    path=filepath,
                    status=FileStatus.MODIFIED,
                    additions=additions,
                    deletions=deletions
                ))
                
                total_additions += additions
                total_deletions += deletions
        
        # Get full diff text
        diff_cmd = ["diff"]
        if staged:
            diff_cmd.append("--cached")
        if paths:
            diff_cmd.extend(paths)
        
        diff_text = await self._run_git_command(diff_cmd)
        
        return GitDiff(
            files=files,
            total_additions=total_additions,
            total_deletions=total_deletions,
            diff_text=diff_text
        )
    
    async def git_commit(
        self,
        message: str,
        paths: Optional[List[str]] = None,
        all_changes: bool = False
    ) -> CommitResult:
        """
        Commit changes.
        
        Args:
            message: Commit message
            paths: Specific paths to commit
            all_changes: Commit all tracked changes
            
        Returns:
            CommitResult
        """
        # Stage files if needed
        if paths:
            await self._run_git_command(["add"] + paths)
        elif all_changes:
            await self._run_git_command(["add", "-A"])
        
        # Commit
        output = await self._run_git_command([
            "commit",
            "-m",
            message
        ])
        
        # Parse output
        commit_hash = ""
        files_changed = 0
        insertions = 0
        deletions = 0
        
        if "nothing to commit" in output:
            return CommitResult(success=False)
        
        for line in output.split("\n"):
            if line.startswith("["):
                # Extract commit hash
                parts = line.split()
                if len(parts) >= 2:
                    commit_hash = parts[1].rstrip("]")
            
            if "files changed" in line or "file changed" in line:
                # Parse stats
                parts = line.split(",")
                for part in parts:
                    if "file" in part:
                        files_changed = int(part.split()[0])
                    elif "insertion" in part:
                        insertions = int(part.split()[0])
                    elif "deletion" in part:
                        deletions = int(part.split()[0])
        
        return CommitResult(
            commit_hash=commit_hash,
            message=message,
            files_changed=files_changed,
            insertions=insertions,
            deletions=deletions,
            success=True
        )
    
    async def git_push(
        self,
        remote: str = "origin",
        branch: Optional[str] = None,
        force: bool = False
    ) -> PushResult:
        """
        Push changes to remote.
        
        Args:
            remote: Remote name
            branch: Branch name (defaults to current)
            force: Force push
            
        Returns:
            PushResult
        """
        if not branch:
            status = await self.git_status()
            branch = status.branch
        
        cmd = ["push", remote, branch]
        if force:
            cmd.append("--force")
        
        output = await self._run_git_command(cmd)
        
        # Count commits pushed
        commits_pushed = 0
        for line in output.split("\n"):
            if ".." in line and "->" in line:
                # Parse commit range
                parts = line.split("..")
                if len(parts) >= 2:
                    commits_pushed = 1  # Simplified
        
        return PushResult(
            remote=remote,
            branch=branch,
            commits_pushed=commits_pushed,
            success=True,
            output=output
        )
    
    async def git_pull(
        self,
        remote: str = "origin",
        branch: Optional[str] = None,
        rebase: bool = False
    ) -> PullResult:
        """
        Pull changes from remote.
        
        Args:
            remote: Remote name
            branch: Branch name (defaults to current)
            rebase: Use rebase instead of merge
            
        Returns:
            PullResult
        """
        if not branch:
            status = await self.git_status()
            branch = status.branch
        
        cmd = ["pull", remote, branch]
        if rebase:
            cmd.append("--rebase")
        
        output = await self._run_git_command(cmd)
        
        # Parse output
        files_changed = 0
        insertions = 0
        deletions = 0
        
        for line in output.split("\n"):
            if "files changed" in line or "file changed" in line:
                parts = line.split(",")
                for part in parts:
                    if "file" in part:
                        files_changed = int(part.split()[0])
                    elif "insertion" in part:
                        insertions = int(part.split()[0])
                    elif "deletion" in part:
                        deletions = int(part.split()[0])
        
        return PullResult(
            remote=remote,
            branch=branch,
            files_changed=files_changed,
            insertions=insertions,
            deletions=deletions,
            success=True,
            output=output
        )
    
    async def _run_git_command(self, args: List[str]) -> str:
        """
        Run git command.
        
        Args:
            args: Git command arguments
            
        Returns:
            Command output
        """
        cmd = ["git"] + args
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(self.repo_path),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"Git command failed: {stderr.decode()}")
        
        return stdout.decode().strip()
    
    def _parse_status_code(self, code: str) -> FileStatus:
        """Parse git status code."""
        status_map = {
            "M": FileStatus.MODIFIED,
            "A": FileStatus.ADDED,
            "D": FileStatus.DELETED,
            "R": FileStatus.RENAMED,
            "?": FileStatus.UNTRACKED,
        }
        return status_map.get(code, FileStatus.MODIFIED)
