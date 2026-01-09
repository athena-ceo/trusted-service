#!/usr/bin/env python
"""
Python-based test runner for cross-platform compatibility
Can run on Windows, macOS, and Linux

Usage:
    python run_tests.py --help
    python run_tests.py smoke
    python run_tests.py unit
    python run_tests.py all
"""

import argparse
import subprocess
import sys
import time
import os
import signal
from pathlib import Path
from typing import Optional, List


class Colors:
    """ANSI color codes for terminal output"""
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


class TestRunner:
    def __init__(self):
        self.root_dir = Path(__file__).parent
        self.backend_pid: Optional[int] = None
        self.frontend_pid: Optional[int] = None
        
    def print_colored(self, message: str, color: str = Colors.NC):
        """Print colored message"""
        print(f"{color}{message}{Colors.NC}")
    
    def check_port(self, port: int) -> bool:
        """Check if port is in use"""
        import socket
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        result = sock.connect_ex(('localhost', port))
        sock.close()
        return result == 0
    
    def wait_for_service(self, url: str, name: str, max_attempts: int = 30) -> bool:
        """Wait for service to be ready"""
        import urllib.request
        
        self.print_colored(f"Waiting for {name} to be ready...", Colors.YELLOW)
        
        for attempt in range(max_attempts):
            try:
                urllib.request.urlopen(url, timeout=2)
                self.print_colored(f"{name} is ready!", Colors.GREEN)
                return True
            except Exception:
                time.sleep(2)
        
        self.print_colored(f"{name} failed to start", Colors.RED)
        return False
    
    def start_backend(self):
        """Start backend server"""
        if self.check_port(8002):
            self.print_colored("Backend already running on port 8002", Colors.GREEN)
            return True
        
        self.print_colored("Starting backend...", Colors.YELLOW)
        
        # Start backend process
        process = subprocess.Popen(
            [sys.executable, "launcher_api.py", "./runtime"],
            stdout=subprocess.PIPE,
            stderr=subprocess.PIPE,
            cwd=self.root_dir
        )
        self.backend_pid = process.pid
        
        # Wait for backend to be ready
        return self.wait_for_service("http://localhost:8002/api/health", "Backend API")
    
    def stop_backend(self):
        """Stop backend server"""
        if self.backend_pid:
            self.print_colored("Stopping backend...", Colors.YELLOW)
            try:
                os.kill(self.backend_pid, signal.SIGTERM)
            except Exception as e:
                print(f"Error stopping backend: {e}")
    
    def run_pytest(self, test_path: str, markers: Optional[List[str]] = None, 
                   extra_args: Optional[List[str]] = None) -> int:
        """Run pytest with specified parameters"""
        cmd = [sys.executable, "-m", "pytest", test_path, "-v"]
        
        if markers:
            cmd.extend(["-m", " and ".join(markers)])
        
        if extra_args:
            cmd.extend(extra_args)
        
        result = subprocess.run(cmd, cwd=self.root_dir)
        return result.returncode
    
    def run_smoke_tests(self, target: str = "all") -> int:
        """Run smoke tests"""
        self.print_colored("\n=== Running Smoke Tests ===", Colors.BLUE)
        
        results = []
        
        if target in ["backend", "all"]:
            self.print_colored("\n=== Backend Smoke Tests ===", Colors.BLUE)
            
            # Start backend if needed
            if not self.start_backend():
                return 1
            
            # Set environment variables
            os.environ["API_BASE_URL"] = "http://localhost:8002"
            
            # Run backend smoke tests
            result = self.run_pytest(
                "tests/smoke/test_backend_api.py",
                markers=["not requires_llm"],
                extra_args=["--tb=short"]
            )
            results.append(("Backend", result))
            
            self.stop_backend()
        
        if target in ["frontend", "all"]:
            self.print_colored("\n=== Frontend Smoke Tests ===", Colors.BLUE)
            self.print_colored("Note: Frontend tests require manual service startup", Colors.YELLOW)
            # Frontend tests would go here
        
        # Print summary
        self.print_colored("\n=== Test Summary ===", Colors.BLUE)
        all_passed = True
        for name, result in results:
            if result == 0:
                self.print_colored(f"✓ {name} tests passed", Colors.GREEN)
            else:
                self.print_colored(f"✗ {name} tests failed", Colors.RED)
                all_passed = False
        
        return 0 if all_passed else 1
    
    def run_unit_tests(self) -> int:
        """Run unit tests"""
        self.print_colored("\n=== Running Unit Tests ===", Colors.BLUE)
        
        result = self.run_pytest(
            "tests/unit/",
            extra_args=["--cov=src", "--cov-report=term", "--cov-report=html"]
        )
        
        if result == 0:
            self.print_colored("\n✓ Unit tests passed", Colors.GREEN)
        else:
            self.print_colored("\n✗ Unit tests failed", Colors.RED)
        
        return result
    
    def run_integration_tests(self) -> int:
        """Run integration tests"""
        self.print_colored("\n=== Running Integration Tests ===", Colors.BLUE)
        
        result = self.run_pytest("tests/integration/", extra_args=["--tb=long"])
        
        if result == 0:
            self.print_colored("\n✓ Integration tests passed", Colors.GREEN)
        else:
            self.print_colored("\n✗ Integration tests failed", Colors.RED)
        
        return result
    
    def run_all_tests(self) -> int:
        """Run all tests"""
        results = []
        
        # Run unit tests
        results.append(("Unit", self.run_unit_tests()))
        
        # Run smoke tests
        results.append(("Smoke", self.run_smoke_tests()))
        
        # Run integration tests
        results.append(("Integration", self.run_integration_tests()))
        
        # Print summary
        self.print_colored("\n=== Final Test Summary ===", Colors.BLUE)
        all_passed = True
        for name, result in results:
            if result == 0:
                self.print_colored(f"✓ {name} tests passed", Colors.GREEN)
            else:
                self.print_colored(f"✗ {name} tests failed", Colors.RED)
                all_passed = False
        
        return 0 if all_passed else 1


