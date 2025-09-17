#!/usr/bin/env python3

import subprocess
import sys
import os

def run_command(command, description):
    """Run a command and handle errors"""
    print(f"🔄 {description}...")
    try:
        result = subprocess.run(command, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        return result
    except subprocess.CalledProcessError as e:
        print(f"❌ Error during {description}")
        print(f"Command: {command}")
        print(f"Error: {e.stderr}")
        return None

def main():
    print("🚀 Setting up Research Paper Agent...")
    print("=" * 50)

    # Check Python version
    if sys.version_info < (3, 8):
        print("❌ Python 3.8+ is required")
        sys.exit(1)

    # Install requirements
    if not run_command("pip install -r requirements.txt", "Installing Python dependencies"):
        print("💡 Try using: python -m pip install -r requirements.txt")
        return

    print("\n🎉 Setup completed successfully!")
    print("\n📋 Next steps:")
    print("1. Run the application: python app.py")
    print("2. Open your browser to: http://127.0.0.1:5000")
    print("3. Paste a paper abstract and find related papers!")
    print("\n💡 The first search may take a moment as it downloads the ML model.")

if __name__ == "__main__":
    main()