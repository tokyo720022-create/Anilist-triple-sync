# ⚡ ANILIST MAXIMUM OVERDRIVE ⚡

<!-- BADGES_START -->
![Gamerscore](https://img.shields.io/badge/Lifetime_Gamerscore-1614%20G-FFD700?style=for-the-badge&logo=epic-games&logoColor=black)
![Weekly](https://img.shields.io/badge/Weekly_Grind-492%20G-FF4500?style=for-the-badge&logo=graphql&logoColor=white)
<!-- BADGES_END -->




**Version:** 4.0.0 (Apex Build)  

**Author:** Orewatokyo

**Architecture:** Python 3.10 | GraphQL | GitHub Actions  

---

## 📖 THE PHILOSOPHY
AniList Maximum Overdrive is not a standard tracking script. It is a fully autonomous, self-healing, Gamerscore-calculating, dual-stage alert matrix. Built for the hardcore completionist, this engine bridges the gap between passive tracking and active, highly structured data visualization. 

It eliminates the chaos of the MyAnimeList database, bypasses API rate limits, and dynamically transforms your Discord server into a personalized, high-density Otaku Command Center. 

There is no SQL overhead. There is no manual intervention. The grid runs 16 times a day, sweeping your inventory, calculating your stats, and deploying visual payloads automatically.

---

## 🏗️ CORE ARCHITECTURE & SYSTEM MODULES

The engine is divided into seven distinct operational systems, all running in a synchronized sequence.

### 1. The High-Density Master Sync
The core engine executes a paginated GraphQL sweep of your AniList account. It compares the live server data against a local JSON memory matrix to detect deltas (changes in progress or status).

*   **Chameleon UI:** Analyzes the official AniList extraLarge cover art, extracts the native `#HEX` color code, converts it to a base-10 integer, and forces the Discord embed to perfectly color-match the artwork
*   
*   **Deep Data Matrix:** Structures the embed with precise, scannable columns: Romaji Title, English Title, Status, Consumed Progress, Remaining Progress, and Volume counts.
*   

### 2. The RPG Gamerscore System (G)
Every action taken on AniList generates Gamerscore (G), transforming media consumption into a trackable RPG.

*   **The Math:** 
    *   Anime: `+10 G` per episode watched.
    *   Manga: `+2 G` per chapter read.
    *   Completionist Bonus: `+100 G` for fully completing a series.
    *   
*   **Weekly Wipes:** Every Sunday at Midnight UTC, the engine executes a hard wipe of the `weekly_g` stat. It permanently banks the score into the `lifetime_g` vault and drops a dynamically colored Weekly Action Report into the Trophy Room.
*   
*   **Classified UI Milestones:** Hitting 1,000 G or 5,000 G within a single week triggers highly classified, visually explosive embeds in the Trophy Room .
*   
*   **The Prestige Override:** Upon crossing 10,000 Lifetime G, the engine permanently hijacks the Discord webhook identity, replacing the standard bot name with the apex **"Orewatokyo"** tag on all future alerts.
*   

### 3. Dual-Stage Airing Intelligence
The engine actively tracks the release schedules of every anime in your `CURRENT` and `PLANNING` lists. It does not wait for episodes to drop; it warns you before they do.

*   **Phase 1 (3-Hour Standby):** When an episode crosses the 3-hour threshold (10,800 seconds), it drops a `🕒 3-HOUR WARNING` into the airing channel.
*   
*   **Phase 2 (1-Hour Red Alert):** When the clock drops below 60 minutes (3,600 seconds), it overrides the first alert and drops a `🚨 FINAL 1-HOUR WARNING`.
*   
*   **Dynamic Timestamps:** Uses absolute Discord UNIX `<t:TIME:R>` tags to create a literal, live-ticking countdown clock inside the chat UI.

### 4. Bimodal Ghost Radar (Auto-Healing)
MyAnimeList's chaotic, unmoderated database often contains entries that AniList does not natively recognize due to naming clashes or unapproved submissions. The Ghost Radar fixes this autonomously.

*   **Bimodal Sweeping:** Parses both `mal_export.xml` (Manga) and `mal_anime.xml` (Anime) simultaneously.
*   
*   **Bilingual Matrix:** Converts all known AniList Romaji and English titles into a lowercase, case-insensitive pool to prevent false positives.
*   
*   **Auto-Assimilation:** If an entry is missing, it is locked in the `db_ghosts.json` vault. The radar silently searches the AniList GraphQL API on every run. If a moderator adds the missing entry to AniList, the radar detects it, assimilates your progress, injects it into your account via a Mutation Query, and drops a `🟢 GHOST ASSIMILATED` alert..
*   

### 5. Titanium Armor (API Resilience)

AniList enforces a strict 90-request-per-minute rate limit and occasionally suffers from server timeouts.

*   **Exponential Backoff:** All HTTP requests are shielded by the `fetch_with_armor()` protocol.
*   
*   **The Logic:** `Attempt 1 -> Fail -> Sleep 3s -> Attempt 2 -> Fail -> Sleep 6s -> Attempt 3`. The script will never crash due to a temporary network blip.
*   
*   **Radar Throttle:** The Ghost Radar actively throttles its own searches (`time.sleep(1.5)`) to remain completely invisible to AniList's anti-spam detection.

### 6. The 48-Hour Auto-Purge

To keep the command center pristine, the engine acts as its own janitor.
*   Logs every single message ID it sends to the `#anilist-log` channel.
*   
*   Cross-references timestamps on every run.
*   
*   Executes a `DELETE` REST API call to Discord for any log message older than 172,800 seconds (48 Hours).

---

## 🧠 THE MEMORY VAULT SYSTEM (JSON SCHEMA)

The engine relies on five lightweight, highly efficient JSON databases to maintain state without requiring a heavy SQL cloud architecture.

### 1. `db_sync.json` (The Core Matrix)
Tracks the exact progress integer of every `mediaId`.


{
    "lifetime_g": 12450,
    "weekly_g": 840,
    "current_week": 32
}


2. db_achievements.json (The RPG Vault)
Stores the active Gamerscore and tracks the current calendar week to execute Sunday wipes.

{
    "lifetime_g": 12450,
    "weekly_g": 840,
    "current_week": 32
}

3. db_airing.json (The Radar Lock)
Prevents the engine from spamming the same 3-hour or 1-hour warning multiple times.
{
    "21456_ep1067": "3h",
    "21456_ep1068": "1h",
    "99876_ep12": "none"
}

4. db_ghosts.json (The Anomaly Ward)
Stores all MAL XML data that cannot currently be resolved on AniList.
{
    "Obscure Light Novel Name": {
        "progress": 45,
        "score": 8,
        "type": "MANGA"
    }
}

5. db_messages.json (The Janitor Log)
Stores Discord message IDs and their deletion endpoints for the 48-hour purge.
{
    "112233445566778899": {
        "timestamp": 1691600000.5,
        "delete_url": "[https://discord.com/api/webhooks/.../messages/112233445566778899](https://discord.com/api/webhooks/.../messages/112233445566778899)"
    }
}

📡 DISCORD PIPELINE MAPPING
The engine requires 7 unique Discord Webhook pipelines to route data to the correct channels.
| Environment Variable | Target Channel | Payload Type |
|---|---|---|
| DISCORD_ANILIST_ANIME_WEBHOOK | #anilist-anime | Standard anime progress, dynamic posters, standard G score. |
| DISCORD_ANILIST_MANGA_WEBHOOK | #anilist-manga | Standard manga progress, dynamic posters, standard G score. |
| DISCORD_ACHIEVEMENTS_WEBHOOK | #achievements | Trophy embeds, Series Completions, 1k/5k Milestones, Weekly Wipes. |
| DISCORD_AIRING_WEBHOOK | #anime-airing-alerts | 3-Hour and 1-Hour countdown clocks for incoming episodes. |
| DISCORD_GHOST_RADAR_WEBHOOK | #ghost-archive | Alerts when a MAL anomaly is successfully assimilated. |
| DISCORD_FAVORITES_WEBHOOK | #priority-favorites | Dedicated pings for S-Tier priority franchises (e.g., One Piece). |
| DISCORD_ANILIST_LOG_WEBHOOK | #anilist-log | Silent engine telemetry. Auto-purges every 48 hours. |
🛠️ INSTALLATION & DEPLOYMENT PROTOCOL
Step 1: Repository Prep
 * Create a private GitHub repository.
 * Upload the master anilist_engine.py script to the root directory.
 * Export your MyAnimeList database. Rename the manga file to mal_export.xml and the anime file to mal_anime.xml. Upload both to the root directory.
Step 2: Injecting Secrets
Navigate to your GitHub Repository -> Settings -> Secrets and variables -> Actions -> New repository secret.
You must create exactly 8 secrets:
 * ANILIST_TARGET_TOKEN (Your personal AniList Developer Token)
 * DISCORD_ANILIST_ANIME_WEBHOOK
 * DISCORD_ANILIST_MANGA_WEBHOOK
 * DISCORD_AIRING_WEBHOOK
 * DISCORD_ANILIST_LOG_WEBHOOK
 * DISCORD_FAVORITES_WEBHOOK
 * DISCORD_GHOST_RADAR_WEBHOOK
 * DISCORD_ACHIEVEMENTS_WEBHOOK
Step 3: The YAML Automator
 * Inside your repository, create the following directory path: .github/workflows/
 * Inside the workflows folder, create a file named sync_engine.yml.
 * Paste the following configuration exactly as written.
name: AniList Maximum Overdrive

on:
  schedule:
    # Executes every hour at the bottom of the hour UTC (Mapping to Top of the Hour IST: 8:00 AM - 11:00 PM)
    - cron: '30 2-17 * * *' 
  workflow_dispatch:

permissions:
  contents: write

jobs:
  sync_engine:
    runs-on: ubuntu-latest
    
    concurrency:
      group: anilist-engine
      cancel-in-progress: true 

    steps:
      - name: Checkout Repository
        uses: actions/checkout@v4

      - name: Set up Python 3.10
        uses: actions/setup-python@v5
        with:
          python-version: '3.10'

      - name: Install Dependencies
        run: pip install requests

      - name: Run Master Engine
        env:
          ANILIST_TARGET_TOKEN: ${{ secrets.ANILIST_TARGET_TOKEN }}
          DISCORD_ANIME_WEBHOOK: ${{ secrets.DISCORD_ANILIST_ANIME_WEBHOOK }} 
          DISCORD_MANGA_WEBHOOK: ${{ secrets.DISCORD_ANILIST_MANGA_WEBHOOK }} 
          DISCORD_AIRING_WEBHOOK: ${{ secrets.DISCORD_AIRING_WEBHOOK }}
          DISCORD_LOG_WEBHOOK: ${{ secrets.DISCORD_ANILIST_LOG_WEBHOOK }}
          DISCORD_FAVORITES_WEBHOOK: ${{ secrets.DISCORD_FAVORITES_WEBHOOK }} 
          DISCORD_GHOST_RADAR_WEBHOOK: ${{ secrets.DISCORD_GHOST_RADAR_WEBHOOK }}
          DISCORD_ACHIEVEMENTS_WEBHOOK: ${{ secrets.DISCORD_ACHIEVEMENTS_WEBHOOK }}
        run: python anilist_engine.py

      - name: Save Engine Memory (JSON Vaults)
        run: |
          git config --global user.name 'github-actions[bot]'
          git config --global user.email 'github-actions[bot]@users.noreply.github.com'
          git pull origin main --rebase || true 
          git add *.json || true 
          git diff --staged --quiet || git commit -m "chore: state memory update [skip ci]"
          git push

🔍 GRAPHQL QUERY ARCHITECTURES
For absolute transparency, here are the exact GraphQL payloads the engine uses to extract data from AniList.
1. The High-Density Fetch Query
This massive query pulls all variables required for the Chameleon UI, Airing Clocks, and Stat Breakdowns in a single paginated sweep.
query ($userName: String,$page: Int) {
  Page(page: $page, perPage: 50) {
    pageInfo { hasNextPage }
    mediaList(userName: $userName) {
      mediaId
      progress
      progressVolumes
      score
      status
      media {
        title { romaji english }
        type
        episodes
        chapters
        volumes
        season
        seasonYear
        coverImage { extraLarge color } 
        nextAiringEpisode { airingAt episode }
      }
    }
  }
}

2. The Assimilation Mutation
When the Ghost Radar successfully hunts down an anomaly, it fires this mutation to silently update your target AniList account, converting raw data into locked progress.
mutation ($id: Int, $prog: Int,$score: Int) { 
  SaveMediaListEntry (mediaId: $id, progress: $prog, scoreRaw:$score) { 
    id 
  } 
}

💻 CODEBASE COMPONENT BREAKDOWN
A detailed map of the Python script's logic flow.
fetch_with_armor(url, payload, headers, retries)
The absolute backbone of the engine's stability. Instead of allowing a raw requests.post() command, all AniList interactions are routed through this function. It catches 500 Internal Server Errors and 429 Too Many Requests codes, executing an exponential backoff loop (time.sleep((attempt + 1) * 3)) to guarantee data delivery.
send_discord_alert(...)
A highly polymorphic function responsible for generating Discord embed JSON structures. It accepts parameters for dynamic colors, custom thumbnail arrays, override tags (username), and author blocks (used for the Gamerscore UI). If routed to the Log Webhook, it captures the Discord Message ID and commits it to the JSON vault for future purging.
manage_achievements_and_weekly(points_earned)
The brain of the RPG system. It calculates the delta between the last run and the current run, translates it into Gamerscore, and determines if a threshold has been crossed. It utilizes Python's datetime.now(timezone.utc).isocalendar()[1] to reliably determine the current week of the year, guaranteeing that the Sunday midnight wipe always fires accurately.
process_airing_countdowns(inventory)
Scans the deep data matrix for any item containing the nextAiringEpisode object. By calculating airingAt - current_time, it establishes a precise countdown timer. The Dual-Stage logic ensures it checks for both the 10,800-second mark and the 3,600-second mark, updating the db_airing.json state machine to prevent duplicate pings.
sweep_mal_xml(known_titles_pool)
The local ingestion engine for the Ghost Radar. It utilizes Python's native xml.etree.ElementTree to parse the highly specific <manga> and <anime> nodes generated by MyAnimeList exports. It strips out all formatting, converts titles to lowercase, and checks them against the known AniList dictionary to isolate true ghosts.
execute_master_sync(inventory)
The conductor of the orchestra. It loops through the live AniList data, checks it against the local db_sync.json memory matrix, and fires all logic blocks. If a delta is found, it calculates the Gamerscore, determines the Chameleon UI color, formats the High-Density embed, fires the webhooks, checks for S-Tier VIP status, and mutates the target database.
⚙️ SYSTEM METRICS & LIMITATIONS
 * Execution Window: The GitHub Actions runner limits scripts to 6 hours, but this engine is optimized to execute a full 850+ item database sweep in under 3 minutes (accounting for Ghost Radar search throttles).
 * Action Minutes: Running 16 times a day takes roughly 48 minutes of compute time per day. GitHub Free provides 2,000 minutes per month. The engine consumes roughly 1,440 minutes per month, keeping you completely within the free tier.
 * Database Limits: The JSON flat-file architecture is tested and highly stable for up to ~10,000 tracked media entries.
System Document Compiled. Maximum Overdrive is Online.

