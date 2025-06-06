
#!/usr/bin/env python3
"""
Test runner for O Estúdio application.
Run this script to execute all unit tests.
"""

import sys
import os
import pytest
import subprocess

# Add the backend directory to Python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

def run_tests():
    """Run all unit tests with coverage reporting."""
    
    print("🧪 Running O Estúdio Unit Tests...")
    print("=" * 50)
    
    # Change to the backend directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Test discovery and execution
    test_args = [
        'unit tests/',  # Test directory
        '-v',  # Verbose output
        '--tb=short',  # Short traceback format
        '--color=yes',  # Colored output
        '--durations=10',  # Show 10 slowest tests
    ]
    
    try:
        # Run tests
        exit_code = pytest.main(test_args)
        
        if exit_code == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Tests failed with exit code: {exit_code}")
            
        return exit_code
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


def run_specific_test(test_file):
    """Run a specific test file."""
    print(f"🧪 Running specific test: {test_file}")
    print("=" * 50)
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    test_args = [
        f'unit tests/{test_file}',
        '-v',
        '--tb=short',
        '--color=yes'
    ]
    
    try:
        exit_code = pytest.main(test_args)
        return exit_code
    except Exception as e:
        print(f"❌ Error running test: {e}")
        return 1


def run_tests_with_coverage():
    """Run tests with coverage reporting."""
    print("🧪 Running O Estúdio Unit Tests with Coverage...")
    print("=" * 60)
    
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    try:
        # Install pytest-cov if not available
        subprocess.run(['pip', 'install', 'pytest-cov'], 
                      capture_output=True, check=False)
        
        test_args = [
            'unit tests/',
            '--cov=.',
            '--cov-report=term-missing',
            '--cov-report=html:htmlcov',
            '-v',
            '--tb=short',
            '--color=yes'
        ]
        
        exit_code = pytest.main(test_args)
        
        if exit_code == 0:
            print("\n✅ All tests passed!")
            print("📊 Coverage report generated in 'htmlcov/' directory")
        else:
            print(f"\n❌ Tests failed with exit code: {exit_code}")
            
        return exit_code
        
    except Exception as e:
        print(f"❌ Error running tests with coverage: {e}")
        return 1


if __name__ == '__main__':
    import argparse
    
    parser = argparse.ArgumentParser(description='Run O Estúdio unit tests')
    parser.add_argument('--coverage', action='store_true', 
                       help='Run tests with coverage reporting')
    parser.add_argument('--file', type=str, 
                       help='Run specific test file (e.g., test_models.py)')
    
    args = parser.parse_args()
    
    if args.file:
        exit_code = run_specific_test(args.file)
    elif args.coverage:
        exit_code = run_tests_with_coverage()
    else:
        exit_code = run_tests()
    
    sys.exit(exit_code)
