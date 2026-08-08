import os
import json
import requests
import traceback
from sync_utils import fetch_source_activity, send_item_log, send_run_report, send_error_report

SOURCE_USERNAME = "Orewatokyo" # Your main public account
SYNC_FILE = "sync_data_anilist.json"
TARGET_TOKEN = os.environ['ANILIST_TARGET_TOKEN']
WEBHOOK_URL = os.environ['DISCORD_ANILIST_WEBHOOK']
LOG_WEBHOOK = os.environ['DISCORD_ANILIST_LOG_WEBHOOK']
ERROR_WEBHOOK = os.environ['ANILIST_ERROR_REPORT_WEBHOOK']

def push_to_target(media_id, progress):
    url = 'https://graphql.anilist.co'
    query = '''
    mutation ($mediaId: Int, $progress: Int) {
      SaveMediaListEntry (mediaId: $mediaId, progress: $progress) { id }
    }
    '''
    headers = {'Authorization': f'Bearer {TARGET_TOKEN}', 'Content-Type': 'application/json'}
    requests.post(url, json={'query': query, 'variables': {'mediaId': media_id, 'progress': progress}}, headers=headers)

def main():
    try:
        last_sync = json.load(open(SYNC_FILE)).get("last_updated", 0) if os.path.exists(SYNC_FILE) else 0
        new_data = fetch_source_activity(SOURCE_USERNAME, last_sync)
        
        highest_timestamp = last_sync
        for item in new_data:
            push_to_target(item['mediaId'], item['progress'])
            send_item_log(WEBHOOK_URL, item['title'], item['progress'], item['img'], item['type'], item['list_name'])
            highest_timestamp = max(highest_timestamp, item['updatedAt'])

        if new_data:
            with open(SYNC_FILE, "w") as f:
                json.dump({"last_updated": highest_timestamp}, f)
            
        send_run_report(LOG_WEBHOOK, "AniList Target", "Success", len(new_data))
        
    except Exception as e:
        send_error_report(ERROR_WEBHOOK, "AniList Target Sync", str(e), traceback.format_exc())

if __name__ == "__main__":
    main()
                          
