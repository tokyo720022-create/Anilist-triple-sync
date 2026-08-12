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

WEBHOOK_ANIME = os.environ.get('DISCORD_ANIME_WEBHOOK')
WEBHOOK_MANGA = os.environ.get('DISCORD_MANGA_WEBHOOK')
WEBHOOK_AIRING = os.environ.get('DISCORD_AIRING_WEBHOOK')
WEBHOOK_LOG = os.environ.get('DISCORD_LOG_WEBHOOK')
WEBHOOK_VIP = os.environ.get('DISCORD_FAVORITES_WEBHOOK') # 🛠️ THE VIP CHANNEL
WEBHOOK_GHOST = os.environ.get('DISCORD_GHOST_RADAR_WEBHOOK')
WEBHOOK_ACHIEVEMENTS = os.environ.get('DISCORD_ACHIEVEMENTS_WEBHOOK') 

# 🛠️ TELEGRAM PIPELINE
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_BOT_TOKEN')
TELEGRAM_CHAT_ID = os.environ.get('TELEGRAM_CHAT_ID')

# 🗄️ ZULIP GRAND ARCHIVE PIPELINE
ZULIP_URL = os.environ.get('ZULIP_SERVER_URL')
ZULIP_EMAIL = os.environ.get('ZULIP_BOT_EMAIL')
ZULIP_API_KEY = os.environ.get('ZULIP_API_KEY')

DB_SYNC = 'db_sync.json'
DB_MESSAGES = 'db_messages.json'
DB_GHOSTS = 'db_ghosts.json'
DB_AIRING = 'db_airing.json'
DB_ACHIEVEMENTS = 'db_achievements.json' 
XML_FILE_PATH = 'mal_export.xml'

# 🛠️ S-TIER FRANCHISES
PRIORITY_FAVORITES = ["One Piece", "Detective Conan", "JoJo's Bizarre Adventure", "Dragon Ball Z"]

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

# ==========================================
# 🛡️ 2. TITANIUM ARMOR (API RETRY LOGIC)
# ==========================================
def fetch_with_armor(url, payload, headers, retries=3):
    for attempt in range(retries):
        try:
            res = requests.post(url, json=payload, headers=headers, timeout=15)
            if res.status_code == 200:
                return res
            print(f"[SYSTEM] API Strike {attempt+1} failed (Status: {res.status_code}).")
        except Exception as e:
            print(f"[SYSTEM] Network error: {e}")
        time.sleep((attempt + 1) * 3) 
    return None

# ==========================================
# 📡 3. COMMUNICATION PROTOCOLS
# ==========================================
def send_discord_alert(webhook_url, title, description, color, image_url=None, fields=None, author=None, override_name=None):
    if not webhook_url: return
    
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if image_url: embed["image"] = {"url": image_url}
    if fields: embed["fields"] = fields
    if author: embed["author"] = author
        
    payload = {"embeds": [embed]}
    if override_name: payload["username"] = override_name
    
    response = requests.post(webhook_url + "?wait=true", json=payload)
    
    if response and response.status_code in [200, 204] and webhook_url == WEBHOOK_LOG:
        try:
            msg_id = response.json().get("id")
            if msg_id:
                messages_db = load_db(DB_MESSAGES)
                if isinstance(messages_db, list): messages_db = {}
                messages_db[msg_id] = {"timestamp": time.time(), "delete_url": f"{webhook_url}/messages/{msg_id}"}
                save_db(DB_MESSAGES, messages_db)
        except Exception: pass

def send_telegram_alert(message, image_url=None):
    if not TELEGRAM_TOKEN or not TELEGRAM_CHAT_ID: return
    
    if image_url:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendPhoto"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID, 
            "photo": image_url, 
            "caption": message, 
            "parse_mode": "Markdown"
        }
    else:
        url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
        payload = {
            "chat_id": TELEGRAM_CHAT_ID, 
            "text": message, 
            "parse_mode": "Markdown"
        }
        
    try:
        res = requests.post(url, json=payload, timeout=10)
        if res.status_code != 200 and image_url:
            fallback_url = f"https://api.telegram.org/bot{TELEGRAM_TOKEN}/sendMessage"
            fallback_payload = {"chat_id": TELEGRAM_CHAT_ID, "text": message, "parse_mode": "Markdown"}
            requests.post(fallback_url, json=fallback_payload, timeout=10)
    except Exception as e:
        print(f"[SYSTEM] Telegram strike failed: {e}")

