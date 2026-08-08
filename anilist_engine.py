import os
import time
import json
import traceback
import requests
from datetime import datetime

# --- CONFIGURATION ---
SOURCE_USERNAME = "Orewatokyo"
DB_SYNC_FILE = "db_sync.json"
DB_AIRING_FILE = "db_airing.json"
DB_THREADS_FILE = "db_threads.json"
DB_MESSAGES_FILE = "db_messages.json"

# ==============================================================================
# ⭐ VIP PRIORITY FAVORITES LIST
# ==============================================================================
PRIORITY_FAVORITES = [
    "One Piece",
    "Detective Conan",
]

TARGET_TOKEN = os.environ.get('ANILIST_TARGET_TOKEN')
ANIME_WEBHOOK = os.environ.get('DISCORD_ANIME_WEBHOOK')
MANGA_WEBHOOK = os.environ.get('DISCORD_MANGA_WEBHOOK')
AIRING_WEBHOOK = os.environ.get('DISCORD_AIRING_WEBHOOK')
LOG_WEBHOOK = os.environ.get('DISCORD_LOG_WEBHOOK')
FAVORITES_WEBHOOK = os.environ.get('DISCORD_FAVORITES_WEBHOOK')
ERROR_WEBHOOK = os.environ.get('ERROR_REPORT_WEBHOOK')

# --- DATABASE LOGIC ---
def load_db(file_name, default_type=dict):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            return json.load(f)
    return default_type()

def save_db(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)
    print(f"[MEMORY] Successfully saved {file_name}")

def is_favorite(entry):
    media = entry['media']
    media_id = media['mediaId'] if 'mediaId' in media else entry.get('mediaId')
    romaji = (media['title']['romaji'] or "").lower()
    english = (media['title']['english'] or "").lower()
    
    for item in PRIORITY_FAVORITES:
        if isinstance(item, int) and item == media_id:
            return True
        elif isinstance(item, str):
            target = item.lower()
            if target in romaji or target in english:
                return True
    return False

# --- 48-HOUR AUTO-DELETE LOGIC ---
def cleanup_old_messages(msg_db):
    print("[SYSTEM] Running 48-hour auto-cleanup scan...")
    current_time = int(time.time())
    active_messages = []
    deleted_count = 0
    
    for msg in msg_db:
        if current_time - msg["timestamp"] > 172800:
            try:
                requests.delete(msg["delete_url"], timeout=15)
                deleted_count += 1
                time.sleep(1) 
            except Exception as e:
                print(f"[WARNING] Failed to delete expired log: {e}")
        else:
            active_messages.append(msg)
            
    print(f"[SYSTEM] Cleanup complete. {deleted_count} messages purged.")
    return active_messages, deleted_count

# --- DISCORD LOGIC ---
def send_favorite_alert(entry):
    if not FAVORITES_WEBHOOK:
        return

    media = entry['media']
    progress = entry['progress']
    score = entry.get('scoreRaw', 0)
    media_type = media['type']
    
    romaji = media['title']['romaji'] or "Unknown"
    english = media['title']['english'] or "N/A"
    image = media['coverImage']['extraLarge']
    
    total = media['episodes'] if media_type == "ANIME" else media['chapters']
    unit = "Episode" if media_type == "ANIME" else "Chapter"
    
    if total:
        left_count = total - progress
        if left_count == 1:
            remaining_str = f"**1 {unit} left!** 🚨 **FINALE INBOUND!** 🔥"
        elif left_count == 0:
            remaining_str = "**COMPLETED!** 🏆"
        else:
            remaining_str = f"{left_count} {unit}s remaining"
    else:
        remaining_str = "Ongoing / Active Release"

    type_icon = "👑🎬" if media_type == "ANIME" else "👑📖"
    
    lines = [
        f"🌟 **VIP FAVORITE UPDATE DETECTED** 🌟",
        f"🇯🇵 **Title:** {romaji}",
        f"🌐 **English:** {english}",
        f"{type_icon} **Current Progress:** {unit} {progress}",
        f"⏳ **Status:** {remaining_str}"
    ]
    
    if score > 0:
        lines.append(f"⭐ **Rating:** {int(score)}/100")

    payload = {
        "embeds": [{
            "title": f"🔥 VIP RELEASE ALERT | {romaji}",
            "description": "\n".join(lines),
            "color": 16766720, 
            "image": {"url": image}
        }]
    }
    try:
        requests.post(FAVORITES_WEBHOOK, json=payload, timeout=15)
    except Exception as e:
        print(f"[ERROR] Failed to send VIP favorite alert: {e}")
    time.sleep(2)

