import os
import json
import time
import requests
import random
import re
import xml.etree.ElementTree as ET
from datetime import datetime, timezone, date
from requests.auth import HTTPBasicAuth

# ==========================================
# ⚙️ 1. SYSTEM CONFIGURATION & SECRETS (ANIME ISOLATED)
# ==========================================
SOURCE_USERNAME = "Orewatokyo"
TARGET_TOKEN = os.environ.get('ANILIST_TARGET_TOKEN')

WEBHOOK_ANIME = os.environ.get('DISCORD_ANILIST_ANIME_WEBHOOK')
WEBHOOK_LOG = os.environ.get('DISCORD_ANILIST_LOG_WEBHOOK')
WEBHOOK_AIRING = os.environ.get('DISCORD_AIRING_WEBHOOK')
WEBHOOK_VIP = os.environ.get('DISCORD_FAVORITES_WEBHOOK')
WEBHOOK_GHOST = os.environ.get('DISCORD_GHOST_RADAR_WEBHOOK')
WEBHOOK_ACHIEVEMENTS = os.environ.get('DISCORD_ACHIEVEMENTS_WEBHOOK') 
WEBHOOK_PERFORMANCE = os.environ.get('DISCORD_PERFORMANCE_WEBHOOK') 

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

ZULIP_URL = os.environ.get('ZULIP_SERVER_URL')
ZULIP_EMAIL = os.environ.get('ZULIP_BOT_EMAIL')
ZULIP_API_KEY = os.environ.get('ZULIP_API_KEY')

# ⚡ Anime-Specific Memory Vaults
DB_SYNC = 'db_anime_sync.json'
DB_MESSAGES = 'db_anime_messages.json'
DB_GHOSTS = 'db_anime_ghosts.json'
DB_VOID = 'db_anime_void.json'
DB_AIRING = 'db_anime_airing.json'
DB_ACHIEVEMENTS = 'db_anime_achievements.json' 
DB_PERFORMANCE_MSG = 'db_anime_performance_msg.json'
DB_THREADS = 'db_anime_threads.json'     
DB_INVENTORY = 'db_anime_inventory.json' 
DB_TIMESTAMP = 'db_anime_timestamp.json' 
XML_FILE_PATH = 'mal_export.xml'

PRIORITY_FAVORITES = ["One Piece", "Detective Conan", "Kono Suba", "Dragon Ball Z"]

