import os
import json
import time
import requests
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

# ==========================================
# 🛡️ 2. TITANIUM ARMOR (JIKAN RETRY LOGIC)
# ==========================================
def fetch_jikan(url, params=None, retries=3):
    """Wraps Jikan requests in armor to survive 504 Gateway Timeouts."""
    for attempt in range(retries):
        try:
            res = requests.get(url, params=params, timeout=15)
            if res.status_code == 200:
                return res
            elif res.status_code in [500, 502, 503, 504]:
                print(f"[SYSTEM] Jikan server struggling (Status {res.status_code}). Retrying in {5 * (attempt + 1)}s...")
                time.sleep(5 * (attempt + 1))
            else:
                return res # Return 404s normally so they don't loop endlessly
        except Exception as e:
            print(f"[SYSTEM] Network timeout: {e}. Retrying...")
            time.sleep(5 * (attempt + 1))
    return None

# ==========================================
# 🔍 3. XML ID EXTRACTION
# ==========================================
def extract_mal_ids():
    title_to_id = {}
    if os.path.exists(MAL_ANIME_XML):
        try:
            for anime in ET.parse(MAL_ANIME_XML).getroot().findall('anime'):
                title = anime.find('series_title').text
                mal_id = anime.find('series_animedb_id').text
                title_to_id[title] = {"id": mal_id, "type": "anime"}
        except Exception: pass
    
    if os.path.exists(MAL_MANGA_XML):
        try:
            for manga in ET.parse(MAL_MANGA_XML).getroot().findall('manga'):
                title = manga.find('manga_title').text
                mal_id = manga.find('manga_mangadb_id').text
                title_to_id[title] = {"id": mal_id, "type": "manga"}
        except Exception: pass
    return title_to_id

# ==========================================
# 📁 4. JIKAN DOSSIER GENERATION
# ==========================================
def generate_dossier(mal_id, media_type, ghost_title):
    url = f"https://api.jikan.moe/v4/{media_type}/{mal_id}"
    res = fetch_jikan(url)
    
    if not res or res.status_code != 200:
        print(f"[ERROR] Jikan API Strike Failed for ID {mal_id} | Status: {res.status_code if res else 'Timeout'}")
        return None
        
    data = res.json().get('data', {})
    
    title_eng = data.get('title_english') or 'N/A'
    title_jap = data.get('title_japanese') or 'N/A'
    title_rom = data.get('title') or 'N/A'
    
    raw_synopsis = data.get('synopsis') or "No synopsis available."
    synopsis = raw_synopsis[:400] + "..." if len(raw_synopsis) > 400 else raw_synopsis
    
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
        submit_url = "https://anilist.co/submission/anime"
    else:
        chp = data.get('chapters') or '?'
        vol = data.get('volumes') or '?'
        authors = ", ".join([a['name'] for a in data.get('authors', [])]) or "N/A"
        fields.extend([
            {"name": "📖 Chapters (Vol)", "value": f"{chp} ({vol})", "inline": True},
            {"name": "✍️ Author", "value": authors, "inline": True}
        ])
        submit_url = "https://anilist.co/submission/manga"

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
        mapping = title_to_id.get(ghost_title)
        mal_id = None
        
        if mapping:
            mal_id = mapping['id']
        else:
            print(f"[SYSTEM] No XML match for '{ghost_title}'. Engaging Jikan Search Protocol...")
            
            # ⚡ FIX: Safely encoding the query using params dictionary instead of raw f-strings
            search_url = f"https://api.jikan.moe/v4/{media_type}"
            payload = {"q": ghost_title, "limit": 1}
            
            res = fetch_jikan(search_url, params=payload)
            time.sleep(2.5) 
            
            if res and res.status_code == 200:
                results = res.json().get('data', [])
                if results:
                    mal_id = results[0]['mal_id']
                else:
                    print(f"[ERROR] Jikan Search found zero results for '{ghost_title}'. Skipping.")
                    continue
            else:
                print(f"[ERROR] Jikan Search API completely failed for '{ghost_title}'. Skipping to next.")
                continue
                
        print(f"[ENGINE] Extracting heavy data for: {ghost_title} (MAL ID: {mal_id})")
        embed = generate_dossier(mal_id, media_type, ghost_title)
        
        if embed and WEBHOOK_URL:
            try:
                res = requests.post(WEBHOOK_URL + "?wait=true", json={"embeds": [embed]}, timeout=10)
                if res.status_code in [200, 204]:
                    dossiers[ghost_title] = {"mal_id": mal_id, "processed_at": time.time()}
            except Exception: pass
                
        time.sleep(2.5) 
        
    save_db(DB_DOSSIERS, dossiers)
    print("=== DOSSIER EXTRACTION COMPLETE ===")
        
