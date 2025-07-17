#!/usr/bin/env python3
"""
Sample test cases for performance testing.
Randomly selects N test cases from the full dataset.
"""

import pandas as pd
import os
import sys
from pathlib import Path

def sample_test_cases(input_csv: str, output_csv: str, sample_size: int = 3, random_seed: int = 42):
    """
    Randomly sample test cases from input CSV and write to output CSV.
    
    Args:
        input_csv: Path to full test cases CSV
        output_csv: Path to write sampled test cases
        sample_size: Number of test cases to sample (default: 3)
        random_seed: Random seed for reproducible sampling (default: 42)
    """
    df = pd.read_csv(input_csv)
    
    # Sample without replacement, ensuring we don't exceed available rows
    actual_sample_size = min(sample_size, len(df))
    sampled_df = df.sample(n=actual_sample_size, random_state=random_seed)
    
    # Write sampled data
    sampled_df.to_csv(output_csv, index=False)
    
    print(f"✅ Sampled {actual_sample_size} test cases from {len(df)} total")
    print(f"   Input: {input_csv}")
    print(f"   Output: {output_csv}")
    
    return actual_sample_size

def get_var(var_name, prompt, other_vars):
    """
    Promptfoo variable extractor for dynamic sampling.
    Called by promptfoo to get the EVAL_SAMPLE_SIZE variable.
    """
    if var_name == "EVAL_SAMPLE_SIZE":
        # Get sample size from environment variable, default to 3
        sample_size = int(os.getenv("EVAL_SAMPLE_SIZE", "3"))
        
        # Generate sampled dataset
        input_csv = "data/test_cases.csv"
        output_csv = "data/sampled_test_cases.csv"
        
        actual_size = sample_test_cases(input_csv, output_csv, sample_size)
        
        return {'output': str(actual_size)}
    
    return {'output': ''}

if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Sample test cases for evaluation")
    parser.add_argument("--input", default="data/test_cases.csv", help="Input CSV file")
    parser.add_argument("--output", default="data/sampled_test_cases.csv", help="Output CSV file")
    parser.add_argument("--size", type=int, default=3, help="Sample size (default: 3)")
    parser.add_argument("--seed", type=int, default=42, help="Random seed (default: 42)")
    
    args = parser.parse_args()
    
    sample_test_cases(args.input, args.output, args.size, args.seed)