#!/usr/bin/env python3
"""
End-to-end evaluation runner for product overview template.
Runs Promptfoo evaluation and provides summary reporting.
"""

import subprocess
import json
import argparse
import os
from pathlib import Path

def run_evaluation(config_path: str = "promptfooconfig.yaml", verbose: bool = False):
    """Run complete evaluation suite"""
    
    print("🚀 Starting Product Overview Evaluation...")
    
    # Ensure we're in the correct directory
    eval_dir = Path(__file__).parent
    original_dir = os.getcwd()
    os.chdir(eval_dir)
    
    try:
        # Run Promptfoo evaluation
        cmd = ["promptfoo", "eval", "-c", config_path]
        if verbose:
            cmd.append("-v")
        
        print(f"📝 Running: {' '.join(cmd)}")
        
        result = subprocess.run(cmd, capture_output=True, text=True)
        
        if result.returncode != 0:
            print(f"❌ Evaluation failed:")
            print(f"STDOUT: {result.stdout}")
            print(f"STDERR: {result.stderr}")
            return False
        
        print("✅ Evaluation completed successfully!")
        
        # Parse and summarize results if available
        results_path = Path("results/evaluation_results.json")
        if results_path.exists():
            try:
                with open(results_path) as f:
                    results = json.load(f)
                print_summary(results)
            except Exception as e:
                print(f"⚠️  Could not parse results: {e}")
        else:
            print("📊 Results file not found - check Promptfoo output above")
        
        return True
        
    finally:
        # Restore original directory
        os.chdir(original_dir)

def print_summary(results: dict):
    """Print evaluation summary"""
    
    # Extract key metrics from Promptfoo results format
    test_results = results.get("results", [])
    
    if not test_results:
        print("📊 No test results found in output")
        return
    
    total_tests = len(test_results)
    passed_tests = 0
    failed_tests = 0
    
    # Count pass/fail based on assertion results
    for test_result in test_results:
        assertions = test_result.get("gradingResult", {}).get("componentResults", [])
        test_passed = all(assertion.get("pass", False) for assertion in assertions)
        
        if test_passed:
            passed_tests += 1
        else:
            failed_tests += 1
    
    pass_rate = (passed_tests / total_tests * 100) if total_tests > 0 else 0
    
    print(f"\n📊 Evaluation Summary:")
    print(f"Total Tests: {total_tests}")
    print(f"Passed: {passed_tests}")
    print(f"Failed: {failed_tests}")
    print(f"Pass Rate: {pass_rate:.1f}%")
    
    # Show failing tests
    if failed_tests > 0:
        print(f"\n❌ Failed Tests:")
        for i, test_result in enumerate(test_results):
            assertions = test_result.get("gradingResult", {}).get("componentResults", [])
            test_passed = all(assertion.get("pass", False) for assertion in assertions)
            
            if not test_passed:
                test_vars = test_result.get("vars", {})
                url = test_vars.get("input_website_url", "Unknown")
                context = test_vars.get("context_type", "Unknown")
                print(f"  - Test {i+1}: {url} ({context} context)")
                
                for assertion in assertions:
                    if not assertion.get("pass", False):
                        assertion_type = assertion.get("assertion", {}).get("type", "Unknown")
                        error = assertion.get("reason", "No reason provided")
                        print(f"    {assertion_type}: {error}")

def main():
    parser = argparse.ArgumentParser(description="Run Product Overview Template Evaluation")
    parser.add_argument("--config", default="promptfooconfig.yaml", help="Promptfoo config file")
    parser.add_argument("--verbose", "-v", action="store_true", help="Verbose output")
    
    args = parser.parse_args()
    
    success = run_evaluation(args.config, args.verbose)
    
    if success:
        print("\n🎉 Evaluation completed successfully!")
    else:
        print("\n💥 Evaluation failed!")
        exit(1)

if __name__ == "__main__":
    main()