HEADERS = {
    'Authorization': f'Bearer {TARGET_TOKEN}' if TARGET_TOKEN else '',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

# ⚡ V3 PERFORMANCE CONTROLS
REQUEST_TIMEOUT = 15
FULL_SYNC_INTERVAL = 24 * 60 * 60          # Full reconciliation once per day.
GHOST_INITIAL_COOLDOWN = 6 * 60 * 60       # First failed lookup retries after 6 hours.
MAX_ENTITY_COOLDOWN = 7 * 24 * 60 * 60     # Never retry ghosts/void more than once per week.
AIRING_BATCH_SIZE = 50

# Reuse HTTP connections across the entire run.
SESSION = requests.Session()

# Batch disk writes during a run.
PERFORMANCE_CACHE = {}
PERFORMANCE_DIRTY = set()
ACHIEVEMENT_CACHE = None
ACHIEVEMENT_DIRTY = False

def load_db(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f: return json.load(f)
        except Exception: return {}
    return {}

def save_db(filepath, data):
    # Avoid touching files when content is unchanged.
    try:
        serialized = json.dumps(data, indent=4, ensure_ascii=False)
        if os.path.exists(filepath):
            with open(filepath, 'r', encoding='utf-8') as f:
                if f.read() == serialized:
                    return False
        with open(filepath, 'w', encoding='utf-8') as f:
            f.write(serialized)
        return True
    except Exception as e:
        print(f"[WARN] Could not save '{filepath}': {e}")
        return False

def safe_int(val, default=0):
    if val is None: return default
    try:
        match = re.search(r'-?\d+', str(val))
        return int(match.group()) if match else default
    except Exception:
        return default
        
# ==========================================
# 🧵 1.5. SELECTIVE THREAD ROUTER
# ==========================================
TARGET_LISTS = [
    "anime movies", "iseki", "isekai", "milf", "loli", "rom com",
    "plan to continue", "hentai", "favourite", "fav", "planning"
]

def get_or_create_thread(list_name, media_type, base_webhook):
    if not base_webhook: return None
    threads = load_db(DB_THREADS)
    
    # ⚡ SAFETY FIX: Prevent NoneType errors if list_name is empty
    clean_name = str(list_name or "Unknown").lower().strip()
    
    # ⚡ THE CATCH-ALL
    if clean_name not in TARGET_LISTS:
        display_name = "General Updates"
    else:
        display_name = str(list_name).title()
        
    thread_key = f"[{media_type}] {display_name}" 
    
    if thread_key in threads and threads[thread_key] and threads[thread_key] != "None":
        return str(threads[thread_key])
        
    print(f"[SYSTEM] Forging new dedicated Forum thread: '{thread_key}'...")
    
    payload = {
        "content": f"📡 **{display_name}** | {media_type} Telemetry Dashboard",
        "thread_name": thread_key
    }
    
    target_url = base_webhook
    separator = "&" if "?" in target_url else "?"
    target_url = f"{target_url}{separator}wait=true"
    
    try:
        res = SESSION.post(target_url, json=payload, timeout=15)
        if res.status_code in [200, 201, 204]:
            try:
                response_data = res.json()
            except Exception:
                response_data = {}

            new_thread_id = str(response_data.get('channel_id') or response_data.get('id') or '').strip()
            if new_thread_id and new_thread_id != "None":
                threads[thread_key] = new_thread_id
                save_db(DB_THREADS, threads)
                return new_thread_id

            print(f"[ERROR] Discord created the thread but returned no usable thread ID. Response: {res.text}")
        else:
            print(f"[ERROR] Failed to forge thread. Code: {res.status_code} | Reason: {res.text}")
    except Exception as e:
        print(f"[ERROR] Thread network failure: {e}")

    return None


# ==========================================
# 📊 2. THE V2 TELEMETRY HUB
# ==========================================
def _performance_path_map():
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
        "lifetime": "performance/lifetime.json",
    }


def update_performance_vault(media_type, delta, duration, g_earned, is_completed):
    paths = _performance_path_map()
    for folder in ["daily", "weekly", "monthly", "yearly"]:
        os.makedirs(f"performance/{folder}", exist_ok=True)

    ep_add = safe_int(delta) if media_type == "ANIME" else 0
    anime_time = ep_add * max(1, safe_int(duration, 24) - 2) if media_type == "ANIME" else 0
    comp_add = 1 if is_completed else 0

    for key, path in paths.items():
        if path not in PERFORMANCE_CACHE:
            cached = load_db(path)
            PERFORMANCE_CACHE[path] = cached if isinstance(cached, dict) else {}

        data = PERFORMANCE_CACHE[path]
        data["episodes"] = data.get("episodes", 0) + ep_add
        data["anime_minutes"] = data.get("anime_minutes", 0) + anime_time
        data["g_score"] = data.get("g_score", 0) + g_earned
        if key == "lifetime":
            data["completed"] = data.get("completed", 0) + comp_add
        PERFORMANCE_DIRTY.add(path)


def flush_performance_vault():
    for path in list(PERFORMANCE_DIRTY):
        save_db(path, PERFORMANCE_CACHE.get(path, {}))
        PERFORMANCE_DIRTY.discard(path)


def get_performance_stats():
    paths = _performance_path_map()

    def get_data(path):
        if path in PERFORMANCE_CACHE:
            return PERFORMANCE_CACHE[path]
        return load_db(path)

    return {
        "daily": get_data(paths["daily"]),
        "weekly": get_data(paths["weekly"]),
        "lifetime": get_data(paths["lifetime"]),
    }

# ==========================================
# 🛡️ 3. TITANIUM ARMOR (API RETRY LOGIC)
# ==========================================
def _retry_after_seconds(response, default=3):
    try:
        value = response.headers.get("Retry-After")
        if value is None:
            return default
        return max(1, min(60, int(float(value))))
    except Exception:
        return default


def fetch_with_armor(url, payload, headers, retries=3):
    # Retry only transient failures. Fail fast on auth/validation errors.
    for attempt in range(retries):
        try:
            res = SESSION.post(url, json=payload, headers=headers, timeout=REQUEST_TIMEOUT)

            if res.status_code == 200:
                return res

            if res.status_code in {400, 401, 403, 404, 405, 422}:
                print(f"[ERROR] AniList request rejected: HTTP {res.status_code} | {res.text[:300]}")
                return None

            if res.status_code == 429:
                if attempt >= retries - 1:
                    return None
                delay = _retry_after_seconds(res, default=min(60, 3 * (attempt + 1)))
                print(f"[RATE LIMIT] AniList requested {delay}s delay before retry.")
                time.sleep(delay)
                continue

            if 500 <= res.status_code < 600 and attempt < retries - 1:
                delay = min(20, 2 ** attempt)
                print(f"[RETRY] AniList server error {res.status_code}; retrying in {delay}s.")
                time.sleep(delay)
                continue

            print(f"[ERROR] AniList request failed: HTTP {res.status_code} | {res.text[:300]}")
            return None

        except requests.RequestException as e:
            if attempt >= retries - 1:
                print(f"[ERROR] AniList network failure: {e}")
                return None
            delay = min(20, 2 ** attempt)
            print(f"[RETRY] AniList network failure; retrying in {delay}s.")
            time.sleep(delay)

    return None

# ==========================================
# 📡 4. COMMUNICATION PROTOCOLS
# ==========================================
def send_discord_alert(webhook_url, title, desc, color, image=None, fields=None, author=None, override_tag=None, thread_id=None):
    if not webhook_url: return
    
    target_url = webhook_url
    if thread_id and thread_id != "IGNORE":
        separator = "&" if "?" in target_url else "?"
        target_url = f"{target_url}{separator}thread_id={thread_id}"
        
    embed = {
        "title": title[:256],
        "description": desc,
        "color": color
    }
    
    if fields: embed["fields"] = fields[:25]
    if image: embed["image"] = {"url": image}
    if author: embed["author"] = author
    
    payload = {"embeds": [embed]}
    if override_tag: payload["username"] = override_tag
    
    try:
        res = SESSION.post(target_url, json=payload, timeout=15)
        if res.status_code not in [200, 201, 204]:
            print(f"\n[ERROR] Discord rejected payload for '{title}'.")
            print(f"Status: {res.status_code} | Reason: {res.text}\n")
    except Exception as e:
        print(f"\n[ERROR] Discord transmission completely failed: {e}\n")

def fire_zulip_archive(media_type, title, progress, total_episodes, score):
    if not ZULIP_URL or not ZULIP_EMAIL or not ZULIP_API_KEY: return
    content = f"✅ **Sync Log Executed**\n* **📺 Watched Episode:** {progress} / {total_episodes if total_episodes else '?'}\n* **Current Score:** {score if score else 'Unrated'}"
    payload = {"type": "stream", "to": "Anime-Vault", "topic": title, "content": content}
    try: SESSION.post(ZULIP_URL, auth=HTTPBasicAuth(ZULIP_EMAIL, ZULIP_API_KEY), data=payload, timeout=10)
    except Exception: pass

def send_telegram_alert(message, image_url=None):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto" if image_url else f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "photo": image_url, "caption": message, "parse_mode": "Markdown"} if image_url else {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try: SESSION.post(url, json=payload, timeout=10)
    except Exception: pass

def execute_48hr_purge():
    messages_db = load_db(DB_MESSAGES)
    if isinstance(messages_db, list):
        messages_db = {}

    current_time = time.time()
    keys_to_delete = [
        msg_id for msg_id, data in messages_db.items()
        if isinstance(data, dict) and current_time - data.get("timestamp", current_time) > 172800
    ]

    for key in keys_to_delete:
        delete_url = messages_db[key].get("delete_url")
        if not delete_url:
            del messages_db[key]
            continue
        try:
            res = SESSION.delete(delete_url, timeout=10)
            if res.status_code == 429:
                delay = _retry_after_seconds(res, default=3)
                print(f"[RATE LIMIT] Purge delayed by {delay}s.")
                time.sleep(delay)
                res = SESSION.delete(delete_url, timeout=10)

            if res.status_code in {200, 204, 404}:
                del messages_db[key]
            else:
                print(f"[WARN] Could not purge Discord message {key}: HTTP {res.status_code}")
        except requests.RequestException as e:
            print(f"[WARN] Purge network failure for {key}: {e}")

    save_db(DB_MESSAGES, messages_db)

# ==========================================
# 🏆 5. THE RPG ENGINE (ACHIEVEMENTS)
# ==========================================
def hex_to_int(hex_color): return int(hex_color.lstrip('#'), 16) if hex_color else 3447003 

def manage_achievements_and_weekly(points_earned):
    global ACHIEVEMENT_CACHE, ACHIEVEMENT_DIRTY

    if ACHIEVEMENT_CACHE is None:
        ach_db = load_db(DB_ACHIEVEMENTS)
        if not isinstance(ach_db, dict):
            ach_db = {}
        if not ach_db or "current_week" not in ach_db:
            ach_db = {
                "lifetime_g": 0,
                "weekly_g": 0,
                "current_week": datetime.now(timezone.utc).isocalendar()[1],
            }
        ACHIEVEMENT_CACHE = ach_db

    ach_db = ACHIEVEMENT_CACHE
    current_week = datetime.now(timezone.utc).isocalendar()[1]

    if current_week != ach_db.get("current_week"):
        ach_db["weekly_g"] = 0
        ach_db["current_week"] = current_week

    old_weekly = ach_db.get("weekly_g", 0)
    ach_db["weekly_g"] = old_weekly + points_earned
    ach_db["lifetime_g"] = ach_db.get("lifetime_g", 0) + points_earned

    hit_1k = old_weekly < 1000 <= ach_db["weekly_g"]
    hit_5k = old_weekly < 5000 <= ach_db["weekly_g"]
    is_prestige = ach_db["lifetime_g"] >= 10000

    ACHIEVEMENT_DIRTY = True
    return ach_db, hit_1k, hit_5k, is_prestige


def flush_achievements():
    global ACHIEVEMENT_DIRTY
    if ACHIEVEMENT_CACHE is not None and ACHIEVEMENT_DIRTY:
        save_db(DB_ACHIEVEMENTS, ACHIEVEMENT_CACHE)
        ACHIEVEMENT_DIRTY = False


def drop_classified_ui(tier):
    if not WEBHOOK_ACHIEVEMENTS: return
    if tier == 1000: send_discord_alert(WEBHOOK_ACHIEVEMENTS, "💠 1,000 G REACHED", ">> CLASS-A MILESTONE CLEARED <<", 16776960, "https://i.imgur.com/QzXoX1j.gif")
    elif tier == 5000: send_discord_alert(WEBHOOK_ACHIEVEMENTS, "🔥 5,000 G: OVERDRIVE", ">> SYSTEM MAXIMIZED. APEX TIER REACHED <<", 16711680, "https://i.imgur.com/W2dM9Ue.gif")

# ==========================================
# 🔎 6. ANILIST GRAPHQL CORE (DELTA-SYNC)
# ==========================================
def fetch_latest_inventory_marker(username):
    query = """query ($userName: String) {
        Page(page: 1, perPage: 1) {
            mediaList(userName: $userName, type: ANIME, sort: [UPDATED_TIME_DESC]) {
                updatedAt
            }
        }
    }"""
    res = fetch_with_armor(
        'https://graphql.anilist.co',
        {'query': query, 'variables': {"userName": username}},
        HEADERS,
    )
    if not res:
        return None
    try:
        items = res.json().get('data', {}).get('Page', {}).get('mediaList', [])
        return safe_int(items[0].get('updatedAt')) if items else 0
    except (ValueError, TypeError, IndexError):
        return None


def refresh_cached_airing_data(inventory):
    media_ids = [safe_int(data.get("mediaId"), 0) for data in inventory.values()]
    media_ids = [mid for mid in media_ids if mid]
    if not media_ids:
        return False

    query = """query ($ids: [Int]) {
        Page(page: 1, perPage: 50) {
            media(id_in: $ids, type: ANIME) {
                id
                nextAiringEpisode { airingAt episode }
            }
        }
    }"""

    changed = False
    by_id = {safe_int(data.get("mediaId"), 0): data for data in inventory.values()}

    for start in range(0, len(media_ids), AIRING_BATCH_SIZE):
        res = fetch_with_armor(
            'https://graphql.anilist.co',
            {'query': query, 'variables': {"ids": media_ids[start:start + AIRING_BATCH_SIZE]}},
            HEADERS,
        )
        if not res:
            continue
        try:
            rows = res.json().get('data', {}).get('Page', {}).get('media', [])
        except (ValueError, TypeError):
            continue

        for row in rows:
            mid = safe_int(row.get("id"), 0)
            data = by_id.get(mid)
            if data is not None and data.get("nextAiring") != row.get("nextAiringEpisode"):
                data["nextAiring"] = row.get("nextAiringEpisode")
                changed = True
    return changed


def fetch_anilist_inventory(username):
    # ⚡ SHIELD: Exclusively pulls ANIME format
    query = '''
    query ($userName: String,$page: Int) {
      Page(page: $page, perPage: 50) {
        pageInfo { hasNextPage }
        mediaList(userName: $userName, type: ANIME, sort: [UPDATED_TIME_DESC]) {
          updatedAt
          mediaId progress score status customLists
          media {
            title { romaji english }
            type format episodes duration
            genres tags { name }
            coverImage { extraLarge color }
            nextAiringEpisode { airingAt episode }
          }
        }
      }
    }
    '''

    inventory = load_db(DB_INVENTORY)
    timestamps = load_db(DB_TIMESTAMP)
    if not isinstance(inventory, dict):
        inventory = {}
    if not isinstance(timestamps, dict):
        timestamps = {}

    last_sync = safe_int(timestamps.get("last_update"), 0)
    last_full_scan = safe_int(timestamps.get("last_full_scan"), 0)
    now = int(time.time())
    is_first_run = (last_sync == 0 or not inventory)
    force_full = is_first_run or (now - last_full_scan >= FULL_SYNC_INTERVAL)

    if not force_full:
        latest_update = fetch_latest_inventory_marker(username)
        if latest_update is not None and latest_update <= last_sync:
            print(">>> [SYSTEM] ANIME DELTA-SYNC: NO LIST CHANGES DETECTED.")
            if refresh_cached_airing_data(inventory):
                save_db(DB_INVENTORY, inventory)
            return inventory

    if is_first_run:
        print(">>> [SYSTEM] INITIATING ANIME DEEP ANALYSIS...")
    elif force_full:
        print(">>> [SYSTEM] DAILY ANIME RECONCILIATION...")
    else:
        print(">>> [SYSTEM] ANIME DELTA-SYNC ENGAGED...")

    page, has_next_page, highest_update = 1, True, last_sync
    fresh_inventory = {}

    while has_next_page:
        res = fetch_with_armor(
            'https://graphql.anilist.co',
            {'query': query, 'variables': {"userName": username, "page": page}},
            HEADERS,
        )
        if not res:
            # Keep the existing cache on a failed remote pull.
            return inventory

        try:
            data = res.json().get('data', {}).get('Page', {})
        except (ValueError, TypeError):
            return inventory

        has_next_page = data.get('pageInfo', {}).get('hasNextPage', False)

        for item in data.get('mediaList', []):
            try:
                if not item:
                    continue
                updated_at = safe_int(item.get('updatedAt'), 0)

                if not is_first_run and not force_full and updated_at <= last_sync:
                    has_next_page = False
                    break

                highest_update = max(highest_update, updated_at)
                media = item.get('media')
                if not media:
                    continue

                title_data = media.get('title') or {}
                primary_title = str(title_data.get('english') or title_data.get('romaji') or "Unknown_Classified_Media")
                genres = media.get('genres') or []
                tags = [t.get('name') for t in (media.get('tags') or []) if t.get('name')]
                descriptors = [g.lower() for g in genres] + [t.lower() for t in tags]
                format_type = media.get('format') or ""

                raw_custom = item.get('customLists')
                active_lists = [k for k, v in raw_custom.items() if v] if isinstance(raw_custom, dict) else []
                smart_category = None
                if active_lists:
                    smart_category = active_lists[0]
                else:
                    if format_type == "MOVIE": smart_category = "Anime movies"
                    elif "isekai" in descriptors: smart_category = "Iseki"
                    elif any(x in descriptors for x in ["hentai", "ecchi", "adult", "smut"]): smart_category = "Hentai"
                    elif any(x in descriptors for x in ["milf", "older woman", "mother"]): smart_category = "Milf"
                    elif "loli" in descriptors: smart_category = "Loli"

                raw_status = item.get('status') or "UNKNOWN"
                list_category = smart_category if smart_category else raw_status.replace('_', ' ').title()

                if is_first_run:
                    print(f"[SCAN/UPDATE] {primary_title[:40]:<40} -> Cached as: {list_category}")

                fresh_inventory[primary_title] = {
                    "mediaId": item.get('mediaId'),
                    "progress": item.get('progress', 0),
                    "status": raw_status,
                    "list_category": list_category,
                    "scoreRaw": item.get('score', 0),
                    "type": media.get('type') or 'UNKNOWN',
                    "cover": (media.get('coverImage') or {}).get('extraLarge'),
                    "color": (media.get('coverImage') or {}).get('color'),
                    "duration": media.get('duration') or 24,
                    "nextAiring": media.get('nextAiringEpisode'),
                    "romaji": title_data.get('romaji'),
                    "english": title_data.get('english'),
                    "total_episodes": media.get('episodes')
                }
            except Exception:
                continue
        page += 1

    # Full scans replace the cache, which also removes entries no longer on the source list.
    # An empty but successfully fetched full list is also a valid state and must clear stale data.
    if force_full:
        inventory = fresh_inventory
    elif fresh_inventory:
        inventory.update(fresh_inventory)

    timestamps = {
        "last_update": highest_update,
        "last_full_scan": now if force_full else last_full_scan,
    }
    save_db(DB_INVENTORY, inventory)
    save_db(DB_TIMESTAMP, timestamps)
    return inventory

# ==========================================
# ⏰ 7. AIRING INTELLIGENCE
# ==========================================
def process_airing_countdowns(inventory):
    airing_db = load_db(DB_AIRING)
    current_time = int(time.time())
    
    for title, data in inventory.items():
        next_airing = data.get('nextAiring')
        if not next_airing: continue
            
        time_until = next_airing['airingAt'] - current_time
        db_key = f"{data['mediaId']}_ep{next_airing['episode']}"
        current_status = airing_db.get(db_key, "none")
        
        if time_until > 0:
            alert_type, msg_title = None, ""
            if 3600 < time_until <= 10800 and current_status == "none":
                alert_type, msg_title = "3h", f"🕒 3-HOUR WARNING: Episode {next_airing['episode']}"
            elif 0 < time_until <= 3600 and current_status in ["none", "3h"]:
                alert_type, msg_title = "1h", f"🚨 FINAL 1-HOUR WARNING: Episode {next_airing['episode']}"
                send_telegram_alert(f"🚨 *FINAL 1-HOUR WARNING*\n\n📺 *{data['english'] or data['romaji']}*\nEpisode {next_airing['episode']} is dropping in under 60 minutes.", data.get('cover'))

            if alert_type:
                fields = [{"name": "🇯🇵 Romaji", "value": data['romaji'] or "N/A", "inline": False}, {"name": "📺 Telecast Time", "value": f"<t:{next_airing['airingAt']}:F>", "inline": False}, {"name": "⏳ Live Countdown", "value": f"<t:{next_airing['airingAt']}:R>", "inline": False}]
                send_discord_alert(WEBHOOK_AIRING, msg_title, "", hex_to_int(data["color"]), data.get('cover'), fields)
                airing_db[db_key] = alert_type
            
    save_db(DB_AIRING, airing_db)

# ==========================================
# 👻 8. MAL GHOST RADAR (RESTORED)
# ==========================================
def sweep_mal_xml(known_titles_pool):
    ghosts = load_db(DB_GHOSTS)
    if not isinstance(ghosts, dict):
        ghosts = {}

    if os.path.exists('mal_anime.xml'):
        try:
            for anime in ET.parse('mal_anime.xml').getroot().findall('anime'):
                title_node = anime.find('series_title')
                if title_node is None or not title_node.text:
                    continue
                title = title_node.text.strip()
                if title.lower() not in known_titles_pool and title not in ghosts:
                    ghosts[title] = {
                        "progress": safe_int(anime.findtext('my_watched_episodes') or 0),
                        "score": safe_int(anime.findtext('my_score') or 0),
                        "type": "ANIME",
                        "attempts": 0,
                        "next_check": 0,
                    }
        except Exception as e:
            print(f"[WARN] MAL XML sweep failed: {e}")
    return ghosts


def _entity_next_check(attempts):
    return int(time.time()) + min(MAX_ENTITY_COOLDOWN, GHOST_INITIAL_COOLDOWN * (2 ** max(0, attempts - 1)))


def execute_ghost_radar(ghost_db):
    if not ghost_db:
        return ghost_db

    assimilated = []
    now = int(time.time())
    search_query = '''query ($search: String,$type: MediaType) { Media (search: $search, type:$type) { id } }'''
    write_query = '''mutation ($id: Int,$prog: Int, $score: Int) { SaveMediaListEntry (mediaId:$id, progress: $prog, scoreRaw:$score) { id } }'''

    for title, data in list(ghost_db.items()):
        if not isinstance(data, dict):
            data = {"progress": 0, "score": 0, "type": "ANIME", "attempts": 0, "next_check": 0}
            ghost_db[title] = data
        if safe_int(data.get("next_check"), 0) > now:
            continue

        media_type = data.get("type", "ANIME")
        res = fetch_with_armor(
            'https://graphql.anilist.co',
            {'query': search_query, 'variables': {"search": title, "type": media_type}},
            HEADERS,
        )
        found = None
        if res:
            try:
                found = res.json().get('data', {}).get('Media')
            except (ValueError, TypeError):
                found = None

        if found:
            if TARGET_TOKEN:
                try:
                    SESSION.post(
                        'https://graphql.anilist.co',
                        json={'query': write_query, 'variables': {
                            "id": found['id'],
                            "prog": data.get("progress", 0),
                            "score": safe_int(data.get("score", 0)) * 10,
                        }},
                        headers=HEADERS,
                        timeout=REQUEST_TIMEOUT,
                    )
                except requests.RequestException as e:
                    print(f"[WARN] Ghost write-back failed for '{title}': {e}")
            send_discord_alert(WEBHOOK_GHOST, "🟢 GHOST ASSIMILATED", f"**{title}** recovered.", 3066993)
            assimilated.append(title)
        else:
            attempts = safe_int(data.get("attempts"), 0) + 1
            data["attempts"] = attempts
            data["next_check"] = _entity_next_check(attempts)
            send_discord_alert(
                WEBHOOK_LOG,
                "🔴 GHOST REJECTED / NOT FOUND",
                f"AniList could not locate: **{title}** ({media_type}). Next retry is scheduled automatically.",
                16711680,
            )

    for title in assimilated:
        del ghost_db[title]
    return ghost_db

# ==========================================
# 🌌 9. THE DEEP VOID PROTOCOL
# ==========================================
def execute_void_radar():
    void_db = load_db(DB_VOID)
    if not isinstance(void_db, dict) or not void_db:
        return void_db if isinstance(void_db, dict) else {}

    assimilated = []
    now = int(time.time())
    search_query = '''query ($search: String,$type: MediaType) { Media (search: $search, type:$type) { id } }'''
    write_query = '''mutation ($id: Int,$prog: Int, $score: Int) { SaveMediaListEntry (mediaId:$id, progress: $prog, scoreRaw:$score) { id } }'''

    for title, data in list(void_db.items()):
        if not isinstance(data, dict):
            data = {"progress": 0, "score": 0, "type": "ANIME", "attempts": 0, "next_check": 0}
            void_db[title] = data
        if safe_int(data.get("next_check"), 0) > now:
            continue

        media_type = data.get("type", "ANIME")
        res = fetch_with_armor(
            'https://graphql.anilist.co',
            {'query': search_query, 'variables': {"search": title, "type": media_type}},
            HEADERS,
        )
        found = None
        if res:
            try:
                found = res.json().get('data', {}).get('Media')
            except (ValueError, TypeError):
                found = None

        if found:
            if TARGET_TOKEN:
                try:
                    SESSION.post(
                        'https://graphql.anilist.co',
                        json={'query': write_query, 'variables': {
                            "id": found['id'],
                            "prog": data.get("progress", 0),
                            "score": safe_int(data.get("score", 0)) * 10,
                        }},
                        headers=HEADERS,
                        timeout=REQUEST_TIMEOUT,
                    )
                except requests.RequestException as e:
                    print(f"[WARN] Void write-back failed for '{title}': {e}")
            send_discord_alert(WEBHOOK_LOG, "🌌 VOID ENTITY ASSIMILATED", f"**{title}** has been recovered from the Deep Void.", 10181046)
            assimilated.append(title)
        else:
            attempts = safe_int(data.get("attempts"), 0) + 1
            data["attempts"] = attempts
            data["next_check"] = _entity_next_check(attempts)

    for title in assimilated:
        del void_db[title]
    return void_db

# ==========================================
# ⚡ 10. THE MASTER SYNC ENGINE (ANIME CORE)
# ==========================================
def execute_master_sync(inventory):
    sync_db = load_db(DB_SYNC)
    hologram_trigger = False

    # First run silently establishes the baseline.
    is_first_sync = len(sync_db) == 0

    if is_first_sync:
        print(">>> [SYSTEM] FIRST RUN DETECTED: Silently building Anime Sync Vault. Bypassing Discord to prevent spam...")

    for title, data in inventory.items():
        try:
            media_id = str(data["mediaId"])
            progress = safe_int(data.get("progress"))
            media_type = str(data.get("type") or "ANIME").upper()

            # Anime-only safety gate.
            if media_type != "ANIME":
                continue

            # First-run baseline.
            if is_first_sync and media_id not in sync_db:
                sync_db[media_id] = progress
                continue

            # New Anime discovered after the first run: baseline silently.
            if media_id not in sync_db:
                print(f"[BASELINE] New Anime discovered: {title} | Current progress: {progress}")
                sync_db[media_id] = progress
                continue

            db_progress = safe_int(sync_db.get(media_id))

            # No change.
            if progress == db_progress:
                continue

            # Progress decreased: update memory only; no rewards or alerts.
            if progress < db_progress:
                print(f"[ROLLBACK] {title} | Progress {db_progress} -> {progress}. Memory updated without rewards/alerts.")
                sync_db[media_id] = progress
                continue

            delta = progress - db_progress
            if delta <= 0:
                sync_db[media_id] = progress
                continue

            g_earned = delta * 10
            is_completed = data.get("status") == "COMPLETED"
            if is_completed:
                g_earned += 100

            print(f"\n[🔥 UPDATE DETECTED] {title} | Progress updated to: {progress}")

            update_performance_vault(media_type, delta, data.get("duration") or 24, g_earned, is_completed)
            hologram_trigger = True

            ach_db, hit_1k, hit_5k, is_prestige = manage_achievements_and_weekly(g_earned)
            override_tag = "Orewatokyo" if is_prestige else None
            color = hex_to_int(data.get("color"))

            fields = [
                {"name": "🇯🇵 Romaji", "value": data.get("romaji") or "N/A", "inline": False},
                {"name": "📊 Status", "value": data.get("status") or "UNKNOWN", "inline": False},
            ]

            if is_completed:
                author_block = {"name": f"🏆 {g_earned}G EARNED | SERIES COMPLETED", "icon_url": "https://i.imgur.com/gO0wVp5.png"}
            else:
                author_block = {"name": f"🎮 +{g_earned}G | Weekly: {ach_db.get('weekly_g', 0)}G"}

            total = data.get("total_episodes")
            left = (total - progress) if total is not None else "?"
            fields.extend([
                {"name": "✅ Progress", "value": str(progress), "inline": True},
                {"name": "⏳ Left", "value": str(left), "inline": True},
            ])

            # Special lists get dedicated threads. Everything else goes to General Updates.
            thread_id = get_or_create_thread(data.get("list_category", "General Updates"), media_type, WEBHOOK_ANIME)

            # Forum channels require a valid thread ID.
            if thread_id:
                send_discord_alert(
                    WEBHOOK_ANIME,
                    f"UPDATE: {title}",
                    "",
                    color,
                    data.get("cover"),
                    fields,
                    author_block,
                    override_tag,
                    thread_id=thread_id,
                )
            else:
                print(f"[ERROR] Could not create/find Discord thread for '{title}'. Notification skipped safely.")

            fire_zulip_archive(media_type, title, progress, total, data.get("scoreRaw"))

            is_vip = any(
                vip.lower() in (data.get("romaji") or "").lower()
                or vip.lower() in (data.get("english") or "").lower()
                for vip in PRIORITY_FAVORITES
            )

            if is_vip and WEBHOOK_VIP:
                send_discord_alert(
                    WEBHOOK_VIP,
                    f"⭐ VIP UPDATE: {title}",
                    "S-Tier Franchise Update.",
                    color,
                    data.get("cover"),
                    fields,
                    author_block,
                    override_tag,
                )

            if hit_1k:
                drop_classified_ui(1000)
            if hit_5k:
                drop_classified_ui(5000)

            if TARGET_TOKEN:
                try:
                    SESSION.post(
                        'https://graphql.anilist.co',
                        json={
                            'query': """mutation ($id: Int, $prog: Int, $score: Int) {
                                SaveMediaListEntry(mediaId: $id, progress: $prog, scoreRaw: $score) { id }
                            }""",
                            'variables': {
                                'id': data['mediaId'],
                                'prog': progress,
                                'score': data.get('scoreRaw', 0),
                            },
                        },
                        headers=HEADERS,
                        timeout=15,
                    )
                except Exception as e:
                    print(f"[WARN] AniList write-back failed for '{title}': {e}")

            sync_db[media_id] = progress

        except Exception as e:
            print(f"[ERROR] Master sync failed for '{title}': {e}")
            continue

    save_db(DB_SYNC, sync_db)
    flush_performance_vault()
    flush_achievements()
    if hologram_trigger:
        refresh_performance_hologram()



# ==========================================
# 🔮 11. LIVE README TELEMETRY INJECTOR
# ==========================================
def update_readme_telemetry():
    """Inject the Anime performance board into README.md."""
    cli_board = generate_cli_board()
    telemetry_md = (
        "<!-- ANIME_TELEMETRY_START -->\n"
        "```text\n"
        f"{cli_board}\n"
        "```\n"
        "<!-- ANIME_TELEMETRY_END -->"
    )

    try:
        if not os.path.exists("README.md"):
            print("[SYSTEM] README.md not found; skipping Anime telemetry.")
            return

        with open("README.md", "r", encoding="utf-8") as f:
            content = f.read()

        pattern = (
            r"<!-- ANIME_TELEMETRY_START -->.*?"
            r"<!-- ANIME_TELEMETRY_END -->"
        )

        if re.search(pattern, content, flags=re.DOTALL):
            updated = re.sub(pattern, telemetry_md, content, flags=re.DOTALL)
        else:
            separator = "\n\n" if content.strip() else ""
            updated = content.rstrip() + separator + telemetry_md + "\n"

        if updated != content:
            with open("README.md", "w", encoding="utf-8") as f:
                f.write(updated)
        else:
            print("[SYSTEM] README telemetry unchanged; skipping write.")

    except Exception as e:
        print(f"[SYSTEM] Anime Telemetry Injection Failed: {e}")


# ==========================================
# 🚀 12. INITIATION SEQUENCE
# ==========================================
if __name__ == '__main__':
    run_started = time.perf_counter()
    print("=== MAXIMUM OVERDRIVE V3 ENGINE: ANIME CORE SPINNING UP ===")
    execute_48hr_purge()
    
    live_inventory = fetch_anilist_inventory(SOURCE_USERNAME)
    
    known_titles_pool = set()
    for data in live_inventory.values():
        if data.get('romaji'): known_titles_pool.add(data['romaji'].lower())
        if data.get('english'): known_titles_pool.add(data['english'].lower())
        
    process_airing_countdowns(live_inventory)
    execute_master_sync(live_inventory)
    
    save_db(DB_GHOSTS, execute_ghost_radar(sweep_mal_xml(known_titles_pool)))
    save_db(DB_VOID, execute_void_radar())
    flush_performance_vault()
    flush_achievements()

    update_readme_telemetry()
    elapsed = time.perf_counter() - run_started
    print(f"=== MAXIMUM OVERDRIVE V3 ENGINE: ANIME CYCLE COMPLETE | Runtime: {elapsed:.2f}s ===")
