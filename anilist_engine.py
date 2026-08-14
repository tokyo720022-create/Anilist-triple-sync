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
# ⚙️ 1. SYSTEM CONFIGURATION & SECRETS
# ==========================================
SOURCE_USERNAME = "Orewatokyo"
TARGET_TOKEN = os.environ.get('ANILIST_TARGET_TOKEN')

# ⚡ Webhooks (Wired exactly to your updated GitHub Actions Secrets)
WEBHOOK_ANIME = os.environ.get('DISCORD_ANILIST_ANIME_WEBHOOK')
WEBHOOK_MANGA = os.environ.get('DISCORD_ANILIST_MANGA_WEBHOOK')
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

# ⚡ Legacy Memory Vaults
DB_SYNC = 'db_sync.json'
DB_MESSAGES = 'db_messages.json'
DB_GHOSTS = 'db_ghosts.json'
DB_VOID = 'db_void.json'
DB_AIRING = 'db_airing.json'
DB_ACHIEVEMENTS = 'db_achievements.json' 
DB_PERFORMANCE_MSG = 'db_performance_msg.json'

# ⚡ V2 Infrastructure Vaults
DB_THREADS = 'db_threads.json'     # Forum Post ID Tracking
DB_INVENTORY = 'db_inventory.json' # Local Master Database (Delta-Sync)
DB_TIMESTAMP = 'db_timestamp.json' # Time Radar (Delta-Sync)
XML_FILE_PATH = 'mal_export.xml'

# ⚡ S-Tier Radar Targets
PRIORITY_FAVORITES = ["One Piece", "Detective Conan", "Kono Suba", "Dragon Ball Z"]

