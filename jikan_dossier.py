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
DB_DOSSIERS = 'db_dossiers.json' # Memory file to prevent duplicate spam
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
# 🔍 2. XML ID EXTRACTION
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
# 📁 3. JIKAN DOSSIER GENERATION
# ==========================================
def generate_dossier(mal_id, media_type, ghost_title):
    url = f"https://api.jikan.moe/v4/{media_type}/{mal_id}"
    res = requests.get(url, timeout=15)
    
    if res.status_code != 200:
        print(f"[ERROR] Jikan API Strike Failed for ID {mal_id} | Status: {res.status_code}")
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
# 🚀 4. INITIATION SEQUENCE
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
            continue # Bypass previously extracted ghosts
            
        mapping = title_to_id.get(ghost_title)
        if not mapping:
            print(f"[SYSTEM] Could not locate exact MAL ID for '{ghost_title}' in XML. Skipping.")
            continue
            
        mal_id = mapping['id']
        media_type = mapping['type']
        
        print(f"[ENGINE] Extracting heavy data for: {ghost_title} (MAL ID: {mal_id})")
        embed = generate_dossier(mal_id, media_type, ghost_title)
        
        if embed and WEBHOOK_URL:
            res = requests.post(WEBHOOK_URL + "?wait=true", json={"embeds": [embed]}, timeout=10)
            if res.status_code in [200, 204]:
                dossiers[ghost_title] = {"mal_id": mal_id, "processed_at": time.time()}
                
        time.sleep(2.5) # Jikan API enforces a strict rate limit. Do not lower this.
        
    save_db(DB_DOSSIERS, dossiers)
    print("=== DOSSIER EXTRACTION COMPLETE ===")
  
