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
