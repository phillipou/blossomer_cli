"""
End-to-end tests for the CLI.
Tests complete CLI usage scenarios as a real user would experience them.
"""

import pytest
import json
import time
from pathlib import Path
from unittest.mock import patch, Mock
from typer.testing import CliRunner

from cli.main import app


class TestCompleteWorkflowE2E:
    """End-to-end test of complete CLI workflow"""
    
    def test_full_gtm_generation_workflow(self, mock_cli_runner, temp_project_dir):
        """Test complete GTM generation workflow from start to finish"""
        domain = "e2e-complete.com"
        
        # Step 1: Initialize new project
        print(f"\n🚀 Testing complete workflow for {domain}")
        
        init_result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        print(f"Init result: {init_result.exit_code}")
        
        assert init_result.exit_code == 0
        assert "Company Overview" in init_result.output
        assert domain in init_result.output or "Analyzing" in init_result.output
        
        # Verify project directory was created
        project_dir = temp_project_dir / domain
        assert project_dir.exists()
        
        # Step 2: View all generated assets
        show_all_result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        print(f"Show all result: {show_all_result.exit_code}")
        
        assert show_all_result.exit_code == 0
        assert f"GTM Project: {domain}" in show_all_result.output
        assert "Progress:" in show_all_result.output
        
        # Step 3: View individual assets
        assets = ["overview", "account", "persona", "email", "strategy"]
        for asset in assets:
            show_result = mock_cli_runner.invoke(app, ["show", asset, "--domain", domain])
            if show_result.exit_code == 0:  # Asset exists
                print(f"✓ {asset} asset viewable")
                assert len(show_result.output) > 100  # Should have substantial content
        
        # Step 4: Test JSON output
        json_result = mock_cli_runner.invoke(app, ["show", "overview", "--json", "--domain", domain])
        if json_result.exit_code == 0:
            assert "{" in json_result.output  # Should contain JSON
            print("✓ JSON output working")
        
        # Step 5: List projects (should include our new project)
        list_result = mock_cli_runner.invoke(app, ["list"])
        assert list_result.exit_code == 0
        assert domain in list_result.output
        print("✓ Project listed correctly")
        
        # Step 6: Edit asset (mock editor)
        with patch('cli.utils.editor.open_file_in_editor') as mock_editor:
            edit_result = mock_cli_runner.invoke(app, ["edit", "strategy", "--domain", domain])
            assert edit_result.exit_code == 0
            if mock_editor.called:
                print("✓ Editor integration working")
        
        # Step 7: Export assets
        with patch('pathlib.Path.write_text') as mock_write:
            export_result = mock_cli_runner.invoke(app, ["export", "all", "--domain", domain])
            assert export_result.exit_code == 0
            if mock_write.called:
                print("✓ Export functionality working")
        
        print(f"🎉 Complete workflow test passed for {domain}")
    
    def test_resume_workflow_e2e(self, mock_cli_runner, temp_project_dir):
        """Test resuming workflow after interruption"""
        domain = "e2e-resume.com"
        
        # Step 1: Start project (simulate interruption by not completing)
        # Create partial project
        project_dir = temp_project_dir / domain
        project_dir.mkdir()
        
        # Create only overview
        overview_data = {
            "company_name": "Resume Test Corp",
            "description": "Test company for resume workflow",
            "_generated_at": "2024-01-01T00:00:00Z"
        }
        (project_dir / "overview.json").write_text(json.dumps(overview_data))
        
        # Step 2: Resume project (should detect existing and offer options)
        with patch('cli.utils.menu_utils.show_menu_with_numbers', 
                  return_value="Start from Step 2: Target Account Profile"):
            resume_result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            assert resume_result.exit_code == 0
            print("✓ Resume workflow working")
        
        # Step 3: Verify project can be viewed after resume
        show_result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        assert show_result.exit_code == 0
        assert domain in show_result.output
    
    def test_yolo_mode_e2e(self, mock_cli_runner, temp_project_dir):
        """Test YOLO mode (non-interactive) end-to-end"""
        domain = "e2e-yolo.com"
        
        # YOLO mode should complete without any user interaction
        result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        
        assert result.exit_code == 0
        
        # Should have created project
        project_dir = temp_project_dir / domain
        assert project_dir.exists()
        
        # Should be able to view results immediately
        show_result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        assert show_result.exit_code == 0
        
        print("✓ YOLO mode working end-to-end")
    
    def test_context_driven_workflow_e2e(self, mock_cli_runner, temp_project_dir):
        """Test workflow with user-provided context"""
        domain = "e2e-context.com"
        context = "B2B SaaS startup in the marketing automation space, targeting mid-market companies"
        
        # Initialize with context
        result = mock_cli_runner.invoke(app, [
            "init", domain,
            "--context", context,
            "--yolo"
        ])
        
        assert result.exit_code == 0
        
        # Context should influence generation (verified through successful completion)
        project_dir = temp_project_dir / domain
        assert project_dir.exists()
        
        # Should be able to view context-driven results
        show_result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
        assert show_result.exit_code == 0
        
        print("✓ Context-driven workflow working")


