#!/usr/bin/env python3
"""Simple test runner for gtimes library."""

import subprocess
import sys
from pathlib import Path


def run_tests():
    """Run the test suite with appropriate options."""
    
    # Ensure we're in the right directory
    project_root = Path(__file__).parent
    
    print("🧪 Running gtimes test suite...")
    print(f"📁 Project root: {project_root}")
    
    # Basic test command
    test_cmd = [
        sys.executable, "-m", "pytest", 
        "tests/",
        "-v",
        "--tb=short",
        "-x",  # Stop on first failure for development
    ]
    
    try:
        result = subprocess.run(
            test_cmd, 
            cwd=project_root,
            capture_output=False,
            text=True
        )
        
        if result.returncode == 0:
            print("\n✅ All tests passed!")
        else:
            print(f"\n❌ Tests failed with return code: {result.returncode}")
            
        return result.returncode
        
    except Exception as e:
        print(f"❌ Error running tests: {e}")
        return 1


def run_quality_checks():
    """Run code quality checks."""
    
    print("\n🔍 Running code quality checks...")
    
    # Check if tools are available
    checks = [
        (["ruff", "check", "src/"], "Ruff linting"),
        (["black", "--check", "src/"], "Black formatting"),
        (["mypy", "src/gtimes/"], "MyPy type checking"),
    ]
    
    all_passed = True
    
    for cmd, description in checks:
        print(f"\n📋 {description}...")
        try:
            result = subprocess.run(
                cmd,
                capture_output=True,
                text=True,
                timeout=30
            )
            
            if result.returncode == 0:
                print(f"✅ {description} passed")
            else:
                print(f"❌ {description} failed:")
                print(result.stdout)
                print(result.stderr)
                all_passed = False
                
        except FileNotFoundError:
            print(f"⚠️  {cmd[0]} not found, skipping {description}")
        except Exception as e:
            print(f"❌ Error running {description}: {e}")
            all_passed = False
    
    return all_passed


if __name__ == "__main__":
    import argparse
    
    parser = argparse.ArgumentParser(description="Run gtimes tests and checks")
    parser.add_argument("--quality", action="store_true", help="Run quality checks too")
    parser.add_argument("--slow", action="store_true", help="Run slow tests")
    
    args = parser.parse_args()
    
    exit_code = 0
    
    # Run tests
    if args.slow:
        print("🐌 Including slow tests...")
        test_exit_code = subprocess.run([
            sys.executable, "-m", "pytest", "tests/", "-v", "--runslow"
        ]).returncode
    else:
        test_exit_code = run_tests()
    
    exit_code = max(exit_code, test_exit_code)
    
    # Run quality checks if requested
    if args.quality:
        quality_passed = run_quality_checks()
        if not quality_passed:
            exit_code = 1
    
    print(f"\n🏁 Complete! Exit code: {exit_code}")
    sys.exit(exit_code)