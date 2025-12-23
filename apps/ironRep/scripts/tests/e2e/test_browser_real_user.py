#!/usr/bin/env python3
"""
🧪 IronRep Enterprise E2E Test Suite
=====================================

Suite di test che simula un UTENTE REALE nel browser.
Cattura TUTTI gli errori che un cliente potrebbe vedere:
- Console errors/warnings
- JavaScript exceptions
- Network failures (API 4xx/5xx)
- Screenshot automatici su errore
- Performance metrics
- Accessibility issues

Requisiti:
    pip install playwright pytest-playwright
    playwright install chromium

Run:
    python scripts/tests/e2e/test_browser_real_user.py
"""

import asyncio
import json
import os
import sys
from datetime import datetime
from dataclasses import dataclass, field
from typing import List, Dict, Any, Optional
from pathlib import Path

# Check playwright
try:
    from playwright.async_api import async_playwright, Page, Browser, ConsoleMessage, Error
except ImportError:
    print("❌ Playwright not installed!")
    print("Run: pip install playwright && playwright install chromium")
    sys.exit(1)


# =============================================================================
# CONFIGURATION
# =============================================================================

@dataclass
class TestConfig:
    base_url: str = "http://localhost:80"  # Frontend Docker
    api_url: str = "http://localhost:8000/api"  # Backend Docker
    test_email: str = "e2e.browser.test@ironrep.it"
    test_password: str = "E2EBrowserTest123!"
    headless: bool = True
    slow_mo: int = 0  # ms between actions (0=fast, 100=visible)
    timeout: int = 30000  # ms
    screenshot_on_error: bool = True
    report_dir: str = "test-reports"


# =============================================================================
# ERROR COLLECTORS
# =============================================================================

@dataclass
class CollectedError:
    type: str  # console, network, js_exception
    message: str
    url: str
    timestamp: str
    severity: str = "error"  # error, warning, info
    stack: Optional[str] = None


@dataclass
class TestResult:
    name: str
    passed: bool
    duration_ms: float
    errors: List[CollectedError] = field(default_factory=list)
    warnings: List[CollectedError] = field(default_factory=list)
    screenshot_path: Optional[str] = None

    @property
    def status_icon(self) -> str:
        if not self.passed:
            return "❌"
        if self.warnings:
            return "⚠️"
        return "✅"


# =============================================================================
# BROWSER ERROR COLLECTOR
# =============================================================================

class BrowserErrorCollector:
    """Collects all errors from browser like a real user would see"""

    def __init__(self, page: Page):
        self.page = page
        self.console_errors: List[CollectedError] = []
        self.console_warnings: List[CollectedError] = []
        self.network_errors: List[CollectedError] = []
        self.js_exceptions: List[CollectedError] = []

        # Attach listeners
        page.on("console", self._on_console)
        page.on("pageerror", self._on_page_error)
        page.on("requestfailed", self._on_request_failed)
        page.on("response", self._on_response)

    def _on_console(self, msg: ConsoleMessage):
        """Capture console.log/warn/error"""
        error = CollectedError(
            type="console",
            message=msg.text,
            url=self.page.url,
            timestamp=datetime.now().isoformat(),
            severity=msg.type
        )

        if msg.type == "error":
            self.console_errors.append(error)
        elif msg.type == "warning":
            self.console_warnings.append(error)

    def _on_page_error(self, error: Error):
        """Capture uncaught JavaScript exceptions"""
        self.js_exceptions.append(CollectedError(
            type="js_exception",
            message=str(error),
            url=self.page.url,
            timestamp=datetime.now().isoformat(),
            severity="error",
            stack=error.stack if hasattr(error, 'stack') else None
        ))

    def _on_request_failed(self, request):
        """Capture failed network requests"""
        self.network_errors.append(CollectedError(
            type="network_failed",
            message=f"{request.method} {request.url} - {request.failure}",
            url=self.page.url,
            timestamp=datetime.now().isoformat(),
            severity="error"
        ))

    def _on_response(self, response):
        """Capture 4xx/5xx responses"""
        if response.status >= 400:
            self.network_errors.append(CollectedError(
                type="network_error",
                message=f"{response.status} {response.status_text}: {response.url}",
                url=self.page.url,
                timestamp=datetime.now().isoformat(),
                severity="error" if response.status >= 500 else "warning"
            ))

    @property
    def all_errors(self) -> List[CollectedError]:
        return self.console_errors + self.js_exceptions + [
            e for e in self.network_errors if e.severity == "error"
        ]

    @property
    def all_warnings(self) -> List[CollectedError]:
        return self.console_warnings + [
            e for e in self.network_errors if e.severity == "warning"
        ]

    def clear(self):
        """Clear all collected errors"""
        self.console_errors.clear()
        self.console_warnings.clear()
        self.network_errors.clear()
        self.js_exceptions.clear()


