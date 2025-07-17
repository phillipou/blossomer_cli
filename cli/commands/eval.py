"""
CLI command for running evaluations on prompt templates.
"""

import asyncio
import sys
from pathlib import Path
from typing import Optional

import typer
from rich.console import Console

# Add project root to path for imports
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from evals.core.runner import EvaluationRunner
from evals.core.config import EvalConfig

app = typer.Typer(help="Run evaluations on prompt templates")
console = Console()


@app.command("run")
def run_evaluation(
    prompt_name: str = typer.Argument(..., help="Name of the prompt to evaluate (or 'all' for all prompts)"),
    sample_size: int = typer.Option(5, "--sample-size", "-s", help="Number of test cases to sample"),
    output: Optional[str] = typer.Option(None, "--output", "-o", help="Output file path for results"),
    verbose: bool = typer.Option(False, "--verbose", "-v", help="Enable verbose output")
):
    """Run evaluation on a specific prompt or all prompts."""
    
    async def run_async():
        runner = EvaluationRunner(console=console)
        
        if prompt_name == "all":
            # Run all available prompts
            available_prompts = EvalConfig.list_available_prompts()
            
            if not available_prompts:
                console.print("❌ No prompt configurations found", style="red")
                return False
            
            console.print(f"🚀 Running evaluation for {len(available_prompts)} prompts: {', '.join(available_prompts)}")
            
            all_results = {}
            overall_success = True
            
            for prompt in available_prompts:
                console.print(f"\n{'='*60}")
                console.print(f"🔍 Evaluating prompt: {prompt}")
                console.print(f"{'='*60}")
                
                try:
                    results = await runner.run_evaluation(
                        prompt_name=prompt,
                        sample_size=sample_size,
                        output_file=None,
                        verbose=verbose
                    )
                    
                    if "error" in results:
                        overall_success = False
                        all_results[prompt] = {"error": results["error"]}
                    else:
                        all_results[prompt] = results
                        if results["test_cases"]["pass_rate"] < 0.9:
                            overall_success = False
                            
                except Exception as e:
                    console.print(f"❌ Error evaluating {prompt}: {e}", style="red")
                    overall_success = False
                    all_results[prompt] = {"error": str(e)}
            
            # Save combined results if output file specified
            if output:
                combined_results = {
                    "evaluation_type": "all_prompts",
                    "prompt_results": all_results,
                    "overall_success": overall_success,
                    "summary": {
                        "total_prompts": len(available_prompts),
                        "passed_prompts": sum(1 for r in all_results.values() 
                                            if "error" not in r and r.get("test_cases", {}).get("pass_rate", 0) >= 0.9),
                        "failed_prompts": sum(1 for r in all_results.values() 
                                            if "error" in r or r.get("test_cases", {}).get("pass_rate", 0) < 0.9)
                    }
                }
                
                runner.results_manager.save_results(combined_results, output)
            
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
            
            return overall_success
            
        else:
            # Run single prompt evaluation
            try:
                results = await runner.run_evaluation(
                    prompt_name=prompt_name,
                    sample_size=sample_size,
                    output_file=output,
                    verbose=verbose
                )
                
                if "error" in results:
                    return False
                
                # Success criteria check
                overall_pass_rate = results["test_cases"]["pass_rate"]
                if overall_pass_rate >= 0.9:
                    console.print("✅ Evaluation PASSED", style="green")
                    return True
                else:
                    console.print("❌ Evaluation FAILED", style="red")
                    return False
                    
            except Exception as e:
                console.print(f"❌ Evaluation failed: {e}", style="red")
                return False
    
    # Run the async function
    success = asyncio.run(run_async())
    
    if not success:
        raise typer.Exit(1)


@app.command("list")
def list_prompts():
    """List all available prompt configurations."""
    
    available_prompts = EvalConfig.list_available_prompts()
    
    if not available_prompts:
        console.print("❌ No prompt configurations found", style="red")
        console.print("📝 Create a prompt configuration in: evals/prompts/{prompt_name}/config.yaml")
        return
    
    console.print(f"📋 Available prompt configurations ({len(available_prompts)} total):")
    
    for prompt_name in available_prompts:
        config = EvalConfig.load_prompt_config(prompt_name)
        if config:
            console.print(f"  • {prompt_name}: {config.name}")
        else:
            console.print(f"  • {prompt_name}: [red]Error loading config[/red]")


