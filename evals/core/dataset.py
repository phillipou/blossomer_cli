"""
Dataset management for evaluation system.
"""

import csv
import json
import random
from pathlib import Path
from typing import Dict, List, Any, Optional


class DatasetManager:
    """Manages test datasets for evaluation."""
    
    def __init__(self):
        self.prompts_dir = Path("evals/prompts")
    
    def load_test_cases(self, prompt_name: str, sample_size: int = 5, dataset_path: Optional[str] = None, context_type: Optional[str] = None) -> List[Dict[str, Any]]:
        """Load and sample test cases for a prompt."""
        if dataset_path:
            # Use custom dataset path (relative to evals/prompts/{prompt_name}/)
            base_path = self.prompts_dir / prompt_name
            data_path = base_path / dataset_path
        else:
            # Use default data.csv in prompt directory
            data_path = self.prompts_dir / prompt_name / "data.csv"
        
        if not data_path.exists():
            return []
        
        try:
            test_cases = []
            with open(data_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                for row in reader:
                    # Load website content if available
                    website_content = self._load_website_content(prompt_name, row)
                    if website_content:
                        row['website_content'] = website_content
                    
                    test_cases.append(row)
            
            # Filter by context type if specified
            if context_type:
                test_cases = [tc for tc in test_cases if tc.get('context_type') == context_type]
            
            # Sample test cases
            if sample_size and len(test_cases) > sample_size:
                return random.sample(test_cases, sample_size)
            
            return test_cases
            
        except Exception as e:
            print(f"Error loading test cases for {prompt_name}: {e}")
            return []
    
    def _load_website_content(self, prompt_name: str, test_case: Dict[str, Any]) -> Optional[str]:
        """Load website content for a test case if available."""
        content_dir = self.prompts_dir / prompt_name / "website_content"
        
        if not content_dir.exists():
            return None
        
        # Try to find content file based on URL or other identifier
        url = test_case.get('input_website_url', '')
        if not url:
            return None
        
        # Generate filename from URL (same logic as in existing code)
        import hashlib
        url_hash = hashlib.sha256(url.encode()).hexdigest()
        content_file = content_dir / f"{url_hash}.json"
        
        if content_file.exists():
            try:
                with open(content_file, 'r', encoding='utf-8') as f:
                    content_data = json.load(f)
                    return content_data.get('content', '')
            except Exception:
                pass
        
        # Fallback: look for any content file with similar name
        for content_file in content_dir.glob("*.json"):
            try:
                with open(content_file, 'r', encoding='utf-8') as f:
                    content_data = json.load(f)
                    if content_data.get('url') == url:
                        return content_data.get('content', '')
            except Exception:
                continue
        
        return None
    
    def get_dataset_stats(self, prompt_name: str) -> Dict[str, Any]:
        """Get statistics about a dataset."""
        data_path = self.prompts_dir / prompt_name / "data.csv"
        
        if not data_path.exists():
            return {"exists": False}
        
        try:
            with open(data_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                # Count by context type
                context_counts = {}
                for row in rows:
                    context_type = row.get('context_type', 'none')
                    context_counts[context_type] = context_counts.get(context_type, 0) + 1
                
                return {
                    "exists": True,
                    "total_cases": len(rows),
                    "context_distribution": context_counts,
                    "fields": list(rows[0].keys()) if rows else []
                }
                
        except Exception as e:
            return {"exists": False, "error": str(e)}
    
    def validate_dataset(self, prompt_name: str) -> List[str]:
        """Validate a dataset and return any issues."""
        errors = []
        data_path = self.prompts_dir / prompt_name / "data.csv"
        
        if not data_path.exists():
            errors.append(f"Dataset file not found: {data_path}")
            return errors
        
        try:
            with open(data_path, 'r', newline='', encoding='utf-8') as f:
                reader = csv.DictReader(f)
                rows = list(reader)
                
                if not rows:
                    errors.append("Dataset is empty")
                    return errors
                
                # Check required fields
                required_fields = ['input_website_url', 'context_type']
                for field in required_fields:
                    if field not in rows[0]:
                        errors.append(f"Missing required field: {field}")
                
                # Check for expected_company_name field (useful for validation)
                if 'expected_company_name' not in rows[0]:
                    errors.append("Missing expected_company_name field (useful for validation)")
                
                # Check for empty URLs
                for i, row in enumerate(rows):
                    if not row.get('input_website_url', '').strip():
                        errors.append(f"Row {i+1}: Empty input_website_url")
                
                # Check context types
                valid_context_types = ['none', 'valid', 'noise']
                for i, row in enumerate(rows):
                    context_type = row.get('context_type', '')
                    if context_type not in valid_context_types:
                        errors.append(f"Row {i+1}: Invalid context_type '{context_type}' (must be one of: {valid_context_types})")
                
        except Exception as e:
            errors.append(f"Error reading dataset: {e}")
        
        return errors
    
    def create_sample_dataset(self, prompt_name: str, size: int = 10) -> bool:
        """Create a sample dataset for a prompt (for testing purposes)."""
        data_path = self.prompts_dir / prompt_name / "data.csv"
        
        # Create directory if it doesn't exist
        data_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Sample data
        sample_data = [
            {
                'input_website_url': 'https://example.com',
                'context_type': 'none',
                'user_inputted_context': ''
            },
            {
                'input_website_url': 'https://test.com',
                'context_type': 'valid',
                'user_inputted_context': 'Looking for enterprise software solutions'
            },
            {
                'input_website_url': 'https://demo.com',
                'context_type': 'noise',
                'user_inputted_context': 'Random irrelevant text here'
            }
        ]
        
        try:
            with open(data_path, 'w', newline='', encoding='utf-8') as f:
                if sample_data:
                    writer = csv.DictWriter(f, fieldnames=sample_data[0].keys())
                    writer.writeheader()
                    
                    # Cycle through sample data to reach desired size
                    for i in range(size):
                        writer.writerow(sample_data[i % len(sample_data)])
            
            return True
            
        except Exception as e:
            print(f"Error creating sample dataset: {e}")
            return False