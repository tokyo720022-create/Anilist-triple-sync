import os
import json
import time
import requests
import xml.etree.ElementTree as ET
from difflib import SequenceMatcher

# ==========================================
# ⚙️ 1. SYSTEM CONFIGURATION
# ==========================================

WEBHOOK_URL = os.environ.get("DISCORD_DOSSIER_WEBHOOK")

DB_GHOSTS = "db_ghosts.json"
DB_DOSSIERS = "db_dossiers.json"

MAL_ANIME_XML = "mal_anime.xml"
MAL_MANGA_XML = "mal_export.xml"

JIKAN_BASE_URL = "https://api.jikan.moe/v4"

# Stay well below Jikan's public rate limits.
REQUEST_DELAY = 2.5
MAX_RETRIES = 4

HEADERS = {
    "User-Agent": "Ghost-Jikan-Dossier/1.0"
}


# ==========================================
# 🛠️ 2. FILE DATABASE HELPERS
# ==========================================

def load_db(filepath):
    """Load JSON database safely."""
    if not os.path.exists(filepath):
        return {}

    try:
        with open(filepath, "r", encoding="utf-8") as f:
            data = json.load(f)

        if isinstance(data, dict):
            return data

        print(f"[WARNING] {filepath} does not contain a JSON object.")
        return {}

    except (json.JSONDecodeError, OSError) as e:
        print(f"[ERROR] Failed to load {filepath}: {e}")
        return {}


def save_db(filepath, data):
    """Save JSON database safely."""
    try:
        with open(filepath, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4, ensure_ascii=False)

    except OSError as e:
        print(f"[ERROR] Failed to save {filepath}: {e}")


# ==========================================
# 🧹 3. STRING / DATA HELPERS
# ==========================================

def normalize_title(title):
    """
    Normalize titles so harmless differences in spacing,
    punctuation and capitalization don't break XML matching.
    """
    if not title:
        return ""

    title = str(title).strip().lower()

    replacements = {
        "–": "-",
        "—": "-",
        "_": " ",
        ":": " ",
        "/": " ",
        "\\": " ",
    }

    for old, new in replacements.items():
        title = title.replace(old, new)

    cleaned = []
    for char in title:
        if char.isalnum() or char.isspace():
            cleaned.append(char)

    return " ".join("".join(cleaned).split())


def safe_text(element, default=""):
    """Safely extract .text from an XML element."""
    if element is None or element.text is None:
        return default

    value = element.text.strip()
    return value if value else default


def shorten(text, max_length):
    """Discord-safe text trimming."""
    if not text:
        return ""

    text = str(text)

    if len(text) <= max_length:
        return text

    return text[:max_length - 3].rstrip() + "..."


def join_names(items):
    """Convert Jikan name objects into a readable string."""
    names = []

    for item in items or []:
        if isinstance(item, dict):
            name = item.get("name")
        else:
            name = None

        if name:
            names.append(str(name))

    return ", ".join(names) if names else "N/A"


def format_date(date_value):
    """Turn Jikan ISO dates into a simple YYYY-MM-DD string."""
    if not date_value:
        return "N/A"

    return str(date_value)[:10]


def normalize_media_type(media_type):
    """Normalize Ghost media type values."""
    media_type = str(media_type or "MANGA").strip().lower()

    if media_type in ("anime", "animation"):
        return "anime"

    if media_type in ("manga", "manhwa", "manhua", "light novel", "novel"):
        return "manga"

    return "manga"


# ==========================================
# 🛡️ 4. TITANIUM ARMOR - JIKAN REQUESTS
# ==========================================

