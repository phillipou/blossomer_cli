#!/usr/bin/env python3
"""
Test runner for the Blossomer GTM CLI test suite.
Provides different test execution modes and reporting.
"""

import sys
import argparse
import subprocess
from pathlib import Path


def run_command(cmd, description=""):
    """Run a command and return the result"""
    if description:
        print(f"\n🏃 {description}")
    print(f"Running: {' '.join(cmd)}")
    
    result = subprocess.run(cmd, capture_output=True, text=True)
    
    if result.returncode == 0:
        print("✅ Success")
        if result.stdout:
            print(result.stdout)
    else:
        print("❌ Failed")
        if result.stderr:
            print("STDERR:", result.stderr)
        if result.stdout:
            print("STDOUT:", result.stdout)
    
    return result.returncode


def check_pytest_available():
    """Check if pytest is available"""
    try:
        result = subprocess.run(["pytest", "--version"], capture_output=True, text=True)
        if result.returncode == 0:
            print(f"✅ pytest available: {result.stdout.strip()}")
            return True
        else:
            print("❌ pytest not available")
            return False
    except FileNotFoundError:
        print("❌ pytest not found")
        return False


def run_unit_tests():
    """Run unit tests only"""
    cmd = [
        "pytest", 
        "tests/cli/test_init_command.py",
        "tests/cli/test_show_command.py", 
        "tests/cli/test_other_commands.py",
        "tests/cli/test_services.py",
        "tests/cli/test_utilities.py",
        "-v"
    ]
    return run_command(cmd, "Running unit tests")


def run_integration_tests():
    """Run integration tests"""
    cmd = [
        "pytest",
        "tests/cli/test_integration.py",
        "-v"
    ]
    return run_command(cmd, "Running integration tests")


def run_e2e_tests():
    """Run end-to-end tests"""
    cmd = [
        "pytest",
        "tests/cli/test_e2e.py",
        "-v"
    ]
    return run_command(cmd, "Running end-to-end tests")


def run_error_tests():
    """Run error handling tests"""
    cmd = [
        "pytest",
        "tests/cli/test_error_handling.py",
        "-v"
    ]
    return run_command(cmd, "Running error handling tests")


def run_all_tests():
    """Run all tests"""
    cmd = [
        "pytest",
        "tests/cli/",
        "-v"
    ]
    return run_command(cmd, "Running all CLI tests")


def run_with_coverage():
    """Run tests with coverage report"""
    cmd = [
        "pytest",
        "tests/cli/",
        "--cov=cli",
        "--cov=app", 
        "--cov-report=term-missing",
        "--cov-report=html:htmlcov",
        "-v"
    ]
    return run_command(cmd, "Running tests with coverage")


def run_fast_tests():
    """Run only fast tests (unit tests)"""
    cmd = [
        "pytest",
        "tests/cli/",
        "-m", "not slow",
        "-v"
    ]
    return run_command(cmd, "Running fast tests only")


def run_smoke_tests():
    """Run smoke tests (basic functionality)"""
    cmd = [
        "pytest",
        "tests/cli/test_init_command.py::TestInitCommand::test_init_yolo_mode_new_domain",
        "tests/cli/test_show_command.py::TestShowCommand::test_show_all_assets_single_project",
        "tests/cli/test_services.py::TestGTMGenerationService::test_generate_company_overview_new",
        "-v"
    ]
    return run_command(cmd, "Running smoke tests")


def run_performance_tests():
    """Run performance tests"""
    cmd = [
        "pytest",
        "tests/cli/",
        "-k", "performance",
        "-v"
    ]
    return run_command(cmd, "Running performance tests")


def lint_code():
    """Run code linting"""
    print("\n🔍 Running code quality checks")
    
    # Check if flake8 is available
    try:
        subprocess.run(["flake8", "--version"], capture_output=True, check=True)
        run_command(["flake8", "tests/cli/", "--max-line-length=120"], "Running flake8")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("⚠️  flake8 not available, skipping")
    
    # Check if black is available
    try:
        subprocess.run(["black", "--version"], capture_output=True, check=True)
        run_command(["black", "--check", "tests/cli/"], "Running black (check mode)")
    except (FileNotFoundError, subprocess.CalledProcessError):
        print("⚠️  black not available, skipping")


def generate_test_report():
    """Generate comprehensive test report"""
    cmd = [
        "pytest",
        "tests/cli/",
        "--html=test_report.html",
        "--self-contained-html",
        "-v"
    ]
    return run_command(cmd, "Generating test report")


def main():
    parser = argparse.ArgumentParser(description="Run Blossomer GTM CLI tests")
    parser.add_argument("--mode", choices=[
        "unit", "integration", "e2e", "error", "all", "coverage", 
        "fast", "smoke", "performance", "lint", "report"
    ], default="all", help="Test mode to run")
    
    parser.add_argument("--no-mock-check", action="store_true", 
                       help="Skip check for real API calls (dangerous)")
    
    args = parser.parse_args()
    
    print("🧪 Blossomer GTM CLI Test Runner")
    print("=" * 40)
    
    # Check pytest availability
    if not check_pytest_available():
        print("\n❌ pytest is required to run tests")
        print("Install with: pip install pytest")
        sys.exit(1)
    
    # Warning about API costs
    if not args.no_mock_check:
        print("\n🚨 IMPORTANT: All tests use mocked API calls to avoid costs")
        print("If you see real API calls in test output, STOP and fix the mocks!")
        print("Use --no-mock-check to skip this warning (not recommended)")
        
        response = input("\nContinue with tests? (y/N): ")
        if response.lower() not in ['y', 'yes']:
            print("Tests cancelled by user")
            sys.exit(0)
    
    # Run requested test mode
    if args.mode == "unit":
        exit_code = run_unit_tests()
    elif args.mode == "integration":
        exit_code = run_integration_tests()
    elif args.mode == "e2e":
        exit_code = run_e2e_tests()
    elif args.mode == "error":
        exit_code = run_error_tests()
    elif args.mode == "all":
        exit_code = run_all_tests()
    elif args.mode == "coverage":
        exit_code = run_with_coverage()
    elif args.mode == "fast":
        exit_code = run_fast_tests()
    elif args.mode == "smoke":
        exit_code = run_smoke_tests()
    elif args.mode == "performance":
        exit_code = run_performance_tests()
    elif args.mode == "lint":
        exit_code = lint_code()
    elif args.mode == "report":
        exit_code = generate_test_report()
    else:
        print(f"Unknown mode: {args.mode}")
        exit_code = 1
    
    # Summary
    print("\n" + "=" * 40)
    if exit_code == 0:
        print("🎉 All tests passed!")
    else:
        print("❌ Some tests failed")
    
    print(f"Exit code: {exit_code}")
    sys.exit(exit_code)


if __name__ == "__main__":
    main()