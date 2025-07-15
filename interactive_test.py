#!/usr/bin/env python3
"""
Interactive Test Scenarios for Stage 2

This script provides interactive scenarios to test the complete data flow
and see how the CLI components work together in realistic usage patterns.
"""

import asyncio
import json
import sys
from pathlib import Path
from datetime import datetime

# Add CLI modules to path
sys.path.insert(0, str(Path(__file__).parent))

from cli.services.gtm_generation_service import gtm_service
from cli.services.project_storage import project_storage
from cli.utils.domain import normalize_domain


def print_header(title: str):
    """Print a formatted header"""
    print(f"\n{'='*60}")
    print(f"🔬 {title}")
    print(f"{'='*60}")


def print_step(step: str):
    """Print a formatted step"""
    print(f"\n📋 {step}")
    print("-" * 40)


def print_json(data: dict, title: str = "Data"):
    """Pretty print JSON data"""
    print(f"\n📄 {title}:")
    print(json.dumps(data, indent=2, default=str))


async def scenario_1_project_lifecycle():
    """Scenario 1: Complete project lifecycle"""
    print_header("Scenario 1: Complete Project Lifecycle")
    
    domain = "example-startup.com"
    normalized = normalize_domain(domain)
    
    print_step("1. Check if project exists")
    exists_before = project_storage.project_exists(normalized)
    print(f"Project exists before creation: {exists_before}")
    
    print_step("2. Create new project")
    project_dir = project_storage.create_project(normalized)
    print(f"Created project at: {project_dir}")
    
    print_step("3. Check project status")
    status = gtm_service.get_project_status(domain)
    print_json(status, "Initial Project Status")
    
    print_step("4. Add some mock data for each step")
    
    # Mock overview data
    overview_data = {
        "company_name": "Example Startup",
        "company_url": "https://example-startup.com",
        "description": "A revolutionary AI-powered productivity platform",
        "capabilities": ["AI automation", "Team collaboration", "Analytics"],
        "metadata": {"confidence": "high", "generated_at": datetime.now().isoformat()}
    }
    project_storage.save_step_data(normalized, "overview", overview_data)
    print("✓ Added company overview data")
    
    # Mock account data
    account_data = {
        "target_account_name": "Mid-market SaaS Companies",
        "target_account_description": "Growing SaaS companies with 50-500 employees",
        "firmographics": {
            "industry": ["Software", "SaaS"],
            "employees": "50-500",
            "revenue": "$5M-$50M"
        },
        "metadata": {"confidence": "high", "generated_at": datetime.now().isoformat()}
    }
    project_storage.save_step_data(normalized, "account", account_data)
    print("✓ Added target account data")
    
    # Mock persona data
    persona_data = {
        "target_persona_name": "VP of Engineering",
        "target_persona_description": "Senior engineering leader responsible for team productivity",
        "demographics": {
            "job_titles": ["VP Engineering", "Head of Engineering"],
            "departments": ["Engineering"],
            "seniority": ["VP", "Director"]
        },
        "metadata": {"confidence": "high", "generated_at": datetime.now().isoformat()}
    }
    project_storage.save_step_data(normalized, "persona", persona_data)
    print("✓ Added target persona data")
    
    print_step("5. Check updated project status")
    status_after = gtm_service.get_project_status(domain)
    print_json(status_after, "Updated Project Status")
    
    print_step("6. List all available steps")
    steps = project_storage.get_available_steps(normalized)
    print(f"Available steps: {steps}")
    
    print_step("7. Load and display each step's data")
    for step in steps:
        data = project_storage.load_step_data(normalized, step)
        if data:
            print(f"\n{step.upper()} Data:")
            print(f"  Company: {data.get('company_name', 'N/A')}")
            print(f"  Generated: {data.get('_generated_at', 'N/A')}")
            print(f"  Keys: {list(data.keys())}")
    
    return normalized


