import os
import json
import time
import requests
import re
import xml.etree.ElementTree as ET

# ==========================================
# ⚙️ 1. SYSTEM CONFIGURATION
# ==========================================
WEBHOOK_URL = os.environ.get('DISCORD_DOSSIER_WEBHOOK')

DB_GHOSTS = 'db_ghosts.json'
DB_DOSSIERS = 'db_dossiers.json'
MAL_ANIME_XML = 'mal_anime.xml'
MAL_MANGA_XML = 'mal_export.xml'

def load_db(filepath):
    if os.path.exists(filepath):
        try:
            with open(filepath, 'r') as f: return json.load(f)
        except Exception: return {}
    return {}

def save_db(filepath, data):
    with open(filepath, 'w') as f: json.dump(data, f, indent=4)

def normalize_title(title):
    if not title: return ""
    # Strip parenthetical metadata like (TV), (Manga), etc.
    cleaned = re.sub(r'\(.*?\)', '', title)
    # Strip special characters and normalize whitespace
    cleaned = re.sub(r'[^a-zA-Z0-9\s]', '', cleaned)
    return ' '.join(cleaned.lower().split())

# ==========================================
# 🛡️ 2. TITANIUM ARMOR (RATE LIMITS & RETRIES)
# ==========================================
def fetch_jikan(url, params=None, retries=3):
    for attempt in range(retries):
        try:
            res = requests.get(url, params=params, timeout=15)
            
            # Explicit Rate Limit Handling
            if res.status_code == 429:
                retry_after = int(res.headers.get("Retry-After", 5))
                print(f"[SYSTEM] Rate limited (429). Backing off for {retry_after}s...")
                time.sleep(retry_after)
                continue
                
            if res.status_code == 200:
                return res
            elif res.status_code in [500, 502, 503, 504]:
                wait_time = 5 * (attempt + 1)
                print(f"[SYSTEM] Server error ({res.status_code}). Retrying in {wait_time}s...")
                time.sleep(wait_time)
            else:
                return res
        except Exception as e:
            wait_time = 5 * (attempt + 1)
            print(f"[SYSTEM] Network error: {e}. Retrying in {wait_time}s...")
            time.sleep(wait_time)
    return None

# ==========================================
# 🔍 3. NORMALIZED XML ID EXTRACTION
# ==========================================
def extract_mal_ids():
    title_to_id = {}
    
    if os.path.exists(MAL_ANIME_XML):
        try:
            for anime in ET.parse(MAL_ANIME_XML).getroot().findall('anime'):
                title = anime.find('series_title')
                mal_id = anime.find('series_animedb_id')
                if title is not None and mal_id is not None and title.text and mal_id.text:
                    norm = normalize_title(title.text)
                    title_to_id[norm] = {"id": mal_id.text, "type": "anime"}
        except Exception: pass
    
    if os.path.exists(MAL_MANGA_XML):
        try:
            for manga in ET.parse(MAL_MANGA_XML).getroot().findall('manga'):
                title = manga.find('manga_title')
                mal_id = manga.find('manga_mangadb_id')
                if title is not None and mal_id is not None and title.text and mal_id.text:
                    norm = normalize_title(title.text)
                    title_to_id[norm] = {"id": mal_id.text, "type": "manga"}
        except Exception: pass
        
    return title_to_id

