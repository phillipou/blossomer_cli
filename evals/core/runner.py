#!/usr/bin/env python3
"""
Main evaluation orchestrator with unified CLI interface.

Usage:
    python -m evals.core.runner product_overview
    python -m evals.core.runner product_overview --sample-size 3
    python -m evals.core.runner all --sample-size 5
"""

import argparse
import asyncio
import sys
from pathlib import Path
from typing import Dict, List, Optional, Any
import time
import json
from datetime import datetime

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from rich.console import Console
from rich.progress import Progress, TaskID, TimeElapsedColumn, TextColumn

from evals.core.config import EvalConfig
from evals.core.dataset import DatasetManager
from evals.core.results import ResultsManager
from evals.core.judges.deterministic import DeterministicJudge
from evals.core.judges.llm_judge import LLMJudge


class EvaluationRunner:
    """Main evaluation orchestrator that coordinates all evaluation components."""
    
    def __init__(self, console: Console = None):
        self.console = console or Console()
        self.results_manager = ResultsManager(console=self.console)
        self.dataset_manager = DatasetManager()
        
    async def run_evaluation(
        self,
        prompt_name: str,
        sample_size: int = 5,
        output_file: Optional[str] = None,
        verbose: bool = False,
        context_type: Optional[str] = None
    ) -> Dict[str, Any]:
        """
        Run complete evaluation for a specific prompt.
        
        Args:
            prompt_name: Name of the prompt to evaluate (e.g., 'product_overview')
            sample_size: Number of test cases to sample
            output_file: Optional output file path
            verbose: Enable verbose output
            
        Returns:
            Dict containing evaluation results
        """
        start_time = time.time()
        
        # Load configuration
        config = EvalConfig.load_prompt_config(prompt_name)
        if not config:
            self.console.print(f"❌ Configuration not found for prompt: {prompt_name}", style="red")
            return {"error": f"Configuration not found for prompt: {prompt_name}"}
        
        self.console.print(f"🚀 Starting evaluation for: {config.name}")
        self.console.print(f"📊 Sample size: {sample_size}")
        if context_type:
            self.console.print(f"🔍 Context type filter: {context_type}")
        
        # Load and sample test cases
        test_cases = self.dataset_manager.load_test_cases(prompt_name, sample_size, config.dataset_path, context_type)
        if not test_cases:
            self.console.print(f"❌ No test cases found for prompt: {prompt_name}", style="red")
            return {"error": f"No test cases found for prompt: {prompt_name}"}
        
        self.console.print(f"📋 Loaded {len(test_cases)} test cases")
        
        # Initialize judges
        deterministic_judge = DeterministicJudge(config)
        llm_judge = LLMJudge(config, console=self.console)
        
        # Run evaluations with progress tracking
        results = []
        
        with Progress(
            TextColumn("[bold blue]{task.description}[/bold blue]"),
            "[progress.percentage]{task.percentage:>3.0f}%",
            TimeElapsedColumn(),
            console=self.console
        ) as progress:
            task = progress.add_task(f"Evaluating {prompt_name}...", total=len(test_cases))
            
            for i, test_case in enumerate(test_cases):
                case_result = await self._evaluate_single_case(
                    test_case, config, deterministic_judge, llm_judge, verbose
                )
                case_result["test_case_id"] = i + 1
                results.append(case_result)
                progress.update(task, advance=1)
        
        # Aggregate results
        evaluation_results = self._aggregate_results(results, config, start_time)
        
        # Always save results to timestamped JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path(__file__).parent.parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        auto_output_file = results_dir / f"{prompt_name}_{timestamp}.json"
        self._save_results_json(evaluation_results, auto_output_file)
        
        # Save to user-specified file if provided
        if output_file:
            self.results_manager.save_results(evaluation_results, output_file)
        
        self.results_manager.display_results(evaluation_results, verbose)
        
        # Show saved file location
        self.console.print(f"📁 Results saved to: {auto_output_file}", style="dim")
        
        return evaluation_results
    
    async def _evaluate_single_case(
        self,
        test_case: Dict[str, Any],
        config: EvalConfig,
        deterministic_judge: DeterministicJudge,
        llm_judge: LLMJudge,
        verbose: bool = False
    ) -> Dict[str, Any]:
        """Evaluate a single test case."""
        
        case_result = {
            "test_case": test_case,
            "deterministic_results": {},
            "llm_results": {},
            "overall_pass": False,
            "errors": []
        }
        
        try:
            # Generate output using the same service as the CLI
            output = await self._generate_output(test_case, config, verbose)
            if not output:
                case_result["errors"].append("Failed to generate output")
                return case_result
            
            case_result["generated_output"] = output
            
            # Run deterministic checks first (fail-fast)
            det_results = deterministic_judge.evaluate_all(output, test_case)
            case_result["deterministic_results"] = det_results
            
            if not det_results.get("overall_pass", False):
                if verbose:
                    self.console.print(f"❌ Deterministic checks failed: {det_results.get('reason', 'Unknown')}")
                return case_result
            
            # Run LLM judges if deterministic checks pass
            llm_results = await llm_judge.evaluate_all(output, test_case)
            case_result["llm_results"] = llm_results
            
            # Overall pass requires both deterministic and LLM judges to pass
            case_result["overall_pass"] = (
                det_results.get("overall_pass", False) and 
                llm_results.get("overall_pass", False)
            )
            
        except Exception as e:
            case_result["errors"].append(str(e))
            if verbose:
                self.console.print(f"❌ Error evaluating test case: {e}", style="red")
        
        return case_result
    
    async def _generate_output(self, test_case: Dict[str, Any], config: EvalConfig, verbose: bool = False) -> Optional[str]:
        """Generate output using the same service as the CLI."""
        try:
            # Suppress website content warnings for persona and account evals (only matters for product_overview)
            import logging
            if config.service_module in ["app.services.target_persona_service", "app.services.target_account_service"]:
                logging.getLogger("app.services.context_orchestrator_service").setLevel(logging.ERROR)
            # Import the service dynamically based on config
            service_module = __import__(config.service_module, fromlist=[''])
            service_function = getattr(service_module, config.service_function)
            
            # Import required dependencies based on service
            if config.service_module == "app.services.product_overview_service":
                from app.services.context_orchestrator_agent import ContextOrchestrator
                from app.schemas import ProductOverviewRequest
                request_class = ProductOverviewRequest
                needs_orchestrator = True
            elif config.service_module == "app.services.target_account_service":
                from app.schemas import TargetAccountRequest
                request_class = TargetAccountRequest
                needs_orchestrator = False
            elif config.service_module == "app.services.target_persona_service":
                from app.schemas import TargetPersonaRequest
                request_class = TargetPersonaRequest
                needs_orchestrator = False
            else:
                # Default fallback - assume it's like product_overview
                from app.services.context_orchestrator_agent import ContextOrchestrator
                from app.schemas import ProductOverviewRequest
                request_class = ProductOverviewRequest
                needs_orchestrator = True
            
            # Create request object - map CSV fields to ProductOverviewRequest schema
            # Build context from available hypothesis data
            context_parts = []
            if test_case.get('account_profile_name'):
                context_parts.append(f"Target Account: {test_case.get('account_profile_name')}")
            if test_case.get('persona_profile_name'):
                context_parts.append(f"Target Persona: {test_case.get('persona_profile_name')}")
            if test_case.get('persona_hypothesis'):
                context_parts.append(f"Persona Details: {test_case.get('persona_hypothesis')}")
            if test_case.get('account_hypothesis'):
                context_parts.append(f"Account Details: {test_case.get('account_hypothesis')}")
            
            # Combine user context with hypothesis context
            user_context = test_case.get('user_inputted_context', '')
            if context_parts:
                company_context = '. '.join(context_parts)
                if user_context:
                    combined_context = f"{user_context}. {company_context}"
                else:
                    combined_context = company_context
            else:
                combined_context = user_context
            
            # Create request object based on service type
            if request_class.__name__ == "ProductOverviewRequest":
                request = request_class(
                    website_url=test_case.get('input_website_url', ''),
                    user_inputted_context=combined_context,
                    company_context=None  # Could be used for additional context if needed
                )
            elif request_class.__name__ == "TargetAccountRequest":
                request = request_class(
                    website_url=test_case.get('input_website_url', ''),
                    account_profile_name=test_case.get('account_profile_name', ''),
                    hypothesis=test_case.get('account_hypothesis', ''),
                    additional_context=combined_context
                )
            elif request_class.__name__ == "TargetPersonaRequest":
                request = request_class(
                    website_url=test_case.get('input_website_url', ''),
                    persona_profile_name=test_case.get('persona_profile_name', ''),
                    hypothesis=test_case.get('persona_hypothesis', ''),
                    additional_context=combined_context
                )
            else:
                # Fallback to ProductOverviewRequest format
                request = request_class(
                    website_url=test_case.get('input_website_url', ''),
                    user_inputted_context=combined_context,
                    company_context=None
                )
            
            # Call the service function based on signature
            if needs_orchestrator:
                # Create orchestrator for services that need it
                orchestrator = ContextOrchestrator()
                result = await service_function(request, orchestrator)
            else:
                # Call directly for services that don't need orchestrator
                result = await service_function(request)
            
            # Debug: Let's see what we're getting back
            if verbose:
                self.console.print(f"🔍 Service returned type: {type(result)}")
                self.console.print(f"🔍 Service result: {str(result)[:200]}...")
            
            # Handle different response types
            if hasattr(result, 'text'):
                output = result.text
            elif hasattr(result, 'model_dump_json'):
                output = result.model_dump_json()
            elif hasattr(result, 'model_dump'):
                import json
                output = json.dumps(result.model_dump(), ensure_ascii=False, indent=2)
            elif hasattr(result, 'dict'):
                import json
                output = json.dumps(result.dict(), ensure_ascii=False, indent=2)
            else:
                output = str(result)
            
            return output
            
        except Exception as e:
            self.console.print(f"❌ Error generating output: {e}", style="red")
            return None
    
    def _save_results_json(self, results: Dict[str, Any], output_file: Path):
        """Save results to JSON file with proper formatting."""
        try:
            with open(output_file, 'w', encoding='utf-8') as f:
                json.dump(results, f, indent=2, ensure_ascii=False, default=str)
        except Exception as e:
            self.console.print(f"❌ Error saving results to {output_file}: {e}", style="red")
    
    def _aggregate_results(
        self, 
        results: List[Dict[str, Any]], 
        config: EvalConfig,
        start_time: float
    ) -> Dict[str, Any]:
        """Aggregate individual test case results."""
        
        total_cases = len(results)
        passed_cases = sum(1 for r in results if r["overall_pass"])
        failed_cases = total_cases - passed_cases
        
        # Calculate deterministic pass rate
        det_passed = sum(1 for r in results if r["deterministic_results"].get("overall_pass", False))
        det_pass_rate = det_passed / total_cases if total_cases > 0 else 0
        
        # Calculate LLM judge pass rate (only for cases that passed deterministic)
        llm_eligible = sum(1 for r in results if r["deterministic_results"].get("overall_pass", False))
        llm_passed = sum(1 for r in results if r["llm_results"].get("overall_pass", False))
        llm_pass_rate = llm_passed / llm_eligible if llm_eligible > 0 else 0
        
        
        return {
            "prompt_name": config.name,
            "timestamp": datetime.now().isoformat(),
            "evaluation_time": time.time() - start_time,
            "test_cases": {
                "total": total_cases,
                "passed": passed_cases,
                "failed": failed_cases,
                "pass_rate": passed_cases / total_cases if total_cases > 0 else 0
            },
            "deterministic_checks": {
                "pass_rate": det_pass_rate,
                "passed": det_passed,
                "total": total_cases
            },
            "llm_judges": {
                "pass_rate": llm_pass_rate,
                "passed": llm_passed,
                "eligible": llm_eligible
            },
            "detailed_results": results
        }