def fire_zulip_archive(media_type, title, progress, total_episodes, score):
    """Routes the log to the correct vault and threads it by Title."""
    if not ZULIP_URL or not ZULIP_EMAIL or not ZULIP_API_KEY:
        return
        
    stream_name = "Anime-Vault" if media_type == "ANIME" else "Manga-Vault"
    action_text = "📺 Watched Episode" if media_type == "ANIME" else "📖 Read Chapter"
    
    content = f"✅ **Sync Log Executed**\n* **{action_text}:** {progress} / {total_episodes if total_episodes else '?'}\n* **Current Score:** {score if score else 'Unrated'}"
    
    payload = {
        "type": "stream",
        "to": stream_name,
        "topic": title,
        "content": content
    }
    
    try:
        print(f"🗄️ [ZULIP] Archiving {title} into {stream_name}...")
        requests.post(ZULIP_URL, auth=HTTPBasicAuth(ZULIP_EMAIL, ZULIP_API_KEY), data=payload, timeout=10)
    except Exception as e:
        print(f"[SYSTEM] Zulip archive failed: {e}")

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
# 🏆 4. THE RPG ENGINE (ACHIEVEMENTS)
# ==========================================
def hex_to_int(hex_color):
    if not hex_color: return 3447003 
    return int(hex_color.lstrip('#'), 16)

def manage_achievements_and_weekly(points_earned):
    ach_db = load_db(DB_ACHIEVEMENTS)
    if not ach_db or "current_week" not in ach_db: 
        ach_db = {"lifetime_g": 0, "weekly_g": 0, "current_week": datetime.now(timezone.utc).isocalendar()[1]}
        
    current_week = datetime.now(timezone.utc).isocalendar()[1]
    
    if current_week != ach_db["current_week"]:
        final_weekly = ach_db.get("weekly_g", 0)
        ach_db["weekly_g"] = 0
        ach_db["current_week"] = current_week
        random_color = random.randint(0, 16777215)
        
        send_discord_alert(
            WEBHOOK_ACHIEVEMENTS, "🔄 WEEKLY CYCLE COMPLETE", 
            f"The grid has been wiped. You secured **{final_weekly} G** last week.\nTotal Lifetime Score: **{ach_db.get('lifetime_g', 0)} G**.\n\nA new cycle begins now.", 
            random_color, None, None, None, override_name="System Oracle"
        )

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
    if tier == 1000:
        send_discord_alert(WEBHOOK_ACHIEVEMENTS, "💠 1,000 G REACHED", ">> CLASS-A MILESTONE CLEARED <<", 16776960, "https://i.imgur.com/QzXoX1j.gif")
    elif tier == 5000:
        send_discord_alert(WEBHOOK_ACHIEVEMENTS, "🔥 5,000 G: OVERDRIVE", ">> SYSTEM MAXIMIZED. APEX TIER REACHED <<", 16711680, "https://i.imgur.com/W2dM9Ue.gif")

# ==========================================
# 🔎 5. ANILIST GRAPHQL CORE
# ==========================================
def fetch_anilist_inventory(username):
    print(f"[ENGINE] Fetching High-Density Inventory for Source: {username}...")
    query = '''
    query ($userName: String, $page: Int) {
      Page(page: $page, perPage: 50) {
        pageInfo { hasNextPage }
        mediaList(userName: $userName) {
          mediaId progress progressVolumes score status
          media {
            title { romaji english }
            type episodes chapters volumes season seasonYear
            coverImage { extraLarge color } 
            nextAiringEpisode { airingAt episode }
          }
        }
      }
    }
    '''
    
    inventory = {}
    page = 1
    has_next_page = True
    
    while has_next_page:
        payload = {'query': query, 'variables': {"userName": username, "page": page}}
        response = fetch_with_armor('https://graphql.anilist.co', payload, HEADERS)
        
        if not response: break
            
        data = response.json().get('data', {}).get('Page', {})
        media_list = data.get('mediaList', [])
        has_next_page = data.get('pageInfo', {}).get('hasNextPage', False)
        
        for item in media_list:
            media = item['media']
            primary_title = media['title'].get('english') or media['title'].get('romaji')
            
            inventory[primary_title] = {
                "mediaId": item['mediaId'],
                "progress": item['progress'],
                "progressVolumes": item.get('progressVolumes', 0),
                "status": item['status'],
                "scoreRaw": item.get('score', 0), 
                "type": media['type'],
                "cover": media['coverImage']['extraLarge'] if media.get('coverImage') else None,
                "color": media['coverImage'].get('color'), 
                "nextAiring": media.get('nextAiringEpisode'),
                "romaji": media['title'].get('romaji'),
                "english": media['title'].get('english'),
                "total_episodes": media.get('episodes'),
                "total_chapters": media.get('chapters')
            }
        page += 1
        time.sleep(1) 
    return inventory

