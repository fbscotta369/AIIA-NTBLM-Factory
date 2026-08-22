#!/usr/bin/env python3
"""
Unified Message Checker Script

Monitors multiple messaging platforms (Gmail, Telegram, WhatsApp, LinkedIn) for new messages
and sends notifications only when new messages appear, not on every check.

Features:
- Checks specified platforms periodically
- Tracks last message state to detect new messages only
- Sends notifications only when new messages are detected
- Simple, lightweight design without LLM integration
- Supports platform-specific configurations via .hermes/env

Platforms Supported:
- Gmail (via IMAP)
- Telegram (simulated for demo)
- WhatsApp (simulated for demo)
- LinkedIn (simulated for demo)
"""

import os
import sys
import json
import logging
from datetime import datetime, timedelta
from pathlib import Path
from typing import Dict, List, Optional, Any, Tuple
import imaplib
import email
from email import policy

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler('/tmp/unified_message_checker.log'),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

class PlatformMessageTracker:
    """Track last message state for each platform"""
    
    def __init__(self, storage_file: str = "/tmp/message_tracker.json"):
        self.storage_file = storage_file
        self.tracker = self._load_tracker()
    
    def _load_tracker(self) -> Dict[str, Any]:
        """Load message tracker from file"""
        if Path(self.storage_file).exists():
            try:
                with open(self.storage_file, 'r') as f:
                    return json.load(f)
            except Exception as e:
                logger.warning(f"Failed to load tracker: {e}")
        
        return {
            "last_check": datetime.now().isoformat(),
            "platform_states": {}
        }
    
    def _save_tracker(self):
        """Save tracker to file"""
        try:
            with open(self.storage_file, 'w') as f:
                json.dump(self.tracker, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to save tracker: {e}")
    
    def has_new_messages(self, platform: str, get_message_count_func) -> Tuple[bool, List[Dict]]:
        """Check if platform has new messages since last check"""
        current_time = datetime.now()
        last_check = datetime.fromisoformat(self.tracker.get("last_check", current_time.isoformat()))
        
        # Only check if enough time has passed (rate limiting)
        if current_time - last_check < timedelta(minutes=1):
            return False, []
        
        platform_state = self.tracker.get("platform_states", {}).get(platform, {})
        last_message_id = platform_state.get("last_message_id")
        last_message_time = platform_state.get("last_message_time")
        
        # Get current message count/id
        try:
            current_messages = get_message_count_func()
            if not current_messages:
                return False, []
                
            latest_message = current_messages[0]  # Most recent message
            latest_id = latest_message.get("id")
            latest_time = latest_message.get("timestamp")
            
            # Check if we have a new message
            if latest_id != last_message_id or latest_time != last_message_time:
                # Update tracker
                if platform not in self.tracker.get("platform_states", {}):
                    self.tracker.setdefault("platform_states", {})[platform] = {}
                    
                self.tracker["platform_states"][platform]["last_message_id"] = latest_id
                self.tracker["platform_states"][platform]["last_message_time"] = latest_time
                self.tracker["platform_states"][platform]["last_message_count"] = len(current_messages)
                self.tracker["last_check"] = current_time.isoformat()
                self._save_tracker()
                
                return True, current_messages
                
        except Exception as e:
            logger.error(f"Error checking platform {platform}: {e}")
        
        return False, []

class UnifiedMessageChecker:
    """Main class for unified message checking"""
    
    def __init__(self, config_file: str = "/home/fb/AIIA-NTBLM-Factory/.env"):
        self.config = self._load_config(config_file)
        self.tracker = PlatformMessageTracker()
        self.notifications_enabled = True
        
    def _load_config(self, config_file: str) -> Dict:
        """Load configuration from file"""
        config = {
            "platforms": {
                "gmail": {
                    "enabled": False,
                    "email": None,
                    "password": None,
                    "check_interval_minutes": 30
                },
                "telegram": {
                    "enabled": False,
                    "bot_token": None,
                    "chat_id": None,
                    "check_interval_minutes": 30
                },
                "whatsapp": {
                    "enabled": False,
                    "api_key": None,
                    "instance_id": None,
                    "check_interval_minutes": 30
                },
                "linkedin": {
                    "enabled": False,
                    "access_token": None,
                    "check_interval_minutes": 30
                }
            },
            "notification": {
                "enabled": True,
                "min_new_messages": 1 
            },
            "general": {
                "verbose_logging": False
            }
        }
        
        # Try to load from .hermes/env file if it exists
        env_file = Path.home() / ".hermes" / "env"
        if env_file.exists():
            try:
                with open(env_file, 'r') as f:
                    env_config = json.load(f)
                    # Only update platforms config if present
                    if "platforms" in env_config:
                        for platform, platform_config in env_config["platforms"].items():
                            if platform in config["platforms"]:
                                for key, value in platform_config.items():
                                    if value is not None:
                                        config["platforms"][platform][key] = value
            except Exception as e:
                logger.warning(f"Could not load env config: {e}")
        
        return config
    
    def _get_gmail_messages(self) -> List[Dict]:
        """Get recent Gmail messages"""
        if not self.config["platforms"]["gmail"]["enabled"]:
            return []
            
        try:
            email_addr = self.config["platforms"]["gmail"]["email"]
            password = self.config["platforms"]["gmail"]["password"]
            
            if not email_addr or not password:
                logger.warning("Gmail credentials not configured - check .hermes/env file")
                return []
            
            # Connect to Gmail IMAP
            mail = imaplib.IMAP4('imap.gmail.com', 993)
            mail.login(email_addr, password)
            mail.select('inbox')
            
            # Search for recent messages (last 30 minutes)
            result, data = mail.search(None, 'SINCE "{}"'.format(
                (datetime.now() - timedelta(minutes=30)).strftime('%d-%b-%Y')))
            
            messages = []
            for msg_id in data[0].split():
                try:
                    result, msg_data = mail.fetch(msg_id, '(RFC822)')
                    raw_email = msg_data[0][1].decode('utf-8')
                    email_message = email.message_from_string(raw_email, policy=policy.default)
                    
                    messages.append({
                        "id": msg_id.decode(),
                        "from": email_message['From'],
                        "subject": email_message['Subject'],
                        "date": email_message['Date'],
                        "timestamp": datetime.now().isoformat()
                    })
                except Exception as e:
                    logger.warning(f"Error parsing message {msg_id}: {e}")
                    continue
            
            mail.logout()
            return messages
            
        except Exception as e:
            logger.error(f"Gmail check failed: {e}")
            return []
    
    def _get_telegram_messages(self) -> List[Dict]:
        """Get recent Telegram messages"""
        if not self.config["platforms"]["telegram"]["enabled"]:
            return []
            
        try:
            bot_token = self.config["platforms"]["telegram"]["bot_token"]
            chat_id = self.config["platforms"]["telegram"]["chat_id"]
            
            if not bot_token or not chat_id:
                logger.warning("Telegram credentials not configured - check .hermes/env file")
                return []
            
            # Simulate checking messages (in real implementation, use python-telegram-bot API)
            logger.info(f"📱 Simulating Telegram message check for chat {chat_id}")
            
            # Simulate finding some messages randomly (for demo purposes)
            import random
            recent_messages = random.randint(0, 3)
            
            messages = []
            for i in range(recent_messages):
                messages.append({
                    "id": f"telegram_{int(time.time())}_{i}",
                    "from": f"user_{random.randint(1000, 9999)}",
                    "message": f"Sample Telegram message {i+1}",
                    "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "timestamp": datetime.now().isoformat()
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"Telegram check failed: {e}")
            return []
    
    def _get_whatsapp_messages(self) -> List[Dict]:
        """Get recent WhatsApp messages"""
        if not self.config["platforms"]["whatsapp"]["enabled"]:
            return []
            
        try:
            api_key = self.config["platforms"]["whatsapp"]["api_key"]
            instance_id = self.config["platforms"]["whatsapp"]["instance_id"]
            
            if not api_key or not instance_id:
                logger.warning("WhatsApp credentials not configured - check .hermes/env file")
                return []
            
            # Simulate checking messages (in real implementation, use WhatsApp Business API)
            logger.info(f"📱 Simulating WhatsApp message check for instance {instance_id}")
            
            # Simulate finding some messages randomly (for demo purposes)
            import random
            recent_messages = random.randint(0, 2)
            
            messages = []
            for i in range(recent_messages):
                messages.append({
                    "id": f"whatsapp_{int(time.time())}_{i}",
                    "from": f"+1{random.randint(1000, 9999)}",
                    "message": f"Sample WhatsApp message {i+1}",
                    "date": datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
                    "timestamp": datetime.now().isoformat()
                })
            
            return messages
            
        except Exception as e:
            logger.error(f"WhatsApp check failed: {e}")
            return []
    
    def _get_linkedin_messages(self) -> List[Dict]:
        """Get recent LinkedIn messages"""
        if not self.config["platforms"]["linkedin"]["enabled"]:
            return []
            
        try:
            access_token = self.config["platforms"]["linkedin"]["access_token"]
            
            if not access_token:
                logger.warning("LinkedIn credentials not configured - check .hermes/env file")
                return []
            
            # Simulate checking messages (in real implementation, use LinkedIn API)
            logger.info("LinkedIn message checking would be implemented with LinkedIn API")
            return []
            
        except Exception as e:
            logger.error(f"LinkedIn check failed: {e}")
            return []
    
    def _send_notification(self, platform: str, messages: List[Dict]):
        """Send notification for new messages"""
        if not self.notifications_enabled:
            return
        
        if len(messages) < self.config["notification"]["min_new_messages"]:
            return
        
        # Create notification message
        notification_msg = f"📱 NEW MESSAGES DETECTED\n"
        notification_msg += f"Platform: {platform.upper()}\n"
        notification_msg += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
        notification_msg += f"Messages: {len(messages)}\n"
        
        for i, msg in enumerate(messages, 1):
            content_preview = msg.get('message', msg.get('subject', 'No content'))[:50]
            notification_msg += f"{i}. {msg.get('from', 'Unknown')}: {content_preview}...\n"
        
        notification_msg += f"\nCheck your {platform} account for details."
        
        # Simple notification - just log to file and console
        notification_file = f"/tmp/notification_{platform}_{int(time.time())}.txt"
        try:
            with open(notification_file, 'w') as f:
                f.write(notification_msg)
            
            logger.info(f"✅ Notification saved for {platform}: {len(messages)} new messages")
            logger.info(f"📄 Notification saved to: {notification_file}")
            
        except Exception as e:
            logger.error(f"Failed to save notification: {e}")
    
    def run_check(self):
        """Run complete message check for all platforms"""
        logger.info("🔍 Starting unified message check...")
        
        # Define platform checkers
        platform_checkers = {
            "gmail": self._get_gmail_messages,
            "telegram": self._get_telegram_messages,
            "whatsapp": self._get_whatsapp_messages,
            "linkedin": self._get_linkedin_messages,
        }
        
        total_new_messages = 0
        notifications_sent = 0
        
        for platform, checker_func in platform_checkers.items():
            if not self.config["platforms"][platform]["enabled"]:
                continue
                
            try:
                logger.info(f"📨 Checking {platform.upper()}...")
                has_new, messages = self.tracker.has_new_messages(platform, checker_func)
                
                if has_new:
                    total_new_messages += len(messages)
                    notifications_sent += 1
                    self._send_notification(platform, messages)
                    logger.info(f"✅ {platform.upper()}: {len(messages)} new messages detected")
                else:
                    logger.info(f"📭 {platform.upper()}: No new messages")
                    
            except Exception as e:
                logger.error(f"Error checking {platform}: {e}")
        
        logger.info(f"🎯 Check completed: {total_new_messages} total new messages, {notifications_sent} notifications sent")
        
        # Log summary
        if total_new_messages > 0:
            logger.info(f"📱 SUMMARY: {total_new_messages} new messages detected across {notifications_sent} platforms")
        else:
            logger.info(f"📱 SUMMARY: No new messages detected")
    
    def test_configuration(self):
        """Test current configuration"""
        logger.info("🧪 Testing configuration...")
        
        # Check if required config is present
        issues = []
        
        for platform, config in self.config["platforms"].items():
            if config["enabled"]:
                for key, value in config.items():
                    if key != "enabled" and key != "check_interval_minutes":
                        if not value:
                            issues.append(f"{platform}.{key} is not configured")
        
        if issues:
            logger.warning("Configuration issues found:")
            for issue in issues:
                logger.warning(f"  - {issue}")
            logger.warning("ℹ️  To enable a platform, add to ~/.hermes/env:")
            logger.warning("  {")
            logger.warning("    \"platforms\": {")
            logger.warning("      \"gmail\": { \"enabled\": true, \"email\": \"[EMAIL]\", \"password\": \"your_password\" }")
            logger.warning("    }")
            logger.warning("  }")
            return False
        else:
            logger.info("✅ All platform configurations valid")
            return True


def main():
    """Main execution function"""
    try:
        logger.info("🚀 Starting Unified Message Checker...")
        
        # Create checker instance
        checker = UnifiedMessageChecker()
        
        # Test configuration first
        if not checker.test_configuration():
            logger.warning("⚠️  Configuration not fully set up - continuing anyway")
        
        # Run message check
        checker.run_check()
        
        logger.info("✅ Unified Message Checker completed successfully")
        
    except KeyboardInterrupt:
        logger.info("🛑 Interrupted by user")
        sys.exit(0)
    except Exception as e:
        logger.error(f"💥 Fatal error: {e}")
        sys.exit(1)

if __name__ == "__main__":
    import time
    main()