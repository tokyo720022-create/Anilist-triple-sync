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

TARGET_TOKEN = os.environ.get('ANILIST_TARGET_TOKEN')
ANIME_WEBHOOK = os.environ.get('DISCORD_ANIME_WEBHOOK')
MANGA_WEBHOOK = os.environ.get('DISCORD_MANGA_WEBHOOK')
AIRING_WEBHOOK = os.environ.get('DISCORD_AIRING_WEBHOOK')
ERROR_WEBHOOK = os.environ.get('ERROR_REPORT_WEBHOOK')

# --- DATABASE LOGIC ---
def load_db(file_name):
    if os.path.exists(file_name):
        with open(file_name, "r") as f:
            return json.load(f)
    return {}

def save_db(file_name, data):
    with open(file_name, "w") as f:
        json.dump(data, f, indent=4)

# --- DISCORD LOGIC ---
def send_sync_log(webhook_url, item):
    """Formats and sends the exact 6-point update log."""
    if not webhook_url:
        return

    media = item['media']
    progress = item['progress']
    media_type = media['type']
    
    romaji = media['title']['romaji'] or "Unknown"
    english = media['title']['english'] or "No English Title"
    image = media['coverImage']['extraLarge']
    
    # Calculate Remaining
    total = media['episodes'] if media_type == "ANIME" else media['chapters']
    remaining = (total - progress) if total else "Unknown (Ongoing)"
    
    # Progress Text
    prog_type = "Episode" if media_type == "ANIME" else "Chapter"
    
    # Build Description
    desc = f"**1. Romaji:** {romaji}\n**2. English:** {english}\n"
    
    # 3. Start Date (Only if progress is 1 and start date exists)
    start = item.get('startedAt', {})
    if progress == 1 and start and start.get('year'):
        desc += f"**3. Start Date:** {start['year']}-{start.get('month', 1):02d}-{start.get('day', 1):02d}\n"
        
    desc += f"**4. Watched/Read:** {progress}\n"
    desc += f"**5. {prog_type}s Left:** {remaining}\n"
    
    # 6. End Date (Only if completed)
    end = item.get('completedAt', {})
    if total and progress == total and end and end.get('year'):
        desc += f"**6. End Date:** {end['year']}-{end.get('month', 1):02d}-{end.get('day', 1):02d}\n"

    payload = {
        "embeds": [{
            "title": f"🔄 Target Synced: {romaji}",
            "description": desc,
            "color": 3447003,
            "image": {"url": image}
        }]
    }
    try:
        requests.post(webhook_url, json=payload)
    except Exception as e:
        print(f"Error sending sync log: {e}")
    time.sleep(2) # Anti-spam rate limit protection

def send_airing_alert(media):
    """Sends an alert for anime airing within 90 minutes."""
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
    """Grabs both Sync Data and Airing Data in two safe GraphQL pulls."""
    url = 'https://graphql.anilist.co'
    
    query = '''
    query ($username: String, $type: MediaType) {
      MediaListCollection(userName: $username, type: $type) {
        lists {
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
        sync_db = load_db(DB_SYNC_FILE)
        airing_db = load_db(DB_AIRING_FILE)
        
        lists = fetch_anilist_data()
        current_time = int(time.time())
        updates_made = False
        airings_found = False

        for lst in lists:
            for entry in lst['entries']:
                media_id = str(entry['mediaId'])
                progress = entry['progress']
                media = entry['media']
                
                # 1. SYNC LOGIC
                if media_id not in sync_db or sync_db[media_id] < progress:
                    push_to_target(int(media_id), progress)
                    webhook = ANIME_WEBHOOK if media['type'] == "ANIME" else MANGA_WEBHOOK
                    send_sync_log(webhook, entry)
                    sync_db[media_id] = progress
                    updates_made = True

                # 2. AIRING LOGIC (90 Minute Warning)
                if media['type'] == "ANIME" and entry['status'] == "CURRENT" and media.get('nextAiringEpisode'):
                    air_time = media['nextAiringEpisode']['airingAt']
                    ep = str(media['nextAiringEpisode']['episode'])
                    time_until = air_time - current_time
                    
                    # If airing within 90 mins (5400 seconds) AND hasn't been alerted yet
                    if 0 < time_until <= 5400:
                        db_key = f"{media_id}_ep{ep}"
                        if db_key not in airing_db:
                            send_airing_alert(media)
                            airing_db[db_key] = True
                            airings_found = True

        # Save memories if anything changed
        if updates_made:
            save_db(DB_SYNC_FILE, sync_db)
        if airings_found:
            save_db(DB_AIRING_FILE, airing_db)

    except Exception as e:
        send_error(str(e), traceback.format_exc())

if __name__ == "__main__":
    main()
