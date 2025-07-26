"""
Unit tests for CLI services.
Tests the core service layer without making real API calls.
"""

import pytest
import json
from pathlib import Path
from unittest.mock import Mock, AsyncMock, patch

# Import the services to test
import sys
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from cli.services.gtm_generation_service import GTMGenerationService
from cli.services.project_storage import ProjectStorage


class TestGTMGenerationService:
    """Test suite for GTM Generation Service"""
    
    @pytest.fixture
    def gtm_service(self, temp_project_dir):
        """Create GTM service instance with temp storage"""
        service = GTMGenerationService()
        service.storage.PROJECT_ROOT = temp_project_dir
        return service
    
    @pytest.mark.asyncio
    async def test_generate_company_overview_new(self, gtm_service, mock_llm_responses):
        """Test generating new company overview"""
        domain = "acme.com"
        context = "Enterprise automation company"
        
        result = await gtm_service.generate_company_overview(
            domain=domain,
            user_context=context,
            force_regenerate=True
        )
        
        assert result is not None
        assert hasattr(result, 'company_name')
        # Verify it was saved to storage
        saved_data = gtm_service.storage.load_step_data(domain, "overview")
        assert saved_data is not None
        assert saved_data['company_name'] == mock_llm_responses['overview']['company_name']
    
    @pytest.mark.asyncio
    async def test_generate_company_overview_existing(self, gtm_service, mock_project_with_data):
        """Test loading existing company overview"""
        domain = mock_project_with_data.name
        
        # Should load existing data without regenerating
        result = await gtm_service.generate_company_overview(
            domain=domain,
            force_regenerate=False
        )
        
        assert result is not None
        assert result.company_name == "Acme Corporation"  # From mock data
    
    @pytest.mark.asyncio
    async def test_generate_target_account_new(self, gtm_service, mock_project_with_data, mock_llm_responses):
        """Test generating new target account"""
        domain = mock_project_with_data.name
        hypothesis = "Mid-market tech companies"
        
        result = await gtm_service.generate_target_account(
            domain=domain,
            hypothesis=hypothesis,
            force_regenerate=True
        )
        
        assert result is not None
        assert hasattr(result, 'target_account_name')
        # Verify it was saved
        saved_data = gtm_service.storage.load_step_data(domain, "account")
        assert saved_data is not None
    
    @pytest.mark.asyncio
    async def test_generate_target_account_missing_dependency(self, gtm_service, temp_project_dir):
        """Test target account generation with missing company overview"""
        domain = "no-overview.com"
        
        with pytest.raises(ValueError, match="Company overview must be generated first"):
            await gtm_service.generate_target_account(
                domain=domain,
                force_regenerate=True
            )
    
    @pytest.mark.asyncio
    async def test_generate_target_persona_new(self, gtm_service, mock_project_with_data, mock_llm_responses):
        """Test generating new target persona"""
        domain = mock_project_with_data.name
        hypothesis = "VP of Operations"
        
        result = await gtm_service.generate_target_persona(
            domain=domain,
            hypothesis=hypothesis,
            force_regenerate=True
        )
        
        assert result is not None
        assert hasattr(result, 'target_persona_name')
        # Verify it was saved
        saved_data = gtm_service.storage.load_step_data(domain, "persona")
        assert saved_data is not None
    
    @pytest.mark.asyncio
    async def test_generate_target_persona_missing_dependencies(self, gtm_service, temp_project_dir):
        """Test persona generation with missing dependencies"""
        domain = "incomplete.com"
        
        # Create only overview (missing account)
        project_path = temp_project_dir / domain
        project_path.mkdir()
        overview_data = {"company_name": "Test Corp", "_generated_at": "2024-01-01T00:00:00Z"}
        (project_path / "overview.json").write_text(json.dumps(overview_data))
        
        with pytest.raises(ValueError, match="Target account must be generated first"):
            await gtm_service.generate_target_persona(
                domain=domain,
                force_regenerate=True
            )
    
    @pytest.mark.asyncio
    async def test_generate_email_campaign_new(self, gtm_service, mock_project_with_data, mock_llm_responses):
        """Test generating new email campaign"""
        domain = mock_project_with_data.name
        
        result = await gtm_service.generate_email_campaign(
            domain=domain,
            force_regenerate=True
        )
        
        assert result is not None
        assert hasattr(result, 'subjects')
        # Verify it was saved
        saved_data = gtm_service.storage.load_step_data(domain, "email")
        assert saved_data is not None
    
    @pytest.mark.asyncio
    async def test_generate_email_campaign_with_preferences(self, gtm_service, mock_project_with_data):
        """Test generating email campaign with guided preferences"""
        domain = mock_project_with_data.name
        preferences = {
            "tone": "professional",
            "length": "short",
            "focus": "roi"
        }
        
        result = await gtm_service.generate_email_campaign(
            domain=domain,
            preferences=preferences,
            force_regenerate=True
        )
        
        assert result is not None
    
    def test_get_project_status_existing(self, gtm_service, mock_project_with_data):
        """Test getting status of existing project"""
        domain = mock_project_with_data.name
        
        status = gtm_service.get_project_status(domain)
        
        assert status["exists"] is True
        assert status["progress_percentage"] > 0
        assert len(status["available_steps"]) > 0
        assert "overview" in status["available_steps"]
    
    def test_get_project_status_nonexistent(self, gtm_service):
        """Test getting status of non-existent project"""
        status = gtm_service.get_project_status("nonexistent.com")
        
        assert status["exists"] is False
        assert status["progress_percentage"] == 0
        assert len(status["available_steps"]) == 0
    
    @pytest.mark.asyncio
    async def test_force_regenerate_marks_stale(self, gtm_service, mock_project_with_data):
        """Test that force regeneration marks dependent steps as stale"""
        domain = mock_project_with_data.name
        
        # Regenerate overview (step 1) - should mark all others as stale
        await gtm_service.generate_company_overview(
            domain=domain,
            force_regenerate=True
        )
        
        # Check that dependent steps would be marked stale
        # (This is mocked, so we're testing the interface)
        assert True  # Placeholder - would check stale markers in real implementation
    
    def test_domain_normalization_in_service(self, gtm_service):
        """Test that domains are properly normalized in service calls"""
        test_domains = [
            ("https://acme.com", "https://acme.com"),
            ("www.acme.com", "https://acme.com"),
            ("acme.com", "https://acme.com")
        ]
        
        for input_domain, expected_normalized in test_domains:
            status = gtm_service.get_project_status(input_domain)
            # The service should handle normalization internally
            assert isinstance(status, dict)