def main():
    parser = argparse.ArgumentParser(
        description="Test runner for Trusted Services",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python run_tests.py smoke              # Run smoke tests only
  python run_tests.py unit               # Run unit tests only
  python run_tests.py integration        # Run integration tests only
  python run_tests.py all                # Run all tests
  python run_tests.py smoke --backend    # Run backend smoke tests only
        """
    )
    
    parser.add_argument(
        "test_type",
        choices=["smoke", "unit", "integration", "all"],
        help="Type of tests to run"
    )
    
    parser.add_argument(
        "--backend",
        action="store_true",
        help="Run backend tests only (for smoke tests)"
    )
    
    parser.add_argument(
        "--frontend",
        action="store_true",
        help="Run frontend tests only (for smoke tests)"
    )
    
    args = parser.parse_args()
    
    runner = TestRunner()
    
    try:
        if args.test_type == "smoke":
            if args.backend:
                result = runner.run_smoke_tests("backend")
            elif args.frontend:
                result = runner.run_smoke_tests("frontend")
            else:
                result = runner.run_smoke_tests("all")
        elif args.test_type == "unit":
            result = runner.run_unit_tests()
        elif args.test_type == "integration":
            result = runner.run_integration_tests()
        elif args.test_type == "all":
            result = runner.run_all_tests()
        else:
            parser.print_help()
            result = 1
        
        sys.exit(result)
    
    except KeyboardInterrupt:
        runner.print_colored("\n\nTests interrupted by user", Colors.YELLOW)
        runner.stop_backend()
        sys.exit(130)
    except Exception as e:
        runner.print_colored(f"\nError: {e}", Colors.RED)
        runner.stop_backend()
        sys.exit(1)


if __name__ == "__main__":
    main()