async def main():
    """Main CLI entry point."""
    parser = argparse.ArgumentParser(
        description="Run evaluation on prompt templates",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python -m evals.core.runner product_overview
  python -m evals.core.runner product_overview --sample-size 3
  python -m evals.core.runner all --sample-size 5
        """
    )
    
    parser.add_argument(
        "prompt_name",
        help="Name of the prompt to evaluate (or 'all' for all prompts)"
    )
    
    parser.add_argument(
        "--sample-size", "-s",
        type=int,
        default=5,
        help="Number of test cases to sample (default: 5)"
    )
    
    parser.add_argument(
        "--output", "-o",
        help="Output file path for results"
    )
    
    parser.add_argument(
        "--verbose", "-v",
        action="store_true",
        help="Enable verbose output"
    )
    
    parser.add_argument(
        "--context-type", "-c",
        choices=["none", "valid", "noise"],
        help="Filter test cases by context type (none, valid, noise)"
    )
    
    args = parser.parse_args()
    
    console = Console()
    runner = EvaluationRunner(console=console)
    
    if args.prompt_name == "all":
        # Run all available prompts
        from evals.core.config import EvalConfig
        available_prompts = EvalConfig.list_available_prompts()
        
        if not available_prompts:
            console.print("❌ No prompt configurations found", style="red")
            return 1
        
        console.print(f"🚀 Running evaluation for {len(available_prompts)} prompts: {', '.join(available_prompts)}")
        
        all_results = {}
        overall_success = True
        
        for prompt_name in available_prompts:
            console.print(f"\n{'='*60}")
            console.print(f"🔍 Evaluating prompt: {prompt_name}")
            console.print(f"{'='*60}")
            
            try:
                results = await runner.run_evaluation(
                    prompt_name=prompt_name,
                    sample_size=args.sample_size,
                    output_file=None,  # Don't save individual files
                    verbose=args.verbose
                )
                
                if "error" in results:
                    overall_success = False
                    all_results[prompt_name] = {"error": results["error"]}
                else:
                    all_results[prompt_name] = results
                    if results["test_cases"]["pass_rate"] < 0.9:
                        overall_success = False
                        
            except Exception as e:
                console.print(f"❌ Error evaluating {prompt_name}: {e}", style="red")
                overall_success = False
                all_results[prompt_name] = {"error": str(e)}
        
        # Always save combined results to timestamped JSON file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        results_dir = Path(__file__).parent.parent / "results"
        results_dir.mkdir(exist_ok=True)
        
        combined_results = {
            "evaluation_type": "all_prompts",
            "prompt_results": all_results,
            "overall_success": overall_success,
            "timestamp": timestamp,
            "summary": {
                "total_prompts": len(available_prompts),
                "passed_prompts": sum(1 for r in all_results.values() 
                                    if "error" not in r and r.get("test_cases", {}).get("pass_rate", 0) >= 0.9),
                "failed_prompts": sum(1 for r in all_results.values() 
                                    if "error" in r or r.get("test_cases", {}).get("pass_rate", 0) < 0.9)
            }
        }
        
        auto_output_file = results_dir / f"all_prompts_{timestamp}.json"
        runner._save_results_json(combined_results, auto_output_file)
        
        # Save to user-specified file if provided
        if args.output:
            runner.results_manager.save_results(combined_results, args.output)
        
        console.print(f"📁 Combined results saved to: {auto_output_file}", style="dim")
        
        # Print overall summary
        console.print(f"\n{'='*60}")
        console.print("🎯 Overall Summary")
        console.print(f"{'='*60}")
        
        passed_count = sum(1 for r in all_results.values() 
                          if "error" not in r and r.get("test_cases", {}).get("pass_rate", 0) >= 0.9)
        failed_count = len(available_prompts) - passed_count
        
        status_color = "green" if overall_success else "red"
        status_icon = "✅" if overall_success else "❌"
        
        console.print(f"{status_icon} Overall Result: {'PASS' if overall_success else 'FAIL'}", style=status_color)
        console.print(f"📊 Prompts Passed: {passed_count}/{len(available_prompts)}")
        console.print(f"📊 Prompts Failed: {failed_count}/{len(available_prompts)}")
        
        return 0 if overall_success else 1
    
    try:
        results = await runner.run_evaluation(
            prompt_name=args.prompt_name,
            sample_size=args.sample_size,
            output_file=args.output,
            verbose=args.verbose,
            context_type=args.context_type
        )
        
        if "error" in results:
            return 1
        
        # Success criteria check
        overall_pass_rate = results["test_cases"]["pass_rate"]
        if overall_pass_rate >= 0.9:  # 90% pass rate
            console.print("✅ Evaluation PASSED", style="green")
            return 0
        else:
            console.print("❌ Evaluation FAILED", style="red")
            return 1
            
    except Exception as e:
        console.print(f"❌ Evaluation failed: {e}", style="red")
        return 1


if __name__ == "__main__":
    sys.exit(asyncio.run(main()))