# ==========================================
# ⏰ 6. AIRING INTELLIGENCE (DUAL-STAGE RADAR)
# ==========================================
def process_airing_countdowns(inventory):
    airing_db = load_db(DB_AIRING)
    if isinstance(airing_db, list): airing_db = {}
    current_time = int(time.time())
    
    for title, data in inventory.items():
        next_airing = data.get('nextAiring')
        if not next_airing: continue
            
        airing_at = next_airing['airingAt']
        ep_number = next_airing['episode']
        time_until = airing_at - current_time
        
        db_key = f"{data['mediaId']}_ep{ep_number}"
        current_status = airing_db.get(db_key, "none")
        
        if time_until > 0:
            alert_type = None
            msg_title = ""
            
            if 3600 < time_until <= 10800 and current_status == "none":
                alert_type = "3h"
                msg_title = f"🕒 3-HOUR WARNING: Episode {ep_number}"
                
            elif 0 < time_until <= 3600 and current_status in ["none", "3h"]:
                alert_type = "1h"
                msg_title = f"🚨 FINAL 1-HOUR WARNING: Episode {ep_number}"
                
                title_clean = data['english'] or data['romaji']
                cover_art = data.get('cover')
                tg_payload = f"🚨 *FINAL 1-HOUR WARNING*\n\n📺 *{title_clean}*\nEpisode {ep_number} is dropping in under 60 minutes."
                send_telegram_alert(tg_payload, cover_art)

            if alert_type:
                fields = [
                    {"name": "🇯🇵 Romaji", "value": data['romaji'] or "N/A", "inline": False},
                    {"name": "🇺🇸 English", "value": data['english'] or "N/A", "inline": False},
                    {"name": "📺 Telecast Time", "value": f"<t:{airing_at}:F>", "inline": False}, 
                    {"name": "⏳ Live Countdown", "value": f"<t:{airing_at}:R>", "inline": False}, 
                ]
                
                poster_color = hex_to_int(data["color"])
                send_discord_alert(WEBHOOK_AIRING, msg_title, "", poster_color, data.get('cover'), fields)
                airing_db[db_key] = alert_type
            
    save_db(DB_AIRING, airing_db)

# ==========================================
# 👻 7. MAL GHOST RADAR (BIMODAL)
# ==========================================
def sweep_mal_xml(known_titles_pool):
    ghosts = load_db(DB_GHOSTS)
    if isinstance(ghosts, list): ghosts = {}
    
    if os.path.exists(XML_FILE_PATH):
        try:
            tree = ET.parse(XML_FILE_PATH)
            for manga in tree.getroot().findall('manga'):
                mal_title = manga.find('manga_title').text
                if mal_title.lower() not in known_titles_pool and mal_title not in ghosts:
                    chaps = manga.find('my_read_chapters').text
                    score = manga.find('my_score').text
                    ghosts[mal_title] = {"progress": int(chaps) if chaps else 0, "score": int(score) if score else 0, "type": "MANGA"}
        except Exception: pass

    if os.path.exists('mal_anime.xml'):
        try:
            tree = ET.parse('mal_anime.xml')
            for anime in tree.getroot().findall('anime'):
                mal_title = anime.find('series_title').text
                if mal_title.lower() not in known_titles_pool and mal_title not in ghosts:
                    eps = anime.find('my_watched_episodes').text
                    score = anime.find('my_score').text
                    ghosts[mal_title] = {"progress": int(eps) if eps else 0, "score": int(score) if score else 0, "type": "ANIME"}
        except Exception: pass
        
    return ghosts

def execute_ghost_radar(ghost_db):
    if not ghost_db: return ghost_db
    
    search_query = '''query ($search: String, $type: MediaType) { Media (search: $search, type: $type) { id title { romaji english } } }'''
    mutation_query = '''mutation ($id: Int, $prog: Int, $score: Int) { SaveMediaListEntry (mediaId: $id, progress: $prog, scoreRaw: $score) { id } }'''
    
    assimilated = []
    for title, data in list(ghost_db.items()):
        media_type = data.get("type", "MANGA")
        progress = data.get("progress", data.get("chapters", 0))
        
        res = requests.post('https://graphql.anilist.co', json={'query': search_query, 'variables': {"search": title, "type": media_type}}, headers=HEADERS)
        
        if res and res.status_code == 200:
            result = res.json().get('data', {}).get('Media')
            if result:
                if TARGET_TOKEN:
                    requests.post('https://graphql.anilist.co', json={'query': mutation_query, 'variables': {"id": result['id'], "prog": progress, "score": data["score"] * 10}}, headers=HEADERS)
                send_discord_alert(WEBHOOK_GHOST, "🟢 GHOST ASSIMILATED", f"**{title}** recovered.\nType: {media_type}\nProgress: {progress}", 3066993)
                assimilated.append(title)
        time.sleep(1.5) 
        
    for title in assimilated: del ghost_db[title]
    return ghost_db