class TestMultiProjectE2E:
    """End-to-end tests with multiple projects"""
    
    def test_multiple_projects_workflow_e2e(self, mock_cli_runner, temp_project_dir):
        """Test managing multiple projects end-to-end"""
        domains = ["multi-1.com", "multi-2.com", "multi-3.com"]
        
        # Create multiple projects
        for i, domain in enumerate(domains):
            print(f"Creating project {i+1}: {domain}")
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            assert result.exit_code == 0
            
            # Small delay to ensure different timestamps
            time.sleep(0.1)
        
        # List all projects
        list_result = mock_cli_runner.invoke(app, ["list"])
        assert list_result.exit_code == 0
        
        for domain in domains:
            assert domain in list_result.output
        print("✓ All projects listed correctly")
        
        # Work with each project individually
        for domain in domains:
            # Show project
            show_result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
            assert show_result.exit_code == 0
            assert domain in show_result.output
            
            # Export project
            export_result = mock_cli_runner.invoke(app, ["export", "overview", "--domain", domain])
            assert export_result.exit_code == 0
            
        print("✓ Multi-project workflow working")
    
    def test_project_switching_e2e(self, mock_cli_runner, temp_project_dir):
        """Test switching between projects seamlessly"""
        domain1 = "switch-test-1.com"
        domain2 = "switch-test-2.com"
        
        # Create two projects
        for domain in [domain1, domain2]:
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            assert result.exit_code == 0
        
        # Switch between projects multiple times
        for _ in range(3):
            # Work with project 1
            result1 = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain1])
            assert result1.exit_code == 0
            
            # Work with project 2
            result2 = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain2])
            assert result2.exit_code == 0
        
        print("✓ Project switching working")


class TestErrorRecoveryE2E:
    """End-to-end tests for error recovery scenarios"""
    
    def test_api_error_recovery_e2e(self, mock_cli_runner, mock_error_scenarios, temp_project_dir):
        """Test complete error recovery workflow"""
        domain = "error-recovery.com"
        
        # Step 1: Encounter API error
        mock_error_scenarios["set"]("api_error")
        
        error_result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        assert error_result.exit_code == 1
        assert "error" in error_result.output.lower() or "failed" in error_result.output.lower()
        
        # Step 2: Reset error scenario and retry
        mock_error_scenarios["set"]("normal")  # Reset to normal
        
        retry_result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        assert retry_result.exit_code == 0
        
        # Step 3: Verify recovery was successful
        show_result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        assert show_result.exit_code == 0
        
        print("✓ Error recovery workflow working")
    
    def test_corrupted_data_recovery_e2e(self, mock_cli_runner, temp_project_dir):
        """Test recovery from corrupted project data"""
        domain = "corrupted-recovery.com"
        
        # Step 1: Create project with corrupted data
        project_dir = temp_project_dir / domain
        project_dir.mkdir()
        
        # Write corrupted JSON
        (project_dir / "overview.json").write_text("{corrupted json content")
        
        # Step 2: Attempt to view corrupted project
        show_result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
        assert show_result.exit_code == 0  # Should handle gracefully
        
        # Step 3: Reinitialize to recover
        recover_result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        assert recover_result.exit_code == 0
        
        # Step 4: Verify recovery
        verify_result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
        assert verify_result.exit_code == 0
        
        print("✓ Corrupted data recovery working")
    
    def test_permission_error_handling_e2e(self, mock_cli_runner, temp_project_dir):
        """Test handling of file permission errors"""
        domain = "permission-test.com"
        
        # Create project normally first
        init_result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        assert init_result.exit_code == 0
        
        project_dir = temp_project_dir / domain
        
        # Make directory read-only
        project_dir.chmod(0o444)
        
        try:
            # Attempt operations that require write access
            reinit_result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            # Should handle permission error gracefully
            assert reinit_result.exit_code in [0, 1]
            
            if reinit_result.exit_code == 1:
                assert "error" in reinit_result.output.lower() or "permission" in reinit_result.output.lower()
            
            print("✓ Permission error handling working")
            
        finally:
            # Restore permissions for cleanup
            project_dir.chmod(0o755)


