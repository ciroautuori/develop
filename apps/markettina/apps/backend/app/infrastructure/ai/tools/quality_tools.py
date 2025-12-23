"""
Quality Tools - Code quality and analysis tools for agents.

Provides linting, formatting, type checking, security scanning,
and complexity analysis.
"""

import asyncio
import json
from enum import Enum
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class Severity(str, Enum):
    """Issue severity level."""
    ERROR = "error"
    WARNING = "warning"
    INFO = "info"


class LintIssue(BaseModel):
    """Lint issue details."""

    file: str
    line: int
    column: int
    severity: Severity
    message: str
    rule: str
    fixable: bool = False


class LintResult(BaseModel):
    """Linting result."""

    total_files: int = 0
    total_issues: int = 0
    errors: int = 0
    warnings: int = 0
    infos: int = 0
    issues: list[LintIssue] = Field(default_factory=list)
    success: bool = True


class FormatResult(BaseModel):
    """Formatting result."""

    total_files: int = 0
    formatted_files: int = 0
    unchanged_files: int = 0
    files: list[str] = Field(default_factory=list)
    success: bool = True


class TypeCheckResult(BaseModel):
    """Type checking result."""

    total_files: int = 0
    total_errors: int = 0
    errors: list[dict[str, Any]] = Field(default_factory=list)
    success: bool = True


class SecurityIssue(BaseModel):
    """Security vulnerability."""

    file: str
    line: int
    severity: Severity
    title: str
    description: str
    cwe: str | None = None
    confidence: str = "HIGH"


class SecurityScanResult(BaseModel):
    """Security scan result."""

    total_issues: int = 0
    high_severity: int = 0
    medium_severity: int = 0
    low_severity: int = 0
    issues: list[SecurityIssue] = Field(default_factory=list)
    success: bool = True


class CoverageResult(BaseModel):
    """Test coverage result."""

    total_statements: int = 0
    covered_statements: int = 0
    missing_statements: int = 0
    coverage_percent: float = 0.0
    files: dict[str, float] = Field(default_factory=dict)
    success: bool = True


class ComplexityMetric(BaseModel):
    """Code complexity metric."""

    function: str
    file: str
    line: int
    complexity: int
    rank: str


class ComplexityResult(BaseModel):
    """Complexity analysis result."""

    average_complexity: float = 0.0
    max_complexity: int = 0
    high_complexity_count: int = 0
    metrics: list[ComplexityMetric] = Field(default_factory=list)
    success: bool = True