def send_sync_log(base_webhook, entry, media_id, thread_db, msg_db):
    if not base_webhook:
        return

    media = entry['media']
    progress = entry['progress']
    score = entry.get('scoreRaw', 0) 
    media_type = media['type']
    
    romaji = media['title']['romaji'] or "Unknown"
    english = media['title']['english'] or "N/A"
    image = media['coverImage']['extraLarge']
    
    total = media['episodes'] if media_type == "ANIME" else media['chapters']
    if total:
        left_count = total - progress
        unit = "Episode" if media_type == "ANIME" else "Chapter"
        
        if left_count == 1:
            remaining_str = f"**1 {unit} left!** 🚨 **FINALE INBOUND!** 🔥"
        elif left_count == 0:
            remaining_str = "**0 (Completed!)** 🏆"
        else:
            remaining_str = f"{left_count} {unit}{'s' if left_count != 1 else ''} left"
    else:
        remaining_str = "Ongoing / Unknown"
    
    type_icon = "🎬" if media_type == "ANIME" else "📖"
    prog_label = "Episode" if media_type == "ANIME" else "Chapter"
    
    lines = [
        f"🇯🇵 **Romaji:** {romaji}",
        f"🌐 **English:** {english}",
        f"{type_icon} **Watched/Read:** {prog_label} {progress}",
        f"⏳ **Remaining:** {remaining_str}"
    ]
    
    if score > 0:
        lines.append(f"⭐ **Rating:** {int(score)}/100")
    
    start = entry.get('startedAt', {})
    if progress == 1 and start and start.get('year'):
        lines.append(f"🗓️ **Started:** {start['year']}-{start.get('month', 1):02d}-{start.get('day', 1):02d}")
        
    end = entry.get('completedAt', {})
    if total and progress == total and end and end.get('year'):
        lines.append(f"🏁 **Finished:** {end['year']}-{end.get('month', 1):02d}-{end.get('day', 1):02d}")

    payload = {
        "embeds": [{
            "title": f"⚡ Target Synced | {romaji}",
            "description": "\n".join(lines),
            "color": 3447003,
            "image": {"url": image}
        }]
    }

    if media_type not in thread_db:
        thread_db[media_type] = {}
        
    existing_thread_id = thread_db[media_type].get(media_id)
    
    if existing_thread_id:
        target_url = f"{base_webhook}?thread_id={existing_thread_id}&wait=true"
    else:
        target_url = f"{base_webhook}?wait=true"
        payload["thread_name"] = romaji[:90] 

    try:
        response = requests.post(target_url, json=payload, timeout=15)
        
        if response.status_code == 400 and "thread_name" in payload:
            print(f"[WARNING] Discord blocked thread creation for {romaji}. Falling back to standard message.")
            del payload["thread_name"]
            response = requests.post(f"{base_webhook}?wait=true", json=payload, timeout=15)

        if response.status_code in [200, 201, 204]:
            data = response.json()
            msg_id = data.get("id")
            new_thread_id = data.get("channel_id")
            
            if not existing_thread_id and new_thread_id:
                thread_db[media_type][media_id] = new_thread_id
                existing_thread_id = new_thread_id
                
            if msg_id:
                delete_url = f"{base_webhook}/messages/{msg_id}"
                if existing_thread_id:
                    delete_url += f"?thread_id={existing_thread_id}"
                    
                msg_db.append({
                    "delete_url": delete_url,
                    "timestamp": int(time.time())
                })
                
    except Exception as e:
        print(f"[ERROR] Failed to send Discord sync log: {e}")
    time.sleep(2)

def send_airing_alert(media):
    if not AIRING_WEBHOOK:
        return

    romaji = media['title']['romaji']
    image = media['coverImage']['extraLarge']
    ep = media['nextAiringEpisode']['episode']
    air_time = media['nextAiringEpisode']['airingAt']
    
    payload = {
        "embeds": [{
            "title": f"🔥 AIRING ALERT: {romaji}",
            "description": f"**Episode {ep}** is dropping!\n\n**Telecast Time:** <t:{air_time}:F>\n**Live Countdown:** <t:{air_time}:R>",
            "color": 15158332,
            "image": {"url": image}
        }]
    }
    try:
        requests.post(AIRING_WEBHOOK, json=payload, timeout=15)
    except Exception as e:
        print(f"[ERROR] Failed to send airing alert: {e}")
    time.sleep(2)

def send_run_report(count, deleted_count):
    if not LOG_WEBHOOK:
        return

    desc = f"Successfully synced **{count}** new updates to the target account and routed them to their designated threads."
    if deleted_count > 0:
        desc += f"\n🧹 **Auto-Cleanup:** Purged {deleted_count} expired logs (48h limit)."

    payload = {
        "embeds": [{
            "title": "⚙️ Engine Shutdown & Saved",
            "description": desc,
            "color": 3066993
        }]
    }
    try:
        requests.post(LOG_WEBHOOK, json=payload, timeout=15)
    except Exception as e:
        print(f"[ERROR] Failed to send run report: {e}")

def send_error(error_msg, stack_trace):
    if not ERROR_WEBHOOK:
        return

    payload = {
        "embeds": [{
            "title": "🚨 CRITICAL FAILURE: AniList Engine",
            "description": f"**Error:** {error_msg}\n\n**Traceback:**\n```python\n{stack_trace[:3000]}\n```",
            "color": 16711680
        }]
    }
    try:
        requests.post(ERROR_WEBHOOK, json=payload, timeout=15)
    except Exception as e:
        print(f"[ERROR] Engine failure logger crashed: {e}")

