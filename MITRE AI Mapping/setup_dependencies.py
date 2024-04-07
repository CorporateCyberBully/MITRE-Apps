import subprocess
import sys

def install_packages():
    """Installs required Python packages."""
    required_packages = ["requests", "sentence-transformers", "numpy", "pywin32"]
    for package in required_packages:
        try:
            print(f"Checking and installing {package} if necessary...")
            subprocess.check_call([sys.executable, "-m", "pip", "install", package, "--user"])
        except subprocess.CalledProcessError as e:
            print(f"Failed to install {package}: {e}")
            sys.exit(1)

if __name__ == "__main__":
    try:
        install_packages()
        print("All required packages are installed.")
    except subprocess.CalledProcessError as e:
        print(f"Failed to install required packages: {e}")
        sys.exit(1)