async def scenario_2_dependency_tracking():
    """Scenario 2: Test dependency tracking and stale data"""
    print_header("Scenario 2: Dependency Tracking & Stale Data")
    
    domain = "dependency-test.com"
    normalized = normalize_domain(domain)
    
    print_step("1. Create project with full pipeline")
    project_storage.create_project(normalized)
    
    # Add all steps
    steps_data = {
        "overview": {"company_name": "Dependency Test", "version": 1},
        "account": {"account_name": "Test Accounts", "depends_on": "overview"},
        "persona": {"persona_name": "Test Persona", "depends_on": ["overview", "account"]},
        "email": {"subject": "Test Email", "depends_on": ["overview", "account", "persona"]}
    }
    
    for step, data in steps_data.items():
        project_storage.save_step_data(normalized, step, data)
        print(f"✓ Added {step} data")
    
    print_step("2. Show dependency chain")
    dependencies = project_storage.get_dependency_chain(normalized)
    for step, deps in dependencies.items():
        print(f"  {step}: depends on {deps}")
    
    print_step("3. Regenerate overview (simulate user edit)")
    new_overview_data = {"company_name": "Dependency Test UPDATED", "version": 2}
    project_storage.save_step_data(normalized, "overview", new_overview_data)
    
    # Mark dependent steps as stale
    stale_steps = project_storage.mark_steps_stale(normalized, "overview")
    print(f"Steps marked as stale: {stale_steps}")
    
    print_step("4. Check for stale data")
    for step in ["account", "persona", "email"]:
        data = project_storage.load_step_data(normalized, step)
        if data and data.get("_stale"):
            print(f"  ⚠️  {step} is stale: {data.get('_stale_reason')}")
        else:
            print(f"  ✓ {step} is current")
    
    return normalized


async def scenario_3_project_management():
    """Scenario 3: Multi-project management"""
    print_header("Scenario 3: Multi-Project Management")
    
    print_step("1. Create multiple projects")
    
    companies = [
        {"domain": "techcorp.com", "name": "TechCorp", "steps": ["overview", "account"]},
        {"domain": "aiservice.io", "name": "AI Service", "steps": ["overview"]},
        {"domain": "saasplatform.com", "name": "SaaS Platform", "steps": ["overview", "account", "persona", "email"]}
    ]
    
    for company in companies:
        normalized = normalize_domain(company["domain"])
        project_storage.create_project(normalized)
        
        for i, step in enumerate(company["steps"]):
            mock_data = {
                "company_name": company["name"],
                "step": step,
                "step_number": i + 1,
                "generated_at": datetime.now().isoformat()
            }
            project_storage.save_step_data(normalized, step, mock_data)
        
        print(f"✓ Created {company['domain']} with {len(company['steps'])} steps")
    
    print_step("2. List all projects")
    projects = project_storage.list_projects()
    
    print(f"\nFound {len(projects)} projects:")
    for project in projects:
        status = gtm_service.get_project_status(project["domain"])
        print(f"  📁 {project['domain']}")
        print(f"     Steps: {project['available_steps']}")
        print(f"     Progress: {status['progress_percentage']:.1f}%")
        print(f"     Last updated: {project.get('updated_at', 'Unknown')}")
    
    print_step("3. Compare project completion")
    for project in projects:
        status = gtm_service.get_project_status(project["domain"])
        completion = status['completed_count'] / status['total_steps'] * 100
        
        if completion == 100:
            print(f"  🟢 {project['domain']}: Complete ({completion:.0f}%)")
        elif completion >= 50:
            print(f"  🟡 {project['domain']}: In Progress ({completion:.0f}%)")
        else:
            print(f"  🔴 {project['domain']}: Just Started ({completion:.0f}%)")
    
    return [normalize_domain(c["domain"]) for c in companies]


