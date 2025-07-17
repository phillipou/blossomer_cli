#!/usr/bin/env python3
"""
Dynamic test generation for promptfoo evaluation.
Randomly samples N test cases from the full dataset.
"""

import pandas as pd
import os
import json
from pathlib import Path

def create_tests():
    """
    Generate test cases by sampling from the full CSV dataset.
    
    Environment variables:
    - EVAL_SAMPLE_SIZE: Number of test cases to sample (default: 3)
    - EVAL_RANDOM_SEED: Random seed for reproducible sampling (default: 42)
    
    Returns:
        List of test case dictionaries for promptfoo
    """
    # Get configuration from environment
    sample_size = int(os.getenv("EVAL_SAMPLE_SIZE", "3"))
    random_seed = int(os.getenv("EVAL_RANDOM_SEED", "42"))
    
    # Load the full test dataset
    csv_path = Path(__file__).parent / "data" / "test_cases.csv"
    df = pd.read_csv(csv_path)
    
    # Sample test cases
    if sample_size >= len(df):
        # Use all test cases if sample size exceeds available data
        sampled_df = df
        actual_size = len(df)
    else:
        # Random sampling with fixed seed for reproducibility
        sampled_df = df.sample(n=sample_size, random_state=random_seed)
        actual_size = sample_size
    
    print(f"🎲 Dynamically generating {actual_size} test cases from {len(df)} total")
    print(f"   Sample size: {sample_size} (from EVAL_SAMPLE_SIZE)")
    print(f"   Random seed: {random_seed} (from EVAL_RANDOM_SEED)")
    
    # Convert to promptfoo test format
    test_cases = []
    for _, row in sampled_df.iterrows():
        # Handle NaN values by converting to empty strings
        def safe_get(value):
            return "" if pd.isna(value) else str(value)
        
        test_case = {
            "vars": {
                "input_website_url": row["input_website_url"],
                "context_type": row["context_type"],
                "account_profile_name": safe_get(row.get("account_profile_name")),
                "persona_profile_name": safe_get(row.get("persona_profile_name")),
                "persona_hypothesis": safe_get(row.get("persona_hypothesis")),
                "account_hypothesis": safe_get(row.get("account_hypothesis")),
                "expected_company_name": row["expected_company_name"]
            }
        }
        test_cases.append(test_case)
    
    # Print sample for verification
    if test_cases:
        print(f"   Sample test case: {test_cases[0]['vars']['input_website_url']} ({test_cases[0]['vars']['context_type']})")
    
    return test_cases

# For standalone testing
if __name__ == "__main__":
    import os
    
    # Test with different sample sizes
    for size in [3, 5, 19]:
        print(f"\n--- Testing with EVAL_SAMPLE_SIZE={size} ---")
        os.environ["EVAL_SAMPLE_SIZE"] = str(size)
        tests = create_tests()
        print(f"Generated {len(tests)} test cases")
        
        # Show first test case structure
        if tests:
            print("First test case structure:")
            print(json.dumps(tests[0], indent=2))