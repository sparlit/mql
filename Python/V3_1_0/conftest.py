"""
pytest configuration for the Python trading engine test suite.
Adds the Python/ directory to sys.path so modules can be imported directly.
"""
import sys
import os

# Ensure the Python/ directory is on sys.path for direct imports
sys.path.insert(0, os.path.dirname(__file__))