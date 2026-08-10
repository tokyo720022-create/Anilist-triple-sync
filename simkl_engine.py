import os
import json
import requests
from datetime import datetime, timedelta

# ==========================================
# ⚙️ SIMKL SECRETS & CONFIGURATION
# ==========================================
SIMKL_CLIENT_ID = os.environ.get('SIMKL_CLIENT_ID')
SIMKL_TOKEN = os.environ.get('SIMKL_TOKEN')
DISCORD_WEBHOOK_GHOST = os.environ.get('DISCORD_GHOST')

HEADERS = {
    "Authorization": f"Bearer {SIMKL_TOKEN}",
    "simkl-api-key": SIMKL_CLIENT_ID,
    "Content-Type": "application/json",
    "User-Agent": "AnilistBufferMatrix/1.0"
}

DB_BUFFER = "db_simkl_buffer.json"
DB_GHOSTS = "db_simkl_ghosts.json"

def load_db(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_db(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

def fire_discord_alert(title, anilist_id, status, color):
    if not DISCORD_WEBHOOK_GHOST: return
    payload = {
        "embeds": [{
            "title": status,
            "description": f"**{title}**",
            "color": color,
            "fields": [{"name": "AniList ID", "value": str(anilist_id), "inline": True}]
        }]
    }
    requests.post(DISCORD_WEBHOOK_GHOST, json=payload)

# 🔥 THIS IS FOR ANILIST_ENGINE TO USE
def inject_into_buffer(anilist_id, title, ep_number):
    buffer = load_db(DB_BUFFER)
    if str(anilist_id) not in buffer:
        unlock_time = (datetime.now() + timedelta(hours=4)).isoformat()
        buffer[str(anilist_id)] = {
            "title": title,
            "episode": ep_number,
            "unlock_time": unlock_time
        }
        save_db(DB_BUFFER, buffer)
        print(f"[BUFFER] Locked {title} (Ep {ep_number}). Unlocking in 4 hours.")

# ⚔️ THIS RUNS AT 2 PM & 11 PM
def run_simkl_sync_cycle():
    print("⚡ [SIMKL ENGINE] Executing buffer flush and verification cycle...")
    buffer = load_db(DB_BUFFER)
    ghosts = load_db(DB_GHOSTS)
    now = datetime.now()
    
    buffer_updated = False
    ghosts_updated = False
    keys_to_delete = []

    for al_id, data in buffer.items():
        unlock_time = datetime.fromisoformat(data["unlock_time"])
        
        if now >= unlock_time:
            print(f"[RADAR] Processing: {data['title']} (Ep {data['episode']})")
            search_res = requests.get(f"https://api.simkl.com/search/id?anilist={al_id}&client_id={SIMKL_CLIENT_ID}", headers=HEADERS)
            
            if search_res.status_code == 200 and len(search_res.json()) > 0:
                simkl_id = search_res.json()[0]['id']['simkl']
                sync_payload = {
                    "shows": [{"ids": {"simkl": simkl_id}, "episodes": [{"number": data["episode"]}]}]
                }
                sync_res = requests.post("https://api.simkl.com/sync/history", json=sync_payload, headers=HEADERS)
                
                if sync_res.status_code in [200, 201]:
                    print(f"✅ [SUCCESS] {data['title']} synced or verified via Trakt bypass.")
                    keys_to_delete.append(al_id)
            else:
                print(f"👻 [GHOST DETECTED] {data['title']} not found on Simkl.")
                ghosts[str(al_id)] = {"title": data["title"], "episode": data["episode"], "last_check": now.isoformat()}
                fire_discord_alert(data["title"], al_id, "👻 GHOST PROTOCOL ACTIVATED", 16711680)
                keys_to_delete.append(al_id)
                ghosts_updated = True
                
            buffer_updated = True

    for k in keys_to_delete:
        del buffer[k]
        
    if buffer_updated:
        save_db(DB_BUFFER, buffer)
    
    print("=== SIMKL CYCLE COMPLETE ===")

if __name__ == '__main__':
    run_simkl_sync_cycle()