# ==========================================
# 📁 4. JIKAN DOSSIER GENERATION
# ==========================================
def generate_dossier(mal_id, media_type, ghost_title):
    url = f"https://api.jikan.moe/v4/{media_type}/{mal_id}"
    res = fetch_jikan(url)
    
    if not res or res.status_code != 200:
        print(f"[ERROR] Jikan lookup failed for ID {mal_id} | Status: {res.status_code if res else 'Timeout'}")
        return None
        
    data = res.json().get('data', {})
    
    title_eng = data.get('title_english') or 'N/A'
    title_jap = data.get('title_japanese') or 'N/A'
    title_rom = data.get('title') or 'N/A'
    
    raw_synopsis = data.get('synopsis') or "No synopsis available."
    # Discord limit safety: Hard cap the synopsis string length
    synopsis = raw_synopsis[:1500] + "..." if len(raw_synopsis) > 1500 else raw_synopsis
    
    genres = ", ".join([g['name'] for g in data.get('genres', [])]) or "N/A"
    
    fields = [
        {"name": "🇯🇵 Romaji", "value": title_rom, "inline": True},
        {"name": "🇺🇸 English", "value": title_eng, "inline": True},
        {"name": "🔤 Japanese", "value": title_jap, "inline": True},
        {"name": "🎭 Genres", "value": genres, "inline": False},
    ]
    
    if media_type == "anime":
        eps = data.get('episodes') or '?'
        studios = ", ".join([s['name'] for s in data.get('studios', [])]) or "N/A"
        source = data.get('source') or 'N/A'
        fields.extend([
            {"name": "📺 Episodes", "value": str(eps), "inline": True},
            {"name": "🎬 Studio", "value": studios, "inline": True},
            {"name": "📖 Source", "value": source, "inline": True}
        ])
        submit_url = "https://anilist.co/edit/anime/new"
    else:
        chp = data.get('chapters') or '?'
        vol = data.get('volumes') or '?'
        authors = ", ".join([a['name'] for a in data.get('authors', [])]) or "N/A"
        fields.extend([
            {"name": "📖 Chapters (Vol)", "value": f"{chp} ({vol})", "inline": True},
            {"name": "✍️ Author", "value": authors, "inline": True}
        ])
        submit_url = "https://anilist.co/edit/manga/new"

    embed = {
        "title": f"📂 DOSSIER EXTRACTED: {ghost_title}",
        "url": submit_url,
        "description": f"**MAL ID:** {mal_id}\n\n**Synopsis:**\n{synopsis}\n\n[>> CLICK HERE TO OPEN ANILIST SUBMISSION FORM <<]({submit_url})",
        "color": 15158332,
        "thumbnail": {"url": data.get('images', {}).get('jpg', {}).get('image_url', '')},
        "fields": fields
    }
    
    return embed

# ==========================================
# 🚀 5. INITIATION SEQUENCE
# ==========================================
if __name__ == "__main__":
    print("=== JIKAN DOSSIER EXTRACTION PROTOCOL: ONLINE ===")
    
    ghosts = load_db(DB_GHOSTS)
    dossiers = load_db(DB_DOSSIERS)
    
    if not ghosts:
        print("[SYSTEM] No ghosts detected in the database. Standing by.")
        exit()
        
    title_to_id = extract_mal_ids()
    
    for ghost_title, ghost_data in ghosts.items():
        if ghost_title in dossiers:
            continue
            
        media_type = ghost_data.get("type", "MANGA").lower()
        norm_ghost = normalize_title(ghost_title)
        mapping = title_to_id.get(norm_ghost)
        mal_id = None
        
        if mapping:
            mal_id = mapping['id']
            print(f"[SYSTEM] Normalized XML Match Found: '{ghost_title}' -> MAL ID: {mal_id}")
        else:
            print(f"[SYSTEM] No local XML match for '{ghost_title}'. Engaging Jikan Search Protocol...")
            search_url = f"https://api.jikan.moe/v4/{media_type}"
            payload = {"q": ghost_title, "limit": 1}
            
            res = fetch_jikan(search_url, params=payload)
            time.sleep(2.5)
            
            if res and res.status_code == 200:
                results = res.json().get('data', [])
                if results:
                    mal_id = results[0]['mal_id']
                else:
                    print(f"[ERROR] Jikan search found zero results for '{ghost_title}'. Skipping.")
                    continue
            else:
                print(f"[ERROR] Jikan search request failed for '{ghost_title}'. Skipping.")
                continue
                
        print(f"[ENGINE] Extracting dossier for: {ghost_title} (MAL ID: {mal_id})")
        embed = generate_dossier(mal_id, media_type, ghost_title)
        
        # ⚡ DIAGNOSTIC OVERRIDE: No more silent failures
        if embed and WEBHOOK_URL:
            try:
                print(f"[SYSTEM] Firing dossier to Discord for: {ghost_title}...")
                res = requests.post(WEBHOOK_URL + "?wait=true", json={"embeds": [embed]}, timeout=10)
                if res.status_code in [200, 204]:
                    print(f"[SUCCESS] Payload delivered.")
                    dossiers[ghost_title] = {"mal_id": mal_id, "processed_at": time.time()}
                else:
                    print(f"[ERROR] Discord rejected the payload! Status: {res.status_code} | Reason: {res.text}")
            except Exception as e:
                print(f"[ERROR] Webhook connection completely failed: {e}")
                
        time.sleep(2.5)
        
    save_db(DB_DOSSIERS, dossiers)
    print("=== DOSSIER EXTRACTION COMPLETE ===")
    
