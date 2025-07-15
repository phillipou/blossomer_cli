# Stage 2 Tests

Organized test suite for the Core Generation Engine components.

## Quick Start

```bash
# Run all tests
cd tests && python3 run_all_tests.py

# Run individual test modules
python3 test_domain_utils.py      # Domain normalization
python3 test_project_storage.py   # File storage system  
python3 test_dependencies.py      # Dependency tracking
python3 test_services.py          # Service integration
```

## Test Structure

- **`test_domain_utils.py`** - Domain normalization and validation
- **`test_project_storage.py`** - Project creation, storage, and listing  
- **`test_dependencies.py`** - Step dependencies and stale data detection
- **`test_services.py`** - LLM services and GTM orchestration
- **`run_all_tests.py`** - Main test runner that combines all modules

## What's Tested

✅ Domain normalization (various formats → clean URLs)  
✅ Project file system management  
✅ JSON data storage and retrieval  
✅ Step dependency tracking  
✅ Stale data detection and marking  
✅ GTM service orchestration  
✅ LLM service imports and initialization  

All tests use mock data and clean up after themselves.