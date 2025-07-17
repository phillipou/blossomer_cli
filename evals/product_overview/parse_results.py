#!/usr/bin/env python3
"""
Parse promptfoo evaluation results and display in readable format.
"""

import json
import sys
from pathlib import Path
from typing import Dict, Any

def parse_evaluation_results(results_file: str = "results/evaluation_results.json"):
    """Parse and display evaluation results in readable format."""
    
    results_path = Path(__file__).parent / results_file
    
    if not results_path.exists():
        print(f"❌ Results file not found: {results_path}")
        return
    
    with open(results_path, 'r') as f:
        data = json.load(f)
    
    results = data.get("results", {}).get("results", [])
    
    if not results:
        print("❌ No test results found")
        return
    
    print("=" * 80)
    print("📊 EVALUATION RESULTS SUMMARY")
    print("=" * 80)
    
    for i, result in enumerate(results, 1):
        print(f"\n🧪 TEST CASE {i}")
        print("-" * 40)
        
        # Test case details
        test_vars = result.get("vars", {})
        url = test_vars.get("input_website_url", "Unknown")
        context_type = test_vars.get("context_type", "none")
        
        print(f"🌐 URL: {url}")
        print(f"📝 Context Type: {context_type}")
        
        # Overall result
        overall_pass = result.get("success", False)
        overall_score = result.get("score", 0)
        status_emoji = "✅" if overall_pass else "❌"
        
        print(f"{status_emoji} Overall: {'PASS' if overall_pass else 'FAIL'} (Score: {overall_score:.2f})")
        
        # Component results
        grading_result = result.get("gradingResult", {})
        component_results = grading_result.get("componentResults", [])
        
        for component in component_results:
            print_component_result(component)
    
    # Summary stats
    stats = data.get("results", {}).get("stats", {})
    total_tests = stats.get("successes", 0) + stats.get("failures", 0)
    
    print("\n" + "=" * 80)
    print("📈 SUMMARY STATISTICS")
    print("=" * 80)
    print(f"✅ Successes: {stats.get('successes', 0)}")
    print(f"❌ Failures: {stats.get('failures', 0)}")
    print(f"🔢 Total Tests: {total_tests}")
    if total_tests > 0:
        success_rate = (stats.get('successes', 0) / total_tests) * 100
        print(f"📊 Success Rate: {success_rate:.1f}%")


def print_component_result(component: Dict[str, Any]):
    """Print individual component (deterministic checks or LLM judges) results."""
    
    assertion_value = component.get("assertion", {}).get("value", "")
    
    if "deterministic_checks" in assertion_value:
        print_deterministic_results(component)
    elif "llm_judges" in assertion_value:
        print_llm_judge_results(component)


def print_deterministic_results(component: Dict[str, Any]):
    """Print deterministic check results."""
    
    print(f"\n🔍 DETERMINISTIC CHECKS")
    
    overall_pass = component.get("pass", False)
    score = component.get("score", 0)
    status_emoji = "✅" if overall_pass else "❌"
    
    print(f"  {status_emoji} Overall: {'PASS' if overall_pass else 'FAIL'} (Score: {score:.2f})")
    
    checks = component.get("checks", {})
    for check_name, check_result in checks.items():
        if isinstance(check_result, dict) and "pass" in check_result:
            check_pass = check_result["pass"]
            check_emoji = "✅" if check_pass else "❌"
            print(f"    {check_emoji} {check_name}: {'PASS' if check_pass else 'FAIL'}")
            
            if not check_pass and "error" in check_result:
                print(f"      💬 {check_result['error']}")


def print_llm_judge_results(component: Dict[str, Any]):
    """Print LLM judge results with detailed feedback."""
    
    print(f"\n🤖 LLM JUDGES")
    
    overall_pass = component.get("pass", False)
    score = component.get("score", 0)
    status_emoji = "✅" if overall_pass else "❌"
    
    print(f"  {status_emoji} Overall: {'PASS' if overall_pass else 'FAIL'} (Score: {score:.2f})")
    
    # Cost and performance info
    cost = component.get("total_cost_estimate", 0)
    calls = component.get("judge_calls_made", 0)
    model = component.get("model_used", "Unknown")
    
    print(f"  💰 Cost: ${cost:.6f} | 📞 Calls: {calls} | 🤖 Model: {model}")
    
    judges = component.get("judges", {})
    for judge_name, judge_result in judges.items():
        print_individual_judge(judge_name, judge_result)


def print_individual_judge(judge_name: str, judge_result: Dict[str, Any]):
    """Print individual judge results with failure reasons."""
    
    judge_pass = judge_result.get("pass", False)
    judge_emoji = "✅" if judge_pass else "❌"
    
    print(f"    {judge_emoji} {judge_name}: {'PASS' if judge_pass else 'FAIL'}")
    
    # Show error if present
    if "error" in judge_result:
        print(f"      ⚠️  Error: {judge_result['error']}")
        return
    
    # Show detailed results
    details = judge_result.get("details", [])
    
    if judge_name == "L-1_traceability" and not judge_pass:
        print_traceability_details(details)
    elif judge_name == "L-2_actionability" and not judge_pass:
        print_actionability_details(details)
    elif judge_name == "L-3_redundancy":
        print_redundancy_details(details)
    elif judge_name == "L-4_context_steering":
        print_context_details(details)


def print_traceability_details(details):
    """Print L-1 traceability failure details."""
    print(f"      📋 Claims not supported by website evidence:")
    for detail in details:
        claim = detail.get("claim", "Unknown claim")
        reason = detail.get("reason", "No reason provided")
        # Truncate long claims
        claim_short = claim[:60] + "..." if len(claim) > 60 else claim
        print(f"        • {claim_short}")
        print(f"          → {reason}")


def print_actionability_details(details):
    """Print L-2 actionability failure details."""
    print(f"      📋 Actionability criteria:")
    for detail in details:
        criterion = detail.get("criterion", "unknown")
        criterion_pass = detail.get("pass", False)
        reason = detail.get("reason", "No reason provided")
        emoji = "✅" if criterion_pass else "❌"
        print(f"        {emoji} {criterion.title()}: {reason}")


def print_redundancy_details(details):
    """Print L-3 redundancy details."""
    for detail in details:
        score = detail.get("similarity_score", 0)
        reason = detail.get("reason", "No reason provided")
        print(f"      📊 Similarity Score: {score:.2f} (threshold: 0.30)")
        print(f"      💬 {reason}")


def print_context_details(details):
    """Print L-4 context steering details."""
    for detail in details:
        context_type = detail.get("context_type", "unknown")
        reason = detail.get("reason", "No reason provided")
        print(f"      📝 Context Type: {context_type}")
        print(f"      💬 {reason}")


if __name__ == "__main__":
    results_file = sys.argv[1] if len(sys.argv) > 1 else "results/evaluation_results.json"
    parse_evaluation_results(results_file)