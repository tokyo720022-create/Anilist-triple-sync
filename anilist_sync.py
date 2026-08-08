import os
import time  # Added for rate limiting
import traceback
import requests
from sync_utils import load_database, save_database, fetch_source_activity, send_item_log, send_run_report, send_error_report

SOURCE_USERNAME = "Orewatokyo"
DB_FILE = "db_anilist_target.json"

TARGET_TOKEN = os.environ['ANILIST_TARGET_TOKEN']
ANIME_WEBHOOK = os.environ['DISCORD_ANIME_WEBHOOK']
MANGA_WEBHOOK = os.environ['DISCORD_MANGA_WEBHOOK']
LOG_WEBHOOK = os.environ['DISCORD_LOG_WEBHOOK']
ERROR_WEBHOOK = os.environ['ERROR_REPORT_WEBHOOK']

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
        db = load_database(DB_FILE)
        new_data = fetch_source_activity(SOURCE_USERNAME)
        
        updates_made = 0
        for item in new_data:
            media_id = item['mediaId']
            current_progress = item['progress']
            
            if media_id not in db or db[media_id] < current_progress:
                push_to_target(int(media_id), current_progress)
                
                # Routes to the correct webhook based on type
                target_webhook = ANIME_WEBHOOK if item['type'] == "ANIME" else MANGA_WEBHOOK
                send_item_log(target_webhook, item['title'], current_progress, item['img'], item['type'], item['list_name'])
                
                db[media_id] = current_progress
                updates_made += 1
                
                # THE POSTER FIX: Sleeps for 2 seconds to prevent Discord spam blocks
                time.sleep(2)

        if updates_made > 0:
            save_database(DB_FILE, db)
            
        send_run_report(LOG_WEBHOOK, "AniList Target", "Success", updates_made)
        
    except Exception as e:
        send_error_report(ERROR_WEBHOOK, "AniList Target Sync", str(e), traceback.format_exc())

if __name__ == "__main__":
    main()
