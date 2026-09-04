"""
Shared utilities for all sync engines.
Includes DB operations, API calls, Discord/Telegram/Zulip communication.
"""

import os
import json
import time
import requests
import logging
from typing import Any, Dict, Optional, Tuple
from datetime import datetime, timezone
from requests.auth import HTTPBasicAuth

from config import Config

# ==================== LOGGING SETUP ====================
logger = logging.getLogger('sync_engine')
logger.setLevel(logging.INFO)
handler = logging.StreamHandler()
formatter = logging.Formatter('[%(levelname)s] %(message)s')
handler.setFormatter(formatter)
if not logger.handlers:
    logger.addHandler(handler)


# ==================== DATABASE OPERATIONS ====================
def load_db(filepath: str) -> Dict[str, Any]:
    """
    Load JSON database file with error handling.
    Returns empty dict if file doesn't exist or is corrupted.
    """
    if not os.path.exists(filepath):
        return {}
    
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except json.JSONDecodeError as e:
        logger.warning(f"Corrupted JSON in {filepath}: {e}")
        return {}
    except Exception as e:
        logger.error(f"Failed to load {filepath}: {e}")
        return {}


def save_db(filepath: str, data: Dict[str, Any]) -> bool:
    """
    Save database to JSON file atomically.
    Uses temp file to prevent corruption on crash.
    Returns True if successful.
    """
    try:
        # Ensure directory exists
        os.makedirs(os.path.dirname(filepath) or '.', exist_ok=True)
        
        # Write to temp file first
        tmp_path = filepath + '.tmp'
        with open(tmp_path, 'w', encoding='utf-8') as f:
            json.dump(data, f, indent=2, ensure_ascii=False)
        
        # Atomic rename
        os.replace(tmp_path, filepath)
        return True
    except Exception as e:
        logger.error(f"Failed to save {filepath}: {e}")
        return False


def safe_int(val: Any, default: int = 0) -> int:
    """
    Safely convert value to integer, extracting from strings if needed.
    """
    if val is None:
        return default
    try:
        return int(val)
    except (ValueError, TypeError):
        import re
        match = re.search(r'-?\d+', str(val))
        return int(match.group()) if match else default


# ==================== API RETRY LOGIC ====================
def request_with_retry(
    method: str,
    url: str,
    headers: Optional[Dict] = None,
    json_data: Optional[Dict] = None,
    retries: int = None,
    timeout: int = 15
) -> Optional[requests.Response]:
    """
    Make HTTP request with exponential backoff retry logic.
    Respects Retry-After header and handles rate limits.
    """
    if retries is None:
        retries = Config.MAX_RETRIES
    
    headers = headers or {}
    
    for attempt in range(retries):
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                json=json_data,
                timeout=timeout
            )
            
            # Success
            if response.status_code == 200:
                return response
            
            # Rate limit or server error - retry
            if response.status_code in [429, 500, 502, 503, 504]:
                retry_after = response.headers.get('Retry-After')
                delay = max(2, int(float(retry_after))) if retry_after else 0
                delay = delay or (Config.RETRY_BACKOFF_BASE ** attempt)
                
                logger.warning(
                    f"HTTP {response.status_code} on {url}. "
                    f"Retrying in {delay}s... (attempt {attempt + 1}/{retries})"
                )
                time.sleep(delay)
                continue
            
            # Other errors - return response (caller decides)
            return response
        
        except requests.RequestException as e:
            if attempt == retries - 1:
                logger.error(f"Request failed after {retries} attempts: {e}")
                return None
            
            delay = Config.RETRY_BACKOFF_BASE ** attempt
            logger.warning(f"Request failed: {e}. Retrying in {delay}s...")
            time.sleep(delay)
    
    return None


# ==================== ANILIST GRAPHQL ====================
def get_anilist_headers() -> Dict[str, str]:
    """Get headers for AniList GraphQL requests"""
    return {
        'Authorization': f'Bearer {Config.ANILIST_TOKEN}' if Config.ANILIST_TOKEN else '',
        'Content-Type': 'application/json',
        'Accept': 'application/json',
    }


def query_anilist(query: str, variables: Dict[str, Any]) -> Optional[Dict]:
    """
    Execute AniList GraphQL query.
    Returns the 'data' section of response or None on failure.
    """
    response = request_with_retry(
        'POST',
        Config.ANILIST_ENDPOINT,
        headers=get_anilist_headers(),
        json_data={'query': query, 'variables': variables},
        timeout=Config.REQUEST_TIMEOUT
    )
    
    if not response:
        return None
    
    try:
        data = response.json()
        
        if data.get('errors'):
            logger.error(f"AniList GraphQL errors: {data['errors']}")
            return None
        
        return data.get('data')
    except json.JSONDecodeError as e:
        logger.error(f"Failed to parse AniList response: {e}")
        return None


# ==================== DISCORD COMMUNICATION ====================
def hex_to_int(hex_color: Optional[str]) -> int:
    """Convert hex color to Discord embed color integer"""
    if not hex_color:
        return 3447003
    try:
        return int(hex_color.lstrip('#'), 16)
    except (ValueError, AttributeError):
        return 3447003


