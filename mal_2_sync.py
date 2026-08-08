import os
import json
import requests
import traceback
from sync_utils import fetch_source_activity, send_item_log, send_run_report, send_error_report

SOURCE_USERNAME = "Orewatokyo"
SYNC_FILE = "sync_data_mal2.json"
TOKEN_FILE = "mal2_token.json"

CLIENT_ID = os.environ['MAL_CLIENT_ID']
CLIENT_SECRET = os.environ['MAL_CLIENT_SECRET']
INITIAL_REFRESH = os.environ['MAL_2_REFRESH_TOKEN']

WEBHOOK_URL = os.environ['DISCORD_MAL2_WEBHOOK']
LOG_WEBHOOK = os.environ['DISCORD_MAL_LOG_WEBHOOK']
ERROR_WEBHOOK = os.environ['MAL_ERROR_REPORT']

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
        last_sync = json.load(open(SYNC_FILE)).get("last_updated", 0) if os.path.exists(SYNC_FILE) else 0
        new_data = fetch_source_activity(SOURCE_USERNAME, last_sync)
        
        highest_timestamp = last_sync
        for item in new_data:
            push_to_mal(item, access_token)
            send_item_log(WEBHOOK_URL, item['title'], item['progress'], item['img'], item['type'], item['list_name'])
            highest_timestamp = max(highest_timestamp, item['updatedAt'])

        if new_data:
            with open(SYNC_FILE, "w") as f:
                json.dump({"last_updated": highest_timestamp}, f)
            
        send_run_report(LOG_WEBHOOK, "MAL Account 2", "Success", len(new_data))
        
    except Exception as e:
        send_error_report(ERROR_WEBHOOK, "MAL 2 Sync", str(e), traceback.format_exc())

if __name__ == "__main__":
    main()
      
