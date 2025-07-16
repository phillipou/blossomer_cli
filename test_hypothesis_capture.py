#!/usr/bin/env python3
"""
Quick test script to demonstrate the hypothesis capture feature
"""

import sys
import os

# Add the current directory to the path
sys.path.insert(0, os.getcwd())

from cli.commands.init_sync import capture_hypotheses

def test_hypothesis_capture():
    """Test the hypothesis capture function"""
    print("Testing hypothesis capture function...")
    print("=" * 50)
    
    # Test the capture function
    result = capture_hypotheses()
    
    print("=" * 50)
    print(f"Result: {result}")
    print(f"Type: {type(result)}")
    
    if result:
        print("Context captured successfully!")
        if "account_hypothesis" in result:
            print(f"Account hypothesis: {result['account_hypothesis']}")
        if "persona_hypothesis" in result:
            print(f"Persona hypothesis: {result['persona_hypothesis']}")
    else:
        print("No context provided - proceeding with defaults")

if __name__ == "__main__":
    test_hypothesis_capture()