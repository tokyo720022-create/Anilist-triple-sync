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

TARGET_TOKEN = os.environ.get('ANILIST_TARGET_TOKEN')
ANIME_WEBHOOK = os.environ.get('DISCORD_ANIME_WEBHOOK')
MANGA_WEBHOOK = os.environ.get('DISCORD_MANGA_WEBHOOK')
AIRING_WEBHOOK = os.environ.get('DISCORD_AIRING_WEBHOOK')
LOG_WEBHOOK = os.environ.get('DISCORD_LOG_WEBHOOK')
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
def send_sync_log(base_webhook, item, list_name, thread_db, msg_db):
    if not base_webhook:
        return

    media = item['media']
    progress = item['progress']
    media_type = media['type']
    
    romaji = media['title']['romaji'] or "Unknown"
    english = media['title']['english'] or "N/A"
    image = media['coverImage']['extraLarge']
    
    total = media['episodes'] if media_type == "ANIME" else media['chapters']
    if total:
        left_count = total - progress
        unit = "Episode" if media_type == "ANIME" else "Chapter"
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
    
    start = item.get('startedAt', {})
    if progress == 1 and start and start.get('year'):
        lines.append(f"🗓️ **Started:** {start['year']}-{start.get('month', 1):02d}-{start.get('day', 1):02d}")
        
    end = item.get('completedAt', {})
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
        
    existing_thread_id = thread_db[media_type].get(list_name)
    
    if existing_thread_id:
        target_url = f"{base_webhook}?thread_id={existing_thread_id}&wait=true"
    else:
        target_url = f"{base_webhook}?wait=true"
        payload["thread_name"] = list_name 

    try:
        response = requests.post(target_url, json=payload, timeout=15)
        
        if response.status_code in [200, 201, 204]:
            data = response.json()
            msg_id = data.get("id")
            new_thread_id = data.get("channel_id")
            
            if not existing_thread_id and new_thread_id:
                thread_db[media_type][list_name] = new_thread_id
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

    desc = f"Successfully synced **{count}** new updates to the target account and routed them to their list threads."
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
          name
          entries {
            mediaId
            progress
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
            print(f"[INFO] Fetched {len(chunk)} lists for {media_type}")
            
    return all_lists

def push_to_target(media_id, progress):
    if not TARGET_TOKEN:
        return
    url = 'https://graphql.anilist.co'
    query = '''mutation ($mediaId: Int, $progress: Int) { SaveMediaListEntry (mediaId: $mediaId, progress: $progress) { id } }'''
    headers = {'Authorization': f'Bearer {TARGET_TOKEN}', 'Content-Type': 'application/json'}
    requests.post(url, json={'query': query, 'variables': {'mediaId': media_id, 'progress': progress}}, headers=headers, timeout=15)

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
            list_name = lst.get('name', 'General')
            for entry in lst['entries']:
                media_id = str(entry['mediaId'])
                progress = entry['progress']
                media = entry['media']
                
                # 1. SYNC LOGIC
                if media_id not in sync_db or sync_db[media_id] < progress:
                    print(f"[SYNC] Pushing Target Update -> {media['title']['romaji']} (Progress: {progress})")
                    push_to_target(int(media_id), progress)
                    
                    webhook = ANIME_WEBHOOK if media['type'] == "ANIME" else MANGA_WEBHOOK
                    send_sync_log(webhook, entry, list_name, thread_db, msg_db)
                    
                    sync_db[media_id] = progress
                    update_count += 1

                # 2. AIRING LOGIC (90 Minute Warning)
                if media['type'] == "ANIME" and entry['status'] == "CURRENT" and media.get('nextAiringEpisode'):
                    air_time = media['nextAiringEpisode']['airingAt']
                    ep = str(media['nextAiringEpisode']['episode'])
                    time_until = air_time - current_time
                    
                    if 0 < time_until <= 5400:
                        db_key = f"{media_id}_ep{ep}"
                        if db_key not in airing_db:
                            print(f"[ALERT] Spawning 90-Min Alert for {media['title']['romaji']}")
                            send_airing_alert(media)
                            airing_db[db_key] = True
                            airings_found = True

        if update_count == 0:
            print("[SYSTEM] Zero updates found. Target is completely synced.")

        # 3. SHUTDOWN & SAVE LOGIC
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
