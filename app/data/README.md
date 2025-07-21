# Data Directory

This directory contains static data files used by the GTM CLI services.

## Files

- `gtm_tools.csv` - Master database of GTM tools with categories, descriptions, and Phil's recommendations
- `tools_loader.py` - Utility for loading and parsing the tools database

## Tools Database Schema

The `gtm_tools.csv` file should have these columns:
- `Tool Name` - Name of the tool
- `Descriptions` - Brief description of what the tool does  
- `Website` - Tool's website URL
- `Category` - Tool category (CRM, Email Outreach, LinkedIn Outreach, etc.)
- `Phil's Notes` - Phil's specific notes about the tool
- `Recommended` - TRUE if Phil recommends this tool, otherwise empty

## Usage

The tools database is loaded by the GTM Advisor service to provide personalized tool recommendations based on the company's GTM strategy and requirements.