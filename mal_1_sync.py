import os
import json
import time # Added for rate limiting
import traceback
import requests
from sync_utils import load_database, save_database, fetch_source_activity, send_item_log, send_run_report, send_error_report

SOURCE_USERNAME = "Orewatokyo"
DB_FILE = "db_mal_1.json"
TOKEN_FILE = "mal1_token.json"

CLIENT_ID = os.environ['MAL_CLIENT_ID']
CLIENT_SECRET = os.environ['MAL_CLIENT_SECRET']
INITIAL_REFRESH = os.environ['MAL_REFRESH_TOKEN']

ANIME_WEBHOOK = os.environ['DISCORD_ANIME_WEBHOOK']
MANGA_WEBHOOK = os.environ['DISCORD_MANGA_WEBHOOK']
LOG_WEBHOOK = os.environ['DISCORD_LOG_WEBHOOK']
ERROR_WEBHOOK = os.environ['ERROR_REPORT_WEBHOOK']

def get_mal_access_token():
    refresh_token = INITIAL_REFRESH
    if os.path.exists(TOKEN_FILE):
        with open(TOKEN_FILE, "r") as f:
            refresh_token = json.load(f).get("refresh_token", INITIAL_REFRESH)

    response = requests.post("https://myanimelist.net/v1/oauth2/token", data={
        'client_id': CLIENT_ID,
        'client_secret': CLIENT_SECRET,
        'grant_type': 'refresh_token',
        'refresh_token': refresh_token
    })
    response.raise_for_status()
    tokens = response.json()
    
    with open(TOKEN_FILE, "w") as f:
        json.dump({"refresh_token": tokens['refresh_token']}, f)
        
    return tokens['access_token']

def push_to_mal(item, access_token):
    if not item['idMal']:
        return
        
    headers = {'Authorization': f'Bearer {access_token}'}
    if item['type'] == "ANIME":
        url = f"https://api.myanimelist.net/v2/anime/{item['idMal']}/my_list_status"
        data = {'num_watched_episodes': item['progress']}
    else:
        url = f"https://api.myanimelist.net/v2/manga/{item['idMal']}/my_list_status"
        data = {'num_chapters_read': item['progress']}
        
    requests.patch(url, headers=headers, data=data)

def main():
    try:
        access_token = get_mal_access_token()
        db = load_database(DB_FILE)
        new_data = fetch_source_activity(SOURCE_USERNAME)
        
        updates_made = 0
        for item in new_data:
            media_id = item['mediaId']
            current_progress = item['progress']
            
            if media_id not in db or db[media_id] < current_progress:
                push_to_mal(item, access_token)
                
                target_webhook = ANIME_WEBHOOK if item['type'] == "ANIME" else MANGA_WEBHOOK
                send_item_log(target_webhook, item['title'], current_progress, item['img'], item['type'], item['list_name'])
                
                db[media_id] = current_progress
                updates_made += 1
                
                time.sleep(2)

        if updates_made > 0:
            save_database(DB_FILE, db)
            
        send_run_report(LOG_WEBHOOK, "MAL Account 1", "Success", updates_made)
        
    except Exception as e:
        send_error_report(ERROR_WEBHOOK, "MAL 1 Sync", str(e), traceback.format_exc())

if __name__ == "__main__":
    main()