def send_discord_alert(
    webhook_url: str,
    title: str,
    description: str,
    color: int,
    image: Optional[str] = None,
    fields: Optional[list] = None,
    author: Optional[Dict] = None,
    username: Optional[str] = None,
    thread_id: Optional[str] = None
) -> bool:
    """
    Send Discord embed message.
    Returns True if successful.
    """
    if not webhook_url:
        return False
    
    try:
        # Add thread_id to URL if provided
        target_url = webhook_url
        if thread_id and thread_id != "IGNORE":
            separator = "&" if "?" in target_url else "?"
            target_url = f"{target_url}{separator}thread_id={thread_id}"
        
        # Build embed
        embed = {
            "title": title[:256],
            "description": description,
            "color": color,
            "timestamp": datetime.now(timezone.utc).isoformat()
        }
        
        if fields:
            embed["fields"] = fields[:Config.DISCORD_EMBED_LIMIT]
        if image:
            embed["image"] = {"url": image}
        if author:
            embed["author"] = author
        
        payload = {"embeds": [embed]}
        if username:
            payload["username"] = username
        
        response = request_with_retry(
            'POST',
            target_url,
            json_data=payload,
            timeout=Config.DISCORD_TIMEOUT
        )
        
        if response and response.status_code in [200, 201, 204]:
            return True
        
        logger.error(
            f"Discord alert failed: {response.status_code if response else 'No response'} - {title}"
        )
        return False
    
    except Exception as e:
        logger.error(f"Discord transmission failed: {e}")
        return False


# ==================== TELEGRAM ====================
def send_telegram_alert(
    message: str,
    image_url: Optional[str] = None
) -> bool:
    """Send Telegram message or photo"""
    if not Config.TELEGRAM_TOKEN or not Config.TELEGRAM_CHAT_ID:
        return False
    
    try:
        if image_url:
            url = f"https://api.telegram.org/bot{Config.TELEGRAM_TOKEN}/sendPhoto"
            payload = {
                "chat_id": Config.TELEGRAM_CHAT_ID,
                "photo": image_url,
                "caption": message,
                "parse_mode": "Markdown"
            }
        else:
            url = f"https://api.telegram.org/bot{Config.TELEGRAM_TOKEN}/sendMessage"
            payload = {
                "chat_id": Config.TELEGRAM_CHAT_ID,
                "text": message,
                "parse_mode": "Markdown"
            }
        
        response = request_with_retry(
            'POST',
            url,
            json_data=payload,
            timeout=Config.TELEGRAM_TIMEOUT
        )
        
        return response and response.status_code == 200
    
    except Exception as e:
        logger.error(f"Telegram alert failed: {e}")
        return False


# ==================== ZULIP ====================
def send_zulip_message(
    stream: str,
    topic: str,
    content: str
) -> bool:
    """Send Zulip message"""
    if not Config.ZULIP_SERVER_URL or not Config.ZULIP_BOT_EMAIL or not Config.ZULIP_API_KEY:
        return False
    
    try:
        payload = {
            "type": "stream",
            "to": stream,
            "topic": topic,
            "content": content
        }
        
        response = request_with_retry(
            'POST',
            Config.ZULIP_SERVER_URL,
            json_data=payload,
            headers={"Authorization": f"Basic {Config.ZULIP_API_KEY}"},
            timeout=Config.ZULIP_TIMEOUT,
            retries=2
        )
        
        return response and response.status_code == 200
    
    except Exception as e:
        logger.error(f"Zulip message failed: {e}")
        return False


# ==================== TIME & DATE UTILITIES ====================
def get_performance_paths() -> Dict[str, str]:
    """Get all performance data file paths for current period"""
    now = datetime.now(timezone.utc)
    day_str = now.strftime("%Y-%m-%d")
    week_str = f"{now.isocalendar()[0]}-W{now.isocalendar()[1]:02d}"
    month_str = now.strftime("%Y-%m")
    year_str = now.strftime("%Y")
    
    return {
        "daily": f"performance/daily/{day_str}.json",
        "weekly": f"performance/weekly/{week_str}.json",
        "monthly": f"performance/monthly/{month_str}.json",
        "yearly": f"performance/yearly/{year_str}.json",
        "lifetime": "performance/lifetime.json"
    }


def ensure_performance_dirs():
    """Create performance data directories if they don't exist"""
    for folder in Config.PERFORMANCE_DIRS:
        os.makedirs(f"performance/{folder}", exist_ok=True)


# ==================== CLEANUP UTILITIES ====================
def cleanup_old_messages(db_file: str, max_age_seconds: int = 172800) -> int:
    """
    Remove messages older than max_age_seconds from database.
    Returns count of deleted messages.
    """
    messages_db = load_db(db_file)
    if isinstance(messages_db, list):
        messages_db = {}
    
    current_time = time.time()
    deleted = 0
    keys_to_delete = []
    
    for msg_id, data in messages_db.items():
        if current_time - data.get("timestamp", 0) > max_age_seconds:
            keys_to_delete.append(msg_id)
    
    for key in keys_to_delete:
        # Try to delete from Discord
        try:
            delete_url = messages_db[key].get("delete_url")
            if delete_url:
                requests.delete(delete_url, timeout=5)
        except Exception as e:
            logger.warning(f"Failed to delete Discord message {key}: {e}")
        
        del messages_db[key]
        deleted += 1
        time.sleep(0.5)  # Rate limit
    
    if deleted > 0:
        save_db(db_file, messages_db)
        logger.info(f"Cleaned up {deleted} old messages from {db_file}")
    
    return deleted


# ==================== FORMATTING UTILITIES ====================
def format_number(num: int) -> str:
    """Format number with commas"""
    return f"{num:,}"


def format_delta(old: int, new: int) -> str:
    """Format progress delta"""
    delta = new - old
    if delta > 0:
        return f"+{delta}"
    return str(delta)


# ==================== VALIDATION ====================
def validate_environment() -> bool:
    """Check if required environment variables are set"""
    missing = []
    
    if not Config.ANILIST_TOKEN:
        missing.append("ANILIST_TARGET_TOKEN")
    
    if missing:
        logger.error(f"Missing environment variables: {', '.join(missing)}")
        return False
    
    return True