def fetch_jikan(url, params=None, retries=MAX_RETRIES):
    """
    Robust Jikan request wrapper.

    Handles:
    - 429 rate limiting
    - 500/502/503/504 server errors
    - connection failures
    - timeouts
    """

    for attempt in range(1, retries + 1):

        try:
            response = requests.get(
                url,
                params=params,
                headers=HEADERS,
                timeout=20
            )

        except requests.RequestException as e:
            wait_time = 5 * attempt

            print(
                f"[SYSTEM] Jikan network error: {e}. "
                f"Retrying in {wait_time}s..."
            )

            time.sleep(wait_time)
            continue

        # ------------------------------------------
        # SUCCESS
        # ------------------------------------------

        if response.status_code == 200:
            return response

        # ------------------------------------------
        # RATE LIMIT
        # ------------------------------------------

        if response.status_code == 429:

            retry_after = response.headers.get("Retry-After")

            try:
                wait_time = int(retry_after)
            except (TypeError, ValueError):
                wait_time = 10 * attempt

            print(
                f"[SYSTEM] Jikan rate limit hit (429). "
                f"Retrying in {wait_time}s..."
            )

            time.sleep(wait_time)
            continue

        # ------------------------------------------
        # TEMPORARY SERVER ERROR
        # ------------------------------------------

        if response.status_code in (500, 502, 503, 504):

            wait_time = 5 * attempt

            print(
                f"[SYSTEM] Jikan server error "
                f"(HTTP {response.status_code}). "
                f"Retrying in {wait_time}s..."
            )

            time.sleep(wait_time)
            continue

        # ------------------------------------------
        # NORMAL ERROR
        # ------------------------------------------

        return response

    return None


# ==========================================
# 🔍 5. MAL XML ID EXTRACTION
# ==========================================

def extract_mal_ids():
    """
    Build separate Anime/Manga title maps.

    This avoids Anime/Manga titles overwriting each other.
    """

    database = {
        "anime": {},
        "manga": {}
    }

    # ------------------------------------------
    # ANIME XML
    # ------------------------------------------

    if os.path.exists(MAL_ANIME_XML):

        try:
            root = ET.parse(MAL_ANIME_XML).getroot()

            for anime in root.findall("anime"):

                title = safe_text(anime.find("series_title"))
                mal_id = safe_text(anime.find("series_animedb_id"))

                if not title or not mal_id:
                    continue

                database["anime"][normalize_title(title)] = {
                    "id": mal_id,
                    "type": "anime",
                    "original_title": title
                }

        except (ET.ParseError, OSError) as e:
            print(f"[ERROR] Failed to parse {MAL_ANIME_XML}: {e}")

    # ------------------------------------------
    # MANGA XML
    # ------------------------------------------

    if os.path.exists(MAL_MANGA_XML):

        try:
            root = ET.parse(MAL_MANGA_XML).getroot()

            for manga in root.findall("manga"):

                title = safe_text(manga.find("manga_title"))
                mal_id = safe_text(manga.find("manga_mangadb_id"))

                if not title or not mal_id:
                    continue

                database["manga"][normalize_title(title)] = {
                    "id": mal_id,
                    "type": "manga",
                    "original_title": title
                }

        except (ET.ParseError, OSError) as e:
            print(f"[ERROR] Failed to parse {MAL_MANGA_XML}: {e}")

    return database


# ==========================================
# 🎯 6. JIKAN SEARCH MATCHING
# ==========================================

def score_title_match(query, candidate):
    """Return a simple 0-100 title similarity score."""
    q = normalize_title(query)
    c = normalize_title(candidate)

    if not q or not c:
        return 0

    if q == c:
        return 100

    ratio = SequenceMatcher(None, q, c).ratio()

    return round(ratio * 100)


