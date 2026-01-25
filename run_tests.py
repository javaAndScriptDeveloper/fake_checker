#!/usr/bin/env python3
"""Test runner with error handling."""
import sys
import pytest
from pathlib import Path


def run_tests():
    """Run tests and return exit code."""
    test_dir = Path(__file__).parent / "tests"
    
    if not test_dir.exists():
        print("❌ Tests directory not found!")
        return 1
    
    # Run pytest
    exit_code = pytest.main([
        str(test_dir),
        "-v",
        "--tb=short",
        "--strict-markers",
        "--disable-warnings",
    ])
    
    return exit_code


if __name__ == "__main__":
    sys.exit(run_tests())