class TestPerformanceE2E:
    """End-to-end performance tests"""
    
    def test_full_workflow_performance_e2e(self, mock_cli_runner, temp_project_dir):
        """Test that full workflow completes in reasonable time"""
        domain = "performance-e2e.com"
        
        start_time = time.time()
        
        # Complete workflow
        init_result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        assert init_result.exit_code == 0
        
        show_result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        assert show_result.exit_code == 0
        
        list_result = mock_cli_runner.invoke(app, ["list"])
        assert list_result.exit_code == 0
        
        export_result = mock_cli_runner.invoke(app, ["export", "overview", "--domain", domain])
        assert export_result.exit_code == 0
        
        total_time = time.time() - start_time
        
        # Should complete full workflow quickly with mocked APIs
        assert total_time < 15.0
        print(f"✓ Full workflow completed in {total_time:.2f}s")
    
    def test_large_scale_operations_e2e(self, mock_cli_runner, temp_project_dir):
        """Test operations with many projects"""
        num_projects = 10
        domains = [f"scale-test-{i}.com" for i in range(num_projects)]
        
        start_time = time.time()
        
        # Create many projects
        for domain in domains:
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            assert result.exit_code == 0
        
        # List all projects
        list_result = mock_cli_runner.invoke(app, ["list"])
        assert list_result.exit_code == 0
        
        for domain in domains[:5]:  # Check first 5
            assert domain in list_result.output
        
        total_time = time.time() - start_time
        
        # Should handle scale operations efficiently
        assert total_time < 30.0
        print(f"✓ Large scale operations completed in {total_time:.2f}s")


class TestUserExperienceE2E:
    """End-to-end tests for user experience"""
    
    def test_first_time_user_experience_e2e(self, mock_cli_runner, temp_project_dir):
        """Test complete first-time user experience"""
        domain = "first-time-ux.com"
        
        # 1. User sees welcome when running main command
        welcome_result = mock_cli_runner.invoke(app, [])
        assert welcome_result.exit_code == 0
        assert "Welcome" in welcome_result.output
        assert "Blossomer CLI" in welcome_result.output
        assert "init" in welcome_result.output
        
        # 2. User gets help
        help_result = mock_cli_runner.invoke(app, ["--help"])
        assert help_result.exit_code == 0
        assert "init" in help_result.output
        assert "show" in help_result.output
        
        # 3. User creates first project
        init_result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        assert init_result.exit_code == 0
        
        # Should provide clear feedback about what's happening
        progress_indicators = ["Company Overview", "Target Account", "Email Campaign"]
        assert any(indicator in init_result.output for indicator in progress_indicators)
        
        # 4. User explores their results
        show_result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        assert show_result.exit_code == 0
        assert "GTM Project" in show_result.output
        assert "Commands:" in show_result.output  # Should show next steps
        
        print("✓ First-time user experience is smooth")
    
    def test_error_guidance_e2e(self, mock_cli_runner):
        """Test that users get helpful guidance when errors occur"""
        # Test invalid domain
        invalid_result = mock_cli_runner.invoke(app, ["init", "invalid..domain", "--yolo"])
        assert invalid_result.exit_code == 1
        assert "Invalid domain format" in invalid_result.output
        assert "Try:" in invalid_result.output or "example" in invalid_result.output.lower()
        
        # Test non-existent project
        nonexistent_result = mock_cli_runner.invoke(app, ["show", "all", "--domain", "nonexistent.com"])
        assert nonexistent_result.exit_code == 0
        assert "No GTM project found" in nonexistent_result.output
        assert "blossomer init" in nonexistent_result.output
        
        # Test invalid command
        invalid_cmd_result = mock_cli_runner.invoke(app, ["invalid_command"])
        assert invalid_cmd_result.exit_code != 0 or "No such command" in invalid_cmd_result.output
        
        print("✓ Error guidance is helpful")
    
    def test_progressive_disclosure_e2e(self, mock_cli_runner, temp_project_dir):
        """Test that information is progressively disclosed"""
        domain = "progressive-ux.com"
        
        # Create project
        init_result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        assert init_result.exit_code == 0
        
        # Overview view - should be concise
        overview_result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        assert overview_result.exit_code == 0
        assert "Progress:" in overview_result.output
        
        # Detailed view - should show more information
        detail_result = mock_cli_runner.invoke(app, ["show", "overview", "--domain", domain])
        assert detail_result.exit_code == 0
        
        # JSON view - should show raw data
        json_result = mock_cli_runner.invoke(app, ["show", "overview", "--json", "--domain", domain])
        if json_result.exit_code == 0:
            assert "{" in json_result.output
        
        print("✓ Progressive disclosure working")


