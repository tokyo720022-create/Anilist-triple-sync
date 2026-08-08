import os
import json
import requests
import traceback

THREAD_MEMORY_FILE = "discord_threads.json"

def load_thread_memory():
    """Loads the dynamic thread map, or creates an empty one if it's the first run."""
    if os.path.exists(THREAD_MEMORY_FILE):
        with open(THREAD_MEMORY_FILE, "r") as f:
            return json.load(f)
    return {"ANIME": {}, "MANGA": {}}

def save_thread_memory(memory_data):
    """Saves the newly created thread IDs so they are never duplicated."""
    with open(THREAD_MEMORY_FILE, "w") as f:
        json.dump(memory_data, f, indent=4)

def send_item_log(webhook_url, title, progress, img, media_type, list_name):
    """Autonomous routing: Creates a thread if missing, or routes to an existing one."""
    
    memory = load_thread_memory()
    progress_text = f"Episode {progress}" if media_type == "ANIME" else f"Chapter {progress}"
    
    # Base Payload
    payload = {
        "embeds": [{
            "title": f"🔄 Synced: {title}",
            "description": f"Updated to **{progress_text}**\n📂 AniList Source: {list_name}",
            "color": 3447003,
            "image": {"url": img}
        }]
    }

    # 1. Check if we already created a thread for this AniList category
    existing_thread_id = memory[media_type].get(list_name)
    
    if existing_thread_id:
        # Route to existing thread
        target_url = f"{webhook_url}?thread_id={existing_thread_id}&wait=true"
        requests.post(target_url, json=payload)
    
    else:
        # 2. Spawn a brand new thread automatically
        payload["thread_name"] = list_name # This tells Discord to create the thread!
        target_url = f"{webhook_url}?wait=true" # wait=true returns the new thread data
        
        response = requests.post(target_url, json=payload)
        
        # 3. Harvest the new ID and save it to memory
        if response.status_code in [200, 201, 204]:
            try:
                new_thread_id = response.json().get("channel_id")
                if new_thread_id:
                    memory[media_type][list_name] = new_thread_id
                    save_thread_memory(memory)
                    print(f"✅ Auto-created new thread for {list_name}: {new_thread_id}")
            except Exception as e:
                print(f"Could not parse new thread ID: {e}")
          
