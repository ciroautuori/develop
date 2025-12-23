"""
Execution Tools - Command and script execution for agents.

Provides safe execution of commands, tests, and scripts with
timeout handling and output capture.
"""

import asyncio
import shlex
from datetime import datetime
from pathlib import Path

from pydantic import BaseModel


class CommandResult(BaseModel):
    """Command execution result."""

    command: str
    exit_code: int
    stdout: str
    stderr: str
    execution_time: float
    success: bool


class TestResult(BaseModel):
    """Test execution result."""

    framework: str
    total: int = 0
    passed: int = 0
    failed: int = 0
    skipped: int = 0
    errors: int = 0
    duration: float = 0.0
    output: str = ""
    success: bool = False


class ExecutionTools:
    """
    Command and script execution tools.
    
    Provides safe execution with:
        - Timeout handling
        - Output capture
        - Error handling
        - Async support
    
    Example:
        >>> tools = ExecutionTools()
        >>> result = await tools.run_command("ls -la")
        >>> test_result = await tools.run_tests("pytest", "tests/")
    """

    def __init__(
        self,
        workspace: str | None = None,
        default_timeout: int = 300
    ):
        """
        Initialize ExecutionTools.
        
        Args:
            workspace: Working directory
            default_timeout: Default timeout in seconds
        """
        self.workspace = Path(workspace) if workspace else Path.cwd()
        self.default_timeout = default_timeout

    async def run_command(
        self,
        command: str,
        cwd: str | None = None,
        timeout: int | None = None,
        env: dict[str, str] | None = None,
        shell: bool = False
    ) -> CommandResult:
        """
        Execute shell command.
        
        Args:
            command: Command to execute
            cwd: Working directory
            timeout: Timeout in seconds
            env: Environment variables
            shell: Use shell execution
            
        Returns:
            CommandResult with output and status
        """
        work_dir = Path(cwd) if cwd else self.workspace
        timeout_val = timeout or self.default_timeout

        # Parse command if not using shell
        cmd = command if shell else shlex.split(command)

        start_time = datetime.now()

        try:
            process = await asyncio.create_subprocess_exec(
                *([cmd] if shell else cmd),
                cwd=str(work_dir),
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
                env=env,
                shell=shell
            )

            stdout, stderr = await asyncio.wait_for(
                process.communicate(),
                timeout=timeout_val
            )

            execution_time = (datetime.now() - start_time).total_seconds()

            return CommandResult(
                command=command,
                exit_code=process.returncode or 0,
                stdout=stdout.decode("utf-8", errors="replace"),
                stderr=stderr.decode("utf-8", errors="replace"),
                execution_time=execution_time,
                success=process.returncode == 0
            )

        except TimeoutError:
            return CommandResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=f"Command timed out after {timeout_val}s",
                execution_time=timeout_val,
                success=False
            )
        except Exception as e:
            return CommandResult(
                command=command,
                exit_code=-1,
                stdout="",
                stderr=str(e),
                execution_time=0.0,
                success=False
            )

    async def run_tests(
        self,
        framework: str,
        path: str,
        args: list[str] | None = None,
        timeout: int | None = None
    ) -> TestResult:
        """
        Run tests with specified framework.
        
        Args:
            framework: Test framework (pytest, unittest, jest, etc.)
            path: Path to tests
            args: Additional arguments
            timeout: Timeout in seconds
            
        Returns:
            TestResult with parsed results
        """
        # Build command based on framework
        if framework == "pytest":
            cmd = ["pytest", path, "-v", "--tb=short"]
            if args:
                cmd.extend(args)
        elif framework == "unittest":
            cmd = ["python", "-m", "unittest", "discover", path]
        elif framework == "jest":
            cmd = ["npm", "test", "--", path]
        else:
            raise ValueError(f"Unsupported framework: {framework}")

        # Run command
        result = await self.run_command(
            " ".join(cmd),
            timeout=timeout
        )

        # Parse output based on framework
        if framework == "pytest":
            return self._parse_pytest_output(result)
        if framework == "unittest":
            return self._parse_unittest_output(result)
        return TestResult(
            framework=framework,
            output=result.stdout,
            success=result.success
        )

    async def run_script(
        self,
        script: str,
        interpreter: str = "python",
        args: list[str] | None = None,
        timeout: int | None = None
    ) -> CommandResult:
        """
        Run script file.
        
        Args:
            script: Script file path
            interpreter: Interpreter (python, node, etc.)
            args: Script arguments
            timeout: Timeout in seconds
            
        Returns:
            CommandResult
        """
        cmd_parts = [interpreter, script]
        if args:
            cmd_parts.extend(args)

        return await self.run_command(
            " ".join(cmd_parts),
            timeout=timeout
        )

    def _parse_pytest_output(self, result: CommandResult) -> TestResult:
        """Parse pytest output."""
        import re

        output = result.stdout + result.stderr

        # Parse summary line
        summary_pattern = r"=+ (?:(\d+) failed,? ?)?(?:(\d+) passed,? ?)?(?:(\d+) skipped,? ?)?(?:(\d+) error)?"
        match = re.search(summary_pattern, output)

        if match:
            failed = int(match.group(1) or 0)
            passed = int(match.group(2) or 0)
            skipped = int(match.group(3) or 0)
            errors = int(match.group(4) or 0)

            return TestResult(
                framework="pytest",
                total=passed + failed + skipped,
                passed=passed,
                failed=failed,
                skipped=skipped,
                errors=errors,
                output=output,
                success=failed == 0 and errors == 0
            )

        return TestResult(
            framework="pytest",
            output=output,
            success=result.success
        )

    def _parse_unittest_output(self, result: CommandResult) -> TestResult:
        """Parse unittest output."""
        import re

        output = result.stdout + result.stderr

        # Parse unittest summary
        summary_pattern = r"Ran (\d+) test"
        match = re.search(summary_pattern, output)

        total = int(match.group(1)) if match else 0

        # Check for failures
        failed_pattern = r"FAILED \(failures=(\d+)\)"
        failed_match = re.search(failed_pattern, output)
        failed = int(failed_match.group(1)) if failed_match else 0

        return TestResult(
            framework="unittest",
            total=total,
            passed=total - failed,
            failed=failed,
            output=output,
            success=failed == 0
        )
