import os
import json
import time
import requests
import xml.etree.ElementTree as ET
from datetime import datetime, timezone

# ==========================================
# ⚙️ 1. SYSTEM CONFIGURATION & SECRETS
# ==========================================
SOURCE_USERNAME = "Orewatokyo"
TARGET_TOKEN = os.environ.get('ANILIST_TARGET_TOKEN')

WEBHOOK_ANIME = os.environ.get('DISCORD_ANIME_WEBHOOK')
WEBHOOK_MANGA = os.environ.get('DISCORD_MANGA_WEBHOOK')
WEBHOOK_AIRING = os.environ.get('DISCORD_AIRING_WEBHOOK')
WEBHOOK_LOG = os.environ.get('DISCORD_LOG_WEBHOOK')
WEBHOOK_VIP = os.environ.get('DISCORD_FAVORITES_WEBHOOK')
WEBHOOK_GHOST = os.environ.get('DISCORD_GHOST_RADAR_WEBHOOK')

DB_SYNC = 'db_sync.json'
DB_MESSAGES = 'db_messages.json'
DB_GHOSTS = 'db_ghosts.json'
DB_AIRING = 'db_airing.json'
XML_FILE_PATH = 'mal_export.xml'

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
# 📡 3. DISCORD COMMUNICATION PROTOCOLS
# ==========================================
def send_discord_alert(webhook_url, title, description, color, image_url=None, fields=None):
    """Fires a highly structured embed directly to the command center."""
    if not webhook_url: return
    
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    if image_url: embed["image"] = {"url": image_url}
    if fields: embed["fields"] = fields
        
    payload = {"embeds": [embed]}
    response = requests.post(webhook_url + "?wait=true", json=payload)
    
    if response.status_code in [200, 204] and webhook_url == WEBHOOK_LOG:
        try:
            msg_id = response.json().get("id")
            if msg_id:
                messages_db = load_db(DB_MESSAGES)
                if isinstance(messages_db, list): messages_db = {}
                messages_db[msg_id] = {"timestamp": time.time(), "delete_url": f"{webhook_url}/messages/{msg_id}"}
                save_db(DB_MESSAGES, messages_db)
        except Exception: pass

def execute_48hr_purge():
    messages_db = load_db(DB_MESSAGES)
    if isinstance(messages_db, list): messages_db = {}
    current_time = time.time()
    keys_to_delete = []
    for msg_id, data in messages_db.items():
        if current_time - data["timestamp"] > 172800:
            del_response = requests.delete(data["delete_url"])
            if del_response.status_code == 204: keys_to_delete.append(msg_id)
            time.sleep(1) 
    for key in keys_to_delete: del messages_db[key]
    save_db(DB_MESSAGES, messages_db)