def search_jikan_title(ghost_title, media_type):
    """
    Search Jikan and choose the best title match instead of
    blindly taking the first result.
    """

    search_url = f"{JIKAN_BASE_URL}/{media_type}"

    params = {
        "q": ghost_title,
        "limit": 5
    }

    response = fetch_jikan(search_url, params=params)

    if not response or response.status_code != 200:
        return None

    try:
        results = response.json().get("data", [])
    except ValueError:
        print("[ERROR] Jikan returned invalid JSON.")
        return None

    if not results:
        return None

    best_result = None
    best_score = -1

    for result in results:

        titles_to_test = [
            result.get("title"),
            result.get("title_english"),
            result.get("title_japanese")
        ]

        result_score = max(
            (
                score_title_match(ghost_title, title)
                for title in titles_to_test
                if title
            ),
            default=0
        )

        if result_score > best_score:
            best_score = result_score
            best_result = result

    if not best_result:
        return None

    print(
        f"[SEARCH] Best match: "
        f"{best_result.get('title', 'N/A')} "
        f"(score {best_score}%)"
    )

    return best_result.get("mal_id")


# ==========================================
# 📁 7. JIKAN DOSSIER GENERATION
# ==========================================

def generate_dossier(mal_id, media_type, ghost_title):

    media_type = normalize_media_type(media_type)

    url = f"{JIKAN_BASE_URL}/{media_type}/{mal_id}"

    response = fetch_jikan(url)

    if not response or response.status_code != 200:

        status = response.status_code if response else "Timeout/No Response"

        print(
            f"[ERROR] Jikan dossier request failed "
            f"for MAL ID {mal_id} | Status: {status}"
        )

        return None

    try:
        data = response.json().get("data", {})
    except ValueError:
        print(f"[ERROR] Invalid JSON returned for MAL ID {mal_id}.")
        return None

    if not data:
        print(f"[ERROR] Jikan returned empty data for MAL ID {mal_id}.")
        return None

    # ------------------------------------------
    # BASIC TITLES
    # ------------------------------------------

    title_eng = data.get("title_english") or "N/A"
    title_jap = data.get("title_japanese") or "N/A"
    title_rom = data.get("title") or "N/A"

    # ------------------------------------------
    # DESCRIPTION
    # ------------------------------------------

    raw_synopsis = data.get("synopsis") or "No synopsis available."
    synopsis = shorten(raw_synopsis, 700)

    # ------------------------------------------
    # GENRES
    # ------------------------------------------

    genres = join_names(data.get("genres", []))

    # ------------------------------------------
    # MAL SOURCE
    # ------------------------------------------

    mal_url = data.get(
        "url",
        f"https://myanimelist.net/{media_type}/{mal_id}"
    )

    jikan_url = f"{JIKAN_BASE_URL}/{media_type}/{mal_id}"

    # ------------------------------------------
    # COMMON FIELDS
    # ------------------------------------------

    fields = [
        {
            "name": "🇯🇵 Romaji",
            "value": shorten(title_rom, 1024),
            "inline": True
        },
        {
            "name": "🇺🇸 English",
            "value": shorten(title_eng, 1024),
            "inline": True
        },
        {
            "name": "🔤 Japanese / Native",
            "value": shorten(title_jap, 1024),
            "inline": True
        },
        {
            "name": "🎭 Genres",
            "value": shorten(genres, 1024),
            "inline": False
        },
        {
            "name": "🆔 MAL ID",
            "value": str(mal_id),
            "inline": True
        },
        {
            "name": "📅 Status",
            "value": str(data.get("status") or "N/A"),
            "inline": True
        },
        {
            "name": "📅 Start",
            "value": format_date(data.get("aired", {}).get("from")
                                if media_type == "anime"
                                else data.get("published", {}).get("from")),
            "inline": True
        },
        {
            "name": "📅 End",
            "value": format_date(data.get("aired", {}).get("to")
                                if media_type == "anime"
                                else data.get("published", {}).get("to")),
            "inline": True
        }
    ]

    # ==========================================
    # 🎬 ANIME
    # ==========================================

    if media_type == "anime":

        episodes = data.get("episodes") or "?"

        studios = join_names(data.get("studios", []))

        source = data.get("source") or "N/A"

        duration = data.get("duration") or "N/A"

        anime_type = data.get("type") or "N/A"

        season = data.get("season") or "N/A"

        year = data.get("year") or "N/A"

        fields.extend(
            [
                {
                    "name": "📺 Episodes",
                    "value": str(episodes),
                    "inline": True
                },
                {
                    "name": "🎬 Studio",
                    "value": shorten(studios, 1024),
                    "inline": True
                },
                {
                    "name": "📖 Source",
                    "value": shorten(source, 1024),
                    "inline": True
                },
                {
                    "name": "🎞️ Format",
                    "value": str(anime_type),
                    "inline": True
                },
                {
                    "name": "⏱️ Duration",
                    "value": str(duration),
                    "inline": True
                },
                {
                    "name": "🌸 Season",
                    "value": f"{season or 'N/A'} {year or ''}".strip(),
                    "inline": True
                }
            ]
        )

        # ✅ Current AniList Create Anime page.
        submit_url = "https://anilist.co/edit/anime/new"

    # ==========================================
    # 📚 MANGA / LIGHT NOVEL
    # ==========================================

    else:

        chapters = data.get("chapters") or "?"

        volumes = data.get("volumes") or "?"

        authors = join_names(data.get("authors", []))

        manga_type = data.get("type") or "N/A"

        serialization = join_names(data.get("serializations", []))

        fields.extend(
            [
                {
                    "name": "📖 Chapters",
                    "value": str(chapters),
                    "inline": True
                },
                {
                    "name": "📚 Volumes",
                    "value": str(volumes),
                    "inline": True
                },
                {
                    "name": "✍️ Author",
                    "value": shorten(authors, 1024),
                    "inline": False
                },
                {
                    "name": "📘 Format",
                    "value": str(manga_type),
                    "inline": True
                },
                {
                    "name": "📰 Serialization",
                    "value": shorten(serialization, 1024),
                    "inline": True
                }
            ]
        )

        # ✅ Current AniList Create Manga/Light Novel page.
        submit_url = "https://anilist.co/edit/manga/new"

    # ==========================================
    # 🖼️ COVER IMAGE
    # ==========================================

    image_url = (
        data.get("images", {})
        .get("jpg", {})
        .get("large_image_url")
        or
        data.get("images", {})
        .get("jpg", {})
        .get("image_url", "")
    )

    # ==========================================
    # 📦 DISCORD EMBED
    # ==========================================

    embed = {
        "title": f"📂 DOSSIER EXTRACTED: {ghost_title}",

        "url": submit_url,

        "description": (
            f"**MAL ID:** `{mal_id}`\n\n"
            f"**Jikan Title:** `{title_rom}`\n\n"
            f"**Synopsis:**\n"
            f"{synopsis}\n\n"
            f"🔗 [OPEN ANILIST SUBMISSION FORM]({submit_url})\n"
            f"🔗 [OPEN MAL ENTRY]({mal_url})\n"
            f"🔗 [OPEN JIKAN DATA]({jikan_url})"
        ),

        "color": 15158332,

        "thumbnail": {
            "url": image_url
        },

        "fields": fields,

        "footer": {
            "text": "Ghost × Jikan • Manual AniList Submission Workflow"
        }
    }

    return embed


