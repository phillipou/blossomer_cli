#!/usr/bin/env python3
"""
Shared environment setup for evaluation components.
Consolidates dotenv loading and common imports.
"""

import os
from pathlib import Path


def setup_environment():
    """Load environment variables from .env file in project root."""
    try:
        from dotenv import load_dotenv
        
        # Look for .env file in project root (4 levels up from evals/common/)
        project_root = Path(__file__).parent.parent.parent
        env_file = project_root / ".env"
        
        if env_file.exists():
            load_dotenv(env_file)
            print(f"✅ Loaded .env file from {env_file}")
            return True
        else:
            print(f"⚠️  No .env file found at {env_file}")
            return False
            
    except ImportError:
        print("⚠️  python-dotenv not installed. Run: pip install python-dotenv")
        return False


def check_required_env_vars(required_vars: list = None) -> bool:
    """Check if required environment variables are set."""
    if required_vars is None:
        required_vars = ["FORGE_API_KEY"]
    
    missing_vars = []
    for var in required_vars:
        if not os.getenv(var):
            missing_vars.append(var)
    
    if missing_vars:
        print(f"❌ Missing required environment variables: {', '.join(missing_vars)}")
        return False
    
    return True


def get_project_root() -> Path:
    """Get the project root directory."""
    return Path(__file__).parent.parent.parent


def setup_project_path():
    """Add project root to Python path for imports."""
    import sys
    project_root = get_project_root()
    
    if str(project_root) not in sys.path:
        sys.path.insert(0, str(project_root))
        print(f"✅ Added {project_root} to Python path")


def full_setup(required_vars: list = None) -> bool:
    """Complete environment setup for evaluation components."""
    setup_project_path()
    env_loaded = setup_environment()
    env_vars_ok = check_required_env_vars(required_vars)
    
    return env_loaded and env_vars_ok


if __name__ == "__main__":
    # Test the setup
    print("🧪 Testing environment setup...")
    
    success = full_setup()
    
    if success:
        print("✅ Environment setup successful!")
    else:
        print("❌ Environment setup failed!")
        exit(1)