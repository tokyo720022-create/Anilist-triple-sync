# ⚡ AniList Maximum Overdrive

An autonomous, self-cleaning Python intelligence network that syncs an AniList source account to a target account and streams real-time updates directly into a structured Discord HQ. 

Built to run perfectly on a 5-minute schedule without human intervention.

---

## ⚙️ System Architecture

This engine doesn't just track anime and manga; it operates as a full-scale routing and alert system. The GitHub repository acts as the central brain, storing memory in `.json` files to prevent redundant API calls.

### Core Features
*   **Deep-State Syncing:** Tracks episode progress, chapter progress, and 100-point rating changes. If a change is detected, it instantly pushes the update to the target AniList account.
*   **Autonomous Thread Routing:** Dynamically spawns a dedicated Discord thread for every unique series (e.g., *One Piece* gets its own thread). If Discord rejects the thread creation, it safely defaults back to the main channel.
*   **48-Hour Auto-Purge:** A self-cleaning protocol. Standard watch/read logs are tracked in memory and permanently deleted from Discord after 48 hours to keep the UI clean.
*   **Live Airing Radar:** Scans the target account for currently airing anime and drops a high-res poster and live countdown 90 minutes before the episode drops.
*   **Finale Alerts:** Calculates remaining episodes and hijacks the Discord embed with a high-energy alert when the user reaches the final episode or chapter.
*   **Smart Run Reports:** Drops a summary log into a dedicated channel *only* if updates or deletions occurred. Silently shuts down if the queue is empty.

---

## 🔐 Environment Secrets Vault

To run this engine, the following exact variables must be stored in **Settings > Secrets and variables > Actions**:

| Secret Name | Purpose |
| :--- | :--- |
| `ANILIST_TARGET_TOKEN` | The AniList Developer API Token for the target account. |
| `DISCORD_ANILIST_ANIME_WEBHOOK` | Routes to `#anilist-anime` (Spawns threads). |
| `DISCORD_ANILIST_MANGA_WEBHOOK` | Routes to `#anilist-manga` (Spawns threads). |
| `DISCORD_ANILIST_LOG_WEBHOOK` | Routes to `#anilist-log` for System Shutdown summaries. |
| `DISCORD_AIRING_WEBHOOK` | Routes to `#anime-airing-alerts` for 90-min warnings. |
| `ANILIST_ERROR_REPORT_WEBHOOK` | Routes to `#anilist-error-report` for critical API crashes. |

---

## 📂 Memory Grid (Database Files)

The engine automatically generates and updates these files. **Do not manually edit them.**
*   `db_sync.json`: Remembers the exact progress and score (`progress-scoreRaw`) of all 800+ entries.
*   `db_airing.json`: Tracks which 90-minute alerts have already been sent.
*   `db_threads.json`: Remembers the unique Discord Thread IDs for every series.
*   `db_messages.json`: Tracks Discord Message IDs and timestamps for the 48-hour purge.

---

## ⚠️ Maintenance Protocol (The 60-Day Rule)

GitHub Actions has a hardcoded system rule: **If a repository has no human activity for 60 days, scheduled cron workflows are paused.** 

Because the `github-actions[bot]` commits the JSON memory files, this does not count as human activity. 

**To keep the engine alive forever:**
1. Watch for the automated GitHub warning email around Day 50.
2. Click the link and hit **Keep workflow active**.
3. Alternatively, manually click **Run workflow** in the Actions tab once every two months to reset the timer.