@app.command("validate")
def validate_prompt(prompt_name: str = typer.Argument(..., help="Name of the prompt to validate")):
    """Validate a prompt configuration and dataset."""
    
    console.print(f"🔍 Validating prompt: {prompt_name}")
    
    # Load and validate config
    config = EvalConfig.load_prompt_config(prompt_name)
    if not config:
        console.print(f"❌ Configuration not found for prompt: {prompt_name}", style="red")
        return
    
    config_errors = config.validate()
    if config_errors:
        console.print("❌ Configuration validation failed:", style="red")
        for error in config_errors:
            console.print(f"  • {error}")
        return
    
    console.print("✅ Configuration is valid", style="green")
    
    # Validate dataset
    from evals.core.dataset import DatasetManager
    dataset_manager = DatasetManager()
    
    dataset_errors = dataset_manager.validate_dataset(prompt_name)
    if dataset_errors:
        console.print("❌ Dataset validation failed:", style="red")
        for error in dataset_errors:
            console.print(f"  • {error}")
        return
    
    console.print("✅ Dataset is valid", style="green")
    
    # Show dataset stats
    stats = dataset_manager.get_dataset_stats(prompt_name)
    if stats.get("exists"):
        console.print(f"\n📊 Dataset Statistics:")
        console.print(f"  • Total cases: {stats['total_cases']}")
        console.print(f"  • Context distribution: {stats['context_distribution']}")
        console.print(f"  • Fields: {', '.join(stats['fields'])}")
    
    console.print(f"\n✅ Prompt '{prompt_name}' is ready for evaluation!")


@app.command("create")
def create_prompt_config(
    prompt_name: str = typer.Argument(..., help="Name of the new prompt"),
    service_module: str = typer.Option(..., "--service-module", help="Service module (e.g., app.services.my_service)"),
    service_function: str = typer.Option(..., "--service-function", help="Service function name"),
    create_sample_data: bool = typer.Option(False, "--create-sample-data", help="Create sample dataset")
):
    """Create a new prompt configuration."""
    
    from pathlib import Path
    import yaml
    
    prompt_dir = Path(f"evals/prompts/{prompt_name}")
    
    if prompt_dir.exists():
        console.print(f"❌ Prompt '{prompt_name}' already exists", style="red")
        return
    
    # Create directory structure
    prompt_dir.mkdir(parents=True, exist_ok=True)
    
    # Create config file
    config_data = {
        "name": f"{prompt_name.replace('_', ' ').title()} Evaluation",
        "service": {
            "module": service_module,
            "function": service_function
        },
        "schema": "schema.json",
        "judges": {
            "deterministic": ["D-1", "D-2", "D-3", "D-4", "D-5"],
            "llm": ["traceability", "actionability", "redundancy", "context_steering"]
        },
        "models": {
            "default": "OpenAI/gpt-4.1-nano",
            "fallback": "Gemini/models/gemini-1.5-flash"
        }
    }
    
    config_path = prompt_dir / "config.yaml"
    with open(config_path, 'w') as f:
        yaml.dump(config_data, f, default_flow_style=False, sort_keys=False)
    
    console.print(f"✅ Created configuration: {config_path}")
    
    # Create sample dataset if requested
    if create_sample_data:
        from evals.core.dataset import DatasetManager
        dataset_manager = DatasetManager()
        
        if dataset_manager.create_sample_dataset(prompt_name):
            console.print(f"✅ Created sample dataset: {prompt_dir / 'data.csv'}")
        else:
            console.print("❌ Failed to create sample dataset", style="red")
    
    console.print(f"\n📝 Next steps:")
    console.print(f"  1. Create schema file: {prompt_dir / 'schema.json'}")
    console.print(f"  2. Add test cases: {prompt_dir / 'data.csv'}")
    console.print(f"  3. Validate: python3 -m cli.main eval validate {prompt_name}")
    console.print(f"  4. Run evaluation: python3 -m cli.main eval run {prompt_name}")


if __name__ == "__main__":
    app()