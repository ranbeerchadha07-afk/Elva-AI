import os
import json
import logging
from typing import Dict, List, Optional, Any
from datetime import datetime, timedelta
from pathlib import Path
from cryptography.fernet import Fernet
import base64

logger = logging.getLogger(__name__)

class CookieManager:
    """
    Secure cookie management system for Playwright automation
    Handles saving, loading, and encrypting session cookies
    """
    
    def __init__(self, cookies_dir: str = "cookies"):
        self.cookies_dir = Path(cookies_dir)
        self.cookies_dir.mkdir(exist_ok=True)
        self.encryption_key = self._get_or_create_encryption_key()
        self.fernet = Fernet(self.encryption_key)
        
    def _get_or_create_encryption_key(self) -> bytes:
        """Get or create encryption key for cookie security"""
        key_file = self.cookies_dir / ".key"
        
        if key_file.exists():
            with open(key_file, 'rb') as f:
                return f.read()
        else:
            key = Fernet.generate_key()
            with open(key_file, 'wb') as f:
                f.write(key)
            return key
    
    def save_cookies(self, service_name: str, user_identifier: str, cookies: List[Dict[str, Any]]) -> bool:
        """
        Save cookies securely for a specific service and user
        
        Args:
            service_name: Service identifier (e.g., 'linkedin', 'gmail', 'outlook')
            user_identifier: User identifier (e.g., email or username)
            cookies: List of cookie dictionaries from Playwright
            
        Returns:
            bool: Success status
        """
        try:
            # Create filename with service and user identifier
            safe_identifier = user_identifier.replace('@', '_at_').replace('.', '_dot_')
            cookie_file = self.cookies_dir / f"{service_name}_{safe_identifier}.json"
            
            # Prepare cookie data with metadata
            cookie_data = {
                "service": service_name,
                "user": user_identifier,
                "cookies": cookies,
                "saved_at": datetime.utcnow().isoformat(),
                "expires_at": (datetime.utcnow() + timedelta(days=30)).isoformat()  # 30 days expiry
            }
            
            # Encrypt and save
            json_data = json.dumps(cookie_data).encode()
            encrypted_data = self.fernet.encrypt(json_data)
            
            with open(cookie_file, 'wb') as f:
                f.write(encrypted_data)
                
            logger.info(f"✅ Cookies saved for {service_name} user {user_identifier}")
            return True
            
        except Exception as e:
            logger.error(f"❌ Failed to save cookies for {service_name}: {e}")
            return False
    
    def load_cookies(self, service_name: str, user_identifier: str) -> Optional[List[Dict[str, Any]]]:
        """
        Load cookies for a specific service and user
        
        Args:
            service_name: Service identifier
            user_identifier: User identifier
            
        Returns:
            List of cookies or None if not found/expired
        """
        try:
            safe_identifier = user_identifier.replace('@', '_at_').replace('.', '_dot_')
            cookie_file = self.cookies_dir / f"{service_name}_{safe_identifier}.json"
            
            if not cookie_file.exists():
                logger.warning(f"⚠️ No cookies found for {service_name} user {user_identifier}")
                return None
            
            # Load and decrypt
            with open(cookie_file, 'rb') as f:
                encrypted_data = f.read()
                
            json_data = self.fernet.decrypt(encrypted_data)
            cookie_data = json.loads(json_data.decode())
            
            # Check if cookies are still valid
            expires_at = datetime.fromisoformat(cookie_data.get('expires_at', ''))
            if datetime.utcnow() > expires_at:
                logger.warning(f"⚠️ Cookies expired for {service_name} user {user_identifier}")
                self.delete_cookies(service_name, user_identifier)
                return None
            
            logger.info(f"✅ Cookies loaded for {service_name} user {user_identifier}")
            return cookie_data['cookies']
            
        except Exception as e:
            logger.error(f"❌ Failed to load cookies for {service_name}: {e}")
            return None
    
    def delete_cookies(self, service_name: str, user_identifier: str) -> bool:
        """Delete cookies for a specific service and user"""
        try:
            safe_identifier = user_identifier.replace('@', '_at_').replace('.', '_dot_')
            cookie_file = self.cookies_dir / f"{service_name}_{safe_identifier}.json"
            
            if cookie_file.exists():
                cookie_file.unlink()
                logger.info(f"🗑️ Cookies deleted for {service_name} user {user_identifier}")
                return True
            
            return False
            
        except Exception as e:
            logger.error(f"❌ Failed to delete cookies for {service_name}: {e}")
            return False
    
    def list_saved_sessions(self) -> List[Dict[str, str]]:
        """List all saved cookie sessions"""
        sessions = []
        
        try:
            for cookie_file in self.cookies_dir.glob("*.json"):
                if cookie_file.name.startswith('.'):
                    continue
                    
                try:
                    with open(cookie_file, 'rb') as f:
                        encrypted_data = f.read()
                        
                    json_data = self.fernet.decrypt(encrypted_data)
                    cookie_data = json.loads(json_data.decode())
                    
                    sessions.append({
                        "service": cookie_data['service'],
                        "user": cookie_data['user'],
                        "saved_at": cookie_data['saved_at'],
                        "expires_at": cookie_data['expires_at'],
                        "status": "valid" if datetime.utcnow() < datetime.fromisoformat(cookie_data['expires_at']) else "expired"
                    })
                    
                except Exception as e:
                    logger.warning(f"Failed to read cookie file {cookie_file}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to list sessions: {e}")
            
        return sessions
    
    def cleanup_expired_cookies(self) -> int:
        """Remove all expired cookie files"""
        cleaned_count = 0
        
        try:
            for cookie_file in self.cookies_dir.glob("*.json"):
                if cookie_file.name.startswith('.'):
                    continue
                    
                try:
                    with open(cookie_file, 'rb') as f:
                        encrypted_data = f.read()
                        
                    json_data = self.fernet.decrypt(encrypted_data)
                    cookie_data = json.loads(json_data.decode())
                    
                    expires_at = datetime.fromisoformat(cookie_data.get('expires_at', ''))
                    if datetime.utcnow() > expires_at:
                        cookie_file.unlink()
                        cleaned_count += 1
                        logger.info(f"🧹 Cleaned expired cookies for {cookie_data['service']} user {cookie_data['user']}")
                        
                except Exception as e:
                    logger.warning(f"Failed to process cookie file {cookie_file}: {e}")
                    continue
                    
        except Exception as e:
            logger.error(f"Failed to cleanup expired cookies: {e}")
            
        return cleaned_count

# Global cookie manager instance
cookie_manager = CookieManager()