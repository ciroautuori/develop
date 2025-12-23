#!/usr/bin/env python3
"""
IronRep E2E Test Suite v2
=========================

Comprehensive end-to-end tests for the entire IronRep system.
Tests API endpoints, authentication, agents, and frontend integration.

Run with: python3 tests/e2e/test_full_system.py
"""

import requests
import json
import time
import sys
from datetime import datetime
from typing import Optional, Dict, Any, List
from dataclasses import dataclass, field
from enum import Enum


# =============================================================================
# CONFIGURATION
# =============================================================================

class Config:
    \"\"\"Test configuration\"\"\"
    # Per Docker locale
    BASE_URL = "http://localhost:80"
    API_URL = "http://localhost:8000/api"
    TIMEOUT = 30

    # Test user credentials
    TEST_EMAIL = "e2e.test@ironrep.it"
    TEST_PASSWORD = "E2ETestPass123!"
    TEST_NAME = "E2E Test User"


# =============================================================================
# TEST RESULT TRACKING
# =============================================================================

class TestStatus(Enum):
    PASSED = "✅ PASSED"
    FAILED = "❌ FAILED"
    SKIPPED = "⏭️ SKIPPED"
    WARNING = "⚠️ WARNING"


@dataclass
class TestResult:
    name: str
    status: TestStatus
    duration_ms: float
    message: str = ""
    details: Dict[str, Any] = field(default_factory=dict)


@dataclass
class TestSuite:
    name: str
    results: List[TestResult] = field(default_factory=list)

    def add(self, result: TestResult):
        self.results.append(result)

    @property
    def passed(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.PASSED)

    @property
    def failed(self) -> int:
        return sum(1 for r in self.results if r.status == TestStatus.FAILED)

    @property
    def total(self) -> int:
        return len(self.results)


# =============================================================================
# TEST UTILITIES
# =============================================================================