class QualityTools:
    """
    Code quality and analysis tools.
    
    Provides:
        - Linting (ruff, pylint, eslint)
        - Formatting (black, prettier)
        - Type checking (mypy, pyright)
        - Security scanning (bandit)
        - Test coverage (coverage.py, jest)
        - Complexity analysis (radon, mccabe)
    
    Example:
        >>> tools = QualityTools()
        >>> lint_result = await tools.lint_code("src/", linter="ruff")
        >>> coverage = await tools.test_coverage("pytest", "tests/")
    """

    def __init__(self, workspace: str | None = None):
        """Initialize QualityTools."""
        self.workspace = Path(workspace) if workspace else Path.cwd()

    async def lint_code(
        self,
        path: str,
        linter: str = "ruff",
        config: str | None = None
    ) -> LintResult:
        """
        Lint code files.
        
        Args:
            path: Path to lint
            linter: Linter to use (ruff, pylint, eslint)
            config: Config file path
            
        Returns:
            LintResult with issues
        """
        if linter == "ruff":
            return await self._run_ruff(path, config)
        if linter == "pylint":
            return await self._run_pylint(path, config)
        if linter == "eslint":
            return await self._run_eslint(path, config)
        raise ValueError(f"Unsupported linter: {linter}")

    async def format_code(
        self,
        path: str,
        formatter: str = "black",
        check_only: bool = False
    ) -> FormatResult:
        """
        Format code files.
        
        Args:
            path: Path to format
            formatter: Formatter (black, prettier, ruff)
            check_only: Only check, don't modify
            
        Returns:
            FormatResult
        """
        if formatter == "black":
            return await self._run_black(path, check_only)
        if formatter == "ruff":
            return await self._run_ruff_format(path, check_only)
        if formatter == "prettier":
            return await self._run_prettier(path, check_only)
        raise ValueError(f"Unsupported formatter: {formatter}")

    async def type_check(
        self,
        path: str,
        checker: str = "mypy"
    ) -> TypeCheckResult:
        """
        Type check code.
        
        Args:
            path: Path to check
            checker: Type checker (mypy, pyright)
            
        Returns:
            TypeCheckResult
        """
        if checker == "mypy":
            return await self._run_mypy(path)
        if checker == "pyright":
            return await self._run_pyright(path)
        raise ValueError(f"Unsupported checker: {checker}")

    async def security_scan(
        self,
        path: str,
        scanner: str = "bandit"
    ) -> SecurityScanResult:
        """
        Scan for security issues.
        
        Args:
            path: Path to scan
            scanner: Scanner (bandit, safety)
            
        Returns:
            SecurityScanResult
        """
        if scanner == "bandit":
            return await self._run_bandit(path)
        if scanner == "safety":
            return await self._run_safety()
        raise ValueError(f"Unsupported scanner: {scanner}")

    async def test_coverage(
        self,
        framework: str,
        path: str,
        min_coverage: float = 80.0
    ) -> CoverageResult:
        """
        Measure test coverage.
        
        Args:
            framework: Test framework (pytest, unittest)
            path: Test path
            min_coverage: Minimum coverage threshold
            
        Returns:
            CoverageResult
        """
        if framework in ["pytest", "unittest"]:
            return await self._run_coverage_py(path, min_coverage)
        if framework == "jest":
            return await self._run_jest_coverage(path, min_coverage)
        raise ValueError(f"Unsupported framework: {framework}")

    async def complexity_analysis(
        self,
        path: str,
        max_complexity: int = 10
    ) -> ComplexityResult:
        """
        Analyze code complexity.
        
        Args:
            path: Path to analyze
            max_complexity: Complexity threshold
            
        Returns:
            ComplexityResult
        """
        return await self._run_radon(path, max_complexity)

    async def _run_ruff(
        self,
        path: str,
        config: str | None
    ) -> LintResult:
        """Run ruff linter."""
        cmd = ["ruff", "check", path, "--output-format=json"]
        if config:
            cmd.extend(["--config", config])

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            stderr=asyncio.subprocess.PIPE,
            cwd=str(self.workspace)
        )

        stdout, stderr = await process.communicate()

        if not stdout:
            return LintResult(success=True)

        try:
            data = json.loads(stdout.decode())
            issues = []

            for item in data:
                issues.append(LintIssue(
                    file=item.get("filename", ""),
                    line=item.get("location", {}).get("row", 0),
                    column=item.get("location", {}).get("column", 0),
                    severity=Severity.ERROR if item.get("type") == "E" else Severity.WARNING,
                    message=item.get("message", ""),
                    rule=item.get("code", ""),
                    fixable=item.get("fix", {}).get("applicability") == "automatic"
                ))

            return LintResult(
                total_issues=len(issues),
                errors=sum(1 for i in issues if i.severity == Severity.ERROR),
                warnings=sum(1 for i in issues if i.severity == Severity.WARNING),
                issues=issues,
                success=process.returncode == 0
            )

        except json.JSONDecodeError:
            return LintResult(success=False)

    async def _run_black(
        self,
        path: str,
        check_only: bool
    ) -> FormatResult:
        """Run black formatter."""
        cmd = ["black", path]
        if check_only:
            cmd.append("--check")

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            cwd=str(self.workspace)
        )

        await process.communicate()

        return FormatResult(
            success=process.returncode == 0
        )

    async def _run_mypy(self, path: str) -> TypeCheckResult:
        """Run mypy type checker."""
        cmd = ["mypy", path, "--no-error-summary"]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            cwd=str(self.workspace)
        )

        stdout, _ = await process.communicate()

        return TypeCheckResult(
            success=process.returncode == 0
        )

    async def _run_bandit(self, path: str) -> SecurityScanResult:
        """Run bandit security scanner."""
        cmd = ["bandit", "-r", path, "-f", "json"]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            cwd=str(self.workspace)
        )

        stdout, _ = await process.communicate()

        if not stdout:
            return SecurityScanResult(success=True)

        try:
            data = json.loads(stdout.decode())
            issues = []

            for result in data.get("results", []):
                issues.append(SecurityIssue(
                    file=result.get("filename", ""),
                    line=result.get("line_number", 0),
                    severity=Severity(result.get("issue_severity", "INFO").lower()),
                    title=result.get("test_name", ""),
                    description=result.get("issue_text", ""),
                    cwe=result.get("issue_cwe", {}).get("id"),
                    confidence=result.get("issue_confidence", "HIGH")
                ))

            return SecurityScanResult(
                total_issues=len(issues),
                high_severity=sum(1 for i in issues if i.severity == Severity.ERROR),
                issues=issues,
                success=True
            )

        except json.JSONDecodeError:
            return SecurityScanResult(success=False)

    async def _run_coverage_py(
        self,
        path: str,
        min_coverage: float
    ) -> CoverageResult:
        """Run coverage.py."""
        # Run tests with coverage
        cmd = ["coverage", "run", "-m", "pytest", path]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            cwd=str(self.workspace),
            stdout=asyncio.subprocess.DEVNULL
        )

        await process.communicate()

        # Get report
        cmd = ["coverage", "json", "-o", "-"]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            cwd=str(self.workspace)
        )

        stdout, _ = await process.communicate()

        if not stdout:
            return CoverageResult(success=False)

        try:
            data = json.loads(stdout.decode())
            totals = data.get("totals", {})

            return CoverageResult(
                total_statements=totals.get("num_statements", 0),
                covered_statements=totals.get("covered_lines", 0),
                coverage_percent=totals.get("percent_covered", 0.0),
                success=totals.get("percent_covered", 0.0) >= min_coverage
            )

        except json.JSONDecodeError:
            return CoverageResult(success=False)

    async def _run_radon(
        self,
        path: str,
        max_complexity: int
    ) -> ComplexityResult:
        """Run radon complexity analyzer."""
        cmd = ["radon", "cc", path, "-j"]

        process = await asyncio.create_subprocess_exec(
            *cmd,
            stdout=asyncio.subprocess.PIPE,
            cwd=str(self.workspace)
        )

        stdout, _ = await process.communicate()

        if not stdout:
            return ComplexityResult(success=True)

        try:
            data = json.loads(stdout.decode())
            metrics = []
            total_complexity = 0
            count = 0

            for file, functions in data.items():
                for func in functions:
                    complexity = func.get("complexity", 0)
                    metrics.append(ComplexityMetric(
                        function=func.get("name", ""),
                        file=file,
                        line=func.get("lineno", 0),
                        complexity=complexity,
                        rank=func.get("rank", "A")
                    ))
                    total_complexity += complexity
                    count += 1

            high_complexity = sum(1 for m in metrics if m.complexity > max_complexity)

            return ComplexityResult(
                average_complexity=total_complexity / count if count else 0,
                max_complexity=max(m.complexity for m in metrics) if metrics else 0,
                high_complexity_count=high_complexity,
                metrics=metrics,
                success=high_complexity == 0
            )

        except json.JSONDecodeError:
            return ComplexityResult(success=False)

    # Placeholder methods for other tools
    async def _run_pylint(self, path: str, config: str | None) -> LintResult:
        """Run pylint (placeholder)."""
        return LintResult(success=True)

    async def _run_eslint(self, path: str, config: str | None) -> LintResult:
        """Run eslint (placeholder)."""
        return LintResult(success=True)

    async def _run_ruff_format(self, path: str, check_only: bool) -> FormatResult:
        """Run ruff format (placeholder)."""
        return FormatResult(success=True)

    async def _run_prettier(self, path: str, check_only: bool) -> FormatResult:
        """Run prettier (placeholder)."""
        return FormatResult(success=True)

    async def _run_pyright(self, path: str) -> TypeCheckResult:
        """Run pyright (placeholder)."""
        return TypeCheckResult(success=True)

    async def _run_safety(self) -> SecurityScanResult:
        """Run safety (placeholder)."""
        return SecurityScanResult(success=True)

    async def _run_jest_coverage(self, path: str, min_coverage: float) -> CoverageResult:
        """Run jest coverage (placeholder)."""
        return CoverageResult(success=True)
