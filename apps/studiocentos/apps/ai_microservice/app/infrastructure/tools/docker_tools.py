"""
Docker Tools - Container operations for agents.

Provides Docker container management, image building,
and Dockerfile validation.
"""

import asyncio
import json
from typing import Dict, Any, Optional, List
from pathlib import Path
from pydantic import BaseModel, Field
from datetime import datetime


class DockerImage(BaseModel):
    """Docker image information."""
    
    id: str
    repository: str
    tag: str
    created: datetime
    size: int


class ContainerInfo(BaseModel):
    """Container information."""
    
    id: str
    name: str
    image: str
    status: str
    ports: Dict[str, str] = Field(default_factory=dict)
    created: datetime


class BuildResult(BaseModel):
    """Docker build result."""
    
    image_id: str = ""
    success: bool = False
    output: str = ""
    duration: float = 0.0


class ValidationIssue(BaseModel):
    """Dockerfile validation issue."""
    
    line: int
    severity: str
    message: str
    rule: str


class ValidationResult(BaseModel):
    """Dockerfile validation result."""
    
    valid: bool = True
    issues: List[ValidationIssue] = Field(default_factory=list)
    errors: int = 0
    warnings: int = 0


class DockerTools:
    """
    Docker container operations.
    
    Provides:
        - Image building
        - Container management
        - Dockerfile validation
        - Docker Compose operations
        - Container logs
    
    Example:
        >>> tools = DockerTools()
        >>> result = await tools.build_image(".", "myapp:latest")
        >>> container = await tools.run_container("myapp:latest")
    """
    
    def __init__(self, workspace: Optional[str] = None):
        """Initialize DockerTools."""
        self.workspace = Path(workspace) if workspace else Path.cwd()
    
    async def build_image(
        self,
        path: str,
        tag: str,
        dockerfile: str = "Dockerfile",
        build_args: Optional[Dict[str, str]] = None,
        no_cache: bool = False
    ) -> BuildResult:
        """
        Build Docker image.
        
        Args:
            path: Build context path
            tag: Image tag
            dockerfile: Dockerfile path
            build_args: Build arguments
            no_cache: Don't use cache
            
        Returns:
            BuildResult
        """
        cmd = ["docker", "build", "-t", tag, "-f", dockerfile]
        
        if no_cache:
            cmd.append("--no-cache")
        
        if build_args:
            for key, value in build_args.items():
                cmd.extend(["--build-arg", f"{key}={value}"])
        
        cmd.append(path)
        
        start_time = datetime.now()
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(self.workspace)
        )
        
        stdout, stderr = await process.communicate()
        output = stdout.decode() + stderr.decode()
        
        duration = (datetime.now() - start_time).total_seconds()
        
        # Extract image ID from output
        image_id = ""
        if process.returncode == 0:
            for line in output.split("\n"):
                if "writing image sha256:" in line.lower():
                    image_id = line.split("sha256:")[-1].strip()[:12]
                    break
        
        return BuildResult(
            image_id=image_id,
            success=process.returncode == 0,
            output=output,
            duration=duration
        )
    
    async def run_container(
        self,
        image: str,
        name: Optional[str] = None,
        ports: Optional[Dict[str, int]] = None,
        env: Optional[Dict[str, str]] = None,
        volumes: Optional[Dict[str, str]] = None,
        detach: bool = True,
        remove: bool = False
    ) -> ContainerInfo:
        """
        Run Docker container.
        
        Args:
            image: Image name
            name: Container name
            ports: Port mappings (container_port: host_port)
            env: Environment variables
            volumes: Volume mounts (host_path: container_path)
            detach: Run in background
            remove: Remove container when stopped
            
        Returns:
            ContainerInfo
        """
        cmd = ["docker", "run"]
        
        if detach:
            cmd.append("-d")
        
        if remove:
            cmd.append("--rm")
        
        if name:
            cmd.extend(["--name", name])
        
        if ports:
            for container_port, host_port in ports.items():
                cmd.extend(["-p", f"{host_port}:{container_port}"])
        
        if env:
            for key, value in env.items():
                cmd.extend(["-e", f"{key}={value}"])
        
        if volumes:
            for host_path, container_path in volumes.items():
                cmd.extend(["-v", f"{host_path}:{container_path}"])
        
        cmd.append(image)
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"Failed to run container: {stderr.decode()}")
        
        container_id = stdout.decode().strip()
        
        # Get container info
        return await self._get_container_info(container_id)
    
    async def validate_dockerfile(
        self,
        dockerfile: str = "Dockerfile"
    ) -> ValidationResult:
        """
        Validate Dockerfile.
        
        Args:
            dockerfile: Dockerfile path
            
        Returns:
            ValidationResult
        """
        dockerfile_path = self.workspace / dockerfile
        
        if not dockerfile_path.exists():
            return ValidationResult(
                valid=False,
                issues=[ValidationIssue(
                    line=0,
                    severity="error",
                    message=f"Dockerfile not found: {dockerfile}",
                    rule="file-exists"
                )],
                errors=1
            )
        
        # Read and validate
        content = dockerfile_path.read_text()
        lines = content.split("\n")
        
        issues = []
        
        # Basic validation rules
        has_from = False
        
        for i, line in enumerate(lines, 1):
            line = line.strip()
            
            if not line or line.startswith("#"):
                continue
            
            # Check for FROM
            if line.startswith("FROM"):
                has_from = True
            
            # Check for best practices
            if line.startswith("RUN") and "apt-get" in line:
                if "update" in line and "install" not in line:
                    issues.append(ValidationIssue(
                        line=i,
                        severity="warning",
                        message="apt-get update should be combined with install",
                        rule="DL3008"
                    ))
            
            if line.startswith("RUN") and "sudo" in line:
                issues.append(ValidationIssue(
                    line=i,
                    severity="warning",
                    message="Avoid using sudo in Dockerfile",
                    rule="DL3004"
                ))
        
        if not has_from:
            issues.append(ValidationIssue(
                line=1,
                severity="error",
                message="Dockerfile must have a FROM instruction",
                rule="DL3001"
            ))
        
        errors = sum(1 for i in issues if i.severity == "error")
        warnings = sum(1 for i in issues if i.severity == "warning")
        
        return ValidationResult(
            valid=errors == 0,
            issues=issues,
            errors=errors,
            warnings=warnings
        )
    
    async def docker_compose_up(
        self,
        compose_file: str = "docker-compose.yml",
        detach: bool = True,
        build: bool = False
    ) -> bool:
        """
        Run docker-compose up.
        
        Args:
            compose_file: Docker Compose file
            detach: Run in background
            build: Build images before starting
            
        Returns:
            Success status
        """
        cmd = ["docker-compose", "-f", compose_file, "up"]
        
        if detach:
            cmd.append("-d")
        
        if build:
            cmd.append("--build")
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(self.workspace),
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        await process.communicate()
        
        return process.returncode == 0
    
    async def get_container_logs(
        self,
        container: str,
        tail: int = 100,
        follow: bool = False
    ) -> str:
        """
        Get container logs.
        
        Args:
            container: Container ID or name
            tail: Number of lines from end
            follow: Follow log output
            
        Returns:
            Log output
        """
        cmd = ["docker", "logs", "--tail", str(tail)]
        
        if follow:
            cmd.append("-f")
        
        cmd.append(container)
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, stderr = await process.communicate()
        
        return stdout.decode() + stderr.decode()
    
    async def _get_container_info(self, container_id: str) -> ContainerInfo:
        """Get container information."""
        cmd = ["docker", "inspect", container_id]
        
        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE
        )
        
        stdout, _ = await process.communicate()
        
        if process.returncode != 0:
            raise RuntimeError(f"Failed to inspect container: {container_id}")
        
        data = json.loads(stdout.decode())[0]
        
        # Parse port mappings
        ports = {}
        if "NetworkSettings" in data and "Ports" in data["NetworkSettings"]:
            for container_port, bindings in data["NetworkSettings"]["Ports"].items():
                if bindings:
                    ports[container_port] = bindings[0]["HostPort"]
        
        return ContainerInfo(
            id=data["Id"][:12],
            name=data["Name"].lstrip("/"),
            image=data["Config"]["Image"],
            status=data["State"]["Status"],
            ports=ports,
            created=datetime.fromisoformat(
                data["Created"].replace("Z", "+00:00")
            )
        )
