#!/usr/bin/env python3
"""
Comprehensive test runner for the Blossomer GTM CLI.
Runs all test suites and provides detailed reporting.
"""

import sys
import subprocess
from pathlib import Path
import time
import re
from rich.console import Console
from rich.panel import Panel
from rich.table import Table
from rich.progress import Progress, SpinnerColumn, TextColumn, BarColumn, TimeElapsedColumn
from rich.syntax import Syntax
from rich.text import Text

# Add CLI modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

console = Console()


def parse_pytest_output(output: str) -> dict:
    """Parse pytest output to extract test results"""
    lines = output.split('\n')
    tests = []
    failures = []
    
    # Extract individual test results
    for line in lines:
        if '::test_' in line and ('PASSED' in line or 'FAILED' in line):
            parts = line.split('::')
            if len(parts) >= 2:
                test_name = parts[1].split()[0]
                status = 'PASSED' if 'PASSED' in line else 'FAILED'
                tests.append({'name': test_name, 'status': status})
    
    # Extract failure details
    failure_section = False
    current_failure = []
    for line in lines:
        if line.startswith('FAILURES') or line.startswith('ERRORS'):
            failure_section = True
            continue
        elif line.startswith('=') and failure_section:
            if current_failure:
                failures.append('\n'.join(current_failure))
                current_failure = []
            failure_section = False
        elif failure_section:
            current_failure.append(line)
    
    if current_failure:
        failures.append('\n'.join(current_failure))
    
    return {'tests': tests, 'failures': failures}