# ==========================================
# ⚡ 8. THE MASTER SYNC ENGINE 
# ==========================================
def execute_master_sync(inventory):
    sync_db = load_db(DB_SYNC)
    if isinstance(sync_db, list): sync_db = {}
    mutation_query = '''mutation ($id: Int, $prog: Int, $score: Int) { SaveMediaListEntry (mediaId: $id, progress: $prog, scoreRaw: $score) { id } }'''
    
    for title, data in inventory.items():
        media_id = str(data["mediaId"])
        progress = data["progress"]
        media_type = data["type"]
        
        if str(sync_db.get(media_id)) != str(progress):
            
            delta = progress - int(sync_db.get(media_id, 0))
            if delta < 0: delta = 0 
            g_earned = (delta * 10) if media_type == "ANIME" else (delta * 2)
            if data["status"] == "COMPLETED": g_earned += 100 
            
            ach_db, hit_1k, hit_5k, is_prestige = manage_achievements_and_weekly(g_earned)
            override_tag = "Orewatokyo" if is_prestige else None
            
            color = hex_to_int(data["color"])
            
            fields = [
                {"name": "🇯🇵 Romaji", "value": data['romaji'] or "N/A", "inline": False},
                {"name": "🇺🇸 English", "value": data['english'] or "N/A", "inline": False},
                {"name": "📊 Status", "value": data["status"], "inline": False}
            ]
            
            author_block = None
            if data["status"] == "COMPLETED":
                author_block = {"name": f"🏆 {g_earned}G EARNED | SERIES COMPLETED", "icon_url": "https://i.imgur.com/gO0wVp5.png"}
            else:
                author_block = {"name": f"🎮 +{g_earned}G | Weekly: {ach_db.get('weekly_g', 0)}G"}

            webhook = WEBHOOK_ANIME if media_type == "ANIME" else WEBHOOK_MANGA
            
            total_count = None
            if media_type == "ANIME":
                total = data['total_episodes']
                total_count = total
                eps_left = (total - progress) if total else "?"
                fields.extend([
                    {"name": "✅ Watched", "value": f"{progress}", "inline": True},
                    {"name": "⏳ Left", "value": f"{eps_left}", "inline": True}
                ])
            elif media_type == "MANGA":
                total = data['total_chapters']
                total_count = total
                chaps_left = (total - progress) if total else "?"
                fields.extend([
                    {"name": "📖 Read", "value": f"{progress}", "inline": True},
                    {"name": "⏳ Left", "value": f"{chaps_left}", "inline": True}
                ])

            send_discord_alert(webhook, f"UPDATE: {title}", "", color, data.get('cover'), fields, author_block, override_tag)
            
            # 🗄️ ZULIP GRAND ARCHIVE STRIKE
            fire_zulip_archive(
                media_type=media_type, 
                title=title, 
                progress=progress, 
                total_episodes=total_count, 
                score=data.get('scoreRaw')
            )
            
            # 🛠️ PATCH: VIP ROUTING ACTIVATED
            # This scans both the English and Romaji titles. If it hits one of your S-Tier Priority franchises, it fires a copy straight to the VIP room.
            is_vip = any(vip.lower() in (data['romaji'] or "").lower() or vip.lower() in (data['english'] or "").lower() for vip in PRIORITY_FAVORITES)
            if is_vip and WEBHOOK_VIP:
                send_discord_alert(WEBHOOK_VIP, f"⭐ VIP UPDATE: {title}", "S-Tier Franchise Update Logged.", color, data.get('cover'), fields, author_block, override_tag)
            
            if hit_1k: drop_classified_ui(1000)
            if hit_5k: drop_classified_ui(5000)
            
            if data["status"] == "COMPLETED" and WEBHOOK_ACHIEVEMENTS:
                send_discord_alert(
                    WEBHOOK_ACHIEVEMENTS, 
                    f"🏆 SERIES CONQUERED: {title}", 
                    f"You have fully cleared this series and secured **{g_earned} G** for the vault.\nTotal Lifetime Score: **{ach_db.get('lifetime_g', 0)} G**.", 
                    color, 
                    data.get('cover'),
                    None, None, override_tag
                )
                
                            if TARGET_TOKEN:
                               payload = {
                                 'query': mutation_query, 
                                 'variables': {
                                    "id": data["mediaId"], 
                                    "prog": progress, 
                                    "score": data["scoreRaw"]
                    }
                }
                fetch_with_armor('https://graphql.anilist.co', payload, HEADERS)
                
