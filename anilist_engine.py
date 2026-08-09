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

# Discord Webhook Pipelines
WEBHOOK_ANIME = os.environ.get('DISCORD_ANIME_WEBHOOK')
WEBHOOK_MANGA = os.environ.get('DISCORD_MANGA_WEBHOOK')
WEBHOOK_AIRING = os.environ.get('DISCORD_AIRING_WEBHOOK')
WEBHOOK_LOG = os.environ.get('DISCORD_LOG_WEBHOOK')
WEBHOOK_VIP = os.environ.get('DISCORD_FAVORITES_WEBHOOK')
WEBHOOK_GHOST = os.environ.get('DISCORD_GHOST_RADAR_WEBHOOK')

# Memory Vaults
DB_SYNC = 'db_sync.json'
DB_MESSAGES = 'db_messages.json'
DB_GHOSTS = 'db_ghosts.json'
DB_AIRING = 'db_airing.json'
XML_FILE_PATH = 'mal_export.xml'

# S-Tier VIP Radar (Hardcoded targets for Gold Embeds)
PRIORITY_FAVORITES = [
    "One Piece", 
    "Detective Conan", 
    "JoJo's Bizarre Adventure",
    "Dragon Ball Z"
]

HEADERS = {
    'Authorization': f'Bearer {TARGET_TOKEN}' if TARGET_TOKEN else '',
    'Content-Type': 'application/json',
    'Accept': 'application/json',
}

