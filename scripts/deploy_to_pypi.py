#!/usr/bin/env python3
"""
GTimes PyPI Deployment Script

This script handles the complete deployment process to PyPI, including:
- Pre-deployment validation
- Package building
- Distribution testing
- PyPI upload (test and production)
"""

import os
import sys
import subprocess
import tempfile
import shutil
from pathlib import Path
from typing import Tuple, Optional
import getpass


class PyPIDeployer:
    """Handle GTimes deployment to PyPI."""
    
    def __init__(self, package_dir: str = "."):
        self.package_dir = Path(package_dir).resolve()
        self.temp_venv = None
    
    def run_command(self, cmd: str, cwd: str = None, capture_output: bool = True) -> Tuple[int, str, str]:
        """Run a command and return (returncode, stdout, stderr)."""
        try:
            if cwd is None:
                cwd = str(self.package_dir)
            
            print(f"    Running: {cmd}")
            
            if capture_output:
                result = subprocess.run(
                    cmd, shell=True, cwd=cwd,
                    capture_output=True, text=True, timeout=300
                )
                return result.returncode, result.stdout, result.stderr
            else:
                result = subprocess.run(cmd, shell=True, cwd=cwd, timeout=300)
                return result.returncode, "", ""
        except subprocess.TimeoutExpired:
            return 1, "", "Command timed out"
        except Exception as e:
            return 1, "", str(e)
    
    def setup_virtual_environment(self) -> bool:
        """Set up a virtual environment for deployment."""
        print("🔧 Setting up virtual environment...")
        
        # Create temporary virtual environment
        temp_dir = tempfile.mkdtemp()
        venv_path = Path(temp_dir) / "deploy_env"
        
        # Create venv
        returncode, stdout, stderr = self.run_command(f"python3 -m venv {venv_path}")
        if returncode != 0:
            print(f"❌ Failed to create virtual environment: {stderr}")
            return False
        
        self.temp_venv = venv_path
        print(f"✅ Virtual environment created: {venv_path}")
        
        # Install build tools
        pip_cmd = f"{venv_path}/bin/pip"
        returncode, stdout, stderr = self.run_command(f"{pip_cmd} install --upgrade pip build twine")
        if returncode != 0:
            print(f"❌ Failed to install build tools: {stderr}")
            return False
        
        print("✅ Build tools installed")
        return True
    
    def cleanup_virtual_environment(self):
        """Clean up the temporary virtual environment."""
        if self.temp_venv and self.temp_venv.exists():
            shutil.rmtree(self.temp_venv.parent)
            print("🧹 Cleaned up virtual environment")
    
    def validate_package(self) -> bool:
        """Run comprehensive package validation."""
        print("🔍 Running package validation...")
        
        # Run the validation script
        validation_script = self.package_dir / "scripts" / "validate_distribution.py"
        if not validation_script.exists():
            print("❌ Validation script not found")
            return False
        
        returncode, stdout, stderr = self.run_command(f"python3 {validation_script}", capture_output=False)
        if returncode != 0:
            print("❌ Package validation failed")
            return False
        
        print("✅ Package validation passed")
        return True
    
    def build_package(self) -> bool:
        """Build the distribution packages."""
        print("📦 Building distribution packages...")
        
        if not self.temp_venv:
            print("❌ Virtual environment not set up")
            return False
        
        # Clean previous build
        dist_dir = self.package_dir / "dist"
        if dist_dir.exists():
            shutil.rmtree(dist_dir)
        
        build_dir = self.package_dir / "build"
        if build_dir.exists():
            shutil.rmtree(build_dir)
        
        # Build package
        python_cmd = f"{self.temp_venv}/bin/python"
        returncode, stdout, stderr = self.run_command(f"{python_cmd} -m build")
        if returncode != 0:
            print(f"❌ Package build failed: {stderr}")
            return False
        
        # Verify files were created
        if not dist_dir.exists():
            print("❌ No dist directory created")
            return False
        
        wheel_files = list(dist_dir.glob("*.whl"))
        tar_files = list(dist_dir.glob("*.tar.gz"))
        
        if not wheel_files:
            print("❌ No wheel file created")
            return False
        
        if not tar_files:
            print("❌ No source distribution created")
            return False
        
        print(f"✅ Build successful: {len(wheel_files)} wheel(s), {len(tar_files)} sdist(s)")
        for f in wheel_files + tar_files:
            print(f"    📄 {f.name}")
        
        return True
    
    def validate_distribution(self) -> bool:
        """Validate the built distribution."""
        print("🔍 Validating distribution packages...")
        
        if not self.temp_venv:
            print("❌ Virtual environment not set up")
            return False
        
        twine_cmd = f"{self.temp_venv}/bin/twine"
        returncode, stdout, stderr = self.run_command(f"{twine_cmd} check dist/*")
        if returncode != 0:
            print(f"❌ Distribution validation failed: {stderr}")
            return False
        
        print("✅ Distribution validation passed")
        return True
    
    def test_installation(self) -> bool:
        """Test installation in clean environment."""
        print("🧪 Testing installation in clean environment...")
        
        # Create another temp venv for testing
        temp_dir = tempfile.mkdtemp()
        test_venv = Path(temp_dir) / "test_env"
        
        try:
            # Create test environment
            returncode, stdout, stderr = self.run_command(f"python3 -m venv {test_venv}")
            if returncode != 0:
                print(f"❌ Failed to create test environment: {stderr}")
                return False
            
            # Install the package
            pip_cmd = f"{test_venv}/bin/pip"
            dist_files = list((self.package_dir / "dist").glob("*.whl"))
            if not dist_files:
                print("❌ No wheel file to test")
                return False
            
            wheel_file = dist_files[0]
            returncode, stdout, stderr = self.run_command(f"{pip_cmd} install {wheel_file}")
            if returncode != 0:
                print(f"❌ Installation failed: {stderr}")
                return False
            
            # Test basic import
            python_cmd = f"{test_venv}/bin/python"
            returncode, stdout, stderr = self.run_command(
                f"{python_cmd} -c 'import gtimes; from gtimes.gpstime import gpsFromUTC; print(\"GTimes\", gtimes.__version__, \"imported successfully\")'"
            )
            if returncode != 0:
                print(f"❌ Import test failed: {stderr}")
                return False
            
            print(f"✅ Installation test passed: {stdout.strip()}")
            return True
            
        finally:
            # Cleanup test environment
            if test_venv.exists():
                shutil.rmtree(temp_dir)
    
    def get_pypi_credentials(self, test_pypi: bool = False) -> Optional[Tuple[str, str]]:
        """Get PyPI credentials from user."""
        service = "Test PyPI" if test_pypi else "PyPI"
        print(f"🔑 {service} credentials required")
        
        # Check for API token in environment
        token_env = "TEST_PYPI_API_TOKEN" if test_pypi else "PYPI_API_TOKEN"
        api_token = os.environ.get(token_env)
        
        if api_token:
            print(f"✅ Using API token from environment: {token_env}")
            return "__token__", api_token
        
        print(f"Enter your {service} credentials:")
        print("(You can also set the environment variable {token_env} with your API token)")
        
        username = input("Username (or '__token__' for API token): ").strip()
        if not username:
            print("❌ Username required")
            return None
        
        password = getpass.getpass("Password/Token: ")
        if not password:
            print("❌ Password/token required")
            return None
        
        return username, password
    
    def upload_to_pypi(self, test_pypi: bool = True) -> bool:
        """Upload package to PyPI."""
        service = "Test PyPI" if test_pypi else "PyPI"
        print(f"🚀 Uploading to {service}...")
        
        if not self.temp_venv:
            print("❌ Virtual environment not set up")
            return False
        
        # Get credentials
        credentials = self.get_pypi_credentials(test_pypi)
        if not credentials:
            return False
        
        username, password = credentials
        
        # Set up twine command
        twine_cmd = f"{self.temp_venv}/bin/twine"
        
        if test_pypi:
            repository_arg = "--repository testpypi"
        else:
            repository_arg = ""
        
        # Set environment variables for twine
        env = os.environ.copy()
        env["TWINE_USERNAME"] = username
        env["TWINE_PASSWORD"] = password
        
        # Upload
        cmd = f"{twine_cmd} upload {repository_arg} dist/*"
        
        try:
            print(f"    Uploading to {service}...")
            result = subprocess.run(
                cmd, shell=True, cwd=str(self.package_dir),
                env=env, timeout=300
            )
            
            if result.returncode != 0:
                print(f"❌ Upload to {service} failed")
                return False
            
            print(f"✅ Successfully uploaded to {service}")
            return True
            
        except subprocess.TimeoutExpired:
            print(f"❌ Upload to {service} timed out")
            return False
        except Exception as e:
            print(f"❌ Upload to {service} failed: {e}")
            return False
    
    def deploy(self, test_only: bool = False) -> bool:
        """Run the complete deployment process."""
        print("🚀 GTimes PyPI Deployment")
        print("=" * 50)
        
        try:
            # Step 1: Set up environment
            if not self.setup_virtual_environment():
                return False
            
            # Step 2: Validate package
            if not self.validate_package():
                return False
            
            # Step 3: Build package
            if not self.build_package():
                return False
            
            # Step 4: Validate distribution
            if not self.validate_distribution():
                return False
            
            # Step 5: Test installation
            if not self.test_installation():
                return False
            
            # Step 6: Upload to Test PyPI
            print("\n📤 Uploading to Test PyPI first...")
            if not self.upload_to_pypi(test_pypi=True):
                return False
            
            if test_only:
                print("\n✅ Test deployment completed successfully!")
                print("🔗 Check your package at: https://test.pypi.org/project/gtimes/")
                return True
            
            # Step 7: Confirm production upload
            print("\n" + "=" * 50)
            print("🎯 PRODUCTION DEPLOYMENT")
            print("=" * 50)
            print("Test PyPI upload successful!")
            print("Ready to deploy to production PyPI.")
            print("\n⚠️  WARNING: This will make the package publicly available!")
            
            confirm = input("Deploy to production PyPI? (yes/NO): ").lower().strip()
            if confirm != "yes":
                print("❌ Production deployment cancelled")
                return False
            
            # Step 8: Upload to Production PyPI
            if not self.upload_to_pypi(test_pypi=False):
                return False
            
            print("\n🎉 DEPLOYMENT SUCCESSFUL!")
            print("=" * 50)
            print("✅ GTimes has been deployed to PyPI")
            print("🔗 Package available at: https://pypi.org/project/gtimes/")
            print("📦 Install with: pip install gtimes")
            
            return True
            
        finally:
            self.cleanup_virtual_environment()


def main():
    """Main deployment function."""
    import argparse
    
    parser = argparse.ArgumentParser(description="Deploy GTimes to PyPI")
    parser.add_argument("--test-only", action="store_true", 
                       help="Only deploy to Test PyPI")
    parser.add_argument("--skip-validation", action="store_true",
                       help="Skip package validation (not recommended)")
    
    args = parser.parse_args()
    
    # Get package directory
    package_dir = Path(__file__).parent.parent
    
    deployer = PyPIDeployer(package_dir)
    
    try:
        success = deployer.deploy(test_only=args.test_only)
        return 0 if success else 1
    except KeyboardInterrupt:
        print("\n\n❌ Deployment cancelled by user")
        return 1
    except Exception as e:
        print(f"\n❌ Deployment failed with error: {e}")
        return 1


if __name__ == "__main__":
    sys.exit(main())