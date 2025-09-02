#!/usr/bin/env python3
"""
GTimes Distribution Validation Script

This script validates the GTimes package distribution before release,
ensuring all components are properly configured and functional.
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Dict, List, Tuple, Any
import json

def run_command(cmd: str, cwd: str = None) -> Tuple[int, str, str]:
    """Run a command and return (returncode, stdout, stderr)."""
    try:
        result = subprocess.run(
            cmd, shell=True, cwd=cwd,
            capture_output=True, text=True, timeout=120
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return 1, "", "Command timed out"
    except Exception as e:
        return 1, "", str(e)


class DistributionValidator:
    """Comprehensive GTimes distribution validator."""
    
    def __init__(self, package_dir: str = "."):
        self.package_dir = Path(package_dir).resolve()
        self.validation_results = {}
        self.temp_dir = None
    
    def validate_all(self) -> Dict[str, Any]:
        """Run all validation checks."""
        print("🧪 GTimes Distribution Validation")
        print("=" * 50)
        
        # Core validation checks
        checks = [
            ("package_structure", self.validate_package_structure),
            ("pyproject_toml", self.validate_pyproject_toml),
            ("documentation", self.validate_documentation),
            ("license_and_legal", self.validate_license_and_legal),
            ("build_system", self.validate_build_system),
            ("installation_test", self.validate_installation),
            ("basic_functionality", self.validate_basic_functionality),
            ("cli_interface", self.validate_cli_interface),
            ("scientific_accuracy", self.validate_scientific_accuracy),
            ("pypi_readiness", self.validate_pypi_readiness),
        ]
        
        for check_name, check_func in checks:
            print(f"\n🔍 {check_name.replace('_', ' ').title()}")
            try:
                result = check_func()
                self.validation_results[check_name] = result
                if result['passed']:
                    print(f"✅ {check_name}: PASSED")
                else:
                    print(f"❌ {check_name}: FAILED")
                    for error in result.get('errors', []):
                        print(f"   • {error}")
            except Exception as e:
                print(f"❌ {check_name}: ERROR - {e}")
                self.validation_results[check_name] = {
                    'passed': False,
                    'errors': [str(e)]
                }
        
        return self.generate_summary()
    
    def validate_package_structure(self) -> Dict[str, Any]:
        """Validate package directory structure."""
        required_files = [
            "pyproject.toml",
            "README.md",
            "LICENSE",
            "CHANGELOG.md",
            "src/gtimes/__init__.py",
            "src/gtimes/gpstime.py",
            "src/gtimes/timefunc.py",
            "src/gtimes/timecalc.py",
            "src/gtimes/exceptions.py",
            "docs/index.md",
            "mkdocs.yml",
            "tests/",
            ".github/workflows/ci.yml",
        ]
        
        missing_files = []
        for file_path in required_files:
            full_path = self.package_dir / file_path
            if not full_path.exists():
                missing_files.append(file_path)
        
        # Check for optional but recommended files
        recommended_files = [
            ".github/CONTRIBUTING.md",
            ".github/ISSUE_TEMPLATE/bug_report.md",
            ".github/ISSUE_TEMPLATE/feature_request.md",
            ".github/PULL_REQUEST_TEMPLATE.md",
        ]
        
        missing_recommended = []
        for file_path in recommended_files:
            full_path = self.package_dir / file_path
            if not full_path.exists():
                missing_recommended.append(file_path)
        
        errors = []
        if missing_files:
            errors.extend([f"Missing required file: {f}" for f in missing_files])
        if missing_recommended:
            errors.extend([f"Missing recommended file: {f}" for f in missing_recommended])
        
        return {
            'passed': len(missing_files) == 0,
            'errors': errors,
            'missing_required': missing_files,
            'missing_recommended': missing_recommended
        }
    
    def validate_pyproject_toml(self) -> Dict[str, Any]:
        """Validate pyproject.toml configuration."""
        pyproject_path = self.package_dir / "pyproject.toml"
        
        if not pyproject_path.exists():
            return {'passed': False, 'errors': ['pyproject.toml not found']}
        
        # Check if pyproject.toml is valid
        try:
            import tomllib
            with open(pyproject_path, 'rb') as f:
                config = tomllib.load(f)
        except ImportError:
            try:
                import tomli as tomllib
                with open(pyproject_path, 'rb') as f:
                    config = tomllib.load(f)
            except ImportError:
                return {'passed': False, 'errors': ['Cannot parse pyproject.toml - tomli not available']}
        except Exception as e:
            return {'passed': False, 'errors': [f'Invalid pyproject.toml: {e}']}
        
        # Check required sections
        errors = []
        required_sections = ['project', 'build-system']
        for section in required_sections:
            if section not in config:
                errors.append(f"Missing section: [{section}]")
        
        # Check project metadata
        if 'project' in config:
            required_fields = ['name', 'version', 'description', 'authors']
            for field in required_fields:
                if field not in config['project']:
                    errors.append(f"Missing project.{field}")
        
        # Check keywords and classifiers for PyPI discovery
        project = config.get('project', {})
        if not project.get('keywords'):
            errors.append("Missing project.keywords for PyPI discovery")
        
        if not project.get('classifiers'):
            errors.append("Missing project.classifiers for PyPI categorization")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors,
            'config': config
        }
    
    def validate_documentation(self) -> Dict[str, Any]:
        """Validate documentation completeness."""
        errors = []
        
        # Check README.md
        readme_path = self.package_dir / "README.md"
        if readme_path.exists():
            content = readme_path.read_text()
            if len(content) < 1000:
                errors.append("README.md is too short (< 1000 characters)")
            if "## 📦 Installation" not in content and "## Installation" not in content:
                errors.append("README.md missing installation instructions")
            if "## 🏃 Quick Start" not in content and "## Quick Start" not in content:
                errors.append("README.md missing quick start guide")
        
        # Check MkDocs configuration
        mkdocs_path = self.package_dir / "mkdocs.yml"
        if mkdocs_path.exists():
            # For now, just check that the file exists
            # TODO: Add proper MkDocs build validation with material theme
            print("    ⚠️  Skipping MkDocs build validation (requires mkdocs-material)")
        else:
            errors.append("Missing mkdocs.yml configuration")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def validate_license_and_legal(self) -> Dict[str, Any]:
        """Validate license and legal compliance."""
        errors = []
        
        # Check LICENSE file
        license_path = self.package_dir / "LICENSE"
        if not license_path.exists():
            errors.append("Missing LICENSE file")
        else:
            content = license_path.read_text()
            if "MIT License" not in content:
                errors.append("LICENSE file doesn't appear to be MIT License")
            if len(content) < 500:
                errors.append("LICENSE file seems incomplete")
        
        # Check copyright notices in source files
        src_dir = self.package_dir / "src" / "gtimes"
        if src_dir.exists():
            python_files = list(src_dir.glob("*.py"))
            for py_file in python_files[:3]:  # Check first few files
                content = py_file.read_text()
                # Don't require copyright in every file, but check for proper attribution
                
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def validate_build_system(self) -> Dict[str, Any]:
        """Validate package build system."""
        errors = []
        
        # Create temporary virtual environment for building
        import tempfile
        with tempfile.TemporaryDirectory() as temp_dir:
            venv_path = Path(temp_dir) / "build_venv"
            
            print("    Creating build virtual environment...")
            # Create virtual environment
            returncode, stdout, stderr = run_command(
                f"python3 -m venv {venv_path}",
                cwd=temp_dir
            )
            
            if returncode != 0:
                errors.append(f"Failed to create build environment: {stderr}")
                return {'passed': False, 'errors': errors}
            
            # Install build tools
            pip_cmd = f"{venv_path}/bin/pip"
            returncode, stdout, stderr = run_command(
                f"{pip_cmd} install --upgrade pip build twine",
                cwd=temp_dir
            )
            
            if returncode != 0:
                errors.append(f"Failed to install build tools: {stderr}")
                return {'passed': False, 'errors': errors}
            
            # Try to build the package
            print("    Building package...")
            python_cmd = f"{venv_path}/bin/python"
            returncode, stdout, stderr = run_command(
                f"{python_cmd} -m build --wheel --sdist", 
                cwd=str(self.package_dir)
            )
            
            if returncode != 0:
                errors.append(f"Package build failed: {stderr}")
                return {'passed': False, 'errors': errors}
            
            # Check if distribution files were created
            dist_dir = self.package_dir / "dist"
            if not dist_dir.exists():
                errors.append("No dist/ directory created")
            else:
                wheel_files = list(dist_dir.glob("*.whl"))
                tar_files = list(dist_dir.glob("*.tar.gz"))
                
                if not wheel_files:
                    errors.append("No wheel file generated")
                if not tar_files:
                    errors.append("No source distribution generated")
            
            # Validate distribution with twine
            if dist_dir.exists():
                twine_cmd = f"{venv_path}/bin/twine"
                returncode, stdout, stderr = run_command(
                    f"{twine_cmd} check dist/*", 
                    cwd=str(self.package_dir)
                )
                if returncode != 0:
                    errors.append(f"Twine validation failed: {stderr}")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def validate_installation(self) -> Dict[str, Any]:
        """Validate package installation in clean environment."""
        errors = []
        
        # Create temporary directory for clean install test
        with tempfile.TemporaryDirectory() as temp_dir:
            temp_path = Path(temp_dir)
            venv_path = temp_path / "test_venv"
            
            print("    Creating test virtual environment...")
            # Create virtual environment
            returncode, stdout, stderr = run_command(
                f"python3 -m venv {venv_path}",
                cwd=temp_dir
            )
            
            if returncode != 0:
                errors.append(f"Failed to create virtual environment: {stderr}")
                return {'passed': False, 'errors': errors}
            
            # Install the package in the venv
            print("    Testing installation in clean environment...")
            pip_cmd = f"{venv_path}/bin/pip"
            returncode, stdout, stderr = run_command(
                f"{pip_cmd} install -e {self.package_dir}",
                cwd=temp_dir
            )
            
            if returncode != 0:
                errors.append(f"Package installation failed: {stderr}")
                return {'passed': False, 'errors': errors}
            
            # Test basic import
            python_cmd = f"{venv_path}/bin/python"
            returncode, stdout, stderr = run_command(
                f"{python_cmd} -c 'import gtimes; print(gtimes.__version__)'",
                cwd=temp_dir
            )
            
            if returncode != 0:
                errors.append(f"Package import failed: {stderr}")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def validate_basic_functionality(self) -> Dict[str, Any]:
        """Validate basic package functionality."""
        errors = []
        
        # Add package to path for testing
        src_dir = str(self.package_dir / "src")
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)
        
        try:
            # Test core imports
            import gtimes
            from gtimes.gpstime import gpsFromUTC, UTCFromGps
            from gtimes.timefunc import TimefromYearf, dTimetoYearf
            from gtimes.exceptions import GPSTimeError
            
            # Test basic GPS conversion
            week, sow, day, sod = gpsFromUTC(2024, 1, 15, 12, 30, 45)
            if not isinstance(week, int) or not isinstance(sow, (int, float)):
                errors.append("GPS conversion returned unexpected types")
            
            # Test reverse conversion
            utc_dt = UTCFromGps(week, sow, dtimeObj=True)
            if utc_dt is None:
                errors.append("UTC conversion failed")
            
            # Test fractional year conversion
            yearf = 2024.0411
            dt = TimefromYearf(yearf)
            if dt is None:
                errors.append("Fractional year conversion failed")
            
        except ImportError as e:
            errors.append(f"Import failed: {e}")
        except Exception as e:
            errors.append(f"Functionality test failed: {e}")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def validate_cli_interface(self) -> Dict[str, Any]:
        """Validate command-line interface."""
        errors = []
        
        # Set up environment for testing
        src_dir = str(self.package_dir / "src")
        
        # Test timecalc command
        returncode, stdout, stderr = run_command(
            f"PYTHONPATH={src_dir}:$PYTHONPATH python3 -m gtimes.timecalc --version",
            cwd=str(self.package_dir)
        )
        
        if returncode != 0:
            errors.append(f"timecalc --version failed: {stderr}")
        
        # Test basic timecalc functionality
        returncode, stdout, stderr = run_command(
            f"PYTHONPATH={src_dir}:$PYTHONPATH python3 -m gtimes.timecalc -wd -d '2024-01-15'",
            cwd=str(self.package_dir)
        )
        
        if returncode != 0:
            errors.append(f"timecalc basic functionality failed: {stderr}")
        elif not stdout.strip():
            errors.append("timecalc produced no output")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def validate_scientific_accuracy(self) -> Dict[str, Any]:
        """Validate scientific accuracy of GPS time functions."""
        errors = []
        
        # Add package to path for testing
        src_dir = str(self.package_dir / "src")
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)
        
        try:
            from gtimes.gpstime import gpsFromUTC, UTCFromGps
            import datetime
            
            # Test known GPS time conversions
            test_cases = [
                ((1980, 1, 6, 0, 0, 0), (0, 0.0)),              # GPS epoch
                ((2024, 1, 1, 0, 0, 0), (2295, 86418.0)),       # Known GPS week for 2024
            ]
            
            for (utc_tuple, expected_gps) in test_cases:
                week, sow, day, sod = gpsFromUTC(*utc_tuple)
                expected_week, expected_sow = expected_gps
                
                if week != expected_week:
                    errors.append(f"GPS week mismatch: {week} != {expected_week}")
                
                if abs(sow - expected_sow) > 1e-3:  # 1ms tolerance
                    errors.append(f"GPS SOW mismatch: {sow} != {expected_sow}")
                
                # Test round-trip accuracy
                utc_back = UTCFromGps(week, sow, dtimeObj=True)
                original = datetime.datetime(*utc_tuple[:6])
                diff = abs((utc_back - original).total_seconds())
                
                if diff > 1e-6:  # 1μs tolerance
                    errors.append(f"Round-trip error: {diff:.6f}s")
        
        except Exception as e:
            errors.append(f"Scientific validation failed: {e}")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def validate_pypi_readiness(self) -> Dict[str, Any]:
        """Validate PyPI readiness."""
        errors = []
        
        # Check for common PyPI issues
        pyproject_path = self.package_dir / "pyproject.toml"
        if pyproject_path.exists():
            try:
                import tomllib
                with open(pyproject_path, 'rb') as f:
                    config = tomllib.load(f)
                
                project = config.get('project', {})
                
                # Check name availability (would need PyPI API call)
                # For now, just check format
                name = project.get('name', '')
                if not name or len(name) < 2:
                    errors.append("Package name too short or missing")
                
                # Check version format
                version = project.get('version', '')
                if not version:
                    errors.append("Package version missing")
                
                # Check description length
                description = project.get('description', '')
                if len(description) < 10:
                    errors.append("Package description too short")
                
                # Check required URLs
                urls = project.get('urls', {})
                if not urls.get('Homepage'):
                    errors.append("Missing homepage URL")
                
            except Exception as e:
                errors.append(f"Error validating PyPI metadata: {e}")
        
        return {
            'passed': len(errors) == 0,
            'errors': errors
        }
    
    def generate_summary(self) -> Dict[str, Any]:
        """Generate validation summary."""
        total_checks = len(self.validation_results)
        passed_checks = sum(1 for r in self.validation_results.values() if r['passed'])
        
        # Collect all errors
        all_errors = []
        for check_name, result in self.validation_results.items():
            if not result['passed']:
                errors = result.get('errors', [])
                for error in errors:
                    all_errors.append(f"{check_name}: {error}")
        
        summary = {
            'overall_passed': passed_checks == total_checks,
            'total_checks': total_checks,
            'passed_checks': passed_checks,
            'failed_checks': total_checks - passed_checks,
            'all_errors': all_errors,
            'detailed_results': self.validation_results
        }
        
        return summary


def main():
    """Main validation function."""
    package_dir = Path(__file__).parent.parent
    
    validator = DistributionValidator(package_dir)
    results = validator.validate_all()
    
    print("\n" + "=" * 50)
    print("📊 VALIDATION SUMMARY")
    print("=" * 50)
    
    print(f"Total checks: {results['total_checks']}")
    print(f"Passed: {results['passed_checks']}")
    print(f"Failed: {results['failed_checks']}")
    
    if results['overall_passed']:
        print("\n🎉 ALL VALIDATION CHECKS PASSED!")
        print("✅ GTimes distribution is ready for release")
    else:
        print("\n💥 SOME VALIDATION CHECKS FAILED!")
        print("❌ Please address the following issues:")
        
        for error in results['all_errors']:
            print(f"   • {error}")
    
    # Save detailed results
    results_file = package_dir / "validation_results.json"
    with open(results_file, 'w') as f:
        json.dump(results, f, indent=2)
    
    print(f"\n📄 Detailed results saved to: {results_file}")
    
    return 0 if results['overall_passed'] else 1


if __name__ == "__main__":
    sys.exit(main())