# ==========================================
# 🧠 2. MEMORY VAULT MANAGEMENT
# ==========================================
def load_db(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f:
                return json.load(f)
        except Exception:
            return {}
    return {}

def save_db(filepath, data):
    with open(filepath, 'w') as f:
        json.dump(data, f, indent=4)

# ==========================================
# 📡 3. DISCORD COMMUNICATION PROTOCOLS
# ==========================================
def send_discord_alert(webhook_url, title, description, color, image_url=None):
    """Fires a customized embed directly to the command center."""
    if not webhook_url: return
    
    embed = {
        "title": title,
        "description": description,
        "color": color,
        "timestamp": datetime.now(timezone.utc).isoformat()
    }
    
    # 🛠️ PATCH: Changed from 'thumbnail' to 'image' for massive high-res posters
    if image_url:
        embed["image"] = {"url": image_url}
        
    payload = {"embeds": [embed]}
    
    response = requests.post(webhook_url + "?wait=true", json=payload)
    
    if response.status_code in [200, 204] and webhook_url == WEBHOOK_LOG:
        try:
            msg_id = response.json().get("id")
            if msg_id:
                messages_db = load_db(DB_MESSAGES)
                
                if isinstance(messages_db, list):
                    messages_db = {}
                    
                messages_db[msg_id] = {
                    "timestamp": time.time(),
                    "delete_url": f"{webhook_url}/messages/{msg_id}"
                }
                save_db(DB_MESSAGES, messages_db)
        except Exception:
            pass

def execute_48hr_purge():
    print("[SYSTEM] Executing 48-Hour Log Purge...")
    messages_db = load_db(DB_MESSAGES)
    
    if isinstance(messages_db, list):
        print("[SYSTEM] Legacy List format detected. Reformatting memory matrix...")
        messages_db = {}
        
    current_time = time.time()
    keys_to_delete = []
    
    for msg_id, data in messages_db.items():
        if current_time - data["timestamp"] > 172800:
            del_response = requests.delete(data["delete_url"])
            if del_response.status_code == 204:
                keys_to_delete.append(msg_id)
            time.sleep(1) 
            
    for key in keys_to_delete:
        del messages_db[key]
    save_db(DB_MESSAGES, messages_db)

# ==========================================
# 🔎 4. ANILIST GRAPHQL CORE (THE FETCH)
# ==========================================
def fetch_anilist_inventory(username):
    print(f"[ENGINE] Fetching Full Inventory for Source: {username}...")
    
    # 🛠️ PATCH: Requested 'extraLarge' for maximum download quality
    query = '''
    query ($userName: String, $page: Int) {
      Page(page: $page, perPage: 50) {
        pageInfo {
          hasNextPage
        }
        mediaList(userName: $userName) {
          mediaId
          progress
          score
          status
          media {
            title { romaji english }
            type
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
        
        if response.status_code != 200:
            print(f"[ERROR] Failed to fetch AniList data. Status: {response.status_code}")
            break
            
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
                "scoreRaw": item.get('score', 0), 
                "type": media['type'],
                # 🛠️ PATCH: Mapping the extraLarge high-res cover
                "cover": media['coverImage']['extraLarge'] if media.get('coverImage') else None,
                "nextAiring": media.get('nextAiringEpisode'),
                "romaji": romaji_title,
                "english": eng_title
            }
        
        page += 1
        time.sleep(1) 
        
    print(f"[ENGINE] Inventory Sweep Complete. Tracked {len(inventory)} total entries.")
    return inventory

# ==========================================
# ⏰ 5. AIRING INTELLIGENCE PROTOCOL
# ==========================================
def process_airing_countdowns(inventory):
    airing_db = load_db(DB_AIRING)
    
    if isinstance(airing_db, list):
        airing_db = {}
        
    current_time = int(time.time())
    
    for title, data in inventory.items():
        next_airing = data.get('nextAiring')
        if not next_airing:
            continue
            
        airing_at = next_airing['airingAt']
        ep_number = next_airing['episode']
        time_until = airing_at - current_time
        
        db_key = f"{data['mediaId']}_ep{ep_number}"
        
        if 0 < time_until <= 5400 and db_key not in airing_db:
            mins_left = time_until // 60
            print(f"[RADAR] Live Airing Alert: {title} Ep {ep_number} in {mins_left} mins!")
            
            send_discord_alert(
                WEBHOOK_AIRING, 
                f"🚨 AIRING COUNTDOWN: {title}", 
                f"**Episode {ep_number}** will broadcast in Japan in exactly **{mins_left} minutes**!", 
                15548997, 
                data.get('cover')
            )
            airing_db[db_key] = True
            
    save_db(DB_AIRING, airing_db)

# ==========================================
# 👻 6. MAL GHOST RADAR PROTOCOLS
# ==========================================
def sweep_mal_xml(known_titles_pool):
    ghosts = load_db(DB_GHOSTS)
    
    if isinstance(ghosts, list):
        ghosts = {}
    
    if not os.path.exists(XML_FILE_PATH):
        return ghosts
        
    print("[GHOST RADAR] Sweeping MAL XML for unregistered anomalies...")
    try:
        tree = ET.parse(XML_FILE_PATH)
        root = tree.getroot()
        
        new_count = 0
        for manga in root.findall('manga'):
            mal_title = manga.find('manga_title').text
            
            if mal_title.lower() not in known_titles_pool and mal_title not in ghosts:
                chaps = manga.find('my_read_chapters').text
                score = manga.find('my_score').text
                ghosts[mal_title] = {
                    "chapters": int(chaps) if chaps else 0,
                    "score": int(score) if score else 0
                }
                new_count += 1
                
        if new_count > 0: print(f"[GHOST RADAR] Isolated {new_count} NEW missing entries.")
    except Exception as e:
        print(f"[GHOST RADAR] XML Parse Error: {e}")
        
    return ghosts

def execute_ghost_radar(ghost_db):
    if not ghost_db: return ghost_db
    print(f"[GHOST RADAR] Hunting AniList Database for {len(ghost_db)} ghost targets...")
    
    search_query = '''query ($search: String) { Media (search: $search, type: MANGA) { id title { romaji english } } }'''
    mutation_query = '''mutation ($id: Int, $prog: Int, $score: Int) { SaveMediaListEntry (mediaId: $id, progress: $prog, scoreRaw: $score) { id } }'''
    
    assimilated = []
    for title, data in list(ghost_db.items()):
        res = requests.post('https://graphql.anilist.co', json={'query': search_query, 'variables': {"search": title}}, headers=HEADERS)
        
        if res.status_code == 200:
            result = res.json().get('data', {}).get('Media')
            if result:
                media_id = result['id']
                
                if TARGET_TOKEN:
                    mut_vars = {"id": media_id, "prog": data["chapters"], "score": data["score"] * 10}
                    requests.post('https://graphql.anilist.co', json={'query': mutation_query, 'variables': mut_vars}, headers=HEADERS)
                
                send_discord_alert(WEBHOOK_GHOST, "🟢 GHOST ASSIMILATED", f"**{title}** was successfully added to AniList and injected into your account.\n\n**Restored Chapters:** {data['chapters']}", 3066993)
                assimilated.append(title)
                
        time.sleep(1.5) 
        
    for title in assimilated:
        del ghost_db[title]
    return ghost_db

# ==========================================
# ⚡ 7. THE MASTER SYNC ENGINE (CORE DELTA)
# ==========================================
def execute_master_sync(inventory):
    sync_db = load_db(DB_SYNC)
    
    if isinstance(sync_db, list):
        sync_db = {}
        
    mutation_query = '''mutation ($id: Int, $prog: Int, $score: Int) { SaveMediaListEntry (mediaId: $id, progress: $prog, scoreRaw: $score) { id } }'''
    
    updates_made = 0
    
    for title, data in inventory.items():
        media_id = str(data["mediaId"])
        current_progress = data["progress"]
        media_type = data["type"]
        score_raw = data["scoreRaw"]
        
        if str(sync_db.get(media_id)) != str(current_progress):
            print(f"[SYNC DELTA] Update Detected: {title} -> {current_progress}")
            updates_made += 1
            
            webhook = WEBHOOK_ANIME if media_type == "ANIME" else WEBHOOK_MANGA
            color = 3447003 if media_type == "ANIME" else 15105570
            send_discord_alert(webhook, f"📺 UPDATE: {title}", f"Progress locked in at: **{current_progress}**", color, data.get('cover'))
            
            if title in PRIORITY_FAVORITES:
                send_discord_alert(WEBHOOK_VIP, f"🔥 S-TIER VIP UPDATE: {title}", f"Target reached progress count: **{current_progress}**!", 15158332, data.get('cover'))
                
            if TARGET_TOKEN:
                mut_vars = {"id": data["mediaId"], "prog": current_progress, "score": score_raw}
                mut_res = requests.post('https://graphql.anilist.co', json={'query': mutation_query, 'variables': mut_vars}, headers=HEADERS)
                if mut_res.status_code != 200:
                    print(f"[ERROR] Failed to mutate target account for {title}")
            
            sync_db[media_id] = current_progress
            
    save_db(DB_SYNC, sync_db)
    
    if updates_made > 0:
        send_discord_alert(WEBHOOK_LOG, "⚙️ ENGINE LOG", f"Cycle complete. Successfully synced **{updates_made}** new deltas.", 9807270)
    else:
        print("[ENGINE] No new deltas found. System idle.")

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
