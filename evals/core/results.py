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
    
    def display_results(self, results: Dict[str, Any]) -> None:
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
        summary_table.add_column("Metric", style="cyan")
        summary_table.add_column("Value", style="magenta")
        summary_table.add_column("Rate", style="green")
        
        summary_table.add_row("Total Cases", str(test_cases['total']), "100%")
        summary_table.add_row("Passed", str(test_cases['passed']), f"{test_cases['pass_rate']:.1%}")
        summary_table.add_row("Failed", str(test_cases['failed']), f"{(test_cases['total'] - test_cases['passed']) / test_cases['total']:.1%}")
        
        self.console.print(summary_table)
        
        # Detailed results for each check type
        self._display_deterministic_results(results.get('deterministic_checks', {}))
        self._display_llm_judge_results(results.get('llm_judges', {}))
        
        # Show failed cases if any
        if test_cases['failed'] > 0:
            self._display_failed_cases(results.get('detailed_results', []))
    
    def _display_deterministic_results(self, det_results: Dict[str, Any]) -> None:
        """Display deterministic check results."""
        if not det_results:
            return
        
        self.console.print(f"\n🔍 Deterministic Checks")
        
        det_table = Table()
        det_table.add_column("Check Type", style="cyan")
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
        llm_table.add_column("Judge Type", style="cyan")
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
    
    
    def _display_failed_cases(self, detailed_results: List[Dict[str, Any]]) -> None:
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
                        error = check_result.get('error', 'Unknown error')
                        self.console.print(f"  🔍 {check_name}: {error}", style="red")
            
            # Show LLM judge failures with more detail
            llm_results = case.get('llm_results', {})
            if llm_results and not llm_results.get('overall_pass', False):
                for judge_name, judge_result in llm_results.get('judges', {}).items():
                    if not judge_result.get('pass', False):
                        # Check if it's an error or a legitimate failure
                        if 'error' in judge_result:
                            error = judge_result.get('error', 'Unknown error')
                            error_summary = error.split('\n')[0]
                            self.console.print(f"  🧠 {judge_name}: {error_summary}", style="red")
                        else:
                            # It's a legitimate quality failure, show the reason
                            reason = judge_result.get('reason', 'Quality criteria not met')
                            self.console.print(f"  🧠 {judge_name}: {reason}", style="yellow")
                            
                            # Show specific details if available
                            if 'details' in judge_result:
                                details = judge_result['details']
                                if isinstance(details, list) and len(details) > 0:
                                    first_detail = details[0]
                                    if 'reason' in first_detail:
                                        self.console.print(f"    → {first_detail['reason']}", style="dim yellow")
            
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
        comparison_table.add_column("Metric", style="cyan")
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