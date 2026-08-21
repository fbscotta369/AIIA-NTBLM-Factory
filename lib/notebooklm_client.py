#!/usr/bin/env python3
"""
AIIA-NTBLM-Factory — NotebookLM Browser Client
Wraps Playwright to automate Google's NotebookLM: login, create notebooks,
add sources, extract analysis (summary, slides, FAQ, timeline, insights).

Strategy:
1. Try to use saved browser cookies (session persistence)
2. If no cookies, do a fresh login (requires 2FA handling or app-password)
3. Navigate to notebooklm.google.com
4. Create notebook, add sources, wait, extract
5. Save cookies for next run

Environment:
  GOOGLE_SESSION_COOKIE — base64-encoded Playwright storage_state JSON
  NOTEBOOKLM_EMAIL — Google email (default: fbscotta@gmail.com)
  NOTEBOOKLM_PASSWORD — Google password (NOT recommended; use cookies or app-password)
  NOTEBOOKLM_APP_PASSWORD — app-password for 2FA accounts (recommended)
"""

import json
import os
import base64
import time
from pathlib import Path
from typing import Dict, List, Optional

# Playwright import — will fail if not installed
try:
    from playwright.sync_api import sync_playwright, TimeoutError as PlaywrightTimeoutError
    PLAYWRIGHT_AVAILABLE = True
except ImportError:
    PLAYWRIGHT_AVAILABLE = False

# Constants
NOTEBOOKLM_URL = "https://notebooklm.google.com"
GOOGLE_ACCOUNTS_URL = "https://accounts.google.com"
DEFAULT_EMAIL = "fbscotta@gmail.com"