# ==========================================
# 📡 8. DISCORD WEBHOOK
# ==========================================

def send_to_discord(embed):

    if not WEBHOOK_URL:
        print(
            "[WARNING] DISCORD_DOSSIER_WEBHOOK environment variable "
            "is not configured."
        )
        return False

    try:

        response = requests.post(
            WEBHOOK_URL + "?wait=true",
            json={
                "embeds": [embed]
            },
            headers=HEADERS,
            timeout=15
        )

        if response.status_code in (200, 204):

            print("[DISCORD] Dossier delivered successfully.")
            return True

        print(
            f"[ERROR] Discord webhook failed: "
            f"HTTP {response.status_code}"
        )

        print(response.text[:500])

        return False

    except requests.RequestException as e:

        print(f"[ERROR] Discord webhook request failed: {e}")

        return False


# ==========================================
# 🚀 9. INITIATION SEQUENCE
# ==========================================

if __name__ == "__main__":

    print()
    print("===================================================")
    print("      JIKAN DOSSIER EXTRACTION PROTOCOL")
    print("                   ONLINE")
    print("===================================================")
    print()

    ghosts = load_db(DB_GHOSTS)

    dossiers = load_db(DB_DOSSIERS)

    if not ghosts:

        print("[SYSTEM] No ghosts detected in the database.")
        print("[SYSTEM] Standing by.")

        raise SystemExit(0)

    # ------------------------------------------
    # LOAD MAL XML DATABASE
    # ------------------------------------------

    mal_database = extract_mal_ids()

    anime_count = len(mal_database["anime"])
    manga_count = len(mal_database["manga"])

    print(
        f"[SYSTEM] MAL XML loaded: "
        f"{anime_count} anime | {manga_count} manga"
    )

    # ------------------------------------------
    # PROCESS GHOSTS
    # ------------------------------------------

    for ghost_title, ghost_data in ghosts.items():

        if ghost_title in dossiers:

            print(
                f"[SKIP] Already processed: {ghost_title}"
            )

            continue

        if not isinstance(ghost_data, dict):

            print(
                f"[WARNING] Invalid Ghost record: {ghost_title}"
            )

            continue

        media_type = normalize_media_type(
            ghost_data.get("type", "MANGA")
        )

        normalized_ghost_title = normalize_title(ghost_title)

        mal_id = None


        # ==========================================
        # 1️⃣ XML MATCH
        # ==========================================

        mapping = mal_database.get(media_type, {}).get(
            normalized_ghost_title
        )

        if mapping:

            mal_id = mapping["id"]

            print(
                f"[XML] Match found: "
                f"{ghost_title} → MAL {mal_id}"
            )

        # ==========================================
        # 2️⃣ JIKAN SEARCH FALLBACK
        # ==========================================

        else:

            print(
                f"[SYSTEM] No XML match for "
                f"'{ghost_title}'."
            )

            print(
                "[SYSTEM] Engaging Jikan Search Protocol..."
            )

            mal_id = search_jikan_title(
                ghost_title,
                media_type
            )

            time.sleep(REQUEST_DELAY)

            if not mal_id:

                print(
                    f"[ERROR] Jikan Search found "
                    f"no reliable result for "
                    f"'{ghost_title}'."
                )

                continue

            print(
                f"[SEARCH] Selected MAL ID: {mal_id}"
            )

        # ==========================================
        # 3️⃣ EXTRACT FULL DOSSIER
        # ==========================================

        print(
            f"[ENGINE] Extracting heavy data for: "
            f"{ghost_title} "
            f"(MAL ID: {mal_id})"
        )

        embed = generate_dossier(
            mal_id,
            media_type,
            ghost_title
        )

        if not embed:

            print(
                f"[ERROR] Dossier generation failed "
                f"for '{ghost_title}'."
            )

            continue

        # ==========================================
        # 4️⃣ SEND DOSSIER TO DISCORD
        # ==========================================

        sent = send_to_discord(embed)

        if sent:

            dossiers[ghost_title] = {
                "mal_id": str(mal_id),
                "media_type": media_type,
                "processed_at": time.time()
            }

            # Save immediately so a later crash doesn't
            # cause already-delivered dossiers to repeat.
            save_db(DB_DOSSIERS, dossiers)

        # ==========================================
        # 5️⃣ RATE LIMIT PROTECTION
        # ==========================================

        time.sleep(REQUEST_DELAY)

    # ------------------------------------------
    # FINAL SAVE
    # ------------------------------------------

    save_db(DB_DOSSIERS, dossiers)

    print()
    print("===================================================")
    print("       JIKAN DOSSIER EXTRACTION COMPLETE")
    print("===================================================")