HEADERS = {
    'Authorization': f'Bearer {TARGET_TOKEN}' if TARGET_TOKEN else '',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

def load_db(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f: return json.load(f)
        except Exception: return {}
    return {}

def save_db(filepath, data):
    with open(filepath, 'w') as f: json.dump(data, f, indent=4)

def safe_int(val, default=0):
    if val is None: return default
    try:
        # ⚡ Automatically extracts the first valid number it finds, ignores dashes/letters
        match = re.search(r'-?\d+', str(val))
        return int(match.group()) if match else default
    except Exception:
        return default
        

# ==========================================
# 🧵 1.5. SELECTIVE THREAD ROUTER
# ==========================================
TARGET_LISTS = [
    "anime movies", "iseki", "isekai", "milf", "loli",
    "plan to continue", "hentai", "favourite", "fav", "planning"
]

def get_or_create_thread(list_name, media_type, base_webhook):
    if not base_webhook: return None
    threads = load_db(DB_THREADS)
    
    clean_name = list_name.lower().strip()
    if clean_name not in TARGET_LISTS:
        return "IGNORE"
        
    display_name = list_name.title()
    thread_key = f"[{media_type}] {display_name}" 
    
    # ⚡ SHIELD: Validates that the ID is actual data, not a corrupted null string
    if thread_key in threads and threads[thread_key] and threads[thread_key] != "None":
        return str(threads[thread_key])
        
    print(f"[SYSTEM] Forging new dedicated Forum thread: '{thread_key}'...")
    
    payload = {
        "content": f"📡 **{display_name}** | {media_type} Telemetry Dashboard",
        "thread_name": thread_key
    }
    
    # Safely injects the wait parameter to force Discord to return the message object
    target_url = base_webhook
    separator = "&" if "?" in target_url else "?"
    target_url = f"{target_url}{separator}wait=true"
    
    try:
        res = requests.post(target_url, json=payload, timeout=15)
        if res.status_code in [200, 201, 204]:
            # Extracts the specific channel ID of the newly created thread
            new_thread_id = str(res.json().get('channel_id'))
            if new_thread_id and new_thread_id != "None":
                threads[thread_key] = new_thread_id
                save_db(DB_THREADS, threads)
                return new_thread_id
        else:
            print(f"[ERROR] Failed to forge thread. Code: {res.status_code} | Reason: {res.text}")
    except Exception as e:
        print(f"[ERROR] Thread network failure: {e}")
        
    return None



# ==========================================
# 📊 2. THE V2 TELEMETRY HUB
# ==========================================
def update_performance_vault(media_type, delta, duration, g_earned, is_completed):
    now = datetime.now(timezone.utc)
    day_str = now.strftime("%Y-%m-%d")
    week_str = f"{now.isocalendar()[0]}-W{now.isocalendar()[1]:02d}"
    month_str = now.strftime("%Y-%m")
    year_str = now.strftime("%Y")
    
    paths = {
        "daily": f"performance/daily/{day_str}.json",
        "weekly": f"performance/weekly/{week_str}.json",
        "monthly": f"performance/monthly/{month_str}.json",
        "yearly": f"performance/yearly/{year_str}.json",
        "lifetime": "performance/lifetime.json"
    }
    
    for folder in ["daily", "weekly", "monthly", "yearly"]:
        os.makedirs(f"performance/{folder}", exist_ok=True)
        
    ep_add = delta if media_type == "ANIME" else 0
    ch_add = delta if media_type == "MANGA" else 0
    anime_time = ep_add * max(1, (duration - 2)) if media_type == "ANIME" else 0
    manga_time = ch_add * 5 if media_type == "MANGA" else 0
    comp_add = 1 if is_completed else 0
    
    for key, path in paths.items():
        data = load_db(path)
        data["episodes"] = data.get("episodes", 0) + ep_add
        data["chapters"] = data.get("chapters", 0) + ch_add
        data["anime_minutes"] = data.get("anime_minutes", 0) + anime_time
        data["manga_minutes"] = data.get("manga_minutes", 0) + manga_time
        data["g_score"] = data.get("g_score", 0) + g_earned
        if key == "lifetime":
            data["completed"] = data.get("completed", 0) + comp_add
        save_db(path, data)

def get_performance_stats():
    now = datetime.now(timezone.utc)
    day_str = now.strftime("%Y-%m-%d")
    week_str = f"{now.isocalendar()[0]}-W{now.isocalendar()[1]:02d}"
    
    return {
        "daily": load_db(f"performance/daily/{day_str}.json"),
        "weekly": load_db(f"performance/weekly/{week_str}.json"),
        "lifetime": load_db("performance/lifetime.json")
    }

def generate_cli_board():
    stats = get_performance_stats()
    
    def format_block(title, data, is_lifetime=False):
        eps = data.get('episodes', 0)
        chp = data.get('chapters', 0)
        time_m = data.get('anime_minutes', 0) + data.get('manga_minutes', 0)
        gs = data.get('g_score', 0)
        
        block = f"{title}\n─────────────────────────\n"
        if is_lifetime:
            comp = data.get('completed', 0)
            block += f"Episodes{eps:>11,}\n"
            block += f"Chapters{chp:>11,}\n"
            block += f"Minutes {time_m:>11,}\n"
            block += f"Gamerscore{gs:>8,} G\n"
            block += f"Completed{comp:>10,}\n"
        else:
            block += f"Anime   {eps:>11,} eps\n"
            block += f"Manga   {chp:>11,} ch\n"
            block += f"Time    {time_m:>11,} min\n"
            block += f"Gamerscore{gs:>8,} G\n"
        return block

    board = f"{format_block('TODAY', stats.get('daily', {}))}\n"
    board += f"{format_block('THIS WEEK', stats.get('weekly', {}))}\n"
    board += f"{format_block('ALL TIME', stats.get('lifetime', {}), True)}"
    return board

def refresh_performance_hologram():
    if not WEBHOOK_PERFORMANCE: return
    
    msg_db = load_db(DB_PERFORMANCE_MSG)
    last_msg_id = msg_db.get("message_id")
    
    if last_msg_id:
        try: requests.delete(f"{WEBHOOK_PERFORMANCE}/messages/{last_msg_id}")
        except Exception: pass
        
    cli_board = generate_cli_board()
    
    embed = {
        "title": "⚡ LIVE PERFORMANCE MONITOR",
        "description": f"```text\n{cli_board}\n```",
        "color": 3447003,
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "footer": {"text": "V2 Telemetry Hub Synced"}
    }
    
    try:
        res = requests.post(WEBHOOK_PERFORMANCE + "?wait=true", json={"embeds": [embed]}, timeout=10)
        if res and res.status_code in [200, 204]:
            msg_id = res.json().get("id")
            if msg_id: save_db(DB_PERFORMANCE_MSG, {"message_id": msg_id})
    except Exception as e:
        print(f"[SYSTEM] Hologram refresh failed: {e}")

# ==========================================
# 🛡️ 3. TITANIUM ARMOR (API RETRY LOGIC)
# ==========================================
def fetch_with_armor(url, payload, headers, retries=3):
    for attempt in range(retries):
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            if res.status_code == 200: return res
        except Exception: pass
        time.sleep((attempt + 1) * 3) 
    return None
    
# ==========================================
# 📡 4. COMMUNICATION PROTOCOLS
# ==========================================
# ⚡ UPGRADE: image, fields, and author are now optional (defaulting to None)
def send_discord_alert(webhook_url, title, desc, color, image=None, fields=None, author=None, override_tag=None, thread_id=None):
    if not webhook_url: return
    
    # Safely attaches the thread ID to the webhook URL without breaking query logic
    target_url = webhook_url
    if thread_id and thread_id != "IGNORE":
        separator = "&" if "?" in target_url else "?"
        target_url = f"{target_url}{separator}thread_id={thread_id}"
        
    embed = {
        "title": title[:256],
        "description": desc,
        "color": color
    }
    
    # ⚡ SHIELD: Only attaches these blocks if the module actually provides them
    if fields: embed["fields"] = fields[:25]
    if image: embed["image"] = {"url": image}
    if author: embed["author"] = author
    
    payload = {"embeds": [embed]}
    if override_tag: payload["username"] = override_tag
    
    try:
        res = requests.post(target_url, json=payload, timeout=15)
        # THE ALARM: If Discord rejects it, the engine will yell instead of dying silently
        if res.status_code not in [200, 201, 204]:
            print(f"\n[ERROR] Discord rejected payload for '{title}'.")
            print(f"Status: {res.status_code} | Reason: {res.text}\n")
    except Exception as e:
        print(f"\n[ERROR] Discord transmission completely failed: {e}\n")


def fire_zulip_archive(media_type, title, progress, total_episodes, score):
    if not ZULIP_URL or not ZULIP_EMAIL or not ZULIP_API_KEY: return
    stream_name = "Anime-Vault" if media_type == "ANIME" else "Manga-Vault"
    action_text = "📺 Watched Episode" if media_type == "ANIME" else "📖 Read Chapter"
    content = f"✅ **Sync Log Executed**\n* **{action_text}:** {progress} / {total_episodes if total_episodes else '?'}\n* **Current Score:** {score if score else 'Unrated'}"
    payload = {"type": "stream", "to": stream_name, "topic": title, "content": content}
    try: requests.post(ZULIP_URL, auth=HTTPBasicAuth(ZULIP_EMAIL, ZULIP_API_KEY), data=payload, timeout=10)
    except Exception: pass

def send_telegram_alert(message, image_url=None):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto" if image_url else f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
    payload = {"chat_id": TELEGRAM_CHAT_ID, "photo": image_url, "caption": message, "parse_mode": "Markdown"} if image_url else {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
    try: requests.post(url, json=payload, timeout=10)
    except Exception: pass

def execute_48hr_purge():
    messages_db = load_db(DB_MESSAGES)
    if isinstance(messages_db, list): messages_db = {}
    current_time = time.time()
    keys_to_delete = [msg_id for msg_id, data in messages_db.items() if current_time - data["timestamp"] > 172800]
    for key in keys_to_delete:
        requests.delete(messages_db[key]["delete_url"])
        del messages_db[key]
        time.sleep(1)
    save_db(DB_MESSAGES, messages_db)



# ==========================================
# 🏆 5. THE RPG ENGINE (ACHIEVEMENTS)
# ==========================================
def hex_to_int(hex_color): return int(hex_color.lstrip('#'), 16) if hex_color else 3447003 

def manage_achievements_and_weekly(points_earned):
    ach_db = load_db(DB_ACHIEVEMENTS)
    if not ach_db or "current_week" not in ach_db: 
        ach_db = {"lifetime_g": 0, "weekly_g": 0, "current_week": datetime.now(timezone.utc).isocalendar()[1]}
        
    current_week = datetime.now(timezone.utc).isocalendar()[1]
    
    if current_week != ach_db["current_week"]:
        ach_db["weekly_g"] = 0
        ach_db["current_week"] = current_week
        
    old_weekly = ach_db.get("weekly_g", 0)
    ach_db["weekly_g"] = old_weekly + points_earned
    ach_db["lifetime_g"] = ach_db.get("lifetime_g", 0) + points_earned
    
    hit_1k = old_weekly < 1000 and ach_db["weekly_g"] >= 1000
    hit_5k = old_weekly < 5000 and ach_db["weekly_g"] >= 5000
    is_prestige = ach_db["lifetime_g"] >= 10000
    
    save_db(DB_ACHIEVEMENTS, ach_db)
    return ach_db, hit_1k, hit_5k, is_prestige

def drop_classified_ui(tier):
    if not WEBHOOK_ACHIEVEMENTS: return
    if tier == 1000: send_discord_alert(WEBHOOK_ACHIEVEMENTS, "💠 1,000 G REACHED", ">> CLASS-A MILESTONE CLEARED <<", 16776960, "https://i.imgur.com/QzXoX1j.gif")
    elif tier == 5000: send_discord_alert(WEBHOOK_ACHIEVEMENTS, "🔥 5,000 G: OVERDRIVE", ">> SYSTEM MAXIMIZED. APEX TIER REACHED <<", 16711680, "https://i.imgur.com/W2dM9Ue.gif")

# ==========================================
# 🔎 6. ANILIST GRAPHQL CORE (DELTA-SYNC)
# ==========================================
def fetch_anilist_inventory(username):
    query = '''
    query ($userName: String,$page: Int) {
      Page(page: $page, perPage: 50) {
        pageInfo { hasNextPage }
        mediaList(userName: $userName, sort: [UPDATED_TIME_DESC]) {
          updatedAt
          mediaId progress score status customLists
          media {
            title { romaji english }
            type format episodes chapters duration
            genres tags { name }
            coverImage { extraLarge color } 
            nextAiringEpisode { airingAt episode }
          }
        }
      }
    }
    '''
    
    inventory, timestamps = load_db(DB_INVENTORY), load_db(DB_TIMESTAMP)
    last_sync = timestamps.get("last_update", 0)
    page, has_next_page, highest_update = 1, True, last_sync
    is_first_run = (last_sync == 0 or not inventory)
    
    print(">>> [SYSTEM] INITIATING DEEP ANALYSIS..." if is_first_run else ">>> [SYSTEM] DELTA-SYNC ENGAGED...")

    while has_next_page:
        res = fetch_with_armor('https://graphql.anilist.co', {'query': query, 'variables': {"userName": username, "page": page}}, HEADERS)
        if not res: break
        
        data = res.json().get('data', {}).get('Page', {})
        has_next_page = data.get('pageInfo', {}).get('hasNextPage', False)
        
        for item in data.get('mediaList', []):
            try:
                if not item: continue
                updated_at = item.get('updatedAt', 0)
                
                if not is_first_run and updated_at <= last_sync:
                    has_next_page = False
                    break
                    
                if updated_at > highest_update: highest_update = updated_at

                media = item.get('media')
                if not media: continue 
                
                title_data = media.get('title') or {}
                primary_title = str(title_data.get('english') or title_data.get('romaji') or "Unknown_Classified_Media")
                
                # ⚡ EXTRACTION: Pulling Genres and Tags for AI Sorting
                genres = media.get('genres') or []
                tags = [t.get('name') for t in (media.get('tags') or []) if t.get('name')]
                descriptors = [g.lower() for g in genres] + [t.lower() for t in tags]
                format_type = media.get('format') or ""
                
                # 1. Manual Check (If you DID click the button, use it)
                raw_custom = item.get('customLists')
                active_lists = [k for k, v in raw_custom.items() if v] if isinstance(raw_custom, dict) else []
                
                smart_category = None
                if active_lists:
                    smart_category = active_lists[0]
                else:
                    # 2. ⚡ AI AUTO-CATEGORIZER: Sorting without manual clicks!
                    if format_type == "MOVIE": smart_category = "Anime movies"
                    elif "isekai" in descriptors: smart_category = "Iseki"
                    elif any(x in descriptors for x in ["hentai", "ecchi", "adult", "smut"]): smart_category = "Hentai"
                    elif any(x in descriptors for x in ["milf", "older woman", "mother"]): smart_category = "Milf"
                    elif "loli" in descriptors: smart_category = "Loli"
                
                raw_status = item.get('status') or "UNKNOWN"
                list_category = smart_category if smart_category else raw_status.replace('_', ' ').title()
                
                print(f"[SCAN/UPDATE] {primary_title[:40]:<40} -> Cached as: {list_category}")
                
                inventory[primary_title] = {
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
                    "total_episodes": media.get('episodes'),
                    "total_chapters": media.get('chapters')
                }
            except Exception: continue
        page += 1
        time.sleep(1) 
        
    save_db(DB_INVENTORY, inventory)
    save_db(DB_TIMESTAMP, {"last_update": highest_update})
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
    if os.path.exists(XML_FILE_PATH):
        try:
            for manga in ET.parse(XML_FILE_PATH).getroot().findall('manga'):
                t = manga.find('manga_title').text
                if t.lower() not in known_titles_pool and t not in ghosts:
                    ghosts[t] = {"progress": int(manga.find('my_read_chapters').text or 0), "score": int(manga.find('my_score').text or 0), "type": "MANGA"}
        except Exception: pass
    if os.path.exists('mal_anime.xml'):
        try:
            for anime in ET.parse('mal_anime.xml').getroot().findall('anime'):
                t = anime.find('series_title').text
                if t.lower() not in known_titles_pool and t not in ghosts:
                    ghosts[t] = {"progress": int(anime.find('my_watched_episodes').text or 0), "score": int(anime.find('my_score').text or 0), "type": "ANIME"}
        except Exception: pass
    return ghosts

def execute_ghost_radar(ghost_db):
    if not ghost_db: return ghost_db
    assimilated = []
    for title, data in list(ghost_db.items()):
        res = requests.post('https://graphql.anilist.co', json={'query': '''query ($search: String,$type: MediaType) { Media (search: $search, type:$type) { id } }''', 'variables': {"search": title, "type": data.get("type", "MANGA")}}, headers=HEADERS)
        if res and res.status_code == 200 and res.json().get('data', {}).get('Media'):
            if TARGET_TOKEN: requests.post('https://graphql.anilist.co', json={'query': '''mutation ($id: Int,$prog: Int, $score: Int) { SaveMediaListEntry (mediaId:$id, progress: $prog, scoreRaw:$score) { id } }''', 'variables': {"id": res.json()['data']['Media']['id'], "prog": data.get("progress", 0), "score": data["score"] * 10}}, headers=HEADERS)
            send_discord_alert(WEBHOOK_GHOST, "🟢 GHOST ASSIMILATED", f"**{title}** recovered.", 3066993)
            assimilated.append(title)
        else:
            send_discord_alert(WEBHOOK_LOG, "🔴 GHOST REJECTED / NOT FOUND", f"AniList database rejected or could not locate search query: **{title}** ({data.get('type', 'MANGA')})", 16711680)
        time.sleep(1.5) 
    for title in assimilated: del ghost_db[title]
    return ghost_db

# ==========================================
# 🌌 9. THE DEEP VOID PROTOCOL
# ==========================================
def execute_void_radar():
    void_db = load_db(DB_VOID)
    if not void_db: return void_db
    assimilated = []
    for title, data in list(void_db.items()):
        res = requests.post('https://graphql.anilist.co', json={'query': '''query ($search: String,$type: MediaType) { Media (search: $search, type:$type) { id } }''', 'variables': {"search": title, "type": data.get("type", "MANGA")}}, headers=HEADERS)
        if res and res.status_code == 200 and res.json().get('data', {}).get('Media'):
            if TARGET_TOKEN: requests.post('https://graphql.anilist.co', json={'query': '''mutation ($id: Int,$prog: Int, $score: Int) { SaveMediaListEntry (mediaId:$id, progress: $prog, scoreRaw:$score) { id } }''', 'variables': {"id": res.json()['data']['Media']['id'], "prog": data.get("progress", 0), "score": data.get("score", 0) * 10}}, headers=HEADERS)
            send_discord_alert(WEBHOOK_LOG, "🌌 VOID ENTITY ASSIMILATED", f"**{title}** has been recovered from the Deep Void.", 10181046)
            assimilated.append(title)
        time.sleep(1.5) 
    for title in assimilated: del void_db[title]
    return void_db

# ==========================================
# ⚡ 10. THE MASTER SYNC ENGINE 
# ==========================================
def execute_master_sync(inventory):
    sync_db = load_db(DB_SYNC)
    hologram_trigger = False
    
    for title, data in inventory.items():
        media_id = str(data["mediaId"])
        progress, media_type = safe_int(data["progress"]), data["type"]
        db_progress = safe_int(sync_db.get(media_id, 0))
        
        if str(sync_db.get(media_id)) != str(progress):
            delta = progress - db_progress
            if delta < 0: delta = 0 
            
            g_earned = (delta * 10) if media_type == "ANIME" else (delta * 2)
            is_completed = data["status"] == "COMPLETED"
            if is_completed: g_earned += 100 
            
            if delta > 0:
                print(f"\n[🔥 UPDATE DETECTED] {title} | Progress updated to: {progress}")
                update_performance_vault(media_type, delta, data['duration'], g_earned, is_completed)
                hologram_trigger = True
            
            ach_db, hit_1k, hit_5k, is_prestige = manage_achievements_and_weekly(g_earned)
            override_tag = "Orewatokyo" if is_prestige else None
            color = hex_to_int(data["color"])
            fields = [{"name": "🇯🇵 Romaji", "value": data['romaji'] or "N/A", "inline": False}, {"name": "📊 Status", "value": data["status"], "inline": False}]
            author_block = {"name": f"🏆 {g_earned}G EARNED | SERIES COMPLETED", "icon_url": "https://i.imgur.com/gO0wVp5.png"} if is_completed else {"name": f"🎮 +{g_earned}G | Weekly: {ach_db.get('weekly_g', 0)}G"}
            
            total = data['total_episodes'] if media_type == "ANIME" else data['total_chapters']
            left = (total - progress) if total else "?"
            fields.extend([{"name": "✅ Progress", "value": f"{progress}", "inline": True}, {"name": "⏳ Left", "value": f"{left}", "inline": True}])
            
            webhook = WEBHOOK_ANIME if media_type == "ANIME" else WEBHOOK_MANGA

            # ⚡ SELECTIVE THREAD ROUTER
            # Keep the original dedicated-thread feature for TARGET_LISTS,
            # but NEVER suppress the main Anime/Manga notification when a
            # title does not belong to one of those lists.
            thread_id = get_or_create_thread(data["list_category"], media_type, webhook)

            # Normal/unknown lists are sent directly to the main Anime/Manga
            # webhook. Matching TARGET_LISTS continue to use their dedicated
            # Discord forum thread exactly as before.
            if thread_id == "IGNORE":
                thread_id = None

            send_discord_alert(
                webhook,
                f"UPDATE: {title}",
                "",
                color,
                data.get('cover'),
                fields,
                author_block,
                override_tag,
                thread_id=thread_id
            )
            
            fire_zulip_archive(media_type, title, progress, total, data.get('scoreRaw'))
            
            # S-Tier VIPs get alerts regardless of their list category
            is_vip = any(vip.lower() in (data['romaji'] or "").lower() or vip.lower() in (data['english'] or "").lower() for vip in PRIORITY_FAVORITES)
            if is_vip and WEBHOOK_VIP: 
                send_discord_alert(WEBHOOK_VIP, f"⭐ VIP UPDATE: {title}", "S-Tier Franchise Update.", color, data.get('cover'), fields, author_block, override_tag)
                
            if hit_1k: drop_classified_ui(1000)
            if hit_5k: drop_classified_ui(5000)
            
            if TARGET_TOKEN: requests.post('https://graphql.anilist.co', json={'query': '''mutation ($id: Int, $prog: Int, $score: Int) { SaveMediaListEntry (mediaId: $id, progress: $prog, scoreRaw: $score) { id } }''', 'variables': {"id": data["mediaId"], "prog": progress, "score": data["scoreRaw"]}}, headers=HEADERS)
            
            sync_db[media_id] = progress
            
    save_db(DB_SYNC, sync_db)
    if hologram_trigger: refresh_performance_hologram()

# ==========================================
# 🔮 11. LIVE TELEMETRY INJECTOR
# ==========================================
def update_readme_telemetry():
    cli_board = generate_cli_board()
    telemetry_md = f"<!-- TELEMETRY_START -->\n```text\n{cli_board}\n```\n<!-- TELEMETRY_END -->"
    
    try:
        with open('README.md', 'r', encoding='utf-8') as f: content = f.read()
        with open('README.md', 'w', encoding='utf-8') as f: f.write(re.sub(r'<!-- TELEMETRY_START -->.*?<!-- TELEMETRY_END -->', telemetry_md, content, flags=re.DOTALL))
    except Exception as e: print(f"[SYSTEM] Telemetry Injection Failed: {e}")

# ==========================================
# 🚀 12. INITIATION SEQUENCE
# ==========================================
if __name__ == '__main__':
    print("=== MAXIMUM OVERDRIVE V2 ENGINE: SPINNING UP ===")
    print(f"[DISCORD] Anime webhook: {'READY' if WEBHOOK_ANIME else 'MISSING'}")
    print(f"[DISCORD] Manga webhook: {'READY' if WEBHOOK_MANGA else 'MISSING'}")
    print(f"[DISCORD] Log webhook: {'READY' if WEBHOOK_LOG else 'MISSING'}")
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
    
    update_readme_telemetry()
    print("=== MAXIMUM OVERDRIVE V2 ENGINE: CYCLE COMPLETE ===")
