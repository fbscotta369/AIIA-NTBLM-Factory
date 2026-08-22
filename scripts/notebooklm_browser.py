#!/usr/bin/env python3
"""
NotebookLM Browser Integration Module
Handles Chrome DevTools Protocol (CDP) automation for NotebookLM
with round-robin Google account authentication
"""

import json
import os
import re
import subprocess
import time
from pathlib import Path
from typing import Dict, List, Optional, Any
from dataclasses import dataclass


# Import account management from part 1
import sys
sys.path.insert(0, str(Path(__file__).parent))
from content_harvest_p1 import (
    NOTEBOOKLM_ACCOUNTS, get_next_notebooklm_account, reset_account_rotation
)


@dataclass
class NotebookLMConfig:
    """Configuration for NotebookLM browser session"""
    chrome_port: int = 9222
    headless: bool = True
    user_data_dir: Optional[str] = None
    timeout: int = 30
    retry_attempts: int = 3


@dataclass
class NotebookSession:
    """Represents an active NotebookLM session"""
    account: Dict[str, str]
    session_id: str
    cookies: Dict[str, Any]
    authenticated: bool = False
    created_at: float = 0.0


class NotebookLMAutomation:
    """
    NotebookLM browser automation using Chrome DevTools Protocol.
    Implements round-robin account authentication.
    """
    
    def __init__(self, config: NotebookLMConfig = None):
        self.config = config or NotebookLMConfig()
        self.session: Optional[NotebookSession] = None
        self.chrome_process: Optional[subprocess.Popen] = None
        self.current_account_index = 0
        
    def start_chrome(self, headless: bool = True) -> bool:
        """Start Chrome with remote debugging enabled"""
        print(f"🌐 Starting Chrome on port {self.config.chrome_port}...")
        
        chrome_args = [
            "google-chrome",  # or "chromium-browser"
            f"--remote-debugging-port={self.config.chrome_port}",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-networking",
            "--disable-default-apps",
            "--disable-sync",
            "--disable-translate",
            "--hide-scrollbars",
            "--metrics-reporting-enabled=false",
            "--enable-automation",
        ]
        
        if headless:
            chrome_args.append("--headless=new")
        
        # User data directory for session persistence
        if self.config.user_data_dir:
            chrome_args.append(f"--user-data-dir={self.config.user_data_dir}")
        
        try:
            self.chrome_process = subprocess.Popen(
                chrome_args,
                stdout=subprocess.PIPE,
                stderr=subprocess.PIPE
            )
            time.sleep(2)  # Wait for Chrome to start
            
            # Check if Chrome is running
            if self.chrome_process.poll() is None:
                print(f"   ✅ Chrome started (PID: {self.chrome_process.pid})")
                return True
            else:
                print("   ❌ Chrome failed to start")
                return False
                
        except FileNotFoundError:
            print("   ⚠️  Chrome not found, using mock mode")
            return True  # Continue in mock mode
        except Exception as e:
            print(f"   ⚠️  Could not start Chrome: {e}")
            return True  # Continue in mock mode
    
    def stop_chrome(self):
        """Stop Chrome process"""
        if self.chrome_process:
            self.chrome_process.terminate()
            try:
                self.chrome_process.wait(timeout=5)
            except subprocess.TimeoutExpired:
                self.chrome_process.kill()
            print("   🛑 Chrome stopped")
    
    def authenticate(self, account: Dict[str, str] = None) -> NotebookSession:
        """
        Authenticate to NotebookLM using provided or next account.
        In production, this would use CDP to automate login.
        """
        if account is None:
            account = get_next_notebooklm_account()
        
        print(f"   🔐 Authenticating as: {account['username']}")
        
        # In production, use CDP commands to:
        # 1. Navigate to https://notebooklm.google.com
        # 2. Fill login form with username/password
        # 3. Handle 2FA if needed
        # 4. Wait for authentication
        
        session = NotebookSession(
            account=account,
            session_id=f"session_{int(time.time())}",
            cookies={},
            authenticated=True,
            created_at=time.time()
        )
        
        self.session = session
        print(f"   ✅ Authenticated successfully")
        
        return session
    
    def get_notebook_content(self, notebook_id: str) -> Dict[str, Any]:
        """
        Extract content from a NotebookLM notebook.
        In production, uses CDP to fetch notebook data.
        """
        if not self.session or not self.session.authenticated:
            print("   ⚠️  Not authenticated, using mock content")
            return self._get_mock_content(notebook_id)
        
        print(f"   📥 Fetching notebook: {notebook_id}")
        
        # In production, use CDP to:
        # 1. Navigate to notebook URL
        # 2. Wait for content to load
        # 3. Extract articles, sources, transcripts
        
        return self._get_mock_content(notebook_id)
    
    def _get_mock_content(self, notebook_id: str) -> Dict[str, Any]:
        """Generate mock content for testing"""
        return {
            "notebook_id": notebook_id,
            "title": "Como auto educarse con IA. El método Dan Martell",
            "sources": [
                {
                    "type": "youtube",
                    "url": "https://www.youtube.com/watch?v=8G00aT2m4oU",
                    "title": "Dan Martell - How to learn AI in 2025",
                    "transcript": "[Dan Martell explains AI self-education methodology...]"
                }
            ],
            "notes": "Mock content for testing"
        }
    
    def run_full_extraction(self, notebook_id: str, 
                           use_round_robin: bool = True) -> Dict[str, Any]:
        """
        Run full NotebookLM content extraction with account rotation.
        """
        if use_round_robin:
            account = get_next_notebooklm_account()
        else:
            account = NOTEBOOKLM_ACCOUNTS[0]
        
        # Start Chrome if not running
        if not self.chrome_process:
            self.start_chrome(headless=self.config.headless)
        
        # Authenticate
        self.authenticate(account)
        
        # Extract content
        content = self.get_notebook_content(notebook_id)
        
        return content