# --- CORE ENGINE LOGIC ---
def fetch_anilist_data():
    print("[SYSTEM] Fetching data from AniList API...")
    url = 'https://graphql.anilist.co'
    query = '''
    query ($username: String, $type: MediaType) {
      MediaListCollection(userName: $username, type: $type) {
        lists {
          entries {
            mediaId
            progress
            scoreRaw: score(format: POINT_100) 
            status
            startedAt { year month day }
            completedAt { year month day }
            media {
              type
              episodes
              chapters
              title { romaji english }
              coverImage { extraLarge }
              nextAiringEpisode { airingAt episode }
            }
          }
        }
      }
    }
    '''
    all_lists = []
    
    for media_type in ["ANIME", "MANGA"]:
        variables = {'username': SOURCE_USERNAME, 'type': media_type}
        response = requests.post(url, json={'query': query, 'variables': variables}, timeout=15)
        
        if response.status_code != 200:
            raise Exception(f"AniList API Error {response.status_code}: {response.text}")
            
        data = response.json()
        if 'errors' not in data and 'data' in data and data['data'].get('MediaListCollection'):
            chunk = data['data']['MediaListCollection']['lists']
            all_lists.extend(chunk)
            
    return all_lists

def push_to_target(media_id, progress, scoreRaw):
    if not TARGET_TOKEN:
        return
    url = 'https://graphql.anilist.co'
    query = '''mutation ($mediaId: Int, $progress: Int, $scoreRaw: Int) { SaveMediaListEntry (mediaId: $mediaId, progress: $progress, scoreRaw: $scoreRaw) { id } }'''
    headers = {'Authorization': f'Bearer {TARGET_TOKEN}', 'Content-Type': 'application/json'}
    variables = {'mediaId': media_id, 'progress': progress}
    if scoreRaw > 0:
        variables['scoreRaw'] = int(scoreRaw)
        
    requests.post(url, json={'query': query, 'variables': variables}, headers=headers, timeout=15)

def main():
    try:
        print("[SYSTEM] Engine Online. Loading memory arrays...")
        sync_db = load_db(DB_SYNC_FILE, dict)
        airing_db = load_db(DB_AIRING_FILE, dict)
        thread_db = load_db(DB_THREADS_FILE, dict)
        msg_db = load_db(DB_MESSAGES_FILE, list) 
        
        msg_db, deleted_count = cleanup_old_messages(msg_db)
        
        lists = fetch_anilist_data()
        current_time = int(time.time())
        update_count = 0
        airings_found = False

        print("[SYSTEM] Scanning for new watchlist updates...")
        for lst in lists:
            for entry in lst['entries']:
                media_id = str(entry['mediaId'])
                progress = entry['progress']
                scoreRaw = entry.get('scoreRaw', 0)
                media = entry['media']
                
                current_state = f"{progress}-{scoreRaw}"
                saved_state = sync_db.get(media_id, "0-0")
                
                # --- THE AMNESIA PATCH ---
                # Silently converts old integer memory (e.g., 12) to new string format ("12-0")
                if isinstance(saved_state, int):
                    saved_state = f"{saved_state}-0"
                    sync_db[media_id] = saved_state 
                # -------------------------
                
                if current_state != saved_state:
                    print(f"[SYNC] Pushing Target Update -> {media['title']['romaji']} (Prog: {progress} | Score: {scoreRaw})")
                    push_to_target(int(media_id), progress, scoreRaw)
                    
                    webhook = ANIME_WEBHOOK if media['type'] == "ANIME" else MANGA_WEBHOOK
                    send_sync_log(webhook, entry, media_id, thread_db, msg_db)
                    
                    if is_favorite(entry):
                        send_favorite_alert(entry)

                    sync_db[media_id] = current_state
                    update_count += 1

                if media['type'] == "ANIME" and entry['status'] == "CURRENT" and media.get('nextAiringEpisode'):
                    air_time = media['nextAiringEpisode']['airingAt']
                    ep = str(media['nextAiringEpisode']['episode'])
                    time_until = air_time - current_time
                    
                    if 0 < time_until <= 5400:
                        db_key = f"{media_id}_ep{ep}"
                        if db_key not in airing_db:
                            send_airing_alert(media)
                            
                            if is_favorite(entry):
                                send_favorite_alert(entry)
                                
                            airing_db[db_key] = True
                            airings_found = True

        if update_count == 0:
            print("[SYSTEM] Zero updates found. Target is completely synced.")

        if update_count > 0 or deleted_count > 0:
            send_run_report(update_count, deleted_count)
            
        save_db(DB_SYNC_FILE, sync_db)
        save_db(DB_AIRING_FILE, airing_db)
        save_db(DB_THREADS_FILE, thread_db)
        save_db(DB_MESSAGES_FILE, msg_db)
        print("[SYSTEM] Engine Shutdown Sequence Complete.")

    except Exception as e:
        print(f"[CRITICAL ERROR] {e}")
        send_error(str(e), traceback.format_exc())

if __name__ == "__main__":
    main()
