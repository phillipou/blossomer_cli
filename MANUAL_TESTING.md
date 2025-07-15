# Manual Testing Guide for Stage 2

This guide shows how to manually test each Stage 2 component from the command line.

## Prerequisites

```bash
# Make sure you're in the project directory
cd /Users/phillipou/dev/active/blossomer-cli

# Set up environment (if not already done)
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

## 1. Test Domain Normalization

```bash
# Test the domain utility directly
python -c "
from cli.utils.domain import normalize_domain
test_cases = ['acme.com', 'https://acme.com', 'www.acme.com', 'http://www.acme.com/about']
for domain in test_cases:
    print(f'{domain} → {normalize_domain(domain)}')
"
```

## 2. Test Project Storage System

```bash
# Test project storage initialization
python -c "
from cli.services.project_storage import project_storage
print(f'Base directory: {project_storage.base_dir}')
print(f'State file: {project_storage.state_file}')
print(f'Directory exists: {project_storage.base_dir.exists()}')
"
```

```bash
# Test project creation
python -c "
from cli.services.project_storage import project_storage
from cli.utils.domain import normalize_domain

domain = 'manual-test.com'
normalized = normalize_domain(domain)
project_dir = project_storage.create_project(normalized)
print(f'Created project: {project_dir}')
print(f'Project exists: {project_storage.project_exists(normalized)}')
"
```

```bash
# Test step data storage
python -c "
from cli.services.project_storage import project_storage
from cli.utils.domain import normalize_domain

domain = 'manual-test.com'
normalized = normalize_domain(domain)

# Save test data
test_data = {'company_name': 'Manual Test Co', 'test': True}
step_file = project_storage.save_step_data(normalized, 'overview', test_data)
print(f'Saved to: {step_file}')

# Load test data
loaded = project_storage.load_step_data(normalized, 'overview')
print(f'Loaded: {loaded[\"company_name\"]}')

# List available steps
steps = project_storage.get_available_steps(normalized)
print(f'Available steps: {steps}')
"
```

## 3. Test Project Listing

```bash
# List all projects
python -c "
from cli.services.project_storage import project_storage

projects = project_storage.list_projects()
print(f'Found {len(projects)} projects:')
for project in projects:
    print(f'  - {project[\"domain\"]}: {project[\"step_count\"]} steps')
"
```

## 4. Test GTM Service

```bash
# Test GTM service status
python -c "
from cli.services.gtm_generation_service import gtm_service

# Test non-existent project
status = gtm_service.get_project_status('non-existent.com')
print(f'Non-existent project: {status}')

# Test existing project (if you created manual-test.com above)
status = gtm_service.get_project_status('manual-test.com')
print(f'Existing project status: {status}')
"
```

## 5. Test LLM Service Imports

```bash
# Test that all CLI services can be imported
python -c "
try:
    from cli.services.llm_service import LLMClient, OpenAIProvider
    print('✓ Core LLM classes imported')
    
    from cli.services.llm_singleton import get_llm_client
    print('✓ LLM singleton imported')
    
    from cli.services.context_orchestrator_service import ContextOrchestratorService
    print('✓ Context orchestrator imported')
    
    from cli.services.product_overview_service import generate_product_overview_service
    from cli.services.target_account_service import generate_target_account_profile
    from cli.services.target_persona_service import generate_target_persona_profile
    from cli.services.email_generation_service import generate_email_campaign_service
    print('✓ All generation services imported')
    
    print('All imports successful!')
except ImportError as e:
    print(f'Import error: {e}')
"
```

## 6. Test Dependency Tracking

```bash
# Test dependency chain
python -c "
from cli.services.project_storage import project_storage

dependencies = project_storage.get_dependency_chain('test')
print('Dependency chain:')
for step, deps in dependencies.items():
    print(f'  {step}: {deps}')

