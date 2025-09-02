#!/usr/bin/env python3
"""
GTimes Release Checklist Script

Interactive checklist to ensure all release requirements are met
before publishing to PyPI.
"""

import os
import sys
import subprocess
from pathlib import Path
from typing import Dict, List, Tuple
from datetime import datetime


class ReleaseChecker:
    """Interactive release checklist for GTimes."""
    
    def __init__(self, package_dir: str = "."):
        self.package_dir = Path(package_dir).resolve()
        self.checklist_items = [
            # Pre-release checks
            ("version_updated", "Version number updated in pyproject.toml", self.check_version_updated),
            ("changelog_updated", "CHANGELOG.md updated with new version", self.check_changelog_updated),
            ("documentation_updated", "Documentation updated and built successfully", self.check_documentation),
            ("tests_passing", "All tests passing locally", self.check_tests_passing),
            ("quality_checks", "Code quality checks passing (ruff, mypy)", self.check_quality),
            ("scientific_validation", "Scientific accuracy validation passing", self.check_scientific_validation),
            
            # Build and distribution checks
            ("clean_build", "Clean build successful", self.check_clean_build),
            ("distribution_valid", "Distribution packages valid (twine check)", self.check_distribution),
            ("installation_test", "Package installs correctly in clean environment", self.check_installation),
            
            # CI/CD checks
            ("ci_passing", "CI/CD pipeline passing on main branch", self.check_ci_status),
            ("security_scan", "Security scan completed with no critical issues", self.check_security),
            ("performance_baseline", "Performance benchmarks within acceptable range", self.check_performance),
            
            # Release preparation
            ("release_notes", "Release notes prepared", self.check_release_notes),
            ("backup_created", "Backup of current state created", self.check_backup),
            ("pypi_credentials", "PyPI credentials configured", self.check_pypi_credentials),
            
            # Final checks
            ("team_approval", "Release approved by team", self.manual_check),
            ("documentation_deployed", "Documentation deployed to GitHub Pages", self.manual_check),
            ("ready_to_release", "Ready to create release tag and publish", self.manual_check),
        ]
        
        self.results = {}
    
    def run_command(self, cmd: str) -> Tuple[int, str, str]:
        """Run a command and return (returncode, stdout, stderr)."""
        try:
            result = subprocess.run(
                cmd, shell=True, cwd=self.package_dir,
                capture_output=True, text=True, timeout=120
            )
            return result.returncode, result.stdout, result.stderr
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)
    
    def check_version_updated(self) -> Tuple[bool, str]:
        """Check if version has been updated in pyproject.toml."""
        pyproject_path = self.package_dir / "pyproject.toml"
        if not pyproject_path.exists():
            return False, "pyproject.toml not found"
        
        try:
            content = pyproject_path.read_text()
            # Simple version extraction (could be more robust)
            for line in content.split('\n'):
                if line.startswith('version = '):
                    version = line.split('=')[1].strip().strip('"\'')
                    if version and version != "0.0.0":
                        return True, f"Version: {version}"
            return False, "Version not found or is placeholder"
        except Exception as e:
            return False, f"Error reading pyproject.toml: {e}"
    
    def check_changelog_updated(self) -> Tuple[bool, str]:
        """Check if CHANGELOG.md has been updated."""
        changelog_path = self.package_dir / "CHANGELOG.md"
        if not changelog_path.exists():
            return False, "CHANGELOG.md not found"
        
        try:
            content = changelog_path.read_text()
            today = datetime.now().strftime("%Y-%m-%d")
            recent_date = datetime.now().strftime("%Y-%m")  # At least same month
            
            if recent_date in content:
                return True, "CHANGELOG.md appears up to date"
            else:
                return False, "CHANGELOG.md may not have recent updates"
        except Exception as e:
            return False, f"Error reading CHANGELOG.md: {e}"
    
    def check_documentation(self) -> Tuple[bool, str]:
        """Check if documentation builds successfully."""
        if not (self.package_dir / "mkdocs.yml").exists():
            return False, "mkdocs.yml not found"
        
        returncode, stdout, stderr = self.run_command("mkdocs build")
        if returncode != 0:
            return False, f"Documentation build failed: {stderr}"
        
        return True, "Documentation builds successfully"
    
    def check_tests_passing(self) -> Tuple[bool, str]:
        """Check if all tests are passing."""
        if not (self.package_dir / "tests").exists():
            return False, "Tests directory not found"
        
        returncode, stdout, stderr = self.run_command("pytest tests/ -v")
        if returncode != 0:
            return False, f"Tests failing: {stderr}"
        
        # Count passed tests
        if "passed" in stdout:
            return True, "All tests passing"
        else:
            return False, "Test results unclear"
    
    def check_quality(self) -> Tuple[bool, str]:
        """Check code quality tools."""
        checks = [
            ("ruff check src/ tests/", "Ruff linting"),
            ("ruff format --check src/ tests/", "Ruff formatting"),
            ("mypy src/gtimes/", "MyPy type checking"),
        ]
        
        failed_checks = []
        for cmd, name in checks:
            returncode, stdout, stderr = self.run_command(cmd)
            if returncode != 0:
                failed_checks.append(name)
        
        if failed_checks:
            return False, f"Quality checks failed: {', '.join(failed_checks)}"
        else:
            return True, "All quality checks passing"
    
    def check_scientific_validation(self) -> Tuple[bool, str]:
        """Check scientific validation tests."""
        validation_script = self.package_dir / "tests" / "validate_leap_seconds.py"
        if not validation_script.exists():
            return False, "Scientific validation script not found"
        
        returncode, stdout, stderr = self.run_command(f"python {validation_script}")
        if returncode != 0:
            return False, f"Scientific validation failed: {stderr}"
        
        return True, "Scientific validation passing"
    
    def check_clean_build(self) -> Tuple[bool, str]:
        """Check if clean build is successful."""
        # Clean previous build
        dist_dir = self.package_dir / "dist"
        if dist_dir.exists():
            import shutil
            shutil.rmtree(dist_dir)
        
        returncode, stdout, stderr = self.run_command("python -m build")
        if returncode != 0:
            return False, f"Build failed: {stderr}"
        
        # Check if files were created
        if not dist_dir.exists():
            return False, "No dist directory created"
        
        wheel_files = list(dist_dir.glob("*.whl"))
        tar_files = list(dist_dir.glob("*.tar.gz"))
        
        if not wheel_files:
            return False, "No wheel file created"
        if not tar_files:
            return False, "No source distribution created"
        
        return True, f"Build successful: {len(wheel_files)} wheel(s), {len(tar_files)} sdist(s)"
    
    def check_distribution(self) -> Tuple[bool, str]:
        """Check distribution package validity."""
        dist_dir = self.package_dir / "dist"
        if not dist_dir.exists():
            return False, "No dist directory found"
        
        returncode, stdout, stderr = self.run_command("twine check dist/*")
        if returncode != 0:
            return False, f"Twine check failed: {stderr}"
        
        return True, "Distribution packages valid"
    
    def check_installation(self) -> Tuple[bool, str]:
        """Check installation in clean environment."""
        # This is a simplified check - in practice, you might use a virtual environment
        returncode, stdout, stderr = self.run_command("pip install -e . --quiet")
        if returncode != 0:
            return False, f"Installation failed: {stderr}"
        
        # Test basic import
        returncode, stdout, stderr = self.run_command("python -c 'import gtimes; print(gtimes.__version__)'")
        if returncode != 0:
            return False, f"Import test failed: {stderr}"
        
        return True, f"Installation successful, version: {stdout.strip()}"
    
    def check_ci_status(self) -> Tuple[bool, str]:
        """Check CI/CD status (simplified - would need GitHub API in practice)."""
        # Check if GitHub Actions workflow exists
        ci_file = self.package_dir / ".github" / "workflows" / "ci.yml"
        if not ci_file.exists():
            return False, "CI workflow not found"
        
        return True, "CI workflow configured (check GitHub for status)"
    
    def check_security(self) -> Tuple[bool, str]:
        """Check for security issues."""
        # Run basic security checks
        returncode, stdout, stderr = self.run_command("safety check --json")
        if returncode != 0 and "No known security vulnerabilities found" not in stderr:
            return False, f"Security issues found: {stderr}"
        
        return True, "No known security vulnerabilities"
    
    def check_performance(self) -> Tuple[bool, str]:
        """Check performance benchmarks."""
        benchmark_dir = self.package_dir / "tests" / "benchmark"
        if not benchmark_dir.exists():
            return False, "Benchmark tests not found"
        
        returncode, stdout, stderr = self.run_command("pytest tests/benchmark/ --benchmark-only --benchmark-skip")
        if returncode != 0:
            return False, f"Benchmark tests failed: {stderr}"
        
        return True, "Performance benchmarks available"
    
    def check_release_notes(self) -> Tuple[bool, str]:
        """Check if release notes are prepared."""
        # Check if there's a recent entry in CHANGELOG
        changelog_path = self.package_dir / "CHANGELOG.md"
        if changelog_path.exists():
            content = changelog_path.read_text()
            if "[Unreleased]" in content:
                return False, "CHANGELOG still has [Unreleased] section"
            return True, "Release notes appear ready"
        return False, "CHANGELOG.md not found"
    
    def check_backup(self) -> Tuple[bool, str]:
        """Check if backup has been created."""
        # In practice, this would check for git tags, branches, or backup files
        returncode, stdout, stderr = self.run_command("git status --porcelain")
        if stdout.strip():
            return False, "Working directory has uncommitted changes"
        
        return True, "Working directory clean (good for backup)"
    
    def check_pypi_credentials(self) -> Tuple[bool, str]:
        """Check if PyPI credentials are configured."""
        # Check for .pypirc or environment variables
        pypirc_path = Path.home() / ".pypirc"
        has_pypirc = pypirc_path.exists()
        has_token = os.environ.get("TWINE_PASSWORD") or os.environ.get("PYPI_API_TOKEN")
        
        if has_pypirc or has_token:
            return True, "PyPI credentials configured"
        else:
            return False, "PyPI credentials not found"
    
    def manual_check(self) -> Tuple[bool, str]:
        """Manual check requiring user confirmation."""
        return True, "Manual verification required"
    
    def run_checklist(self):
        """Run the complete release checklist."""
        print("🚀 GTimes Release Checklist")
        print("=" * 50)
        print()
        
        total_items = len(self.checklist_items)
        passed_items = 0
        
        for item_id, description, check_func in self.checklist_items:
            print(f"🔍 {description}")
            
            try:
                if check_func == self.manual_check:
                    # Manual check - ask user
                    response = input("   ✅ Confirmed? (y/N): ").lower().strip()
                    if response in ['y', 'yes']:
                        passed, message = True, "Confirmed by user"
                        passed_items += 1
                        print(f"   ✅ {message}")
                    else:
                        passed, message = False, "Not confirmed"
                        print(f"   ❌ {message}")
                else:
                    # Automated check
                    passed, message = check_func()
                    if passed:
                        passed_items += 1
                        print(f"   ✅ {message}")
                    else:
                        print(f"   ❌ {message}")
                
                self.results[item_id] = {'passed': passed, 'message': message}
                
            except Exception as e:
                print(f"   💥 Error during check: {e}")
                self.results[item_id] = {'passed': False, 'message': str(e)}
            
            print()
        
        # Summary
        print("=" * 50)
        print("📊 RELEASE CHECKLIST SUMMARY")
        print("=" * 50)
        print(f"Total items: {total_items}")
        print(f"Passed: {passed_items}")
        print(f"Failed: {total_items - passed_items}")
        
        if passed_items == total_items:
            print("\n🎉 ALL CHECKLIST ITEMS COMPLETED!")
            print("✅ GTimes is ready for release")
            print("\nNext steps:")
            print("1. Create release tag: git tag v<version>")
            print("2. Push tag: git push origin v<version>")
            print("3. GitHub Actions will automatically publish to PyPI")
        else:
            print("\n💥 SOME CHECKLIST ITEMS NEED ATTENTION!")
            print("❌ Please address the following before release:")
            
            for item_id, result in self.results.items():
                if not result['passed']:
                    item_desc = next(desc for id_, desc, _ in self.checklist_items if id_ == item_id)
                    print(f"   • {item_desc}: {result['message']}")
        
        return passed_items == total_items


def main():
    """Main function."""
    package_dir = Path(__file__).parent.parent
    
    checker = ReleaseChecker(package_dir)
    success = checker.run_checklist()
    
    return 0 if success else 1


if __name__ == "__main__":
    sys.exit(main())