class NotebookLMClient:
    """Browser automation client for NotebookLM via Playwright."""

    # Internal temp directory for cookies
    COOKIE_FILE = Path.home() / ".aiia-ntblm" / "notebooklm_cookies.json"

    # CSS selectors — these may need updating if Google changes UI
    SELECTORS = {
        # Google login
        "email_input": 'input[type="email"]',
        "next_button": 'div[data-id="identifierNext"] button',
        "password_input": 'input[type="password"]',
        "password_next": 'div[data-id="passwordNext"] button',

        # NotebookLM
        "new_notebook_button": '[role="button"]:has-text("New notebook")',
        "notebook_title_input": 'input[placeholder*="title"]',
        "create_button": 'button:has-text("Create")',
        "add_source_button": '[role="button"]:has-text("Add source")',
        "source_url_input": 'input[placeholder*="URL"]',
        "source_add_button": 'button:has-text("Add")',

        # Analysis tabs (in NotebookLM)
        "summary_tab": '[role="tab"]:has-text("Summary")',
        "slides_tab": '[role="tab"]:has-text("Slides")',
        "faq_tab": '[role="tab"]:has-text("FAQ")',
        "timeline_tab": '[role="tab"]:has-text("Timeline")',

        # Loading indicator
        "loading_spinner": '.loading, [role="progressbar"], .spinner',
    }

    def __init__(self, headless: bool = True, timeout: int = 60000):
        self.headless = headless
        self.timeout = timeout
        self.playwright = None
        self.browser = None
        self.context = None
        self.page = None
        self.email = os.environ.get("NOTEBOOKLM_EMAIL", DEFAULT_EMAIL)
        self.password = os.environ.get("NOTEBOOKLM_PASSWORD", "")
        self.app_password = os.environ.get("NOTEBOOKLM_APP_PASSWORD", "")
        self.cookie_data = None  # Will be loaded from file or env

    def load_cookies(self):
        """Load saved browser cookies for session persistence."""
        cookie_env = os.environ.get("GOOGLE_SESSION_COOKIE", "")

        if cookie_env:
            try:
                self.cookie_data = json.loads(base64.b64decode(cookie_env))
                print("  📂 Loaded cookies from env variable")
                return True
            except Exception as e:
                print(f"  ⚠️  Failed to decode cookies from env: {e}")

        if self.COOKIE_FILE.exists():
            try:
                with open(self.COOKIE_FILE) as f:
                    self.cookie_data = json.load(f)
                print(f"  📂 Loaded cookies from {self.COOKIE_FILE}")
                return True
            except Exception as e:
                print(f"  ⚠️  Failed to load cookies from file: {e}")

        print("  ℹ️  No saved cookies found — will need to login fresh")
        return False

    def save_cookies(self):
        """Save current browser cookies for future sessions."""
        if not self.context:
            return

        try:
            cookies = self.context.cookies()
            self.cookie_data = cookies

            # Save to file
            self.COOKIE_FILE.parent.mkdir(parents=True, exist_ok=True)
            with open(self.COOKIE_FILE, "w") as f:
                json.dump(cookies, f, indent=2)

            # Also set env var for current process
            env_value = base64.b64encode(json.dumps(cookies).encode()).decode()
            print(f"  💾 Cookies saved ({len(cookies)} entries)")

        except Exception as e:
            print(f"  ⚠️  Failed to save cookies: {e}")

    def start_browser(self):
        """Start Playwright browser."""
        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError(
                "Playwright not installed. Install with: pip install playwright && playwright install chromium"
            )

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.launch(
            headless=self.headless,
            args=["--no-sandbox", "--disable-setuid-sandbox"],
        )

        # Create context with cookies if available
        if self.cookie_data:
            self.context = self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
                storage_state={"cookies": self.cookie_data, "localStorage": []},
            )
        else:
            self.context = self.browser.new_context(
                viewport={"width": 1920, "height": 1080},
            )

        self.context.set_default_timeout(self.timeout)
        self.page = self.context.new_page()

    def login(self) -> bool:
        """
        Login to Google/NotebookLM.

        Returns True if logged in successfully, False otherwise.
        """
        if not PLAYWRIGHT_AVAILABLE:
            print("  ❌ Playwright not available")
            return False

        try:
            self.start_browser()
        except RuntimeError as e:
            print(f"  ❌ {e}")
            return False

        try:
            print(f"  🌐 Navegando a {NOTEBOOKLM_URL}...")
            self.page.goto(NOTEBOOKLM_URL, wait_until="domcontentloaded", timeout=self.timeout)

            # Check if already logged in
            if self.page.is_visible(self.SELECTORS["new_notebook_button"], timeout=5000):
                print("  ✅ Already logged in to NotebookLM")
                self.save_cookies()
                return True

            # Need to login — check if redirected to Google
            current_url = self.page.url
            if "accounts.google.com" not in current_url:
                # Try navigating to Google login
                print("  🔐 Need to login — navigating to Google...")
                self.page.goto(GOOGLE_ACCOUNTS_URL, wait_until="domcontentloaded", timeout=self.timeout)

            # Step 1: Enter email
            try:
                email_input = self.page.wait_for_selector(self.SELECTORS["email_input"], timeout=10000)
                print(f"  📧 Ingresando email: {self.email}")
                email_input.fill(self.email)
                self.page.click(self.SELECTORS["next_button"])
                time.sleep(2)
            except PlaywrightTimeoutError:
                print("  ⚠️  Email input not found — may already be logged in or UI changed")
                if self.page.is_visible(self.SELECTORS["new_notebook_button"], timeout=5000):
                    self.save_cookies()
                    return True
                return False

            # Step 2: Enter password
            try:
                # Check if 2FA page appears instead of password
                if self.page.is_visible('input[name="selectedAccount"]', timeout=3000):
                    # Account selection page — select the account
                    print("  📋 Selecting account...")
                    # Click the first suggested account or enter password
                    self.page.click('div[role="button"]:first-child')
                    time.sleep(2)

                password_input = self.page.wait_for_selector(self.SELECTORS["password_input"], timeout=10000)
                print("  🔑 Ingresando password...")
                password_to_use = self.app_password or self.password
                if not password_to_use:
                    print("  ❌ No password provided. Set NOTEBOOKLM_PASSWORD or NOTEBOOKLM_APP_PASSWORD")
                    self.close()
                    return False
                password_input.fill(password_to_use)
                self.page.click(self.SELECTORS["password_next"])
                time.sleep(3)
            except PlaywrightTimeoutError:
                print("  ⚠️  Password input not found")
                if self.page.is_visible(self.SELECTORS["new_notebook_button"], timeout=5000):
                    self.save_cookies()
                    return True
                return False

            # Step 3: Handle 2FA if needed
            if self.page.is_visible('input[name="badPassword"]', timeout=2000):
                # Wrong password
                print("  ❌ Password incorrect")
                self.close()
                return False

            # Wait for login to complete
            print("  ⏳ Waiting for login...")
            time.sleep(5)

            # Check result
            for attempt in range(3):
                try:
                    if self.page.is_visible(self.SELECTORS["new_notebook_button"], timeout=8000):
                        print("  ✅ Login successful!")
                        self.save_cookies()
                        return True
                except PlaywrightTimeoutError:
                    pass
                print(f"  ⏳ Still waiting for login... (attempt {attempt + 1}/3)")
                time.sleep(5)

            # Final check
            if "accounts.google.com" in self.page.url:
                print("  ❌ Still on Google login page — login failed")
                self.close()
                return False

            # Might be logged in but selector changed
            print("  ✅ Appears to be logged in (final verification needed)")
            self.save_cookies()
            return True

        except Exception as e:
            print(f"  ❌ Login error: {e}")
            self.close()
            return False

    def create_notebook(self, title: str) -> Optional[Dict]:
        """Create a new notebook in NotebookLM."""
        if not self.page:
            print("  ❌ Not logged in — call login() first")
            return None

        try:
            # Navigate to NotebookLM
            self.page.goto(NOTEBOOKLM_URL, wait_until="domcontentloaded", timeout=self.timeout)
            time.sleep(2)

            # Click "New notebook"
            print(f"  📝 Creando notebook: '{title}'")
            self.page.click(self.SELECTORS["new_notebook_button"])
            time.sleep(1)

            # Enter title
            title_input = self.page.wait_for_selector(self.SELECTORS["notebook_title_input"], timeout=10000)
            title_input.fill(title)
            time.sleep(0.5)

            # Click Create
            self.page.click(self.SELECTORS["create_button"])
            time.sleep(3)

            # Wait for notebook to open
            self.page.wait_for_selector('[role="main"]', timeout=15000)

            notebook_id = self.page.url.split("/")[-1] if "/" in self.page.url else "unknown"
            print(f"  ✅ Notebook creado: {notebook_id}")

            return {
                "id": notebook_id,
                "title": title,
                "url": self.page.url,
            }

        except Exception as e:
            print(f"  ❌ Error creating notebook: {e}")
            return None

    def add_sources(self, notebook: Dict, urls: List[str]) -> bool:
        """Add YouTube/source URLs to a notebook."""
        if not self.page:
            print("  ❌ Not logged in")
            return False

        if not urls:
            print("  ℹ️  No URLs to add")
            return True

        try:
            # Navigate to the notebook
            notebook_url = notebook.get("url", NOTEBOOKLM_URL)
            self.page.goto(notebook_url, wait_until="domcontentloaded", timeout=self.timeout)
            time.sleep(2)

            for i, url in enumerate(urls):
                print(f"  🔗 Agregando fuente {i+1}/{len(urls)}: {url[:60]}...")

                # Click "Add source"
                self.page.click(self.SELECTORS["add_source_button"])
                time.sleep(1)

                # Fill URL
                url_input = self.page.wait_for_selector(self.SELECTORS["source_url_input"], timeout=10000)
                url_input.fill(url)
                time.sleep(0.5)

                # Click Add
                self.page.click(self.SELECTORS["source_add_button"])
                time.sleep(2)

                # Check for error
                if "Error" in self.page.content() or "error" in self.page.content().lower():
                    print(f"  ⚠️  Error adding {url}")
                    continue

            print(f"  ✅ {len(urls)} fuentes agregadas")
            return True

        except Exception as e:
            print(f"  ❌ Error adding sources: {e}")
            return False

    def extract_analysis(self, notebook: Dict) -> Dict:
        """
        Extract analysis from NotebookLM: summary, slides, FAQ, timeline.

        Note: NotebookLM generates these automatically after sources are added.
        We extract what's available.
        """
        if not self.page:
            return {"error": "Not logged in"}

        results = {
            "summary": [],
            "slides": [],
            "faq": [],
            "timeline": [],
            "insights": [],
            "extracted_at": time.time(),
        }

        try:
            # Navigate to notebook
            notebook_url = notebook.get("url", NOTEBOOKLM_URL)
            self.page.goto(notebook_url, wait_until="domcontentloaded", timeout=self.timeout)
            time.sleep(3)

            # Extract all text content from the main area
            content = self.page.evaluate("() => document.body.innerText")

            # Parse content into sections (basic parsing — NotebookLM UI may change)
            lines = content.split("\n")
            current_section = None
            section_content = []

            section_markers = {
                "summary": ["Summary", "Resumen", "Summary & Analysis"],
                "slides": ["Slides", "Diapositivas", "Presentation"],
                "faq": ["FAQ", "Preguntas", "FAQ & Q&A", "Questions"],
                "timeline": ["Timeline", "Línea de tiempo", "Timeline & Events"],
                "insights": ["Insights", "Insights & Ideas", "Claves", "Key Takeaways"],
            }

            for line in lines:
                line_stripped = line.strip()
                if not line_stripped:
                    continue

                # Check if this is a section header
                for section_name, markers in section_markers.items():
                    if any(marker.lower() in line_stripped.lower() for marker in markers):
                        if current_section:
                            results[current_section] = section_content
                        current_section = section_name
                        section_content = []
                        break
                else:
                    if current_section:
                        section_content.append(line_stripped)

            # Save last section
            if current_section:
                results[current_section] = section_content

            # Also try to click tabs and get content
            for tab_name in ["summary_tab", "slides_tab", "faq_tab", "timeline_tab"]:
                try:
                    self.page.click(self.SELECTORS[tab_name])
                    time.sleep(2)
                    tab_content = self.page.evaluate("() => document.body.innerText")
                    # Map to results key
                    key_map = {
                        "summary_tab": "summary",
                        "slides_tab": "slides",
                        "faq_tab": "faq",
                        "timeline_tab": "timeline",
                    }
                    results[key_map[tab_name]] = tab_content.split("\n")
                except Exception:
                    pass  # Tab might not be available

            print(f"  📊 Analysis extracted: {sum(len(v) for v in results.values() if isinstance(v, list))} lines total")
            return results

        except Exception as e:
            print(f"  ❌ Error extracting analysis: {e}")
            return {"error": str(e)}

    def close(self):
        """Close browser and clean up."""
        try:
            if self.context:
                self.context.close()
            if self.browser:
                self.browser.close()
            if self.playwright:
                self.playwright.stop()
        except Exception:
            pass

    def __enter__(self):
        return self

    def __exit__(self, *args):
        self.close()


def test_login():
    """Test if login works."""
    client = NotebookLMClient(headless=True)

    print("=== NotebookLM Login Test ===")
    print(f"  Email: {client.email}")
    print(f"  Has password: {bool(client.password or client.app_password)}")
    print(f"  Playwright available: {PLAYWRIGHT_AVAILABLE}")

    if not PLAYWRIGHT_AVAILABLE:
        print("\n  ❌ Install Playwright first: pip install playwright && playwright install chromium")
        return False

    if client.load_cookies():
        print("  ✅ Cookies loaded — trying session first...")

    success = client.login()
    client.close()
    return success


if __name__ == "__main__":
    test_login()
