#!/usr/bin/env python3
"""
Adaptive evaluation runner with configurable sampling.
"""

import os
import sys
import subprocess
import argparse
from pathlib import Path

# Add utils to path
sys.path.insert(0, str(Path(__file__).parent / "utils"))
from sample_test_cases import sample_test_cases

def run_evaluation(sample_size: int = 3, config: str = "promptfooconfig.yaml"):
    """
    Run evaluation with specified sample size.
    
    Args:
        sample_size: Number of test cases to sample (3=quick, 19=full, 0=smoke test only)
        config: Promptfoo config file to use
    """
    print(f"🚀 Starting evaluation with sample size: {sample_size}")
    
    if sample_size == 0:
        # Use smoke test configuration (3 hand-picked cases)
        config = "promptfooconfig_smoke.yaml"
        print("   Using smoke test configuration (3 hand-picked cases)")
    elif sample_size < 19:
        # Sample from full dataset
        input_csv = "data/test_cases.csv"
        output_csv = "data/sampled_test_cases.csv"
        
        actual_size = sample_test_cases(input_csv, output_csv, sample_size)
        print(f"   Sampled {actual_size} cases from full dataset")
        
        # Create temporary config for sampled data
        config_content = f"""description: "Product Overview Template Evaluation - Sampled ({actual_size} cases)"

prompts:
  - file://product_overview.j2

providers:
  - id: 'file://providers/product_overview_provider.py'

tests:
  - file://data/sampled_test_cases.csv

defaultTest:
  assert:
    - type: python
      value: file://checks/deterministic_checks.py:run_all_checks
    - type: python
      value: file://checks/llm_judges.py:evaluate_with_llm_judges

outputPath: ./results/sampled_results.json"""
        
        with open("promptfooconfig_sampled.yaml", "w") as f:
            f.write(config_content)
        
        config = "promptfooconfig_sampled.yaml"
    else:
        # Use full dataset
        print("   Using full dataset (19 cases)")
    
    # Run promptfoo evaluation
    print(f"   Config: {config}")
    result = subprocess.run([
        "promptfoo", "eval", "-c", config, "--max-concurrency", "2"
    ], capture_output=True, text=True)
    
    if result.returncode != 0:
        print(f"❌ Evaluation failed: {result.stderr}")
        return False
    
    print("✅ Evaluation completed successfully")
    print(result.stdout)
    return True

def main():
    parser = argparse.ArgumentParser(description="Run adaptive evaluation")
    parser.add_argument("--sample-size", "-s", type=int, default=3, 
                       help="Sample size: 0=smoke test, 3=quick (default), 19=full")
    parser.add_argument("--config", "-c", default="promptfooconfig.yaml",
                       help="Promptfoo config file")
    
    args = parser.parse_args()
    
    run_evaluation(args.sample_size, args.config)

if __name__ == "__main__":
    main()