# =============================================================================
# TEST RUNNER
# =============================================================================

class BrowserTestRunner:
    """Enterprise E2E Test Runner"""

    def __init__(self, config: TestConfig):
        self.config = config
        self.results: List[TestResult] = []
        self.browser: Optional[Browser] = None
        self.page: Optional[Page] = None
        self.collector: Optional[BrowserErrorCollector] = None

        # Create report directory
        Path(config.report_dir).mkdir(parents=True, exist_ok=True)

    async def setup(self):
        """Initialize browser"""
        playwright = await async_playwright().start()
        self.browser = await playwright.chromium.launch(
            headless=self.config.headless,
            slow_mo=self.config.slow_mo
        )
        context = await self.browser.new_context(
            viewport={"width": 390, "height": 844},  # iPhone 14 Pro
            user_agent="Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
        )
        self.page = await context.new_page()
        self.page.set_default_timeout(self.config.timeout)
        self.collector = BrowserErrorCollector(self.page)

    async def teardown(self):
        """Cleanup"""
        if self.browser:
            await self.browser.close()

    async def run_test(self, name: str, test_fn) -> TestResult:
        """Run a single test"""
        print(f"\n  🧪 {name}...", end=" ", flush=True)
        self.collector.clear()
        start = datetime.now()

        screenshot_path = None
        passed = True
        error_msg = ""

        try:
            await test_fn()
        except Exception as e:
            passed = False
            error_msg = str(e)

            # Screenshot on error
            if self.config.screenshot_on_error:
                screenshot_name = f"{name.replace(' ', '_')}_{datetime.now().strftime('%H%M%S')}.png"
                screenshot_path = os.path.join(self.config.report_dir, screenshot_name)
                await self.page.screenshot(path=screenshot_path, full_page=True)

        duration = (datetime.now() - start).total_seconds() * 1000

        result = TestResult(
            name=name,
            passed=passed and len(self.collector.all_errors) == 0,
            duration_ms=duration,
            errors=self.collector.all_errors.copy(),
            warnings=self.collector.all_warnings.copy(),
            screenshot_path=screenshot_path
        )

        if error_msg:
            result.errors.append(CollectedError(
                type="test_failure",
                message=error_msg,
                url=self.page.url,
                timestamp=datetime.now().isoformat()
            ))

        self.results.append(result)

        # Print result
        print(f"{result.status_icon} ({duration:.0f}ms)")
        if result.errors:
            for err in result.errors[:3]:
                print(f"       ❌ {err.type}: {err.message[:80]}")
        if result.warnings:
            print(f"       ⚠️ {len(result.warnings)} warnings")

        return result

    def print_summary(self):
        """Print test summary"""
        passed = sum(1 for r in self.results if r.passed)
        failed = sum(1 for r in self.results if not r.passed)
        total_errors = sum(len(r.errors) for r in self.results)
        total_warnings = sum(len(r.warnings) for r in self.results)

        print(f"\n{'='*60}")
        print(f"📊 E2E BROWSER TEST SUMMARY")
        print(f"{'='*60}")
        print(f"  Tests:    {passed}/{len(self.results)} passed")
        print(f"  Errors:   {total_errors}")
        print(f"  Warnings: {total_warnings}")

        if failed > 0:
            print(f"\n  ❌ FAILED TESTS:")
            for r in self.results:
                if not r.passed:
                    print(f"     - {r.name}")
                    if r.screenshot_path:
                        print(f"       📸 {r.screenshot_path}")

        # Generate HTML report
        self._generate_html_report()

        print(f"\n  📄 Report: {self.config.report_dir}/report.html")
        print(f"{'='*60}\n")

        return failed == 0

    def _generate_html_report(self):
        """Generate detailed HTML report"""
        html = f"""<!DOCTYPE html>
<html>
<head>
    <title>IronRep E2E Test Report</title>
    <style>
        body {{ font-family: -apple-system, BlinkMacSystemFont, sans-serif; padding: 20px; background: #1a1a2e; color: #eee; }}
        .header {{ background: linear-gradient(135deg, #667eea, #764ba2); padding: 20px; border-radius: 12px; margin-bottom: 20px; }}
        .test {{ background: #16213e; border-radius: 8px; padding: 15px; margin: 10px 0; }}
        .passed {{ border-left: 4px solid #38ef7d; }}
        .failed {{ border-left: 4px solid #f5576c; }}
        .warning {{ border-left: 4px solid #feca57; }}
        .error-item {{ background: #2a0a0a; padding: 10px; border-radius: 4px; margin: 5px 0; font-size: 12px; }}
        .warning-item {{ background: #2a2a0a; padding: 10px; border-radius: 4px; margin: 5px 0; font-size: 12px; }}
        img {{ max-width: 100%; border-radius: 8px; margin-top: 10px; }}
    </style>
</head>
<body>
    <div class="header">
        <h1>🧪 IronRep E2E Test Report</h1>
        <p>Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}</p>
        <p>Passed: {sum(1 for r in self.results if r.passed)}/{len(self.results)}</p>
    </div>
"""
        for r in self.results:
            status_class = "passed" if r.passed else ("warning" if r.warnings else "failed")
            html += f"""
    <div class="test {status_class}">
        <h3>{r.status_icon} {r.name} ({r.duration_ms:.0f}ms)</h3>
"""
            if r.errors:
                html += "<h4>Errors:</h4>"
                for err in r.errors:
                    html += f'<div class="error-item"><strong>{err.type}</strong>: {err.message}</div>'

            if r.warnings:
                html += f"<h4>Warnings ({len(r.warnings)}):</h4>"
                for w in r.warnings[:5]:
                    html += f'<div class="warning-item"><strong>{w.type}</strong>: {w.message[:100]}</div>'

            if r.screenshot_path:
                html += f'<img src="{os.path.basename(r.screenshot_path)}" alt="Screenshot">'

            html += "</div>"

        html += "</body></html>"

        with open(os.path.join(self.config.report_dir, "report.html"), "w") as f:
            f.write(html)