def run_test_suite(test_file: str, description: str) -> dict:
    """Run a specific test suite and return results"""
    
    with Progress(
        SpinnerColumn(),
        TextColumn(f"[bold blue]{description}[/bold blue]"),
        BarColumn(),
        TimeElapsedColumn(),
        console=console,
        transient=True
    ) as progress:
        task = progress.add_task("Running tests...", total=100)
        
        start_time = time.time()
        
        try:
            # Run pytest on the specific test file
            result = subprocess.run([
                sys.executable, "-m", "pytest", 
                test_file, 
                "-v", 
                "--tb=short",
                "--no-header",
                "--no-summary"
            ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
            
            progress.update(task, completed=100)
            duration = time.time() - start_time
            
            # Parse the output
            parsed = parse_pytest_output(result.stdout)
            passed = result.returncode == 0
            
            # Display results
            if passed:
                console.print(f"✅ [green]{description}[/green] ([blue_violet]{duration:.1f}s[/cyan])")
                if parsed['tests']:
                    for test in parsed['tests']:
                        if test['status'] == 'PASSED':
                            console.print(f"   • [green]{test['name']}[/green]")
            else:
                console.print(f"❌ [red]{description}[/red] ([blue_violet]{duration:.1f}s[/cyan])")
                
                # Show failed tests
                for test in parsed['tests']:
                    if test['status'] == 'FAILED':
                        console.print(f"   • [red]{test['name']} FAILED[/red]")
                    else:
                        console.print(f"   • [green]{test['name']}[/green]")
            
            return {
                "name": description,
                "file": test_file,
                "passed": passed,
                "duration": duration,
                "output": result.stdout,
                "error": result.stderr,
                "parsed": parsed
            }
            
        except Exception as e:
            progress.update(task, completed=100)
            duration = time.time() - start_time
            console.print(f"💥 [red]{description} ERROR[/red] ([blue_violet]{duration:.1f}s[/cyan]): {e}")
            return {
                "name": description,
                "file": test_file,
                "passed": False,
                "duration": duration,
                "output": "",
                "error": str(e),
                "parsed": {"tests": [], "failures": [str(e)]}
            }


def run_legacy_tests() -> list:
    """Run the legacy test files (non-pytest format)"""
    console.print("\n[bold yellow]🔧 Legacy Tests (Non-Pytest Format)[/bold yellow]")
    
    legacy_tests = [
        ("tests/test_domain_utils.py", "Domain Utilities"),
        ("tests/test_project_storage.py", "Project Storage"),
        ("tests/test_services.py", "Core Services"),
        ("tests/test_dependencies.py", "Dependencies & Stale Data")
    ]
    
    results = []
    for test_file, description in legacy_tests:
        with Progress(
            SpinnerColumn(),
            TextColumn(f"[bold blue]{description}[/bold blue]"),
            TimeElapsedColumn(),
            console=console,
            transient=True
        ) as progress:
            task = progress.add_task("Running...", total=100)
            start_time = time.time()
            
            try:
                result = subprocess.run([
                    sys.executable, test_file
                ], capture_output=True, text=True, cwd=Path(__file__).parent.parent)
                
                progress.update(task, completed=100)
                duration = time.time() - start_time
                
                if result.returncode == 0 and "🎉" in result.stdout:
                    console.print(f"✅ [green]{description}[/green] ([blue_violet]{duration:.1f}s[/cyan])")
                    passed = True
                else:
                    console.print(f"❌ [red]{description}[/red] ([blue_violet]{duration:.1f}s[/cyan])")
                    passed = False
                    
                results.append({
                    "name": description,
                    "file": test_file,
                    "passed": passed,
                    "duration": duration,
                    "output": result.stdout,
                    "error": result.stderr,
                    "parsed": {"tests": [], "failures": [result.stderr] if result.stderr else []}
                })
                
            except Exception as e:
                progress.update(task, completed=100)
                duration = time.time() - start_time
                console.print(f"💥 [red]{description} ERROR[/red] ([blue_violet]{duration:.1f}s[/cyan]): {e}")
                results.append({
                    "name": description,
                    "file": test_file,
                    "passed": False,
                    "duration": duration,
                    "output": "",
                    "error": str(e),
                    "parsed": {"tests": [], "failures": [str(e)]}
                })
    
    return results


def show_detailed_failures(failed_results: list):
    """Show detailed failure information in a formatted way"""
    if not failed_results:
        return
    
    console.print("\n[bold red]🔍 Detailed Failure Analysis[/bold red]")
    
    for result in failed_results:
        # Create a panel for each failed test suite
        failure_content = []
        
        if result.get('parsed', {}).get('failures'):
            for i, failure in enumerate(result['parsed']['failures'], 1):
                # Clean up the failure text
                failure_lines = failure.strip().split('\n')
                # Take the most relevant parts
                relevant_lines = []
                for line in failure_lines:
                    line = line.strip()
                    if line and not line.startswith('===') and not line.startswith('___'):
                        if any(keyword in line.lower() for keyword in ['error', 'failed', 'assert', 'exception']):
                            relevant_lines.append(line)
                        elif len(relevant_lines) < 3:  # Keep first few lines for context
                            relevant_lines.append(line)
                
                if relevant_lines:
                    failure_content.extend(relevant_lines[:5])  # Limit to 5 lines per failure
        
        if not failure_content and result.get('error'):
            failure_content = [result['error']]
        
        if failure_content:
            panel_content = '\n'.join(failure_content)
            console.print(Panel(
                panel_content,
                title=f"[red]{result['name']}[/red]",
                title_align="left",
                border_style="red"
            ))


def main():
    """Run all test suites and provide summary"""
    # Header with rich formatting
    console.print(Panel.fit(
        "[bold blue]🚀 Blossomer GTM CLI - Test Suite Runner[/bold blue]",
        border_style="blue"
    ))
    
    start_total = time.time()
    all_results = []
    
    # 1. Run legacy tests first
    legacy_results = run_legacy_tests()
    all_results.extend(legacy_results)
    
    # 2. Run new pytest-based test suites
    console.print("\n[bold yellow]🧪 Pytest Test Suites[/bold yellow]")
    test_suites = [
        ("tests/test_gtm_flow_integration.py", "GTM Flow Integration Tests"),
        ("tests/test_cli_commands.py", "CLI Command Tests"),
        ("tests/test_error_handling.py", "Error Handling Tests"),
        ("tests/test_guided_email_builder.py", "Guided Email Builder Tests")
    ]
    
    for test_file, description in test_suites:
        test_path = Path(__file__).parent.parent / test_file
        if test_path.exists():
            result = run_test_suite(str(test_path), description)
            all_results.append(result)
        else:
            console.print(f"⚠️ [yellow]Test file not found: {test_file}[/yellow]")
            all_results.append({
                "name": description,
                "file": test_file,
                "passed": False,
                "duration": 0,
                "output": "",
                "error": "File not found",
                "parsed": {"tests": [], "failures": ["File not found"]}
            })
    
    # Generate summary
    total_duration = time.time() - start_total
    passed_tests = [r for r in all_results if r["passed"]]
    failed_tests = [r for r in all_results if not r["passed"]]
    
    # Create summary table
    table = Table(title="📊 Test Summary", title_style="bold blue")
    table.add_column("Metric", style="blue_violet", width=20)
    table.add_column("Value", style="green")
    
    table.add_row("Total Duration", f"{total_duration:.1f}s")
    table.add_row("Test Suites", str(len(all_results)))
    table.add_row("✅ Passed", str(len(passed_tests)))
    table.add_row("❌ Failed", str(len(failed_tests)))
    table.add_row("Success Rate", f"{len(passed_tests)/len(all_results)*100:.1f}%")
    
    console.print("\n")
    console.print(table)
    
    # Show passed tests in a compact way
    if passed_tests:
        console.print(f"\n[green]✅ {len(passed_tests)} Test Suites Passed[/green]")
        for result in passed_tests:
            console.print(f"   • [green]{result['name']}[/green] [dim]({result['duration']:.1f}s)[/dim]")
    
    # Show failed tests
    if failed_tests:
        console.print(f"\n[red]❌ {len(failed_tests)} Test Suite(s) Failed[/red]")
        for result in failed_tests:
            console.print(f"   • [red]{result['name']}[/red] [dim]({result['duration']:.1f}s)[/dim]")
        
        # Show detailed failures
        show_detailed_failures(failed_tests)
    
    # Final result
    if failed_tests:
        console.print(f"\n[bold red]💥 {len(failed_tests)} test suite(s) failed![/bold red]")
        return 1
    else:
        console.print(f"\n[bold green]🎉 All test suites passed![/bold green]")
        return 0


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Blossomer GTM CLI Test Runner")
    parser.add_argument("--verbose", "-v", action="store_true", help="Show detailed test output")
    parser.add_argument("--failures-only", "-f", action="store_true", help="Only show failures")
    args = parser.parse_args()
    
    # Set global verbose flag for individual test output
    if args.verbose:
        console.print("[dim]Running in verbose mode - showing all test details[/dim]")
    
    exit_code = main()
    sys.exit(exit_code)