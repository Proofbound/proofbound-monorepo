#!/usr/bin/env python3
"""
Simple test runner script for the book generator API.
Run this script to execute all tests with proper environment setup.
"""

import os
import sys
import subprocess

def setup_test_environment():
    """Set up environment variables for testing."""
    os.environ['HAL9_TOKEN'] = 'test-token-for-testing'
    
def run_tests():
    """Run the test suite."""
    print("Setting up test environment...")
    setup_test_environment()
    
    print("Running unit tests...")
    try:
        # Run pytest on available test files
        try:
            result = subprocess.run([
                sys.executable, '-m', 'pytest', 
                'tests/test_simple_app.py',
                'tests/test_models.py',
                '-v', 
                '--tb=short',
                '--color=yes'
            ], check=True)
            print("✅ All available tests passed!")
            print("\nNote: Full app tests (test_app.py) are available in test_app_full.py.skip")
            print("To enable them, install WeasyPrint system dependencies (see CLAUDE.md)")
            return True
        except subprocess.CalledProcessError as e:
            print(f"❌ Tests failed with exit code {e.returncode}")
            return False
    except FileNotFoundError:
        print("❌ pytest not found. Please install testing dependencies:")
        print("pip install -r requirements.txt")
        return False

if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)