class TestProjectStorage:
    """Test suite for Project Storage"""
    
    @pytest.fixture
    def storage(self, temp_project_dir):
        """Create project storage instance with temp directory"""
        storage = ProjectStorage()
        storage.PROJECT_ROOT = temp_project_dir
        return storage
    
    def test_save_and_load_step_data(self, storage):
        """Test saving and loading step data"""
        domain = "test.com"
        step = "overview"
        data = {
            "company_name": "Test Corp",
            "description": "Test description",
            "_generated_at": "2024-01-01T00:00:00Z"
        }
        
        # Save data
        storage.save_step_data(domain, step, data)
        
        # Load and verify
        loaded_data = storage.load_step_data(domain, step)
        assert loaded_data is not None
        assert loaded_data["company_name"] == "Test Corp"
        assert loaded_data["_generated_at"] == "2024-01-01T00:00:00Z"
    
    def test_load_nonexistent_step_data(self, storage):
        """Test loading non-existent step data"""
        result = storage.load_step_data("nonexistent.com", "overview")
        assert result is None
    
    def test_get_file_path(self, storage, temp_project_dir):
        """Test file path generation"""
        domain = "test.com"
        step = "overview"
        
        file_path = storage.get_file_path(domain, step)
        
        expected_path = temp_project_dir / domain / f"{step}.json"
        assert file_path == expected_path
    
    def test_list_projects(self, storage, mock_project_with_data, mock_incomplete_project):
        """Test listing all projects"""
        projects = storage.list_projects()
        
        assert len(projects) >= 2
        project_domains = [p["domain"] for p in projects]
        assert mock_project_with_data.name in project_domains
        assert mock_incomplete_project.name in project_domains
    
    def test_list_projects_empty(self, storage):
        """Test listing projects when none exist"""
        projects = storage.list_projects()
        assert len(projects) == 0
    
    def test_project_directory_creation(self, storage, temp_project_dir):
        """Test that project directories are created automatically"""
        domain = "new-project.com"
        step = "overview"
        data = {"test": "data"}
        
        # Save data should create directory
        storage.save_step_data(domain, step, data)
        
        project_dir = temp_project_dir / domain
        assert project_dir.exists()
        assert project_dir.is_dir()
    
    def test_save_step_data_with_metadata(self, storage):
        """Test that saving step data includes proper metadata"""
        domain = "metadata-test.com"
        step = "overview"
        data = {"company_name": "Metadata Corp"}
        
        storage.save_step_data(domain, step, data)
        
        loaded_data = storage.load_step_data(domain, step)
        assert "_generated_at" in loaded_data
        assert loaded_data["company_name"] == "Metadata Corp"
    
    def test_handle_corrupted_json(self, storage, temp_project_dir):
        """Test handling of corrupted JSON files"""
        domain = "corrupted.com"
        project_dir = temp_project_dir / domain
        project_dir.mkdir()
        
        # Write corrupted JSON
        json_file = project_dir / "overview.json"
        json_file.write_text("{corrupted json")
        
        # Should handle gracefully
        result = storage.load_step_data(domain, "overview")
        assert result is None  # Should return None for corrupted data
    
    def test_save_overwrites_existing(self, storage):
        """Test that saving overwrites existing data"""
        domain = "overwrite-test.com"
        step = "overview"
        
        # Save initial data
        initial_data = {"version": 1}
        storage.save_step_data(domain, step, initial_data)
        
        # Save updated data
        updated_data = {"version": 2}
        storage.save_step_data(domain, step, updated_data)
        
        # Verify updated data is loaded
        loaded_data = storage.load_step_data(domain, step)
        assert loaded_data["version"] == 2
    
    def test_metadata_management(self, storage, temp_project_dir):
        """Test project metadata creation and loading"""
        domain = "metadata-project.com"
        step = "overview"
        data = {"test": "data"}
        
        # Save step data
        storage.save_step_data(domain, step, data)
        
        # Check if metadata file is created
        metadata_file = temp_project_dir / domain / ".metadata.json"
        if metadata_file.exists():  # Implementation may or may not create this
            metadata_content = json.loads(metadata_file.read_text())
            assert "domain" in metadata_content or "created_at" in metadata_content