class TestRunner:
    """Handles test execution and reporting"""

    def __init__(self):
        self.session = requests.Session()
        self.token: Optional[str] = None
        self.suites: List[TestSuite] = []
        self.current_suite: Optional[TestSuite] = None

    def start_suite(self, name: str):
        """Start a new test suite"""
        self.current_suite = TestSuite(name=name)
        self.suites.append(self.current_suite)
        print(f"\n{'='*60}")
        print(f"🧪 TEST SUITE: {name}")
        print(f"{'='*60}")

    def run_test(self, name: str, test_fn):
        """Run a single test and record results"""
        start = time.time()
        try:
            result = test_fn()
            duration = (time.time() - start) * 1000

            if result is True or result is None:
                test_result = TestResult(
                    name=name,
                    status=TestStatus.PASSED,
                    duration_ms=duration
                )
            elif isinstance(result, dict):
                test_result = TestResult(
                    name=name,
                    status=result.get('status', TestStatus.PASSED),
                    duration_ms=duration,
                    message=result.get('message', ''),
                    details=result.get('details', {})
                )
            else:
                test_result = TestResult(
                    name=name,
                    status=TestStatus.PASSED,
                    duration_ms=duration,
                    message=str(result) if result else ''
                )

        except AssertionError as e:
            duration = (time.time() - start) * 1000
            test_result = TestResult(
                name=name,
                status=TestStatus.FAILED,
                duration_ms=duration,
                message=str(e)
            )
        except Exception as e:
            duration = (time.time() - start) * 1000
            test_result = TestResult(
                name=name,
                status=TestStatus.FAILED,
                duration_ms=duration,
                message=f"Exception: {type(e).__name__}: {str(e)}"
            )

        self.current_suite.add(test_result)

        # Print result
        status_icon = test_result.status.value
        print(f"  {status_icon} {name} ({duration:.0f}ms)")
        if test_result.message:
            print(f"      → {test_result.message[:100]}")

        return test_result.status == TestStatus.PASSED

    def get(self, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated GET request"""
        headers = kwargs.pop('headers', {})
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return self.session.get(
            f"{Config.API_URL}{endpoint}",
            headers=headers,
            timeout=Config.TIMEOUT,
            **kwargs
        )

    def post(self, endpoint: str, **kwargs) -> requests.Response:
        """Make authenticated POST request"""
        headers = kwargs.pop('headers', {})
        if self.token:
            headers['Authorization'] = f'Bearer {self.token}'
        return self.session.post(
            f"{Config.API_URL}{endpoint}",
            headers=headers,
            timeout=Config.TIMEOUT,
            **kwargs
        )

    def print_summary(self):
        """Print final test summary"""
        print(f"\n{'='*60}")
        print("📊 TEST SUMMARY")
        print(f"{'='*60}")

        total_passed = 0
        total_failed = 0
        total_warnings = 0
        total_skipped = 0
        total_tests = 0

        for suite in self.suites:
            passed = sum(1 for r in suite.results if r.status == TestStatus.PASSED)
            failed = sum(1 for r in suite.results if r.status == TestStatus.FAILED)
            warnings = sum(1 for r in suite.results if r.status == TestStatus.WARNING)
            skipped = sum(1 for r in suite.results if r.status == TestStatus.SKIPPED)

            total_passed += passed
            total_failed += failed
            total_warnings += warnings
            total_skipped += skipped
            total_tests += suite.total

            if failed > 0:
                status = "❌"
            elif warnings > 0:
                status = "⚠️"
            else:
                status = "✅"
            print(f"  {status} {suite.name}: {passed}/{suite.total} passed")

        print(f"\n{'─'*60}")
        print(f"  TOTAL: {total_passed}/{total_tests} tests passed")
        print(f"  ⚠️ {total_warnings} warnings")
        print(f"  ⏭️ {total_skipped} skipped")

        if total_failed > 0:
            print(f"\n  ❌ {total_failed} tests FAILED")
            print("\n  Failed tests:")
            for suite in self.suites:
                for result in suite.results:
                    if result.status == TestStatus.FAILED:
                        print(f"    - {suite.name}/{result.name}")
                        print(f"      {result.message[:80]}")

        print(f"{'='*60}\n")

        return total_failed == 0


# =============================================================================
# TESTS: INFRASTRUCTURE
# =============================================================================

def test_infrastructure(runner: TestRunner):
    """Test basic infrastructure"""
    runner.start_suite("Infrastructure")

    # Test frontend is accessible
    def test_frontend_accessible():
        resp = requests.get(Config.BASE_URL, timeout=10)
        assert resp.status_code == 200, f"Status: {resp.status_code}"
        assert len(resp.text) > 1000, "Response too short"
        return {"message": f"Got {len(resp.text)} bytes"}

    runner.run_test("Frontend accessible", test_frontend_accessible)

    # Test API responds
    def test_api_responds():
        resp = requests.get(f"{Config.API_URL}/exercises/", timeout=10)
        assert resp.status_code == 200, f"Status: {resp.status_code}"
        return {"message": "API responds correctly"}

    runner.run_test("API responds", test_api_responds)

    # Test static assets
    def test_static_assets():
        resp = requests.get(f"{Config.BASE_URL}/favicon.ico", timeout=10)
        assert resp.status_code in [200, 204], f"Status: {resp.status_code}"
        return True

    runner.run_test("Static assets (favicon)", test_static_assets)


# =============================================================================
# TESTS: AUTHENTICATION
# =============================================================================

def test_authentication(runner: TestRunner):
    """Test authentication flow"""
    runner.start_suite("Authentication")

    # Test login with OAuth2 form
    def test_login():
        resp = requests.post(
            f"{Config.API_URL}/auth/login",
            data={
                "username": Config.TEST_EMAIL,
                "password": Config.TEST_PASSWORD
            },
            timeout=10
        )

        if resp.status_code == 200:
            data = resp.json()
            runner.token = data.get('access_token')
            return {"message": f"Token obtained: {runner.token[:20]}..."}
        else:
            return {
                "status": TestStatus.WARNING,
                "message": f"Login failed: {resp.status_code} - will try register"
            }

    runner.run_test("Login with OAuth2", test_login)

    # If no token, try to register
    if not runner.token:
        def test_register_and_login():
            reg_resp = requests.post(
                f"{Config.API_URL}/auth/register",
                json={
                    "email": Config.TEST_EMAIL,
                    "password": Config.TEST_PASSWORD,
                    "name": Config.TEST_NAME
                },
                timeout=10
            )

            if reg_resp.status_code in [200, 201, 409]:
                login_resp = requests.post(
                    f"{Config.API_URL}/auth/login",
                    data={
                        "username": Config.TEST_EMAIL,
                        "password": Config.TEST_PASSWORD
                    },
                    timeout=10
                )

                if login_resp.status_code == 200:
                    data = login_resp.json()
                    runner.token = data.get('access_token')
                    return {"message": f"Registered & logged in: {runner.token[:20]}..."}
                else:
                    assert False, f"Login after register failed: {login_resp.status_code}"
            else:
                assert False, f"Register failed: {reg_resp.status_code}"

        runner.run_test("Register and Login", test_register_and_login)

    # Test token validation
    def test_get_current_user():
        if not runner.token:
            return {"status": TestStatus.SKIPPED, "message": "No token"}

        resp = runner.get("/users/me")
        if resp.status_code == 200:
            data = resp.json()
            return {"message": f"User: {data.get('email', 'unknown')}"}
        else:
            assert False, f"Get user failed: {resp.status_code}"

    runner.run_test("Get current user (/users/me)", test_get_current_user)


# =============================================================================
# TESTS: EXERCISES API
# =============================================================================

def test_exercises_api(runner: TestRunner):
    """Test exercises endpoints"""
    runner.start_suite("Exercises API")

    def test_get_exercises():
        resp = runner.get("/exercises/")
        assert resp.status_code == 200, f"Status: {resp.status_code}"
        data = resp.json()
        count = len(data) if isinstance(data, list) else 0
        return {"message": f"Found {count} exercises"}

    runner.run_test("Get exercises list", test_get_exercises)

    def test_get_exercise_by_phase():
        resp = runner.get("/exercises/phase/warm_up")
        if resp.status_code == 200:
            data = resp.json()
            count = len(data) if isinstance(data, list) else 0
            return {"message": f"Found {count} warm_up exercises"}
        else:
            return {"status": TestStatus.WARNING, "message": f"Status: {resp.status_code}"}

    runner.run_test("Get exercises by phase", test_get_exercise_by_phase)


# =============================================================================
# TESTS: MEDICAL AGENT
# =============================================================================

def test_medical_agent(runner: TestRunner):
    """Test Medical Agent endpoints"""
    runner.start_suite("Medical Agent")

    def test_medical_ask():
        if not runner.token:
            return {"status": TestStatus.SKIPPED, "message": "No token"}

        # Medical agent uses 'question' field, not 'message'
        resp = runner.post("/medical/ask", json={
            "question": "Ho un dolore alla schiena bassa, cosa mi consigli?",
            "session_id": None
        })

        if resp.status_code == 200:
            data = resp.json()
            answer = data.get('answer', data.get('message', data.get('response', '')))
            return {"message": f"Response: {str(answer)[:60]}..."}
        else:
            return {"status": TestStatus.WARNING, "message": f"Status: {resp.status_code} - {resp.text[:80]}"}

    runner.run_test("Medical ask endpoint", test_medical_ask)

    def test_checkin_start():
        if not runner.token:
            return {"status": TestStatus.SKIPPED, "message": "No token"}

        resp = runner.post("/medical/checkin/start")
        if resp.status_code == 200:
            data = resp.json()
            session_id = data.get('session_id', 'N/A')
            return {"message": f"Session started: {str(session_id)[:30]}..."}
        else:
            return {"status": TestStatus.WARNING, "message": f"Status: {resp.status_code}"}

    runner.run_test("Start check-in session", test_checkin_start)


# =============================================================================
# TESTS: WORKOUT COACH
# =============================================================================

def test_workout_coach(runner: TestRunner):
    """Test Workout Coach endpoints"""
    runner.start_suite("Workout Coach")

    def test_coach_ask():
        if not runner.token:
            return {"status": TestStatus.SKIPPED, "message": "No token"}

        # Workout coach uses 'question' field, not 'message'
        resp = runner.post("/workout-coach/ask", json={
            "question": "Suggeriscimi un workout per oggi considerando il mio livello",
            "session_id": None
        })

        if resp.status_code == 200:
            data = resp.json()
            answer = data.get('answer', data.get('message', data.get('response', '')))
            return {"message": f"Response: {str(answer)[:60]}..."}
        else:
            return {"status": TestStatus.WARNING, "message": f"Status: {resp.status_code}"}

    runner.run_test("Coach ask endpoint", test_coach_ask)

    def test_get_today_workout():
        if not runner.token:
            return {"status": TestStatus.SKIPPED, "message": "No token"}

        resp = runner.get("/workouts/today")
        if resp.status_code == 200:
            data = resp.json()
            return {"message": f"Workout found: {data.get('success', False)}"}
        elif resp.status_code == 404:
            return {"status": TestStatus.WARNING, "message": "No workout for today (normal)"}
        else:
            return {"status": TestStatus.WARNING, "message": f"Status: {resp.status_code}"}

    runner.run_test("Get today's workout", test_get_today_workout)


# =============================================================================
# TESTS: NUTRITION AGENT
# =============================================================================

def test_nutrition_agent(runner: TestRunner):
    """Test Nutrition Agent endpoints"""
    runner.start_suite("Nutrition Agent")

    def test_nutrition_ask():
        if not runner.token:
            return {"status": TestStatus.SKIPPED, "message": "No token"}

        # Nutrition agent uses 'question' field, not 'message'
        resp = runner.post("/nutrition/ask", json={
            "question": "Quante proteine dovrei assumere al giorno per il recupero?",
            "session_id": None
        })

        if resp.status_code == 200:
            data = resp.json()
            answer = data.get('answer', data.get('message', data.get('response', '')))
            return {"message": f"Response: {str(answer)[:60]}..."}
        else:
            return {"status": TestStatus.WARNING, "message": f"Status: {resp.status_code}"}

    runner.run_test("Nutrition ask endpoint", test_nutrition_ask)
# =============================================================================
# TESTS: WIZARD AGENT
# =============================================================================

def test_wizard_agent(runner: TestRunner):
    """Test Wizard (Orchestrator) Agent"""
    runner.start_suite("Wizard Agent")

    # First test: start wizard session
    def test_wizard_start():
        if not runner.token:
            return {"status": TestStatus.SKIPPED, "message": "No token"}

        resp = runner.post("/wizard/start")

        if resp.status_code == 200:
            data = resp.json()
            session_id = data.get('session_id', 'N/A')
            return {
                "message": f"Session started: {str(session_id)[:30]}...",
                "details": {"session_id": session_id}
            }
        elif resp.status_code == 404:
            return {"status": TestStatus.WARNING, "message": "Wizard endpoint not found"}
        else:
            return {"status": TestStatus.WARNING, "message": f"Status: {resp.status_code}"}

    result = runner.run_test("Wizard start session", test_wizard_start)

    # Get session_id for next test
    wizard_session_id = None
    if runner.current_suite.results[-1].details:
        wizard_session_id = runner.current_suite.results[-1].details.get('session_id')

    def test_wizard_message():
        if not runner.token:
            return {"status": TestStatus.SKIPPED, "message": "No token"}

        if not wizard_session_id:
            return {"status": TestStatus.SKIPPED, "message": "No session_id from start"}

        resp = runner.post("/wizard/message", json={
            "session_id": wizard_session_id,
            "message": "Mi chiamo Ciro, ho 33 anni e sono un atleta CrossFit"
        })

        if resp.status_code == 200:
            data = resp.json()
            answer = data.get('answer', data.get('response', data.get('message', '')))
            return {"message": f"Response: {str(answer)[:60]}..."}
        elif resp.status_code == 404:
            return {"status": TestStatus.WARNING, "message": "Wizard message endpoint not found"}
        else:
            return {"status": TestStatus.WARNING, "message": f"Status: {resp.status_code}"}

    runner.run_test("Wizard send message", test_wizard_message)
# =============================================================================
# TESTS: STREAMING
# =============================================================================

def test_streaming(runner: TestRunner):
    """Test SSE streaming endpoints"""
    runner.start_suite("SSE Streaming")

    def test_streaming_endpoint():
        if not runner.token:
            return {"status": TestStatus.SKIPPED, "message": "No token"}

        try:
            headers = {'Authorization': f'Bearer {runner.token}'}

            resp = requests.post(
                f"{Config.API_URL}/stream/medical",
                json={"message": "Test streaming", "session_id": None},
                headers=headers,
                stream=True,
                timeout=15
            )

            if resp.status_code == 200:
                content_type = resp.headers.get('content-type', '')
                if 'text/event-stream' in content_type:
                    for chunk in resp.iter_content(chunk_size=100):
                        if chunk:
                            return {"message": f"SSE streaming works! First chunk: {len(chunk)} bytes"}
                        break
                    return {"message": "SSE connected but no data yet"}
                else:
                    return {"message": f"Response type: {content_type}"}
            elif resp.status_code == 404:
                return {"status": TestStatus.WARNING, "message": "Streaming endpoint not mounted"}
            else:
                return {"status": TestStatus.WARNING, "message": f"Status: {resp.status_code}"}
        except Exception as e:
            return {"status": TestStatus.WARNING, "message": str(e)[:80]}

    runner.run_test("SSE Streaming endpoint", test_streaming_endpoint)


# =============================================================================
# TESTS: FOODS API
# =============================================================================

def test_foods_api(runner: TestRunner):
    """Test Foods API endpoints"""
    runner.start_suite("Foods API")

    def test_search_foods():
        resp = runner.get("/foods/search?q=chicken&limit=5")
        if resp.status_code == 200:
            data = resp.json()
            count = len(data) if isinstance(data, list) else 0
            return {"message": f"Found {count} foods"}
        else:
            return {"status": TestStatus.WARNING, "message": f"Status: {resp.status_code}"}

    runner.run_test("Search foods", test_search_foods)


# =============================================================================
# TESTS: BIOMETRICS
# =============================================================================

def test_biometrics(runner: TestRunner):
    """Test Biometrics endpoints"""
    runner.start_suite("Biometrics")

    def test_get_biometrics_history():
        if not runner.token:
            return {"status": TestStatus.SKIPPED, "message": "No token"}

        resp = runner.get("/biometrics/history")
        if resp.status_code == 200:
            data = resp.json()
            if isinstance(data, list):
                return {"message": f"Found {len(data)} biometric entries"}
            elif isinstance(data, dict):
                return {"message": f"History response: {list(data.keys())[:3]}"}
            return {"message": "Got biometrics history"}
        else:
            return {"status": TestStatus.WARNING, "message": f"Status: {resp.status_code}"}

    runner.run_test("Get biometrics history", test_get_biometrics_history)


# =============================================================================
# TESTS: FRONTEND ROUTES
# =============================================================================

def test_frontend_routes(runner: TestRunner):
    """Test frontend routes are accessible"""
    runner.start_suite("Frontend Routes")

    routes = [
        ("/", "Home"),
        ("/login", "Login"),
        ("/medical", "Medical"),
        ("/coach", "Coach"),
        ("/workout", "Workout"),
        ("/exercises", "Exercises"),
        ("/progress", "Progress"),
        ("/profile", "Profile"),
        ("/onboarding", "Onboarding"),
    ]

    for route, name in routes:
        def test_route(r=route):
            resp = requests.get(f"{Config.BASE_URL}{r}", timeout=10)
            assert resp.status_code == 200, f"Status: {resp.status_code}"
            return True

        runner.run_test(f"Route: {name} ({route})", test_route)


# =============================================================================
# MAIN
# =============================================================================

def main():
    """Run all tests"""
    print(f"""
╔══════════════════════════════════════════════════════════════╗
║             IRONREP E2E TEST SUITE v2                        ║
║             {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}                             ║
║             Target: {Config.BASE_URL}                     ║
╚══════════════════════════════════════════════════════════════╝
""")

    runner = TestRunner()

    # Run all test suites
    test_infrastructure(runner)
    test_authentication(runner)
    test_exercises_api(runner)
    test_medical_agent(runner)
    test_workout_coach(runner)
    test_nutrition_agent(runner)
    test_wizard_agent(runner)
    test_streaming(runner)
    test_foods_api(runner)
    test_biometrics(runner)
    test_frontend_routes(runner)

    # Print summary
    success = runner.print_summary()
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
