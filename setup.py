#!/usr/bin/env python
"""
EduNova Setup Script
This script helps set up the EduNova project by installing dependencies and initializing the database.
"""

import os
import subprocess
import sys

def print_header(message):
    print("\n" + "=" * 80)
    print(f" {message}")
    print("=" * 80)

def run_command(command, cwd=None):
    print(f"> Running: {command}")
    try:
        subprocess.run(command, shell=True, check=True, cwd=cwd)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error executing command: {e}")
        return False

def install_python_deps():
    print_header("Installing Python dependencies")
    if not run_command("pip install -r requirements.txt"):
        print("Failed to install Python dependencies")
        return False
    return True

def install_node_deps():
    print_header("Installing Node.js dependencies")
    if not run_command("npm install"):
        print("Failed to install Node.js dependencies")
        return False
    return True

def init_database():
    print_header("Initializing database")
    if not run_command("python init_db.py", cwd="backend"):
        print("Failed to initialize database")
        return False
    return True

def main():
    print_header("EduNova Setup")
    
    # Check if Python is installed
    if not run_command("python --version"):
        print("Python is not installed or not in PATH")
        return False
    
    # Check if Node.js is installed
    if not run_command("node --version"):
        print("Node.js is not installed or not in PATH")
        return False
    
    # Install dependencies
    if not install_python_deps():
        return False
    
    if not install_node_deps():
        return False
    
    # Initialize database
    if not init_database():
        return False
    
    print_header("Setup completed successfully!")
    print("\nYou can now run the application with:")
    print("  - Backend: npm run start:backend")
    print("  - Frontend: npm run start:frontend")
    
    return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1) 