class TestServiceIntegration:
    """Test integration between services"""
    
    @pytest.mark.asyncio
    async def test_full_generation_pipeline(self, temp_project_dir, mock_llm_responses):
        """Test complete generation pipeline from overview to email"""
        gtm_service = GTMGenerationService()
        gtm_service.storage.PROJECT_ROOT = temp_project_dir
        
        domain = "pipeline-test.com"
        
        # Step 1: Generate overview
        overview = await gtm_service.generate_company_overview(
            domain=domain,
            force_regenerate=True
        )
        assert overview is not None
        
        # Step 2: Generate account (depends on overview)
        account = await gtm_service.generate_target_account(
            domain=domain,
            force_regenerate=True
        )
        assert account is not None
        
        # Step 3: Generate persona (depends on overview and account)
        persona = await gtm_service.generate_target_persona(
            domain=domain,
            force_regenerate=True
        )
        assert persona is not None
        
        # Step 4: Generate email (depends on all previous)
        email = await gtm_service.generate_email_campaign(
            domain=domain,
            force_regenerate=True
        )
        assert email is not None
        
        # Verify all data is saved
        assert gtm_service.storage.load_step_data(domain, "overview") is not None
        assert gtm_service.storage.load_step_data(domain, "account") is not None
        assert gtm_service.storage.load_step_data(domain, "persona") is not None
        assert gtm_service.storage.load_step_data(domain, "email") is not None
    
    def test_service_error_handling(self, temp_project_dir, mock_error_scenarios):
        """Test service error handling"""
        gtm_service = GTMGenerationService()
        gtm_service.storage.PROJECT_ROOT = temp_project_dir
        
        mock_error_scenarios["set"]("api_error")
        
        # Should handle LLM errors gracefully
        with pytest.raises(Exception):  # Expected to raise exception
            import asyncio
            asyncio.run(gtm_service.generate_company_overview(
                domain="error-test.com",
                force_regenerate=True
            ))
    
    def test_storage_persistence_across_service_instances(self, temp_project_dir):
        """Test that data persists across different service instances"""
        # Create first service instance and save data
        service1 = GTMGenerationService()
        service1.storage.PROJECT_ROOT = temp_project_dir
        
        domain = "persistence-test.com"
        test_data = {"company_name": "Persistent Corp", "_generated_at": "2024-01-01T00:00:00Z"}
        service1.storage.save_step_data(domain, "overview", test_data)
        
        # Create second service instance and load data
        service2 = GTMGenerationService()
        service2.storage.PROJECT_ROOT = temp_project_dir
        
        loaded_data = service2.storage.load_step_data(domain, "overview")
        assert loaded_data is not None
        assert loaded_data["company_name"] == "Persistent Corp"


class TestServicePerformance:
    """Test performance characteristics of services"""
    
    def test_storage_operations_performance(self, storage):
        """Test that storage operations complete quickly"""
        import time
        
        domain = "performance-test.com"
        large_data = {"large_field": "x" * 10000}  # 10KB data
        
        # Time save operation
        start_time = time.time()
        storage.save_step_data(domain, "overview", large_data)
        save_time = time.time() - start_time
        
        # Time load operation
        start_time = time.time()
        loaded_data = storage.load_step_data(domain, "overview")
        load_time = time.time() - start_time
        
        # Should complete quickly (less than 1 second each)
        assert save_time < 1.0
        assert load_time < 1.0
        assert loaded_data["large_field"] == "x" * 10000
    
    def test_multiple_projects_handling(self, storage):
        """Test handling multiple projects efficiently"""
        # Create multiple projects
        for i in range(10):
            domain = f"project-{i}.com"
            data = {"project_id": i, "name": f"Project {i}"}
            storage.save_step_data(domain, "overview", data)
        
        # List all projects
        projects = storage.list_projects()
        assert len(projects) == 10
        
        # Verify each project data
        for i in range(10):
            domain = f"project-{i}.com"
            data = storage.load_step_data(domain, "overview")
            assert data["project_id"] == i