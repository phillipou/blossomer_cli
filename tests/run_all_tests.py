#!/usr/bin/env python3
"""
Main test runner for all Stage 2 components.

This replaces the monolithic test_stage2.py with organized test modules.
"""

import sys
from pathlib import Path

# Add CLI modules to path
sys.path.insert(0, str(Path(__file__).parent.parent))

from test_domain_utils import test_domain_normalization
from test_project_storage import (
    test_project_storage_initialization,
    test_project_creation_and_deletion, 
    test_step_data_storage,
    test_project_listing
)
from test_dependencies import (
    test_dependency_tracking,
    test_stale_data_detection
)
from test_services import (
    test_gtm_service_initialization,
    test_llm_service_imports
)


def main():
    """Run all Stage 2 tests"""
    print("🚀 Testing Stage 2: Core Generation Engine")
    print("=" * 60)
    
    try:
        # Domain utilities
        test_domain_normalization()
        
        # Project storage
        test_project_storage_initialization()
        test_project_creation_and_deletion()
        test_step_data_storage()
        test_project_listing()
        
        # Dependencies
        test_dependency_tracking()
        test_stale_data_detection()
        
        # Services
        test_gtm_service_initialization()
        test_llm_service_imports()
        
        print("🎉 All Stage 2 tests passed!")
        print()
        print("📋 Stage 2 Implementation Summary:")
        print("=" * 40)
        print("✅ CLI-adapted LLM services (removed web dependencies)")
        print("✅ Company overview generation service")
        print("✅ Target account generation service")
        print("✅ Target persona generation service")
        print("✅ Email campaign generation service")
        print("✅ JSON file storage and retrieval system")
        print("✅ Data dependency tracking between steps")
        print("✅ Complete GTM generation orchestration")
        print()
        print("⏳ Pending for later stages:")
        print("• GTM plan generation service (needs schema/template)")
        print("• CLI summary field generation in prompt templates")
        print()
        print("🎯 Ready for Stage 3: Interactive CLI Commands")
        
    except Exception as e:
        print(f"❌ Test failed: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()