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

    def start_browser_cdp(self, profile_dir: str = None, chrome_bin: str = None, port: int = 9222):
        """
        Start Playwright by CONNECTING to the user's REAL Google Chrome (with an
        authenticated Google session) over CDP. This bypasses Google's
        "This browser or app may not be secure" block, because we reuse an
        existing logged-in session instead of doing a fresh headless login.

        Args:
            profile_dir: a COPY of ~/.config/google-chrome (must be writable, no lock)
            chrome_bin: path to system google-chrome
            port: CDP remote-debugging port
        """
        import subprocess, shutil, time as _time, urllib.request

        if not PLAYWRIGHT_AVAILABLE:
            raise RuntimeError("Playwright not installed.")

        profile_dir = profile_dir or os.environ.get("CHROME_PROFILE_COPY")
        chrome_bin = chrome_bin or os.environ.get("CHROME_BIN", "/usr/bin/google-chrome-stable")
        if not profile_dir:
            raise RuntimeError("start_browser_cdp requires a Chrome profile copy path")

        # Ensure no stale singleton locks
        for f in ("SingletonLock", "SingletonSocket", "SingletonCookie", "lockfile"):
            p = os.path.join(profile_dir, f)
            if os.path.exists(p):
                try: os.remove(p)
                except OSError: pass

        args = [
            chrome_bin,
            f"--remote-debugging-port={port}",
            f"--user-data-dir={profile_dir}",
            "--headless=new",
            "--no-first-run",
            "--no-default-browser-check",
            "--disable-background-networking",
            "--window-size=1920,1080",
        ]
        self._cdp_proc = subprocess.Popen(
            args, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL,
            start_new_session=True,
        )
        cdp_url = f"http://127.0.0.1:{port}"
        for _ in range(30):
            try:
                with urllib.request.urlopen(f"{cdp_url}/json/version", timeout=2) as r:
                    json.load(r)
                break
            except Exception:
                _time.sleep(1)
        else:
            raise RuntimeError("Chrome CDP did not come up")

        self.playwright = sync_playwright().start()
        self.browser = self.playwright.chromium.connect_over_cdp(cdp_url)
        self.context = self.browser.contexts[0] if self.browser.contexts else self.browser.new_context()
        self.context.set_default_timeout(self.timeout)
        self.page = self.context.new_page()
        self._cdp_url = cdp_url
        return True

    def _is_authenticated(self) -> bool:
        """Return True if the current page shows an authenticated NotebookLM session."""
        try:
            body = self.page.inner_text("body") if self.page.query_selector("body") else ""
        except Exception:
            body = ""
        url = self.page.url
        if "accounts.google.com" in url:
            return False
        markers = ["Create new notebook", "My notebooks", "Featured notebooks",
                   "new notebook", "notebook"]
        return any(m.lower() in body.lower() for m in markers)

    def login(self) -> bool:
        """
        Login to Google/NotebookLM.

        Strategy:
        - If CHROME_PROFILE_COPY (a copy of the user's real Chrome profile) is set,
          connect over CDP and reuse the existing authenticated session. Google
          does NOT block this because no fresh login is attempted.
        - Otherwise, fall back to the password-based flow (which Google may block
          on headless browsers).

        Returns True if logged in successfully, False otherwise.
        """
        if not PLAYWRIGHT_AVAILABLE:
            print("  ❌ Playwright not available")
            return False

        using_cdp = False
        try:
            profile_copy = os.environ.get("CHROME_PROFILE_COPY") or getattr(self, "cdp_profile_dir", None)
            if profile_copy and os.path.isdir(profile_copy):
                print("  🔌 Using real Chrome profile via CDP (no fresh login)")
                self.start_browser_cdp(profile_dir=profile_copy)
                using_cdp = True
            else:
                self.start_browser()

            print(f"  🌐 Navegando a {NOTEBOOKLM_URL}...")
            self.page.goto(NOTEBOOKLM_URL, wait_until="domcontentloaded", timeout=self.timeout)
            self.page.wait_for_timeout(4000)

            # CDP mode: session already authenticated — just verify.
            if using_cdp:
                if self._is_authenticated():
                    print("  ✅ Already logged in to NotebookLM (real profile session)")
                    return True
                print("  ⚠️  CDP profile not authenticated — your desktop Chrome may have logged out of Google")
                self.close()
                return False

            # Password flow: check if already logged in
            if self._is_authenticated():
                print("  ✅ Already logged in to NotebookLM")
                self.save_cookies()
                return True

            # Need to login — check if redirected to Google
            current_url = self.page.url
            if "accounts.google.com" not in current_url:
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
                if self._is_authenticated():
                    self.save_cookies()
                    return True
                return False

            # Step 2: Enter password
            try:
                if self.page.is_visible('input[name="selectedAccount"]', timeout=3000):
                    print("  📋 Selecting account...")
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
                if self._is_authenticated():
                    self.save_cookies()
                    return True
                return False

            # Step 3: Handle 2FA / wrong password
            if self.page.is_visible('input[name="badPassword"]', timeout=2000):
                print("  ❌ Password incorrect")
                self.close()
                return False

            print("  ⏳ Waiting for login...")
            time.sleep(5)

            for attempt in range(3):
                if self._is_authenticated():
                    print("  ✅ Login successful!")
                    self.save_cookies()
                    return True
                print(f"  ⏳ Still waiting for login... (attempt {attempt + 1}/3)")
                time.sleep(5)

            if "accounts.google.com" in self.page.url:
                print("  ❌ Still on Google login page — login failed")
                self.close()
                return False

            print("  ✅ Appears to be logged in (final verification needed)")
            self.save_cookies()
            return True

        except Exception as e:
            print(f"  ❌ Login error: {e}")
            self.close()
            return False

    def _dismiss_dialogs(self):
        """Dismiss any open Material (cdk-overlay) dialogs that block clicks.

        Detects visible dialog containers and clicks a likely dismiss button
        (e.g. "Let's go", "Got it", "Dismiss", the close icon, or ESC).
        Swallows all errors — best-effort.
        """
        try:
            # ESC closes most overlays
            self.page.keyboard.press("Escape")
            self.page.wait_for_timeout(500)

            dialog = self.page.query_selector(
                'mat-dialog-container, .mat-dialog-container, [role="dialog"], .cdk-overlay-pane'
            )
            if not dialog:
                return

            # Try known dismiss button texts
            for txt in ["Let's go", "Got it", "Dismiss", "Close", "OK", "Continue", "Aceptar", "Entendido"]:
                btn = self.page.query_selector(f'[role="button"]:has-text("{txt}"), button:has-text("{txt}")')
                if btn and btn.is_visible():
                    btn.click()
                    self.page.wait_for_timeout(800)
                    return

            # Fallback: click the X / close icon
            close = self.page.query_selector('button[aria-label="Close"], .mat-dialog-close, .close-button')
            if close and close.is_visible():
                close.click()
                self.page.wait_for_timeout(800)
        except Exception:
            pass

    def create_notebook(self, title: str) -> Optional[Dict]:
        """Create a new notebook in NotebookLM. Real DOM: clicking "Create new
        notebook" creates it immediately and lands at /notebook/<uuid>?addSource=true;
        there is no title+Create modal. The title is set via the .title-input field
        that appears on the notebook page."""
        if not self.page:
            print("  ❌ Not logged in — call login() first")
            return None
        try:
            self.page.goto(NOTEBOOKLM_URL, wait_until="domcontentloaded", timeout=self.timeout)
            self.page.wait_for_timeout(3000)
            self._dismiss_dialogs()
            self.page.wait_for_timeout(1500)

            print(f"  📝 Creando notebook: '{title}'")
            self.page.click(self.SELECTORS["new_notebook_button"], timeout=15000, force=True)
            self.page.wait_for_timeout(4000)

            nb_url = self.page.url.rstrip("/")
            nb_id = nb_url.split("/")[-1].split("?")[0]

            # Set title via the .title-input field that appears on the notebook page
            try:
                t = self.page.wait_for_selector(".title-input", timeout=8000)
                if t:
                    t.fill(title)
                    print(f"   title set: {title}")
            except Exception:
                print(f"   (title input not present; leaving default)")

            print(f"   notebook url: {nb_url}")
            return {"id": nb_id, "title": title, "url": nb_url}
        except Exception as e:
            print(f"  ❌ Error creating notebook: {e}")
            return None

    def add_sources(self, notebook: Dict, urls: List[str]) -> bool:
        """Add source URLs to a NotebookLM notebook (YouTube, websites, etc.).
        Robust CDP flow: open the Add-sources panel, select source type (YouTube /
        Web / ...), fill the URL input, click Add. Dismisses overlays between steps."""
        if not self.page:
            print("  ❌ Not logged in")
            return False
        if not urls:
            print("  ℹ️  No URLs to add")
            return True
        try:
            nb_url = notebook.get("url", NOTEBOOKLM_URL).rstrip("/")
            self.page.goto(nb_url + "?addSource=true", wait_until="domcontentloaded", timeout=self.timeout)
            self.page.wait_for_timeout(3000)
            self._dismiss_dialogs()
            self.page.wait_for_timeout(1500)

            for i, url in enumerate(urls):
                print(f"  🔗 Agregando fuente {i+1}/{len(urls)}: {url[:60]}...")

                # Open the "Add sources" panel
                ok = False
                for sel in ['[role="button"]:has-text("Add sources")', 'button:has-text("Add sources")', 'button:has-text("add sources")']:
                    try:
                        b = self.page.query_selector(sel)
                        if b and b.is_visible():
                            b.click(force=True)
                            ok = True
                            break
                    except Exception:
                        continue
                if not ok:
                    print(f"   ⚠️  'Add sources' panel not found")
                    continue
                self.page.wait_for_timeout(1500)
                self._dismiss_dialogs()
                self.page.wait_for_timeout(1000)

                # Classify source type from URL
                source_type = "Web"
                if "youtube.com" in url or "youtu.be" in url:
                    source_type = "YouTube"

                # Select source type tab in the panel
                if source_type != "Web":
                    for sel in [f'button:has-text("{source_type}")', f'[role="button"]:has-text("{source_type}")']:
                        try:
                            b = self.page.query_selector(sel)
                            if b and b.is_visible():
                                b.click(force=True)
                                self.page.wait_for_timeout(1500)
                                self._dismiss_dialogs()
                                self.page.wait_for_timeout(1000)
                                break
                        except Exception:
                            continue

                # Fill the URL input
                url_input = None
                for sel in [
                    'input[placeholder*="URL"]',
                    'input[aria-label*="URL" i]',
                    'input[placeholder*="url" i]',
                    'input[placeholder*="Link"]',
                    'input[placeholder*="link" i]',
                    'textarea[aria-label*="URL" i]',
                ]:
                    try:
                        el = self.page.query_selector(sel)
                        if el and el.is_visible():
                            url_input = el
                            break
                    except Exception:
                        continue
                if not url_input:
                    try:
                        cand = self.page.query_selector('input[type="text"]')
                        if cand and cand.is_visible():
                            url_input = cand
                    except Exception:
                        pass
                if not url_input or not url_input.is_visible():
                    print(f"   ⚠️  URL input not found — retrying after panel open")
                    self.page.wait_for_timeout(2000)
                    self._dismiss_dialogs()
                    try:
                        url_input = self.page.query_selector('input[placeholder*="URL"]')
                        if not url_input.is_visible():
                            url_input = None
                    except Exception:
                        pass
                if not url_input or not url_input.is_visible():
                    print(f"   ❌ URL input still not found for {url[:50]}")
                    continue

                url_input.click(force=True)
                url_input.fill(url)
                self.page.wait_for_timeout(500)

                # Click Add / Publish / Done
                added = False
                for sel in ['button:has-text("Add")', 'button:has-text("Publish")', '[role="button"]:has-text("Add")', 'button:has-text("Done")']:
                    try:
                        b = self.page.query_selector(sel)
                        if b and b.is_visible():
                            b.click(force=True)
                            added = True
                            break
                    except Exception:
                        continue
                if not added:
                    print(f"   ⚠️  Add button not found for {url[:50]}")
                    continue
                self.page.wait_for_timeout(2000)
                self._dismiss_dialogs()
                print(f"   ✅ fuente agregada")

            print(f"  ✅ {len(urls)} fuentes procesadas")
            return True
        except Exception as e:
            print(f"  ❌ Error adding sources: {e}")
            return False
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
            if getattr(self, "context", None):
                self.context.close()
            if getattr(self, "browser", None):
                self.browser.close()
            if getattr(self, "playwright", None):
                self.playwright.stop()
        except Exception:
            pass
        # Terminate the CDP Chrome subprocess if we launched one
        proc = getattr(self, "_cdp_proc", None)
        if proc is not None:
            try:
                proc.terminate()
                proc.wait(timeout=5)
            except Exception:
                try: proc.kill()
                except Exception: pass

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
