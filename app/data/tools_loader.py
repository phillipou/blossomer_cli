"""Tools database loader utility for GTM Advisor service."""

import csv
from pathlib import Path
from typing import List, Dict, Optional


class ToolsDatabase:
    """Utility class for loading and querying the GTM tools database."""
    
    def __init__(self, csv_path: Optional[Path] = None):
        """Initialize the tools database loader.
        
        Args:
            csv_path: Path to the tools CSV file. If None, uses default location.
        """
        if csv_path is None:
            csv_path = Path(__file__).parent / "gtm_tools.csv"
        
        self.csv_path = csv_path
        self._tools = None
    
    @property
    def tools(self) -> List[Dict[str, str]]:
        """Load and return all tools from the database."""
        if self._tools is None:
            self._tools = self._load_tools()
        return self._tools
    
    def _load_tools(self) -> List[Dict[str, str]]:
        """Load tools from CSV file."""
        if not self.csv_path.exists():
            raise FileNotFoundError(f"Tools database not found at {self.csv_path}")
        
        tools = []
        with open(self.csv_path, 'r', encoding='utf-8') as f:
            reader = csv.DictReader(f)
            for row in reader:
                # Clean and normalize the data
                tool = {
                    "name": row.get("Tool Name", "").strip(),
                    "description": row.get("Descriptions", "").strip(),
                    "website": row.get("Website", "").strip(),
                    "category": row.get("Category", "").strip(),
                    "phils_notes": row.get("Phil's Notes", "").strip(),
                    "recommended": row.get("Recommended", "").strip().upper() == "TRUE"
                }
                
                # Skip empty rows
                if tool["name"]:
                    tools.append(tool)
        
        return tools
    
    def get_tools_by_category(self, category: str) -> List[Dict[str, str]]:
        """Get all tools in a specific category.
        
        Args:
            category: The category to filter by (case-insensitive)
            
        Returns:
            List of tools matching the category
        """
        category_lower = category.lower()
        return [
            tool for tool in self.tools 
            if category_lower in tool["category"].lower()
        ]
    
    def get_recommended_tools(self) -> List[Dict[str, str]]:
        """Get all tools marked as recommended by Phil."""
        return [tool for tool in self.tools if tool["recommended"]]
    
    def get_recommended_by_category(self, category: str) -> List[Dict[str, str]]:
        """Get recommended tools in a specific category."""
        category_tools = self.get_tools_by_category(category)
        return [tool for tool in category_tools if tool["recommended"]]
    
    def get_tool_by_name(self, name: str) -> Optional[Dict[str, str]]:
        """Get a specific tool by name (case-insensitive)."""
        name_lower = name.lower()
        for tool in self.tools:
            if tool["name"].lower() == name_lower:
                return tool
        return None
    
    def get_categories(self) -> List[str]:
        """Get all unique categories in the database."""
        categories = set()
        for tool in self.tools:
            # Handle multi-category tools (comma-separated)
            tool_categories = [cat.strip() for cat in tool["category"].split(",")]
            categories.update(tool_categories)
        
        return sorted([cat for cat in categories if cat])


# Convenience function for quick access
def load_tools_database(csv_path: Optional[Path] = None) -> ToolsDatabase:
    """Load the tools database.
    
    Args:
        csv_path: Optional path to CSV file. Uses default if None.
        
    Returns:
        ToolsDatabase instance
    """
    return ToolsDatabase(csv_path)


# Example usage
if __name__ == "__main__":
    # Test the loader (if CSV exists)
    try:
        db = load_tools_database()
        print(f"Loaded {len(db.tools)} tools")
        print(f"Categories: {db.get_categories()}")
        print(f"Recommended tools: {len(db.get_recommended_tools())}")
    except FileNotFoundError:
        print("Tools database CSV not found. Please add tools_database.csv to this directory.")