print()
print('Steps dependent on overview:', project_storage.get_dependent_steps('overview'))
print('Steps dependent on account:', project_storage.get_dependent_steps('account'))
"
```

## 7. Test Step Data with Dependencies

```bash
# Create a project with multiple steps to test dependencies
python -c "
from cli.services.project_storage import project_storage
from cli.utils.domain import normalize_domain

domain = 'dependency-test.com'
normalized = normalize_domain(domain)

# Create project and add steps
project_storage.create_project(normalized)

# Add overview step
overview_data = {'company_name': 'Dependency Test Co', 'step': 'overview'}
project_storage.save_step_data(normalized, 'overview', overview_data)

# Add account step
account_data = {'target_account_name': 'Test Accounts', 'step': 'account'}
project_storage.save_step_data(normalized, 'account', account_data)

# Add persona step
persona_data = {'target_persona_name': 'Test Persona', 'step': 'persona'}
project_storage.save_step_data(normalized, 'persona', persona_data)

print('Created project with steps:', project_storage.get_available_steps(normalized))

# Test marking steps as stale
stale_steps = project_storage.mark_steps_stale(normalized, 'overview')
print(f'Steps marked stale after overview change: {stale_steps}')
"
```

## 8. Inspect Project Files

```bash
# Look at the actual file structure
ls -la gtm_projects/

# Look at a specific project (replace with your test domain)
ls -la gtm_projects/https___manual-test_com/

# View a step file
cat gtm_projects/https___manual-test_com/overview.json | jq .

# View metadata
cat gtm_projects/https___manual-test_com/.metadata.json | jq .
```

## 9. Clean Up Test Projects

```bash
# Delete test projects
python -c "
from cli.services.project_storage import project_storage
from cli.utils.domain import normalize_domain

test_domains = ['manual-test.com', 'dependency-test.com']
for domain in test_domains:
    normalized = normalize_domain(domain)
    if project_storage.project_exists(normalized):
        success = project_storage.delete_project(normalized)
        print(f'Deleted {domain}: {success}')
    else:
        print(f'{domain} does not exist')
"
```

## 10. Test LLM Client (requires API key)

```bash
# Only run this if you have OPENAI_API_KEY set
python -c "
import asyncio
import os
from cli.services.llm_singleton import get_llm_client
from cli.services.llm_service import LLMRequest

async def test_llm():
    if not os.getenv('OPENAI_API_KEY'):
        print('Skipping LLM test - no API key')
        return
    
    try:
        client = get_llm_client()
        print(f'LLM client initialized with {len(client.providers)} providers')
        
        # Test a simple request
        request = LLMRequest(user_prompt='Say hello')
        response = await client.generate(request)
        print(f'LLM response: {response.text[:50]}...')
    except Exception as e:
        print(f'LLM test failed: {e}')

asyncio.run(test_llm())
"
```

## Quick All-in-One Test

```bash
# Run the comprehensive test script
python test_stage2.py
```

## Expected Output Examples

When testing project creation, you should see output like:
```
Created project: gtm_projects/https___manual-test_com
Project exists: True
```

When testing step storage, you should see:
```
Saved to: gtm_projects/https___manual-test_com/overview.json
Loaded: Manual Test Co
Available steps: ['overview']
```

When testing imports, you should see:
```
✓ Core LLM classes imported
✓ LLM singleton imported
✓ Context orchestrator imported
✓ All generation services imported
All imports successful!
```

## Troubleshooting

If you get import errors:
```bash
# Make sure you're in the right directory
pwd
# Should show: /Users/phillipou/dev/active/blossomer-cli

# Check PYTHONPATH
echo $PYTHONPATH

# If needed, set it:
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
```

If you get permission errors:
```bash
# Check directory permissions
ls -la gtm_projects/
```

If LLM tests fail:
```bash
# Check if API key is set
echo $OPENAI_API_KEY
# If not set, LLM functionality won't work but storage/logic tests will still pass
```