# ==========================================
# 🔎 4. ANILIST GRAPHQL CORE (DATA RICH FETCH)
# ==========================================
def fetch_anilist_inventory(username):
    print(f"[ENGINE] Fetching High-Density Inventory for Source: {username}...")
    
    # 🛠️ PATCH: Massive query expansion for Deep Tracking (Episodes, Chapters, Seasons)
    query = '''
    query ($userName: String, $page: Int) {
      Page(page: $page, perPage: 50) {
        pageInfo { hasNextPage }
        mediaList(userName: $userName) {
          mediaId
          progress
          progressVolumes
          score
          status
          media {
            title { romaji english }
            type
            episodes
            chapters
            volumes
            season
            seasonYear
            coverImage { extraLarge } 
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
        variables = {"userName": username, "page": page}
        response = requests.post('https://graphql.anilist.co', json={'query': query, 'variables': variables}, headers=HEADERS)
        
        if response.status_code != 200: break
            
        data = response.json().get('data', {}).get('Page', {})
        media_list = data.get('mediaList', [])
        has_next_page = data.get('pageInfo', {}).get('hasNextPage', False)
        
        for item in media_list:
            media = item['media']
            romaji_title = media['title'].get('romaji')
            eng_title = media['title'].get('english')
            primary_title = eng_title or romaji_title
            
            inventory[primary_title] = {
                "mediaId": item['mediaId'],
                "progress": item['progress'],
                "progressVolumes": item.get('progressVolumes', 0),
                "status": item['status'],
                "scoreRaw": item.get('score', 0), 
                "type": media['type'],
                "cover": media['coverImage']['extraLarge'] if media.get('coverImage') else None,
                "nextAiring": media.get('nextAiringEpisode'),
                "romaji": romaji_title,
                "english": eng_title,
                "total_episodes": media.get('episodes'),
                "total_chapters": media.get('chapters'),
                "total_volumes": media.get('volumes'),
                "season": media.get('season'),
                "seasonYear": media.get('seasonYear')
            }
        
        page += 1
        time.sleep(1) 
        
    return inventory

# ==========================================
# ⏰ 5. AIRING INTELLIGENCE PROTOCOL (LIVE CLOCK)
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
        
        if 0 < time_until <= 5400 and db_key not in airing_db:
            # 🛠️ PATCH: Live Discord Countdown Clocks
            fields = [
                {"name": "🇯🇵 Romaji", "value": data['romaji'] or "N/A", "inline": False},
                {"name": "🇺🇸 English", "value": data['english'] or "N/A", "inline": False},
                {"name": "📺 Telecast Time", "value": f"<t:{airing_at}:F>", "inline": False}, # Absolute Time
                {"name": "⏳ Live Countdown", "value": f"<t:{airing_at}:R>", "inline": False}, # Ticking Clock
            ]
            
            send_discord_alert(WEBHOOK_AIRING, f"🚨 AIRING ALERT: Episode {ep_number}", "", 15548997, data.get('cover'), fields)
            airing_db[db_key] = True
            
    save_db(DB_AIRING, airing_db)

# ==========================================
# 👻 6. MAL GHOST RADAR PROTOCOLS (BIMODAL)
# ==========================================
def sweep_mal_xml(known_titles_pool):
    ghosts = load_db(DB_GHOSTS)
    if isinstance(ghosts, list): ghosts = {}
    new_count = 0
    
    if os.path.exists(XML_FILE_PATH):
        try:
            tree = ET.parse(XML_FILE_PATH)
            for manga in tree.getroot().findall('manga'):
                mal_title = manga.find('manga_title').text
                if mal_title.lower() not in known_titles_pool and mal_title not in ghosts:
                    chaps = manga.find('my_read_chapters').text
                    score = manga.find('my_score').text
                    ghosts[mal_title] = {"progress": int(chaps) if chaps else 0, "score": int(score) if score else 0, "type": "MANGA"}
                    new_count += 1
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
                    new_count += 1
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
        
        if res.status_code == 200:
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
# ⚡ 7. THE MASTER SYNC ENGINE (HIGH-DENSITY EMBEDS)
# ==========================================
def execute_master_sync(inventory):
    sync_db = load_db(DB_SYNC)
    if isinstance(sync_db, list): sync_db = {}
    mutation_query = '''mutation ($id: Int, $prog: Int, $score: Int) { SaveMediaListEntry (mediaId: $id, progress: $prog, scoreRaw: $score) { id } }'''
    updates_made = 0
    
    status_map = {"CURRENT": "Currently Active", "PLANNING": "Planning", "COMPLETED": "Completed", "DROPPED": "Dropped", "PAUSED": "Paused"}
    
    for title, data in inventory.items():
        media_id = str(data["mediaId"])
        progress = data["progress"]
        media_type = data["type"]
        
        if str(sync_db.get(media_id)) != str(progress):
            updates_made += 1
            user_status = status_map.get(data["status"], data["status"])
            
            # 🛠️ PATCH: Structuring the precise data matrix per your specs
            fields = [
                {"name": "🇯🇵 Romaji", "value": data['romaji'] or "N/A", "inline": False},
                {"name": "🇺🇸 English", "value": data['english'] or "N/A", "inline": False},
                {"name": "📊 Status", "value": user_status, "inline": False}
            ]
            
            if media_type == "ANIME":
                total = data['total_episodes']
                eps_left = (total - progress) if total else "?"
                season_info = f"{data['season'].capitalize()} {data['seasonYear']}" if data['season'] else "Unknown"
                
                fields.extend([
                    {"name": "✅ Watched", "value": f"{progress}", "inline": True},
                    {"name": "⏳ Left", "value": f"{eps_left}", "inline": True},
                    {"name": "🗓️ Season", "value": season_info, "inline": True}
                ])
                webhook = WEBHOOK_ANIME
                color = 3447003
                
            elif media_type == "MANGA":
                total_chaps = data['total_chapters']
                chaps_left = (total_chaps - progress) if total_chaps else "?"
                vol_prog = data.get('progressVolumes', 0)
                
                fields.extend([
                    {"name": "📖 Read", "value": f"{progress}", "inline": True},
                    {"name": "⏳ Left", "value": f"{chaps_left}", "inline": True},
                    {"name": "📚 Volume", "value": f"{vol_prog}", "inline": True}
                ])
                webhook = WEBHOOK_MANGA
                color = 15105570

            # Fire the high-density payload
            send_discord_alert(webhook, f"UPDATE: {title}", "", color, data.get('cover'), fields)
            
            if title in PRIORITY_FAVORITES:
                send_discord_alert(WEBHOOK_VIP, f"🔥 VIP TARGET UPDATED", f"**{title}** has reached progress {progress}!", 15158332, data.get('cover'))
                
            if TARGET_TOKEN:
                requests.post('https://graphql.anilist.co', json={'query': mutation_query, 'variables': {"id": data["mediaId"], "prog": progress, "score": data["scoreRaw"]}}, headers=HEADERS)
            
            sync_db[media_id] = progress
            
    save_db(DB_SYNC, sync_db)

# ==========================================
# 🚀 8. INITIATION SEQUENCE
# ==========================================
if __name__ == '__main__':
    print("=== MAXIMUM OVERDRIVE ENGINE: SPINNING UP ===")
    execute_48hr_purge()
    live_inventory = fetch_anilist_inventory(SOURCE_USERNAME)
    
    known_titles_pool = set()
    for data in live_inventory.values():
        if data.get('romaji'): known_titles_pool.add(data['romaji'].lower())
        if data.get('english'): known_titles_pool.add(data['english'].lower())
    
    process_airing_countdowns(live_inventory)
    execute_master_sync(live_inventory)
    
    ghost_db = sweep_mal_xml(known_titles_pool)
    updated_ghost_db = execute_ghost_radar(ghost_db)
    save_db(DB_GHOSTS, updated_ghost_db)
    print("=== MAXIMUM OVERDRIVE ENGINE: CYCLE COMPLETE ===")
    
