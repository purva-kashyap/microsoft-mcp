#!/usr/bin/env python3
"""
Run the Microsoft MCP server without installing the package.
"""
import os
import sys

# Add src directory to Python path
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

# Now import and run
from microsoft_mcp.server import main

if __name__ == "__main__":
    main()