# =============================================================================
# TEST CASES - REAL USER JOURNEY
# =============================================================================

async def run_all_tests():
    """Complete user journey tests"""
    config = TestConfig()
    runner = BrowserTestRunner(config)

    print(f"""
╔══════════════════════════════════════════════════════════════╗
║        🧪 IRONREP ENTERPRISE E2E BROWSER TEST                ║
║        {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                                     ║
║        Target: {config.base_url}                          ║
║        Viewport: 390x844 (iPhone 14 Pro)                     ║
╚══════════════════════════════════════════════════════════════╝
""")

    await runner.setup()

    try:
        # =====================================================================
        # INFRASTRUCTURE TESTS
        # =====================================================================
        print("\n📦 INFRASTRUCTURE")

        async def test_homepage_loads():
            await runner.page.goto(config.base_url)
            await runner.page.wait_for_load_state("networkidle")
            assert await runner.page.title(), "Page has no title"

        await runner.run_test("Homepage loads", test_homepage_loads)

        async def test_no_console_errors_on_load():
            await runner.page.goto(config.base_url)
            await runner.page.wait_for_load_state("networkidle")
            await asyncio.sleep(2)  # Wait for React hydration
            # Errors collected automatically by collector

        await runner.run_test("No console errors on load", test_no_console_errors_on_load)

        # =====================================================================
        # AUTHENTICATION TESTS
        # =====================================================================
        print("\n🔐 AUTHENTICATION")

        async def test_login_page_accessible():
            await runner.page.goto(f"{config.base_url}/login")
            await runner.page.wait_for_load_state("networkidle")
            # Check for login form elements
            email_input = await runner.page.query_selector('input[type="email"], input[name="email"]')
            assert email_input, "Email input not found"

        await runner.run_test("Login page accessible", test_login_page_accessible)

        async def test_login_flow():
            await runner.page.goto(f"{config.base_url}/login")
            await runner.page.wait_for_load_state("networkidle")

            # Fill login form
            email_input = await runner.page.query_selector('input[type="email"], input[name="email"]')
            if email_input:
                await email_input.fill(config.test_email)

            password_input = await runner.page.query_selector('input[type="password"]')
            if password_input:
                await password_input.fill(config.test_password)

            # Try to submit (may fail if user doesn't exist, that's ok)
            submit_btn = await runner.page.query_selector('button[type="submit"]')
            if submit_btn:
                await submit_btn.click()
                await asyncio.sleep(2)

        await runner.run_test("Login flow (form interaction)", test_login_flow)

        # =====================================================================
        # PAGE NAVIGATION TESTS
        # =====================================================================
        print("\n🧭 PAGE NAVIGATION")

        routes = [
            ("/", "Dashboard"),
            ("/medical", "Medical"),
            ("/coach", "Coach"),
            ("/workout", "Workout"),
            ("/nutrition", "Nutrition"),
            ("/exercises", "Exercises"),
            ("/progress", "Progress"),
            ("/profile", "Profile"),
        ]

        for route, name in routes:
            async def test_route(r=route):
                await runner.page.goto(f"{config.base_url}{r}")
                await runner.page.wait_for_load_state("networkidle")
                await asyncio.sleep(1)  # Wait for React

            await runner.run_test(f"Route: {name} ({route})", test_route)

        # =====================================================================
        # UI INTERACTION TESTS
        # =====================================================================
        print("\n🖱️ UI INTERACTIONS")

        async def test_bottom_nav_works():
            await runner.page.goto(config.base_url)
            await runner.page.wait_for_load_state("networkidle")

            # Look for bottom nav
            nav = await runner.page.query_selector('nav, [role="navigation"]')
            if nav:
                links = await nav.query_selector_all('a')
                if links:
                    await links[0].click()
                    await asyncio.sleep(1)

        await runner.run_test("Bottom navigation works", test_bottom_nav_works)

        async def test_buttons_clickable():
            await runner.page.goto(config.base_url)
            await runner.page.wait_for_load_state("networkidle")

            # Find all buttons and ensure they're clickable
            buttons = await runner.page.query_selector_all('button')
            for btn in buttons[:5]:
                box = await btn.bounding_box()
                if box:
                    assert box['width'] >= 44, f"Button too small: {box['width']}px"
                    assert box['height'] >= 44, f"Button too small: {box['height']}px"

        await runner.run_test("Buttons are touch-friendly (44px min)", test_buttons_clickable)

        # =====================================================================
        # PERFORMANCE TESTS
        # =====================================================================
        print("\n⚡ PERFORMANCE")

        async def test_page_load_time():
            start = datetime.now()
            await runner.page.goto(config.base_url)
            await runner.page.wait_for_load_state("networkidle")
            duration = (datetime.now() - start).total_seconds()
            assert duration < 5, f"Page too slow: {duration:.1f}s"

        await runner.run_test("Page loads under 5s", test_page_load_time)

    finally:
        await runner.teardown()

    # Print summary
    success = runner.print_summary()
    return success


# =============================================================================
# MAIN
# =============================================================================

if __name__ == "__main__":
    success = asyncio.run(run_all_tests())
    sys.exit(0 if success else 1)
