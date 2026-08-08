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
DB_THREADS_FILE = "db_threads.json"     # Remembers your Thread IDs
DB_MESSAGES_FILE = "db_messages.json"   # Tracks Message IDs for the 48-hour auto-delete

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

# --- 48-HOUR AUTO-DELETE LOGIC ---
def cleanup_old_messages(msg_db):
    """Hunts down and deletes any Discord message older than 48 hours (172,800 seconds)."""
    current_time = int(time.time())
    active_messages = []
    deleted_count = 0
    
    for msg in msg_db:
        # If older than 48 hours, send the DELETE strike to Discord
        if current_time - msg["timestamp"] > 172800:
            try:
                requests.delete(msg["delete_url"])
                deleted_count += 1
                time.sleep(1) # Rate limit protection
            except:
                pass
        else:
            # Keep the message in memory if it hasn't expired yet
            active_messages.append(msg)
            
    return active_messages, deleted_count

# --- DISCORD LOGIC ---
def send_sync_log(base_webhook, item, list_name, thread_db, msg_db):
    """Routes to threads dynamically, formats sleek logs, and stores IDs for auto-deletion."""
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

    # --- AUTONOMOUS THREAD ROUTING ---
    if media_type not in thread_db:
        thread_db[media_type] = {}
        
    existing_thread_id = thread_db[media_type].get(list_name)
    
    if existing_thread_id:
        target_url = f"{base_webhook}?thread_id={existing_thread_id}&wait=true"
    else:
        target_url = f"{base_webhook}?wait=true"
        payload["thread_name"] = list_name # Triggers Discord to spawn a new thread

    try:
        response = requests.post(target_url, json=payload)
        
        # --- MESSAGE MEMORY FOR AUTO-DELETE ---
        if response.status_code in [200, 201, 204]:
            data = response.json()
            msg_id = data.get("id")
            new_thread_id = data.get("channel_id")
            
            # Save new thread ID to database if we just spawned it
            if not existing_thread_id and new_thread_id:
                thread_db[media_type][list_name] = new_thread_id
                existing_thread_id = new_thread_id
                
            # Log the exact deletion URL for the 48-hour purge
            if msg_id:
                delete_url = f"{base_webhook}/messages/{msg_id}"
                if existing_thread_id:
                    delete_url += f"?thread_id={existing_thread_id}"
                    
                msg_db.append({
                    "delete_url": delete_url,
                    "timestamp": int(time.time())
                })
                
    except Exception as e:
        print(f"Error sending sync log: {e}")
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
        requests.post(AIRING_WEBHOOK, json=payload)
    except Exception as e:
        print(f"Error sending airing alert: {e}")
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
        requests.post(LOG_WEBHOOK, json=payload)
    except Exception as e:
        print(f"Error sending run report: {e}")

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
        requests.post(ERROR_WEBHOOK, json=payload)
    except Exception as e:
        print(f"Error sending error log: {e}")

# --- CORE ENGINE LOGIC ---
def fetch_anilist_data():
    url = 'https://graphql.anilist.co'
    
    # We added 'name' to the lists query so Discord knows which thread to use
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
        response = requests.post(url, json={'query': query, 'variables': variables})
        
        if response.status_code != 200:
            raise Exception(f"AniList API Error {response.status_code}: {response.text}")
            
        data = response.json()
        if 'errors' not in data and 'data' in data and data['data'].get('MediaListCollection'):
            all_lists.extend(data['data']['MediaListCollection']['lists'])
            
    return all_lists

def push_to_target(media_id, progress):
    if not TARGET_TOKEN:
        return
    url = 'https://graphql.anilist.co'
    query = '''mutation ($mediaId: Int, $progress: Int) { SaveMediaListEntry (mediaId: $mediaId, progress: $progress) { id } }'''
    headers = {'Authorization': f'Bearer {TARGET_TOKEN}', 'Content-Type': 'application/json'}
    requests.post(url, json={'query': query, 'variables': {'mediaId': media_id, 'progress': progress}}, headers=headers)

def main():
    try:
        # Load all memories
        sync_db = load_db(DB_SYNC_FILE, dict)
        airing_db = load_db(DB_AIRING_FILE, dict)
        thread_db = load_db(DB_THREADS_FILE, dict)
        msg_db = load_db(DB_MESSAGES_FILE, list) # Loads as a list
        
        # Run the 48-Hour Purge first
        msg_db, deleted_count = cleanup_old_messages(msg_db)
        
        lists = fetch_anilist_data()
        current_time = int(time.time())
        update_count = 0
        airings_found = False

        for lst in lists:
            list_name = lst.get('name', 'General')
            for entry in lst['entries']:
                media_id = str(entry['mediaId'])
                progress = entry['progress']
                media = entry['media']
                
                # 1. SYNC LOGIC
                if media_id not in sync_db or sync_db[media_id] < progress:
                    push_to_target(int(media_id), progress)
                    
                    webhook = ANIME_WEBHOOK if media['type'] == "ANIME" else MANGA_WEBHOOK
                    # Passes list_name, thread_db, and msg_db directly into the Discord router
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
                            send_airing_alert(media)
                            airing_db[db_key] = True
                            airings_found = True

        # 3. SHUTDOWN & SAVE LOGIC
        if update_count > 0 or deleted_count > 0:
            send_run_report(update_count, deleted_count)
            
        # Always save memory if anything changed (threads, deletes, airings, syncs)
        save_db(DB_SYNC_FILE, sync_db)
        save_db(DB_AIRING_FILE, airing_db)
        save_db(DB_THREADS_FILE, thread_db)
        save_db(DB_MESSAGES_FILE, msg_db)

    except Exception as e:
        send_error(str(e), traceback.format_exc())

if __name__ == "__main__":
    main()
