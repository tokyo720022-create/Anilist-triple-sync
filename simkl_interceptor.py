import os
import json
import requests
from datetime import datetime, timedelta

# ==========================================
# ⚙️ SIMKL MATRIX CONFIGURATION
# ==========================================
SIMKL_CLIENT_ID = "ada96e4da580941764fc53baea2b8603de08dd63ce6943784f26e237526a7e65"
SIMKL_TOKEN = "91c24a3a39ac71e9d83cda93d21c57e9300a061c4fd190c07cbf64382e9462b9"
DISCORD_WEBHOOK_GHOST = "https://discord.com/api/webhooks/1536382712871522387/8e-YYsBipOMqw0FdXbkQszKCMK-oDuzAREgtK53jZcpysaHYlcKXNI7vnmEkD-Tb8VR2"

HEADERS = {
    "Authorization": f"Bearer {SIMKL_TOKEN}",
    "simkl-api-key": SIMKL_CLIENT_ID,
    "Content-Type": "application/json"
}

DB_BUFFER = "db_simkl_buffer.json"
DB_GHOSTS = "db_simkl_ghosts.json"

# ==========================================
# 📂 FILE I/O PROTOCOLS
# ==========================================
def load_db(file_path):
    if os.path.exists(file_path):
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    return {}

def save_db(file_path, data):
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4)

# ==========================================
# 📡 DISCORD RADAR ALERTS
# ==========================================
def fire_discord_alert(title, anilist_id, status, color):
    payload = {
        "embeds": [{
            "title": status,
            "description": f"**{title}**",
            "color": color,
            "fields": [
                {"name": "AniList ID", "value": str(anilist_id), "inline": True}
            ]
        }]
    }
    requests.post(DISCORD_WEBHOOK_GHOST, json=payload)

# ==========================================
# ⏳ THE 4-HOUR TIME-LOCK BUFFER
# ==========================================
def inject_into_buffer(anilist_id, title, ep_number):
    buffer = load_db(DB_BUFFER)
    
    # If it's already in the buffer, just update the episode number, don't reset the clock
    if str(anilist_id) not in buffer:
        unlock_time = (datetime.now() + timedelta(hours=4)).isoformat()
        buffer[str(anilist_id)] = {
            "title": title,
            "episode": ep_number,
            "unlock_time": unlock_time
        }
        save_db(DB_BUFFER, buffer)
        print(f"[BUFFER] Locked {title} (Ep {ep_number}). Unlocking in 4 hours.")

# ==========================================
# ⚔️ EXECUTE INTERCEPTION & GHOST PROTOCOL
# ==========================================
def execute_simkl_radar():
    buffer = load_db(DB_BUFFER)
    ghosts = load_db(DB_GHOSTS)
    now = datetime.now()
    
    buffer_updated = False
    ghosts_updated = False
    keys_to_delete = []

    for al_id, data in buffer.items():
        unlock_time = datetime.fromisoformat(data["unlock_time"])
        
        if now >= unlock_time:
            print(f"[RADAR] Unlock time reached for {data['title']}. Initiating strike...")
            
            # Step 1: Verify Simkl ID exists in their master database
            search_res = requests.get(f"https://api.simkl.com/search/id?anilist={al_id}&client_id={SIMKL_CLIENT_ID}")
            
            if search_res.status_code == 200 and len(search_res.json()) > 0:
                simkl_id = search_res.json()[0]['id']['simkl']
                
                # Step 2: Fire payload. If Trakt got it first, Simkl natively ignores it.
                sync_payload = {
                    "shows": [{
                        "ids": {"simkl": simkl_id},
                        "episodes": [{"number": data["episode"]}]
                    }]
                }
                sync_res = requests.post("https://api.simkl.com/sync/history", json=sync_payload, headers=HEADERS)
                
                if sync_res.status_code in [200, 201]:
                    print(f"✅ [SUCCESS] {data['title']} synced or verified via Trakt bypass.")
                    keys_to_delete.append(al_id)
            else:
                # Target is missing from Simkl's database. Move to Ghost Vault.
                print(f"👻 [GHOST DETECTED] {data['title']} not found on Simkl.")
                ghosts[str(al_id)] = {
                    "title": data["title"],
                    "episode": data["episode"],
                    "last_check": now.isoformat()
                }
                fire_discord_alert(data["title"], al_id, "👻 GHOST PROTOCOL ACTIVATED", 16711680)
                keys_to_delete.append(al_id)
                ghosts_updated = True
                
            buffer_updated = True

    # Sweep completed buffer entries
    for k in keys_to_delete:
        del buffer[k]
        
    if buffer_updated:
        save_db(DB_BUFFER, buffer)

    # Step 3: Daily Ghost Radar Ping (Check if Simkl added missing anime)
    ghost_keys_to_recover = []
    for al_id, data in ghosts.items():
        last_check = datetime.fromisoformat(data["last_check"])
        
        # Only ping ghosts once every 24 hours to protect rate limits
        if now >= last_check + timedelta(hours=24):
            search_res = requests.get(f"https://api.simkl.com/search/id?anilist={al_id}&client_id={SIMKL_CLIENT_ID}")
            
            if search_res.status_code == 200 and len(search_res.json()) > 0:
                simkl_id = search_res.json()[0]['id']['simkl']
                
                sync_payload = {
                    "shows": [{
                        "ids": {"simkl": simkl_id},
                        "episodes": [{"number": data["episode"]}]
                    }]
                }
                requests.post("https://api.simkl.com/sync/history", json=sync_payload, headers=HEADERS)
                fire_discord_alert(data["title"], al_id, "🟢 GHOST RECOVERED & SYNCED", 65280)
                ghost_keys_to_recover.append(al_id)
            else:
                # Still a ghost, reset the 24-hour clock
                ghosts[str(al_id)]["last_check"] = now.isoformat()
            
            ghosts_updated = True

    # Sweep recovered ghosts
    for k in ghost_keys_to_recover:
        del ghosts[k]

    if ghosts_updated:
        save_db(DB_GHOSTS, ghosts)
    
    print("=== SIMKL RADAR SWEEP COMPLETE ===")

if __name__ == '__main__':
    execute_simkl_radar()
