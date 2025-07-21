"""
Results management for evaluation system.
"""

import json
from pathlib import Path
from typing import Dict, List, Any, Optional
from datetime import datetime

from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.progress import Progress
from rich.text import Text


class ResultsManager:
    """Manages evaluation results display and storage."""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
    
    def display_results(self, results: Dict[str, Any], verbose: bool = False) -> None:
        """Display evaluation results in a formatted way."""
        
        self.console.print(f"\n🎯 Evaluation Results: {results['prompt_name']}")
        self.console.print(f"⏱️  Evaluation time: {results['evaluation_time']:.2f}s")
        
        # Overall summary
        test_cases = results['test_cases']
        overall_pass = test_cases['pass_rate'] >= 0.9
        
        status_color = "green" if overall_pass else "red"
        status_icon = "✅" if overall_pass else "❌"
        
        self.console.print(f"\n{status_icon} Overall Result: {'PASS' if overall_pass else 'FAIL'}", style=status_color)
        
        # Test cases summary table
        summary_table = Table(title="Test Cases Summary")
        summary_table.add_column("Metric", style="#01A0E4")
        summary_table.add_column("Value", style="magenta")
        summary_table.add_column("Rate", style="green")
        
        summary_table.add_row("Total Cases", str(test_cases['total']), "100%")
        summary_table.add_row("Passed", str(test_cases['passed']), f"{test_cases['pass_rate']:.1%}")
        summary_table.add_row("Failed", str(test_cases['failed']), f"{(test_cases['total'] - test_cases['passed']) / test_cases['total']:.1%}")
        
        self.console.print(summary_table)
        
        # Display individual check results
        self._display_individual_checks(results.get('detailed_results', []))
        
        # Display rating summary for LLM checks
        self._display_rating_summary(results.get('detailed_results', []))
        
        # Display final summary table
        self._display_check_summary(results.get('detailed_results', []))
    
    def _display_deterministic_results(self, det_results: Dict[str, Any]) -> None:
        """Display deterministic check results."""
        if not det_results:
            return
        
        self.console.print(f"\n🔍 Deterministic Checks")
        
        det_table = Table()
        det_table.add_column("Check Type", style="#01A0E4")
        det_table.add_column("Passed", style="green")
        det_table.add_column("Total", style="blue")
        det_table.add_column("Pass Rate", style="magenta")
        
        det_table.add_row(
            "All Checks",
            str(det_results.get('passed', 0)),
            str(det_results.get('total', 0)),
            f"{det_results.get('pass_rate', 0):.1%}"
        )
        
        self.console.print(det_table)
    
    def _display_llm_judge_results(self, llm_results: Dict[str, Any]) -> None:
        """Display LLM judge results."""
        if not llm_results:
            return
        
        self.console.print(f"\n🧠 LLM Judge Results")
        
        llm_table = Table()
        llm_table.add_column("Judge Type", style="#01A0E4")
        llm_table.add_column("Passed", style="green")
        llm_table.add_column("Eligible", style="blue")
        llm_table.add_column("Pass Rate", style="magenta")
        
        llm_table.add_row(
            "All Judges",
            str(llm_results.get('passed', 0)),
            str(llm_results.get('eligible', 0)),
            f"{llm_results.get('pass_rate', 0):.1%}"
        )
        
        self.console.print(llm_table)
    
    def _display_individual_checks(self, detailed_results: List[Dict[str, Any]]) -> None:
        """Display individual check results with proper formatting."""
        if not detailed_results:
            return
            
        self.console.print(f"\n📋 Individual Check Results")
        
        for i, case in enumerate(detailed_results):
            test_case = case.get('test_case', {})
            url = test_case.get('input_website_url', 'Unknown')
            
            self.console.print(f"\n🌐 Test Case {i+1}: {url}")
            
            # Display deterministic checks
            det_results = case.get('deterministic_results', {})
            if det_results and 'checks' in det_results:
                self.console.print(f"\n  🔍 Deterministic Checks:")
                for check_name, check_result in det_results['checks'].items():
                    self._display_single_check(check_result, "  ")
            
            # Display LLM judge checks
            llm_results = case.get('llm_results', {})
            if llm_results and 'judges' in llm_results:
                self.console.print(f"\n  🧠 LLM Judge Checks:")
                for judge_name, judge_result in llm_results['judges'].items():
                    # Check if this is a nested structure (like email_quality with multiple sub-checks)
                    if isinstance(judge_result, dict) and any(
                        isinstance(v, dict) and 'check_name' in v 
                        for v in judge_result.values()
                    ):
                        # Handle nested checks (like email_quality)
                        for sub_check_name, sub_check_result in judge_result.items():
                            if isinstance(sub_check_result, dict) and 'check_name' in sub_check_result:
                                self._display_single_check(sub_check_result, "  ")
                    else:
                        # Handle single check (like existing judges)
                        self._display_single_check(judge_result, "  ")
    
    def _display_single_check(self, check_result: Dict[str, Any], indent: str = "") -> None:
        """Display a single check result with proper formatting."""
        check_name = check_result.get('check_name', 'unknown')
        description = check_result.get('description', 'No description')
        passed = check_result.get('pass', False)
        rating = check_result.get('rating')
        rationale = check_result.get('rationale', check_result.get('error', 'No rationale provided'))
        
        # Status icon
        status_icon = "✅" if passed else "❌"
        status_color = "green" if passed else "red"
        
        # Display check name and status
        self.console.print(f"{indent}    {status_icon} {check_name}", style=status_color)
        
        # Display description
        self.console.print(f"{indent}       {description}", style="dim")
        
        # Always show inputs evaluated first (important for understanding what's being evaluated)
        inputs_evaluated = check_result.get('inputs_evaluated', [])
        if inputs_evaluated:
            self.console.print(f"{indent}       📋 Inputs evaluated:", style="dim")
            for input_item in inputs_evaluated:
                field = input_item.get('field', 'unknown')
                value = input_item.get('value', 'unknown')
                # Make values more readable - truncate very long values but show meaningful content
                value_str = str(value)
                if len(value_str) > 150:
                    value_str = value_str[:150] + '...'
                self.console.print(f"{indent}         • {field}: {value_str}", style="dim")
        
        # Display rating if available (for LLM judges)
        if rating:
            rating_color = {
                "impressive": "green",
                "sufficient": "yellow", 
                "poor": "red"
            }.get(rating, "white")
            self.console.print(f"{indent}       ⭐ Rating: {rating.upper()}", style=rating_color)
        
        # Display rationale
        self.console.print(f"{indent}       → {rationale}", style="yellow" if not passed else "dim")
        
        # Add spacing between checks
        self.console.print()
    
    def _display_check_summary(self, detailed_results: List[Dict[str, Any]]) -> None:
        """Display final summary table with breakdown by check type."""
        if not detailed_results:
            return
            
        # Count check results by type
        det_total = det_passed = llm_total = llm_passed = 0
        
        for case in detailed_results:
            # Count deterministic checks
            det_results = case.get('deterministic_results', {})
            if det_results and 'checks' in det_results:
                for check_name, check_result in det_results['checks'].items():
                    det_total += 1
                    if check_result.get('pass', False):
                        det_passed += 1
            
            # Count LLM judge checks
            llm_results = case.get('llm_results', {})
            if llm_results and 'judges' in llm_results:
                for judge_name, judge_result in llm_results['judges'].items():
                    # Check if this is a nested structure (like email_quality with multiple sub-checks)
                    if isinstance(judge_result, dict) and any(
                        isinstance(v, dict) and 'check_name' in v 
                        for v in judge_result.values()
                    ):
                        # Handle nested checks (like email_quality)
                        for sub_check_name, sub_check_result in judge_result.items():
                            if isinstance(sub_check_result, dict) and 'check_name' in sub_check_result:
                                llm_total += 1
                                if sub_check_result.get('pass', False):
                                    llm_passed += 1
                    else:
                        # Handle single check (like existing judges)
                        llm_total += 1
                        if judge_result.get('pass', False):
                            llm_passed += 1
        
        # Create summary table
        self.console.print(f"\n📊 Check Summary")
        
        summary_table = Table()
        summary_table.add_column("Check Type", style="#01A0E4")
        summary_table.add_column("Passed", style="green")
        summary_table.add_column("Total", style="blue")
        summary_table.add_column("Pass Rate", style="magenta")
        
        # Add deterministic checks row
        if det_total > 0:
            det_rate = det_passed / det_total
            summary_table.add_row(
                "Deterministic",
                str(det_passed),
                str(det_total),
                f"{det_rate:.1%}"
            )
        
        # Add LLM judge checks row
        if llm_total > 0:
            llm_rate = llm_passed / llm_total
            summary_table.add_row(
                "LLM Judges",
                str(llm_passed),
                str(llm_total),
                f"{llm_rate:.1%}"
            )
        
        # Add total row
        total_checks = det_total + llm_total
        total_passed = det_passed + llm_passed
        if total_checks > 0:
            total_rate = total_passed / total_checks
            summary_table.add_row(
                "**Total**",
                f"**{total_passed}**",
                f"**{total_checks}**",
                f"**{total_rate:.1%}**"
            )
        
        self.console.print(summary_table)
    
    def _display_rating_summary(self, detailed_results: List[Dict[str, Any]]) -> None:
        """Display rating distribution for LLM judge checks."""
        if not detailed_results:
            return
        
        # Count ratings from LLM checks
        rating_counts = {"impressive": 0, "sufficient": 0, "poor": 0}
        total_llm_checks = 0
        
        for case in detailed_results:
            llm_results = case.get('llm_results', {})
            if llm_results and 'judges' in llm_results:
                for judge_name, judge_result in llm_results['judges'].items():
                    # Check if this is a nested structure (like email_quality with multiple sub-checks)
                    if isinstance(judge_result, dict) and any(
                        isinstance(v, dict) and 'check_name' in v 
                        for v in judge_result.values()
                    ):
                        # Handle nested checks (like email_quality)
                        for sub_check_name, sub_check_result in judge_result.items():
                            if isinstance(sub_check_result, dict) and 'check_name' in sub_check_result:
                                rating = sub_check_result.get('rating')
                                if rating and rating in rating_counts:
                                    rating_counts[rating] += 1
                                    total_llm_checks += 1
                    else:
                        # Handle single check (like existing judges)
                        rating = judge_result.get('rating')
                        if rating and rating in rating_counts:
                            rating_counts[rating] += 1
                            total_llm_checks += 1
        
        # Only display if we have LLM checks with ratings
        if total_llm_checks == 0:
            return
        
        self.console.print(f"\n⭐ LLM Judge Rating Distribution")
        
        rating_table = Table()
        rating_table.add_column("Rating", style="#01A0E4")
        rating_table.add_column("Count", style="blue")
        rating_table.add_column("Percentage", style="magenta")
        
        for rating in ["impressive", "sufficient", "poor"]:
            count = rating_counts[rating]
            percentage = (count / total_llm_checks) * 100 if total_llm_checks > 0 else 0
            
            # Color code the rating
            rating_color = {
                "impressive": "green",
                "sufficient": "yellow",
                "poor": "red"
            }.get(rating, "white")
            
            rating_display = Text(rating.upper(), style=rating_color)
            rating_table.add_row(rating_display, str(count), f"{percentage:.1f}%")
        
        # Add total row
        rating_table.add_row("**TOTAL**", f"**{total_llm_checks}**", "**100.0%**")
        
        self.console.print(rating_table)
    
    def _display_failed_cases(self, detailed_results: List[Dict[str, Any]], verbose: bool = False) -> None:
        """Display details of failed test cases."""
        failed_cases = [r for r in detailed_results if not r.get('overall_pass', False)]
        
        if not failed_cases:
            return
        
        self.console.print(f"\n❌ Failed Cases ({len(failed_cases)} total)")
        
        for i, case in enumerate(failed_cases[:3]):  # Show first 3 failed cases with more detail
            test_case = case.get('test_case', {})
            url = test_case.get('input_website_url', 'Unknown')
            context_type = test_case.get('context_type', 'Unknown')
            context = test_case.get('user_inputted_context', '')
            
            self.console.print(f"\n📋 Case {case.get('test_case_id', i+1)}: {url} ({context_type})")
            
            # Show input context if available
            if context:
                self.console.print(f"  📝 Context: {context[:100]}{'...' if len(context) > 100 else ''}")
            
            # Show generated output preview
            generated_output = case.get('generated_output', '')
            if generated_output:
                # Try to parse as JSON for better display
                try:
                    import json
                    parsed = json.loads(generated_output)
                    company_name = parsed.get('company_name', 'Unknown')
                    description = parsed.get('description', '')
                    self.console.print(f"  🏢 Generated: {company_name}")
                    if description:
                        self.console.print(f"  📄 Description: {description[:150]}{'...' if len(description) > 150 else ''}")
                except:
                    # If not JSON, show first part
                    self.console.print(f"  🔤 Output: {generated_output[:100]}{'...' if len(generated_output) > 100 else ''}")
            
            # Show deterministic failures
            det_results = case.get('deterministic_results', {})
            if not det_results.get('overall_pass', False):
                for check_name, check_result in det_results.get('checks', {}).items():
                    if not check_result.get('pass', False):
                        # Use the new standardized structure
                        check_display_name = check_result.get('check_name', check_name)
                        rationale = check_result.get('rationale', check_result.get('error', 'Unknown error'))
                        description = check_result.get('description', 'Deterministic check')
                        
                        self.console.print(f"  🔍 {check_display_name}: {description}", style="#01A0E4")
                        self.console.print(f"    → {rationale}", style="red")
                        
                        # Show inputs evaluated if verbose
                        if verbose:
                            inputs_evaluated = check_result.get('inputs_evaluated', [])
                            for input_item in inputs_evaluated:
                                field = input_item.get('field', 'unknown')
                                value = input_item.get('value', 'unknown')
                                value_str = str(value)[:100] + '...' if len(str(value)) > 100 else str(value)
                                self.console.print(f"      📋 {field}: {value_str}", style="dim")
            
            # Show LLM judge failures with more detail
            llm_results = case.get('llm_results', {})
            if llm_results and not llm_results.get('overall_pass', False):
                for judge_name, judge_result in llm_results.get('judges', {}).items():
                    if not judge_result.get('pass', False):
                        # Use the new standardized structure
                        check_display_name = judge_result.get('check_name', judge_name)
                        rationale = judge_result.get('rationale', judge_result.get('error', 'Quality criteria not met'))
                        description = judge_result.get('description', 'LLM judge evaluation')
                        
                        self.console.print(f"  🧠 {check_display_name}: {description}", style="#01A0E4")
                        self.console.print(f"    → {rationale}", style="yellow")
                        
                        # Show inputs evaluated if verbose
                        if verbose:
                            inputs_evaluated = judge_result.get('inputs_evaluated', [])
                            for input_item in inputs_evaluated:
                                field = input_item.get('field', 'unknown')
                                value = input_item.get('value', 'unknown')
                                value_str = str(value)[:100] + '...' if len(str(value)) > 100 else str(value)
                                self.console.print(f"      📋 {field}: {value_str}", style="dim")
            
            # Show any general errors
            errors = case.get('errors', [])
            for error in errors:
                self.console.print(f"  ⚠️  {error}", style="yellow")
        
        if len(failed_cases) > 3:
            self.console.print(f"\n... and {len(failed_cases) - 3} more failed cases")
    
    def save_results(self, results: Dict[str, Any], output_path: str) -> bool:
        """Save evaluation results to a file."""
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)
            
            # Add timestamp
            results['saved_at'] = datetime.now().isoformat()
            
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False)
            
            self.console.print(f"📁 Results saved to: {output_file}")
            return True
            
        except Exception as e:
            self.console.print(f"❌ Error saving results: {e}", style="red")
            return False
    
    def load_results(self, input_path: str) -> Optional[Dict[str, Any]]:
        """Load evaluation results from a file."""
        try:
            input_file = Path(input_path)
            if not input_file.exists():
                self.console.print(f"❌ Results file not found: {input_file}", style="red")
                return None
            
            with open(input_file, 'r', encoding='utf-8') as f:
                results = json.load(f)
            
            return results
            
        except Exception as e:
            self.console.print(f"❌ Error loading results: {e}", style="red")
            return None
    
    def compare_results(self, results1: Dict[str, Any], results2: Dict[str, Any]) -> None:
        """Compare two evaluation results."""
        self.console.print(f"\n🔄 Comparing Results")
        
        comparison_table = Table()
        comparison_table.add_column("Metric", style="#01A0E4")
        comparison_table.add_column("Result 1", style="green")
        comparison_table.add_column("Result 2", style="blue")
        comparison_table.add_column("Change", style="magenta")
        
        # Compare pass rates
        pass_rate1 = results1['test_cases']['pass_rate']
        pass_rate2 = results2['test_cases']['pass_rate']
        change = pass_rate2 - pass_rate1
        
        comparison_table.add_row(
            "Pass Rate",
            f"{pass_rate1:.1%}",
            f"{pass_rate2:.1%}",
            f"{change:+.1%}"
        )
        
        # Compare costs
        cost1 = results1.get('cost_analysis', {}).get('total_cost', 0)
        cost2 = results2.get('cost_analysis', {}).get('total_cost', 0)
        cost_change = cost2 - cost1
        
        comparison_table.add_row(
            "Total Cost",
            f"${cost1:.6f}",
            f"${cost2:.6f}",
            f"${cost_change:+.6f}"
        )
        
        self.console.print(comparison_table)
    
    def generate_summary_report(self, results: Dict[str, Any]) -> str:
        """Generate a text summary report."""
        test_cases = results['test_cases']
        
        report = f"""
Evaluation Summary Report
========================

Prompt: {results['prompt_name']}
Evaluation Time: {results['evaluation_time']:.2f}s
Generated: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}

Test Cases:
- Total: {test_cases['total']}
- Passed: {test_cases['passed']}
- Failed: {test_cases['failed']}
- Pass Rate: {test_cases['pass_rate']:.1%}

Cost Analysis:
- Total Cost: ${results.get('cost_analysis', {}).get('total_cost', 0):.6f}
- Cost per Case: ${results.get('cost_analysis', {}).get('cost_per_case', 0):.6f}

Overall Result: {'PASS' if test_cases['pass_rate'] >= 0.9 else 'FAIL'}
"""
        return report.strip()