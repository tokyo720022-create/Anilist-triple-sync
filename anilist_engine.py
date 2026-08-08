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

TARGET_TOKEN = os.environ['ANILIST_TARGET_TOKEN']
ANIME_WEBHOOK = os.environ['DISCORD_ANIME_WEBHOOK']
MANGA_WEBHOOK = os.environ['DISCORD_MANGA_WEBHOOK']
AIRING_WEBHOOK = os.environ['DISCORD_AIRING_WEBHOOK']
ERROR_WEBHOOK = os.environ['ERROR_REPORT_WEBHOOK']

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
    
    # 3. Start Date (Only if progress is 1)
    if progress == 1 and item['startedAt']['year']:
        start = item['startedAt']
        desc += f"**3. Start Date:** {start['year']}-{start['month']:02d}-{start['day']:02d}\n"
        
    desc += f"**4. Watched/Read:** {progress}\n"
    desc += f"**5. {prog_type}s Left:** {remaining}\n"
    
    # 6. End Date (Only if completed)
    if total and progress == total and item['completedAt']['year']:
        end = item['completedAt']
        desc += f"**6. End Date:** {end['year']}-{end['month']:02d}-{end['day']:02d}\n"

    payload = {
        "embeds": [{
            "title": f"🔄 Target Synced: {romaji}",
            "description": desc,
            "color": 3447003,
            "image": {"url": image}
        }]
    }
    requests.post(webhook_url, json=payload)
    time.sleep(2) # Rate limit protection

def send_airing_alert(media):
    """Sends a hype alert for anime airing within 90 minutes."""
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
    requests.post(AIRING_WEBHOOK, json=payload)
    time.sleep(2)

def send_error(error_msg, stack_trace):
    payload = {
        "embeds": [{
            "title": "🚨 CRITICAL FAILURE: AniList Engine",
            "description": f"**Error:** {error_msg}\n\n**Traceback:**\n```python\n{stack_trace[:3000]}\n```",
            "color": 16711680
        }]
    }
    requests.post(ERROR_WEBHOOK, json=payload)

# --- CORE ENGINE LOGIC ---
def fetch_anilist_data():
    """Grabs both Sync Data and Airing Data in two safe GraphQL pulls."""
    url = 'https://graphql.anilist.co'
    
    # We added $type back into the query since AniList strictly requires it
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
    
    # The engine now loops to pull Anime and Manga separately
    for media_type in ["ANIME", "MANGA"]:
        variables = {'username': SOURCE_USERNAME, 'type': media_type}
        response = requests.post(url, json={'query': query, 'variables': variables})
        
        # If AniList rejects the query, this prints the EXACT reason why in Discord
        if response.status_code != 200:
            raise Exception(f"AniList API Error {response.status_code}: {response.text}")
            
        data = response.json()
        if 'errors' not in data and 'data' in data and data['data'].get('MediaListCollection'):
            all_lists.extend(data['data']['MediaListCollection']['lists'])
            
    return all_lists
    
                
                # 1. SYNC LOGIC
                if media_id not in sync_db or sync_db[media_id] < progress:
                    push_to_target(int(media_id), progress)
                    webhook = ANIME_WEBHOOK if media['type'] == "ANIME" else MANGA_WEBHOOK
                    send_sync_log(webhook, entry)
                    sync_db[media_id] = progress
                    updates_made = True

                # 2. AIRING LOGIC (90 Minute Warning)
                if media['type'] == "ANIME" and entry['status'] == "CURRENT" and media['nextAiringEpisode']:
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
        if updates_made: save_db(DB_SYNC_FILE, sync_db)
        if airings_found: save_db(DB_AIRING_FILE, airing_db)

    except Exception as e:
        send_error(str(e), traceback.format_exc())

if __name__ == "__main__":
    main()
  
