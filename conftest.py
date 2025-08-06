"""
# conftest.py ensures project root is on sys.path for pytest
"""

import sys
import os

# Prepend project root so pytest can import subpackage tests correctly
sys.path.insert(0, os.getcwd())
