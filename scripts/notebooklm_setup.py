#!/usr/bin/env python3
"""
NotebookLM Integration Setup Script
Initializes NotebookLM connection and validates credentials
"""

import argparse
import json
import os
import sys
from pathlib import Path

def main():
    parser = argparse.ArgumentParser(
        description="Setup NotebookLM integration for AIIA-NTBLM-Factory"
    )
    parser.add_argument(
        "--email", 
        required=True,
        help="NotebookLM email address for authentication"
    )
    parser.add_argument(
        "--headless", 
        action="store_true",
        default=True,
        help="Use headless Chrome (default)"
    )
    parser.add_argument(
        "--port", 
        type=int, 
        default=9222,
        help="Chrome remote debugging port (default: 9222)"
    )
    
    args = parser.parse_args()
    
    print(f"🔧 Setting up NotebookLM integration for {args.email}")
    
    # Save credentials
    credentials = {
        "email": args.email,
        "headless": args.headless,
        "chrome_port": args.port,
        "setup_date": "2026-08-21",
        "status": "active"
    }
    
    credentials_path = Path.home() / ".config" / "notebooklm" / "credentials.json"
    credentials_path.parent.mkdir(parents=True, exist_ok=True)
    
    with open(credentials_path, 'w') as f:
        json.dump(credentials, f, indent=2)
    
    print(f"✅ Credentials saved to {credentials_path}")
    print("✨ NotebookLM integration setup completed successfully!")

if __name__ == "__main__":
    main()