async def scenario_4_data_flow_simulation():
    """Scenario 4: Simulate realistic data flow"""
    print_header("Scenario 4: Realistic Data Flow Simulation")
    
    domain = "realistic-test.com"
    normalized = normalize_domain(domain)
    
    print_step("1. Simulate Step 1: Company Overview")
    
    # Simulate what would come from actual LLM generation
    realistic_overview = {
        "company_name": "CloudFlow Analytics",
        "company_url": "https://realistic-test.com",
        "description": "CloudFlow Analytics provides real-time data processing and analytics for enterprise customers.",
        "capabilities": [
            "Real-time data ingestion",
            "Advanced analytics dashboard",
            "Machine learning insights",
            "API integrations",
            "Enterprise security"
        ],
        "business_profile_insights": [
            "Category: Enterprise data analytics platform",
            "Business Model: Subscription-based SaaS with usage tiers",
            "Existing Customers: 150+ enterprise clients including Fortune 500 companies"
        ],
        "objections": [
            "Integration complexity with existing systems",
            "Data security and compliance concerns",
            "ROI timeline and measurement"
        ],
        "metadata": {
            "context_quality": "high",
            "confidence": "high",
            "processing_time_ms": 2500
        }
    }
    
    project_storage.create_project(normalized)
    project_storage.save_step_data(normalized, "overview", realistic_overview)
    print("✓ Generated realistic company overview")
    print(f"  Company: {realistic_overview['company_name']}")
    print(f"  Capabilities: {len(realistic_overview['capabilities'])} identified")
    
    print_step("2. Simulate Step 2: Target Account (depends on overview)")
    
    # This would use the overview data as context
    overview_data = project_storage.load_step_data(normalized, "overview")
    print(f"Using overview context for: {overview_data['company_name']}")
    
    realistic_account = {
        "target_account_name": "Enterprise Data-Driven Organizations",
        "target_account_description": "Large organizations with complex data needs and existing analytics infrastructure",
        "target_account_rationale": [
            "Enterprise companies generate massive amounts of data requiring real-time processing",
            "These organizations have budget for premium analytics solutions",
            "Existing analytics infrastructure indicates sophistication and need for advanced tools"
        ],
        "firmographics": {
            "industry": ["Technology", "Financial Services", "Healthcare", "Manufacturing"],
            "employees": "1000+",
            "revenue": "$100M+",
            "geography": ["North America", "Europe"],
            "keywords": ["data-driven", "analytics", "business intelligence", "digital transformation"]
        },
        "buying_signals": [
            {
                "title": "Data infrastructure investments",
                "description": "Recent investments in cloud data platforms or hiring data engineers",
                "type": "Company Data",
                "priority": "High"
            }
        ],
        "metadata": {
            "confidence_assessment": {
                "overall_confidence": "high",
                "data_quality": "high"
            }
        }
    }
    
    project_storage.save_step_data(normalized, "account", realistic_account)
    print("✓ Generated target account profile")
    print(f"  Target: {realistic_account['target_account_name']}")
    print(f"  Industries: {realistic_account['firmographics']['industry']}")
    
    print_step("3. Simulate dependency chain validation")
    
    # Check what data each step would have access to
    available_steps = project_storage.get_available_steps(normalized)
    print(f"Available context for next steps: {available_steps}")
    
    dependencies = project_storage.get_dependency_chain(normalized)
    for step, deps in dependencies.items():
        available_context = []
        for dep in deps:
            if dep in available_steps:
                dep_data = project_storage.load_step_data(normalized, dep)
                if dep_data:
                    available_context.append(f"{dep}({len(dep_data)} fields)")
        
        if available_context:
            print(f"  {step} can use: {', '.join(available_context)}")
        else:
            print(f"  {step} has no dependencies (root step)")
    
    print_step("4. Simulate partial regeneration scenario")
    
    print("User decides to regenerate company overview with additional context...")
    
    # Add user context and regenerate
    updated_overview = realistic_overview.copy()
    updated_overview["user_inputted_context"] = "Focus on real-time capabilities for financial trading"
    updated_overview["description"] = "CloudFlow Analytics specializes in real-time data processing for financial trading and enterprise analytics."
    updated_overview["_regenerated"] = True
    updated_overview["_regenerated_at"] = datetime.now().isoformat()
    
    project_storage.save_step_data(normalized, "overview", updated_overview)
    
    # Mark dependent steps as stale
    stale_steps = project_storage.mark_steps_stale(normalized, "overview")
    print(f"Steps now stale due to overview update: {stale_steps}")
    
    # Show the impact
    account_data = project_storage.load_step_data(normalized, "account")
    if account_data.get("_stale"):
        print("  ⚠️  Target account data is now stale and should be regenerated")
        print(f"     Reason: {account_data.get('_stale_reason')}")
    
    return normalized


async def cleanup_test_projects(project_domains):
    """Clean up test projects"""
    print_header("Cleanup Test Projects")
    
    for domain in project_domains:
        if project_storage.project_exists(domain):
            success = project_storage.delete_project(domain)
            print(f"{'✓' if success else '❌'} Deleted {domain}")
        else:
            print(f"⚠️  {domain} not found")
    
    # Show remaining projects
    remaining = project_storage.list_projects()
    print(f"\nRemaining projects: {len(remaining)}")


async def main():
    """Run all interactive scenarios"""
    print("🧪 Interactive Testing for Stage 2: Core Generation Engine")
    print("This will create test projects and demonstrate the data flow")
    
    created_projects = []
    
    try:
        # Run scenarios
        project1 = await scenario_1_project_lifecycle()
        created_projects.append(project1)
        
        project2 = await scenario_2_dependency_tracking()
        created_projects.append(project2)
        
        project3_list = await scenario_3_project_management()
        created_projects.extend(project3_list)
        
        project4 = await scenario_4_data_flow_simulation()
        created_projects.append(project4)
        
        print_header("Summary")
        print("✅ All interactive scenarios completed successfully!")
        print("\nKey capabilities demonstrated:")
        print("  • Project lifecycle management")
        print("  • Step-by-step data storage and retrieval")
        print("  • Dependency tracking between steps")
        print("  • Stale data detection and marking")
        print("  • Multi-project management")
        print("  • Realistic data flow simulation")
        
        input("\nPress Enter to clean up test projects...")
        
    finally:
        # Always clean up
        await cleanup_test_projects(created_projects)


if __name__ == "__main__":
    asyncio.run(main())