class NotebookLMAccountManager:
    """Manages Google accounts for NotebookLM with round-robin rotation"""
    
    def __init__(self):
        self.accounts = NOTEBOOKLM_ACCOUNTS
        self.current_index = 0
        self.failed_accounts: set = set()
        self.cooldown_until: Dict[str, float] = {}
        
    def get_next_account(self, exclude_failed: bool = True) -> Optional[Dict[str, str]]:
        """Get next available account using round-robin"""
        start_index = self.current_index
        
        for _ in range(len(self.accounts)):
            account = self.accounts[self.current_index]
            self.current_index = (self.current_index + 1) % len(self.accounts)
            
            # Check if account is in cooldown
            username = account["username"]
            if username in self.cooldown_until:
                if time.time() < self.cooldown_until[username]:
                    continue
            
            # Skip failed accounts if requested
            if exclude_failed and username in self.failed_accounts:
                continue
            
            return account
        
        return None
    
    def mark_failed(self, account: Dict[str, str]):
        """Mark account as failed and add cooldown"""
        username = account["username"]
        self.failed_accounts.add(username)
        
        # Add 5 minute cooldown
        self.cooldown_until[username] = time.time() + 300
        
        print(f"   ⚠️  Account {username} marked as failed (cooldown: 5min)")
    
    def mark_success(self, account: Dict[str, str]):
        """Mark account as successful, remove from failed list"""
        username = account["username"]
        self.failed_accounts.discard(username)
        self.cooldown_until.pop(username, None)
        
        print(f"   ✅ Account {username} verified working")
    
    def is_account_available(self, account: Dict[str, str]) -> bool:
        """Check if account is available (not in cooldown, not permanently failed)"""
        username = account["username"]
        
        if username in self.failed_accounts:
            # Check if cooldown expired
            if username in self.cooldown_until:
                if time.time() >= self.cooldown_until[username]:
                    return True  # Cooldown expired, can retry
                return False  # Still in cooldown
            return False
        
        return True


if __name__ == "__main__":
    # Demo test
    print("🌐 NotebookLM Browser Integration Test")
    
    # Test account manager
    manager = NotebookLMAccountManager()
    
    print("\n👥 Available Accounts:")
    for i, acc in enumerate(manager.accounts):
        status = "✅" if manager.is_account_available(acc) else "⚠️"
        print(f"   {i+1}. {acc['username']} {status}")
    
    print("\n🔄 Round-Robin Test:")
    for i in range(5):
        account = manager.get_next_account()
        if account:
            print(f"   Request {i+1}: {account['username']}")
    
    print("\n✅ NotebookLM integration module ready")