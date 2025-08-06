"""
# conftest.py ensures project root is on sys.path for pytest
"""

import os
import sys

# Prepend project root so pytest can import subpackage tests correctly
sys.path.insert(0, os.getcwd())
