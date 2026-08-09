# ⚡ ANILIST MAXIMUM OVERDRIVE ⚡

![Python](https://img.shields.io/badge/Python-3.10-blue?style=for-the-badge&logo=python)
![License](https://img.shields.io/badge/License-MIT-green?style=for-the-badge)
![Status](https://img.shields.io/badge/Status-Autonomous-red?style=for-the-badge)
![Build](https://img.shields.io/badge/Architecture-Bulletproof-black?style=for-the-badge)

## 📖 PREFACE: THE ARCHITECTURE OF AUTOMATION

**AniList Maximum Overdrive** is not just a standard tracking script. It is an elite, fully automated, self-sustaining intelligence matrix designed for a completionist otaku. 

Built on the foundation of rational, cause-and-effect engineering, this engine completely eliminates manual data entry, bridging a source AniList account with a target account, while simultaneously broadcasting high-fidelity intelligence reports to a centralized Discord Command Center. 

No ghost runs. No time paradox overlaps. No manual syncing. Just pure, autonomous efficiency.

---

## ⚙️ I. CORE PROTOCOLS & FEATURES

This engine operates on a series of strict, logical protocols designed to handle API limitations, Discord rate limits, and time-zone discrepancies without ever crashing.

### 🌟 1. The VIP Priority Radar (S-Tier Targeting)
Not all anime are created equal. When a legendary, long-running series or a top-tier manga updates, it deserves maximum visibility.
*   **The Logic:** A hardcoded `PRIORITY_FAVORITES` array sits at the top of the engine. 
*   **The Execution:** When the engine detects an update or an airing countdown for a title matching this array (e.g., *One Piece*, *Detective Conan*), it bypasses the standard log and blasts a specialized Gold/Flame embed directly into a dedicated VIP Discord channel.

### 🧹 2. The 48-Hour Auto-Purge (Self-Destruct Matrix)
A cluttered log is a useless log. The command center must remain perfectly clean.
*   **The Logic:** Every time the engine sends a standard sync log or a run report to the `#anilist-log` channel, it captures the Discord Message ID.
*   **The Execution:** It converts the exact posting time into a UNIX timestamp and stores it in the `db_messages.json` memory file. On every hourly run, the engine scans this vault. If any message is older than 172,800 seconds (exactly 48 hours), the engine sends a lethal `DELETE` HTTP request to the Discord API, wiping it from the grid.

### 🕒 3. Chronological Precision (The Anti-Spam Barrier)
An unoptimized engine will run wildly in the middle of the night, spamming notifications and creating overlapping queues.
*   **The Logic:** The engine is bound by a strict GitHub Actions Cron schedule mapped precisely to Indian Standard Time (IST).
*   **The Execution:** It wakes up at **8:00 AM IST**, runs exactly once per hour, and completely shuts down into sleep mode at **11:00 PM IST**. Furthermore, the `cancel-in-progress: true` parameter acts as a strict kill-switch, instantly destroying any stalled ghost queues to prevent time paradox loops.

### 📡 4. 90-Minute Airing Intelligence
Never miss a broadcast. 
*   **The Logic:** The engine intercepts the `nextAiringEpisode` node from the AniList GraphQL API.
*   **The Execution:** If the `airingAt` timestamp falls within 5400 seconds (90 minutes) of the engine's current execution time, it fires a live, dynamic countdown embed to the Discord Airing channel.

### 🛡️ 5. Amnesia Patch & 400-Error Bulletproofing
APIs break. Data structures change. The engine must adapt.
*   **The Logic:** Originally, the engine saved memory as standard integers. The VIP upgrade required string-based memory (`Progress-Score`). 
*   **The Execution:** Instead of crashing or restarting the entire 800+ item watchlist, an invisible backward-compatibility patch silently upgrades old data formats to the new structure in the background. Additionally, standard thread-spawning was purged to prevent Discord `400 Bad Request` blocks, replacing it with 100% guaranteed direct-channel delivery.

---

## 🧠 II. THE MEMORY VAULTS

The engine relies on three separate JSON database files, continuously pushed and pulled via Git commands, to maintain perfect persistence across hourly container resets.

### `db_sync.json` (The Master Ledger)
The core tracking matrix. It maps the AniList `MediaID` to the exact state of the user's progress.
*   **Format:** `"MediaID": "Progress-Score"`
*   **Example:** `"21": "1115-100"` (Tracks both episode count and rating).

### `db_airing.json` (The Broadcast Lock)
Prevents the engine from spamming the same 90-minute airing alert multiple times if the engine runs twice within the broadcast window.
*   **Format:** `"MediaID_EpisodeNumber": true`
*   **Example:** `"21_ep1116": true` 

### `db_messages.json` (The Execution List)
The active hit-list for the 48-Hour Auto-Purge.
*   **Format:** Array of objects containing the specific Discord API deletion URL and the UNIX creation timestamp.
*   **Example:** 
```json
[
    {
        "delete_url": "[https://discord.com/api/webhooks/.../messages/123456789](https://discord.com/api/webhooks/.../messages/123456789)",
        "timestamp": 1723171800
         }
  ]
  ```


🏗️ III. COMMAND CENTER BLUEPRINT

To fully utilize this architecture, the Discord server must be rigidly structured. The engine targets six highly specialized pipelines.
| Channel Name | Purpose | Webhook Secret Variable |
|---|---|---|
| #anilist-anime | Standard anime episode progress logs. | DISCORD_ANILIST_ANIME_WEBHOOK |
| #anilist-manga | Standard manga chapter progress logs. | DISCORD_ANILIST_MANGA_WEBHOOK |
| #anilist-log | Rolling 48-hour digest and run reports. | DISCORD_ANILIST_LOG_WEBHOOK |
| #priority-favorites | S-Tier updates (Gold embeds). | DISCORD_FAVORITES_WEBHOOK |
| #anime-airing-alerts | Live 90-minute countdowns. | DISCORD_AIRING_WEBHOOK |
| #anilist-error-report | Critical failure stack traces. | ANILIST_ERROR_REPORT_WEBHOOK |

🚀 IV. DEPLOYMENT PROTOCOL

To forge this engine from scratch or deploy it on a new repository, follow these precise deployment steps.
Step 1: The Codebase
 * Fork or clone this repository.
 * Ensure anilist_engine.py is present in the root directory.
 * Edit the SOURCE_USERNAME variable at the top of the Python script to match the target source account.
 * Add desired media titles or AniList IDs to the PRIORITY_FAVORITES array.
Step 2: The Action Workflow
 * Navigate to .github/workflows/.
 * Ensure sync_engine.yml is present with the following exact specifications:
name: AniList Maximum Overdrive

on:
  schedule:
    # 30 2-17 UTC exactly translates to 8:00 AM through 11:00 PM IST
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

      - name: Set up Python
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
          ERROR_REPORT_WEBHOOK: ${{ secrets.ANILIST_ERROR_REPORT_WEBHOOK }}
        run: python anilist_engine.py

      - name: Save Engine Memory
        run: |
          git config --global user.name 'github-actions[bot]'
          git config --global user.email 'github-actions[bot]@users.noreply.github.com'
          git pull origin main --rebase || true 
          git add *.json || true 
          git diff --staged --quiet || git commit -m "chore: state memory update [skip ci]"
          git push

Step 3: The Security Grid (Secrets)

Navigate to Settings ➡️ Secrets and variables ➡️ Actions ➡️ New repository secret.
You must generate and lock in all 7 secrets perfectly matching the environment variables listed in the YAML file above.
 * Note: The ANILIST_TARGET_TOKEN is an OAuth bearer token obtained via the AniList Developer portal.
   
🛠️ V. MAINTENANCE & OVERRIDE PROTOCOLS
The engine is autonomous, but GitHub enforces a strict inactivity rule for scheduled workflows.
The 60-Day Directive
If no new code is pushed to the repository for 60 consecutive days, GitHub will disable the cron schedule to save server resources.
 * Warning Sign: An automated email from GitHub stating "Your workflow is about to be disabled."
 * The Fix: Click the link in the email and click the Keep workflow active button.
 * The Proactive Fix: Open the GitHub Mobile App, navigate to the Actions tab, and manually click Run workflow once every two months to reset the 60-day timer.
Manual Override Execution
To bypass the 1-hour schedule and force an immediate sync (e.g., immediately after completing a massive episode binge):
 * Open the GitHub Mobile App.
 * Select this repository.
 * Tap Actions.
 * Select AniList Maximum Overdrive.
 * Tap Run workflow.
   The engine will execute immediately, sync the data, and update the memory vault without breaking the standard hourly loop.
🖥️ VI. SYSTEM ARCHITECTURE (PYTHON LOGIC)
For developers analyzing the backend, the anilist_engine.py script executes the following primary functions linearly:
 * Memory Load: Parses local JSON files.
 * Cleanup Sweep (cleanup_old_messages): Evaluates UNIX timestamps and fires DELETE requests to Discord.
 * GraphQL Query (fetch_anilist_data): Queries the AniList API for a complete user inventory (Anime + Manga).
 * Delta Comparison: Compares current live API data against db_sync.json.
 * Target Push (push_to_target): If a delta is found, fires a mutation to the target AniList account.
 * Routing Matrix: Sends relevant Webhook POST requests to standard channels, VIP channels, and Log channels.
 * Memory Save: Dumps the updated dictionaries back into the JSON files for GitHub Actions to commit.

 * 
📜 VII. LICENSE & LEGAL

This software operates under the MIT License. The ultimate standard for open-source structural freedom.
Permission is hereby granted, free of charge, to any person obtaining a copy of this software and associated documentation files (the "Software"), to deal in the Software without restriction, including without limitation the rights to use, copy, modify, merge, publish, distribute, sublicense, and/or sell copies of the Software.
THE SOFTWARE IS PROVIDED "AS IS", WITHOUT WARRANTY OF ANY KIND, EXPRESS OR IMPLIED. The author assumes absolutely zero liability for broken webhook chains, missing database files, or Discord API rate-limiting resulting from misuse of this architecture.


> Forged by Tokyo. 👑
> 