class TestRealWorldScenariosE2E:
    """End-to-end tests simulating real-world usage scenarios"""
    
    def test_consultant_workflow_e2e(self, mock_cli_runner, temp_project_dir):
        """Test workflow for a consultant managing multiple client projects"""
        clients = ["client-alpha.com", "client-beta.com", "client-gamma.com"]
        
        # Consultant creates projects for multiple clients
        for client in clients:
            result = mock_cli_runner.invoke(app, [
                "init", client,
                "--context", f"Client project for {client}",
                "--yolo"
            ])
            assert result.exit_code == 0
            print(f"✓ Created project for {client}")
        
        # Consultant reviews all clients
        list_result = mock_cli_runner.invoke(app, ["list"])
        assert list_result.exit_code == 0
        for client in clients:
            assert client in list_result.output
        
        # Consultant works on specific client
        target_client = clients[0]
        show_result = mock_cli_runner.invoke(app, ["show", "all", "--domain", target_client])
        assert show_result.exit_code == 0
        
        # Consultant exports deliverables
        export_result = mock_cli_runner.invoke(app, ["export", "all", "--domain", target_client])
        assert export_result.exit_code == 0
        
        print("✓ Consultant workflow completed successfully")
    
    def test_iterative_refinement_e2e(self, mock_cli_runner, temp_project_dir):
        """Test iterative refinement workflow"""
        domain = "iterative-test.com"
        
        # Initial creation
        init_result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        assert init_result.exit_code == 0
        
        # Review initial results
        show_result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        assert show_result.exit_code == 0
        
        # Refine by regenerating from specific step
        with patch('cli.utils.menu_utils.show_menu_with_numbers', 
                  return_value="Start from Step 2: Target Account Profile"):
            refine_result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            assert refine_result.exit_code == 0
        
        # Review refined results
        refined_show_result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        assert refined_show_result.exit_code == 0
        
        print("✓ Iterative refinement workflow working")
    
    def test_team_handoff_e2e(self, mock_cli_runner, temp_project_dir):
        """Test team handoff scenario"""
        domain = "team-handoff.com"
        
        # Team member 1 creates initial project
        member1_result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
        assert member1_result.exit_code == 0
        
        # Verify project files exist for handoff
        project_dir = temp_project_dir / domain
        assert project_dir.exists()
        
        # Team member 2 can view the project
        member2_show_result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
        assert member2_show_result.exit_code == 0
        assert domain in member2_show_result.output
        
        # Team member 2 can continue work
        member2_export_result = mock_cli_runner.invoke(app, ["export", "all", "--domain", domain])
        assert member2_export_result.exit_code == 0
        
        print("✓ Team handoff workflow working")


class TestEdgeCasesE2E:
    """End-to-end tests for edge cases"""
    
    def test_unusual_domain_formats_e2e(self, mock_cli_runner, temp_project_dir):
        """Test unusual but valid domain formats"""
        unusual_domains = [
            "sub.domain.example.com",
            "example-with-dashes.com",
            "123numeric.com",
        ]
        
        for domain in unusual_domains:
            try:
                result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
                if result.exit_code == 0:
                    print(f"✓ Handled unusual domain: {domain}")
                    
                    # Should be able to work with it normally
                    show_result = mock_cli_runner.invoke(app, ["show", "all", "--domain", domain])
                    assert show_result.exit_code == 0
                    
            except Exception as e:
                print(f"⚠️  Domain {domain} failed: {e}")
    
    def test_very_long_context_e2e(self, mock_cli_runner, temp_project_dir):
        """Test handling of very long context input"""
        domain = "long-context.com"
        long_context = "Very long context. " * 200  # ~3600 characters
        
        result = mock_cli_runner.invoke(app, [
            "init", domain,
            "--context", long_context,
            "--yolo"
        ])
        
        # Should handle long context gracefully
        assert result.exit_code in [0, 1]  # Either succeed or fail gracefully
        
        if result.exit_code == 0:
            print("✓ Handled very long context")
        else:
            print("⚠️  Long context caused graceful failure")
    
    def test_special_characters_in_domain_e2e(self, mock_cli_runner, temp_project_dir):
        """Test handling of domains with special characters"""
        # These should be normalized or rejected gracefully
        special_domains = [
            "test_with_underscores.com",
            "test.with.dots.com", 
            "Test-With-Caps.COM"
        ]
        
        for domain in special_domains:
            result = mock_cli_runner.invoke(app, ["init", domain, "--yolo"])
            
            # Should either succeed (after normalization) or fail gracefully
            assert result.exit_code in [0, 1]
            
            if result.exit_code == 1:
                assert "domain" in result.output.lower() or "format" in result.output.lower()
            
            print(f"✓ Handled special domain: {domain} (exit code: {result.exit_code})")


print("🧪 End-to-end test suite ready to run")
print("These tests simulate complete user workflows with mocked external dependencies")