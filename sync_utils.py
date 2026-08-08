import os
import json
import requests

THREAD_MEMORY_FILE = "discord_threads.json"

# --- DISCORD LOGIC ---
def load_thread_memory():
    if os.path.exists(THREAD_MEMORY_FILE):
        with open(THREAD_MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"ANIME": {}, "MANGA": {}}

def save_thread_memory(memory_data):
    with open(THREAD_MEMORY_FILE, "w") as f:
        json.dump(memory_data, f, indent=4)

def send_item_log(webhook_url, title, progress, img, media_type, list_name):
    memory = load_thread_memory()
    progress_text = f"Episode {progress}" if media_type == "ANIME" else f"Chapter {progress}"
    
    payload = {
        "embeds": [{
            "title": f"🔄 Synced: {title}",
            "description": f"Updated to **{progress_text}**\n📂 List: {list_name}",
            "color": 3447003,
            "image": {"url": img}
        }]
    }

    existing_thread_id = memory[media_type].get(list_name)
    
    if existing_thread_id:
        requests.post(f"{webhook_url}?thread_id={existing_thread_id}&wait=true", json=payload)
    else:
        payload["thread_name"] = list_name
        response = requests.post(f"{webhook_url}?wait=true", json=payload)
        
        if response.status_code in [200, 201, 204]:
            try:
                new_id = response.json().get("channel_id")
                if new_id:
                    memory[media_type][list_name] = new_id
                    save_thread_memory(memory)
            except Exception:
                pass

def send_run_report(webhook_url, account_name, status, items_synced):
    color = 3066993 if status == "Success" else 15158332
    data = {
        "embeds": [{
            "title": f"⚙️ {account_name} Sync: {status}",
            "description": f"Processed **{items_synced}** new updates.",
            "color": color
        }]
    }
    requests.post(webhook_url, json=data)

def send_error_report(webhook_url, target_system, error_msg, stack_trace):
    data = {
        "embeds": [{
            "title": f"🚨 CRITICAL FAILURE: {target_system}",
            "description": f"**Error:** {error_msg}\n\n**Traceback:**\n```python\n{stack_trace[:3000]}\n```",
            "color": 16711680
        }]
    }
    requests.post(webhook_url, json=data)


# --- DATABASE LOGIC ---
def load_database(db_file):
    if os.path.exists(db_file):
        with open(db_file, "r") as f:
            return json.load(f)
    return {} 

def save_database(db_file, db_data):
    with open(db_file, "w") as f:
        json.dump(db_data, f, indent=4)


# --- ANILIST SOURCE FETCH LOGIC ---
def fetch_source_activity(username):
    url = 'https://graphql.anilist.co'
    query = '''
    query ($username: String, $type: MediaType) {
      MediaListCollection(userName: $username, type: $type) {
        lists {
          name
          entries {
            mediaId
            progress
            media {
              idMal
              type
              title { romaji }
              coverImage { large }
            }
          }
        }
      }
    }
    '''
    updates = []
    for media_type in ["ANIME", "MANGA"]:
        variables = {'username': username, 'type': media_type}
        response = requests.post(url, json={'query': query, 'variables': variables})
        data = response.json()
        
        if 'errors' in data:
            continue
            
        for media_list in data['data']['MediaListCollection']['lists']:
            list_name = media_list['name']
            for entry in media_list['entries']:
                updates.append({
                    'mediaId': str(entry['mediaId']), 
                    'idMal': entry['media']['idMal'],
                    'title': entry['media']['title']['romaji'],
                    'progress': entry['progress'],
                    'img': entry['media']['coverImage']['large'],
                    'type': entry['media']['type'],
                    'list_name': list_name
                })
    
    return updates
                      
