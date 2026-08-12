[# ⚡ ANILIST MAXIMUM OVERDRIVE ⚡

<!-- BADGES_START -->
![Gamerscore](https://img.shields.io/badge/Lifetime_Gamerscore-5024%20G-FFD700?style=for-the-badge&logo=epic-games&logoColor=black)
![Weekly](https://img.shields.io/badge/Weekly_Grind-658%20G-FF4500?style=for-the-badge&logo=graphql&logoColor=white)
<!-- BADGES_END -->
<!-- PERFORMANCE_START -->
![Daily Eps](https://img.shields.io/badge/Daily_Eps-0-blue?style=for-the-badge&logo=youtube&logoColor=white)
![Daily Chp](https://img.shields.io/badge/Daily_Chp-0-green?style=for-the-badge&logo=bookmeter&logoColor=white)
<!-- PERFORMANCE_END -->
---

## 🧬 PROJECT IDENTITY

**Project:** AniList Maximum Overdrive  
**Version:** 4.1.0 — Apex Build (Performance Matrix Integrated)  
**Author:** Hari (Orewatokyo)  
**Runtime:** Python 3.10 (Strict)  
**Architecture:** Python 3.10 + AniList GraphQL + GitHub Actions + Discord Webhooks + JSON State Vaults + Dynamic Performance Matrix

AniList Maximum Overdrive is an autonomous AniList synchronization and monitoring engine designed for heavy anime and manga tracking workflows.

It transforms passive media tracking into an automated command center.

The engine synchronizes AniList progress, calculates a custom Gamerscore system, monitors upcoming anime episodes, processes MyAnimeList exports, maintains persistent local state, distributes information through multiple Discord webhook channels, and performs automatic cleanup of historical engine messages.

The project is designed around a lightweight flat-file architecture.

There is no SQL database requirement.

There is no continuously running server requirement.

There is no manual synchronization requirement.

The system is designed to run through scheduled GitHub Actions executions and persist its memory through JSON state files and segmented performance ledgers.

---

## 📖 TABLE OF CONTENTS

- [Project Identity](#-project-identity)
- [What Maximum Overdrive Does](#-what-maximum-overdrive-does)
- [Core Philosophy](#-core-philosophy)
- [Architecture Overview](#-architecture-overview)
- [System Data Flow](#-system-data-flow)
- [Core Systems](#-core-systems)
- [1. High-Density Master Sync](#1-high-density-master-sync)
- [2. RPG Gamerscore System](#2-rpg-gamerscore-system)
- [3. Live Performance Hologram & Vault](#3-live-performance-hologram--vault)
- [4. Dual-Stage Airing Intelligence](#4-dual-stage-airing-intelligence)
- [5. Bimodal Ghost Radar](#5-bimodal-ghost-radar)
- [6. Titanium Armor](#6-titanium-armor)
- [7. 48-Hour Auto-Purge](#7-48-hour-auto-purge)
- [Discord Command Center](#-discord-command-center)
- [JSON Memory Vault](#-json-memory-vault)
- [Repository Structure](#-repository-structure)
- [Installation](#-installation)
- [MAL Export Preparation](#-mal-export-preparation)
- [GitHub Secrets](#-github-secrets)
- [Discord Webhook Configuration](#-discord-webhook-configuration)
- [GitHub Actions](#-github-actions)
- [Workflow Configuration](#-workflow-configuration)
- [GraphQL Architecture](#-graphql-architecture)
- [AniList Synchronization](#-anilist-synchronization)
- [Gamerscore Architecture](#-gamerscore-architecture)
- [Airing Radar Architecture](#-airing-radar-architecture)
- [Ghost Radar Architecture](#-ghost-radar-architecture)
- [API Resilience](#-api-resilience)
- [Automatic State Persistence](#-automatic-state-persistence)
- [Codebase Components](#-codebase-components)
- [System Metrics](#-system-metrics)
- [Limitations](#-limitations)
- [Security](#-security)
- [Troubleshooting](#-troubleshooting)
- [Operational Checklist](#-operational-checklist)
- [Development Notes](#-development-notes)
- [Future Expansion](#-future-expansion)
- [Project Status](#-project-status)
- [Credits](#-credits)
- [Final Status](#-final-status)

---

## 🧠 WHAT MAXIMUM OVERDRIVE DOES

Maximum Overdrive acts as an automation layer between AniList, MyAnimeList exports, Discord, and GitHub Actions.

At its core, the engine performs the following operations:

1. Fetches AniList media-list data through GraphQL.
2. Reads progress information for anime and manga.
3. Compares current data against locally stored JSON state.
4. Detects progress changes.
5. Calculates Gamerscore and tracks temporal analytics.
6. Generates Discord embed payloads and live holograms.
7. Tracks upcoming anime episodes.
8. Sends staged airing alerts.
9. Reads MAL XML exports.
10. Detects unresolved media entries.
11. Stores unresolved entries inside the Ghost vault.
12. Searches AniList for previously unresolved entries.
13. Assimilates successfully recovered entries.
14. Stores Discord message identifiers.
15. Removes log messages older than 48 hours.
16. Commits JSON state changes back into the repository.

The complete process is designed to operate without a continuously running application server.

---

## 📖 CORE PHILOSOPHY

Maximum Overdrive is not intended to behave like a simple one-shot synchronization script.

It is structured as a persistent automation engine.

The central idea is simple:

> AniList stores the media state.  
> Maximum Overdrive interprets the state.  
> Discord visualizes the state.  
> JSON remembers the state.  
> GitHub Actions executes the state machine.

The engine therefore treats every execution as another step in a continuous synchronization cycle.

---

## 🏗️ ARCHITECTURE OVERVIEW

```text
                    ┌────────────────────────┐
                    │        AniList         │
                    │      GraphQL API       │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │  High-Density Master   │
                    │         Sync           │
                    └────────────┬───────────┘
                                 │
         ┌───────────────┬───────┼───────┬────────────────┐
         │               │       │       │                │
         ▼               ▼       ▼       ▼                ▼
  Gamerscore       Performance Airing Radar       Ghost Radar
         │               │       │       │                │
         └───────────────┴───────┼───────┴────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │     Discord Pipeline   │
                    └────────────┬───────────┘
                                 │
  ┌──────────────────────┬───────┼───────┬───────────────────────┐
  │                      │       │       │                       │
  ▼                      ▼       ▼       ▼                       ▼
Anime/Manga       Achievement Performance Airing             Ghost Archive
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │      JSON Vaults        │
                    │      Persistent State   │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐


🔄 SYSTEM DATA FLOW

The engine follows a synchronized operational sequence.

GitHub Actions starts
        ↓
Repository checkout
        ↓
Python environment initialized
        ↓
Dependencies installed
        ↓
AniList GraphQL request
        ↓
Live media inventory retrieved
        ↓
Local JSON state loaded
        ↓
Current state compared with previous state
        ↓
Progress deltas detected
        ↓
Gamerscore & Temporal Analytics calculated
        ↓
Discord embeds & Live Hologram generated
        ↓
Airing schedules evaluated
        ↓
Ghost Radar processes MAL data
        ↓
Resolved ghosts are assimilated
        ↓
Discord log IDs stored
        ↓
48-hour purge evaluated
        ↓
JSON vaults & Performance Folders updated
        ↓
Repository state committed
        ↓
GitHub Actions execution ends

🧩 CORE SYSTEMS

Maximum Overdrive is divided into seven major operational systems.


System,Purpose
Master Sync,Synchronizes AniList media state
Gamerscore,Converts media activity into RPG-style points
Performance Vault,Tracks daily/weekly/monthly/yearly time consumption
Airing Radar,Tracks upcoming episode releases
Ghost Radar,Resolves missing MAL entries
Titanium Armor,Handles temporary API/network failures
Auto-Purge,Removes old Discord engine logs


Each subsystem has a focused responsibility.

The systems are designed to operate together without requiring a separate database server.

1. HIGH-DENSITY MASTER SYNC
The Master Sync is the core synchronization layer.

It executes a paginated GraphQL sweep against the AniList media-list API.

The engine retrieves the tracked inventory and extracts information required by the downstream systems.

The synchronization layer is responsible for:

Anime progress.

Manga progress.

Episode counts.

Chapter counts.

Volume counts.

Media status.

Exact media runtime (duration).

Romaji titles.

English titles.

Season information.

Season year.

Cover artwork.

Cover artwork color.

Upcoming airing information.

The inventory is then compared against the locally stored synchronization matrix.

🎨 CHAMELEON UI

The Chameleon UI uses the color returned by AniList's media cover information.

The engine reads:

coverImage.color

The returned color is converted into the format required by Discord embeds.

The Discord message can therefore visually match the artwork associated with the media entry.

This provides dynamic presentation without requiring manually selected colors.

2. RPG GAMERSCORE SYSTEM
Maximum Overdrive iActivity,Reward
Anime episode watched,+10 G
Manga chapter read,+2 G
Fully completed series,+100 Gncludes a custom RPG-style scoring layer.

Every tracked action can contribute Gamerscore.



The current scoring model is:

Activity	Reward
Anime episode watched	+10 G
Manga chapter read	+2 G
Fully completed series	+100 G


The system separates weekly activity from lifetime progress.

🎮 LIFETIME GAMERSCORE
Lifetime Gamerscore represents the permanently accumulated score.

Once weekly Gamerscore is transferred into the lifetime vault, it becomes part of the persistent total.

📆 WEEKLY GAMERSCORE
Weekly Gamerscore tracks activity during the current calendar week.

The engine determines the current ISO calendar week using UTC time.

🧹 WEEKLY WIPE
At the beginning of a new weekly cycle, the engine performs the weekly rollover.

🏆 COMPLETIONIST BONUS
A completed series can trigger an additional:

Plaintext
+100 G

completionist reward.

👑 PRESTIGE OVERRIDE
The project includes a prestige system tied to lifetime Gamerscore.

The configured threshold is:

Plaintext
10,000 Lifetime G
After crossing the threshold, the webhook identity is configured to use the:

3. LIVE PERFORMANCE HOLOGRAM & VAULT
The engine converts media progress into precise temporal analytics using a dynamic File System Vault and a self-refreshing Discord Hologram.

🧮 TEMPORAL MATH PROTOCOL
When the engine detects a progress delta, it calculates the exact time consumed:

Anime: Pulls the exact duration dynamically from the AniList GraphQL API and subtracts 2 minutes (to precisely account for standard OP/ED skips). (e.g., 24m becomes 22m, 120m movie becomes 118m).

Manga: Multiplies chapter progression by a flat 5 minutes per chapter.

📂 LOCAL FILE VAULT
Instead of clumping all data into one file, the system dynamically constructs a localized ledger tree directly in the repository:

Plaintext
📁 performance
 ┣ 📂 daily
 ┃ ┗ 📜 2026-08-12.json
 ┣ 📂 weekly
 ┃ ┗ 📜 2026-W33.json
 ┣ 📂 monthly
 ┃ ┗ 📜 2026-08.json
 ┗ 📂 yearly
   ┗ 📜 2026.json

⚡ DISCORD HOLOGRAM
To prevent UI clutter, the engine uses Discord's message_id deletion mechanic to create a "live" dashboard.
When progress is detected, the engine sends a silent DELETE strike to wipe the old dashboard, instantly dropping a newly calculated, live-refreshing performance UI at the bottom of the #performance-monitor channel.

4. DUAL-STAGE AIRING INTELLIGENCE
Maximum Overdrive monitors anime entries containing upcoming airing information.

The system is designed around two warning stages.

🕒 PHASE 1 — THREE-HOUR WARNING
When an episode reaches the configured three-hour threshold:

Plaintext
10,800 seconds
the engine produces a:

Plaintext
🕒 3-HOUR WARNING
alert.

🚨 PHASE 2 — ONE-HOUR WARNING
When the remaining time falls below:

Plaintext
3,600 seconds
the engine produces a:

Plaintext
🚨 FINAL 1-HOUR WARNING
alert.

⏱️ DYNAMIC DISCORD TIMESTAMPS
Discord supports UNIX-based timestamp tags.

Maximum Overdrive uses:

Plaintext
<t:TIME:R>
to create relative timestamps.

5. BIMODAL GHOST RADAR
Ghost Radar exists to handle media that appears in MAL exports but cannot currently be matched against the AniList title inventory.

The system is designed around a local recovery workflow.

👻 WHY GHOSTS EXIST
MyAnimeList and AniList do not always contain perfectly identical databases.

When the engine cannot confidently resolve an imported entry, it stores the item instead of discarding it.

📦 DUAL XML PROCESSING
Ghost Radar processes two files:

Plaintext
mal_export.xml
mal_anime.xml
🗃️ GHOST VAULT
Unresolved entries are stored in:

Plaintext
db_ghosts.json
🟢 GHOST ASSIMILATION
When an unresolved entry eventually becomes available through AniList, the engine can detect the media, submit an AniList mutation, restore progress, and route the assimilation payload to Discord.

6. TITANIUM ARMOR
AniList API calls can encounter temporary failures.

Maximum Overdrive therefore wraps network operations inside a retry layer.

The central helper is:

Python
fetch_with_armor(url, payload, headers, retries)
🛡️ EXPONENTIAL BACKOFF
The documented retry pattern is:

Plaintext
Attempt 1 -> Failure -> Sleep 3s
Attempt 2 -> Failure -> Sleep 6s
Attempt 3
7. 48-HOUR AUTO-PURGE
The command center includes a cleanup mechanism for basic log files.

The engine records Discord message identifiers associated with its log output.

These records are stored inside:

Plaintext
db_messages.json
🧹 PURGE PROCESS
When a stored message timestamp ages past 172,800 seconds (48 hours), the engine sends a targeted DELETE request, ensuring operational channels remain clean.

📡 DISCORD COMMAND CENTER
Maximum Overdrive uses multiple Discord webhooks.

Each webhook is responsible for a distinct class of information.

📋 DISCORD PIPELINE MAPEnvironment VariableTarget ChannelPurposeDISCORD_ANILIST_ANIME_WEBHOOK#anilist-animeAnime progressDISCORD_ANILIST_MANGA_WEBHOOK#anilist-mangaManga progressDISCORD_ACHIEVEMENTS_WEBHOOK#achievementsGamerscore and milestonesDISCORD_PERFORMANCE_WEBHOOK#performance-monitorLive refreshing time hologramsDISCORD_AIRING_WEBHOOK#anime-airing-alertsUpcoming episode alertsDISCORD_GHOST_RADAR_WEBHOOK#ghost-archiveGhost assimilationDISCORD_FAVORITES_WEBHOOK#priority-favoritesPriority franchise alertsDISCORD_ANILIST_LOG_WEBHOOK#anilist-logEngine telemetry🧠 JSON MEMORY VAULTMaximum Overdrive deliberately uses lightweight JSON files instead of an external SQL database.The memory architecture consists of static vaults and a dynamic sub-directory:Plaintextdb_sync.json
db_achievements.json
db_airing.json
db_ghosts.json
db_messages.json
db_performance_msg.json
performance/
Each file has a distinct responsibility.1. db_sync.jsonThe core synchronization matrix tracking progressive changes.2. db_achievements.jsonThe RPG vault tracking weekly and lifetime scores.3. performance/ DIRECTORY & db_performance_msg.jsonThe temporal ledger tracking generated daily, weekly, monthly, and yearly consumption JSON files, while db_performance_msg.json tracks the message_id of the Discord hologram to allow for automatic deletion and refresh.4. db_airing.jsonThe Airing Radar state machine preventing duplicate alerts.5. db_ghosts.jsonThe unresolved MAL entry vault keeping ghosts secure until AniList assimilation.6. db_messages.jsonThe Discord cleanup vault mapping message IDs to deletion endpoints.

📁 REPOSITORY STRUCTURE
A typical repository is organized as:

Plaintext
.
├── anilist_engine.py
│
├── db_sync.json
├── db_achievements.json
├── db_airing.json
├── db_ghosts.json
├── db_messages.json
├── db_performance_msg.json
│
├── performance/
│   ├── daily/
│   ├── weekly/
│   ├── monthly/
│   └── yearly/
│
├── mal_export.xml
├── mal_anime.xml
│
└── .github/
    └── workflows/
        └── sync_engine.yml
🚀 INSTALLATION
Step 1 — Create the Repository
Create a private GitHub repository and add the primary anilist_engine.py to the root.

Step 2 — Add JSON Memory Vaults
Create the required initial state files (e.g., db_sync.json). The performance/ directory will automatically generate on the first active progress delta.

Step 3 — Add MAL Exports
Export your .xml mal files into the root.

Step 4 — Configure Discord & Zulip
Create the required channels, obtain webhook URLs, and generate Zulip bot credentials.

Step 5 — Configure GitHub Secrets
Map the secret variables in GitHub Actions.

📦 MAL EXPORT PREPARATION
The Ghost Radar expects two XML files at the repository root:

mal_export.xml

mal_anime.xml

🔐 GITHUB SECRETS
The engine configuration currently expects core variables mapped in Repository > Settings > Secrets and variables > Actions:

Plaintext
ANILIST_TARGET_TOKEN
DISCORD_ANILIST_ANIME_WEBHOOK
DISCORD_ANILIST_MANGA_WEBHOOK
DISCORD_AIRING_WEBHOOK
DISCORD_ANILIST_LOG_WEBHOOK
DISCORD_FAVORITES_WEBHOOK
DISCORD_GHOST_RADAR_WEBHOOK
DISCORD_ACHIEVEMENTS_WEBHOOK
DISCORD_PERFORMANCE_WEBHOOK
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
ZULIP_BOT_EMAIL
ZULIP_API_KEY
ZULIP_SERVER_URL
(Note: Ensure AniList target tokens remain completely private. Do not embed them in source code.)

📡 DISCORD WEBHOOK CONFIGURATION
Each channel has a specific role to separate the command center and prevent noisy, blended feeds. Prioritize S-Tier updates (e.g. One Piece) in the favorites channel and let the Performance channel remain uncluttered via the auto-deleting hologram protocol.

⚙️ GITHUB ACTIONS
The engine is designed to execute through GitHub Actions.

The workflow file is:

Plaintext
.github/workflows/sync_engine.yml
🕒 EXECUTION SCHEDULE
The configured cron expression is:

YAML
- cron: '30 2-17 * * *'
This schedules automated background processing. The workflow also supports manual execution through workflow_dispatch.

🧵 CONCURRENCY
The workflow uses cancel-in-progress: true to prevent overlapping engine executions from operating against the same persistent state at the same time.

🛠️ WORKFLOW CONFIGURATION
The core workflow runs on Ubuntu, provisions Python 3.10, injects the master environment variables, runs the engine, and safely archives the dynamic JSON matrix through native Git commit rebases.

💾 AUTOMATIC STATE PERSISTENCE
At the end of the workflow, the JSON vaults are synchronized back into the repository.

Bash
git config --global user.name 'github-actions[bot]'
git config --global user.email 'github-actions[bot]@users.noreply.github.com'
git pull origin main --rebase || true 
git add *.json performance/ README.md || true 
git diff --staged --quiet || git commit -m "chore: performance & state memory update [skip ci]"
git push
This is the mechanism that allows future executions to remember earlier runs.

🔍 GRAPHQL ARCHITECTURE
Maximum Overdrive uses a highly dense AniList GraphQL query fetching 50 paginated entries at a time. The query explicitly pulls metadata including season, total episodes, dynamic cover colors, next airing schedules, and precise episode durations for temporal math.

🧬 ASSIMILATION MUTATION
When Ghost Radar successfully resolves an unresolved media entry, it uses the SaveMediaListEntry mutation to restore the localized progress and score back into the target AniList account automatically.

🔄 ANILIST SYNCHRONIZATION
The Master Sync determines the delta by subtracting the Previous Progress from the Current Progress. This isolated delta drives the Gamerscore generation, the Temporal Matrix files, and the Discord embeds. Complete consumption triggers a +100 G bonus multiplier.

📺 AIRING RADAR ARCHITECTURE
Airing radar calculates the remaining seconds until airingAt. It tracks a state machine (none -> 3h -> 1h) to guarantee users only receive targeted early and final warnings without repeated spam notifications on overlapping cron schedules.

👻 GHOST RADAR ARCHITECTURE
The Ghost Radar reads XML data via xml.etree.ElementTree. Titles are normalized to strict lowercase. It queries the AniList known pool and stores missing elements securely until AniList approves the media page.

🛡️ API RESILIENCE
Network requests are routed through a 3-strike Exponential Backoff pattern (Wait 3s -> Wait 6s). Ghost lookups run on an intentional 1.5-second time throttle to respect AniList rate limits.

🧹 AUTOMATIC STATE MAINTENANCE
The system maintains 6 unique operational states (Sync, Achievement, Airing, Ghost, Discord Message, and Hologram).

💻 CODEBASE COMPONENTS
fetch_with_armor(): Resilient HTTP requests.

send_discord_alert(): Payload generator processing embeds and log ID capturing.

manage_achievements_and_weekly(): RPG processing, calendar ISO logic, and prestige logic.

update_performance_vault(): Dynamic directory creation and temporal episode/chapter math generation.

refresh_performance_hologram(): DELETE and POST logic for live dashboard simulation.

process_airing_countdowns(): Temporal schedule logic.

execute_master_sync(): Core orchestrator.

📊 SYSTEM METRICS
The flat-file architecture is highly optimized. A sweeping operation covering 850+ database items (incorporating GraphQL pulls, Ghost searches, API throttling, and file generation) safely resolves in under 3 minutes utilizing standard GitHub Actions compute.

⚠️ LIMITATIONS
JSON vs SQL: No complex relational querying available out of the box.

Serverless Bound: Relies strictly on cron workflow execution; there is no persistent socket connection.

API Constraints: Total outages on AniList servers will halt progress checks despite Titanium Armor retries.

🔐 SECURITY
Treat this repository as heavily classified.

Keep tokens mapped in GitHub Secrets.

Do not expose Discord Webhook URLs in issue tickets or README screenshots.

Rotate leaked tokens immediately, understanding that git history tracks previous commits.

🛠️ TROUBLESHOOTING
Action fails setup: Ensure Python 3.10 is active.

AniList 401/403 Error: Verify target token in secrets.

Hologram not refreshing: Ensure db_performance_msg.json has read/write permissions and a delta occurred.

Zulip 401 Unauthorized: Ensure Bot Email domain precisely matches the Server URL domain.

✅ OPERATIONAL CHECKLIST
Verify presence of engine .py files, required base .json templates, XML sources, webhooks mapping in GitHub settings, and YAML workflows before firing the primary manual dispatch button. Ensure permissions: contents: write is active on the repo.

🎯 DESIGN PRINCIPLES
State Should Persist: Repository history is paramount.

Automation Should Be Idempotent: Avoid double-firing alerts by rigorously checking JSON matrices.

Discord Is Visual, Repo Is Memory: The repository holds the logic; Discord merely reflects it.

🧭 OPERATIONAL PHILOSOPHY
TRACK -> COMPARE -> CALCULATE -> ALERT -> REMEMBER -> REPEAT

⚡ MAXIMUM OVERDRIVE LOOP
Data flows cyclically. Sync detects deltas. Deltas fuel Gamerscore, Temporal Analytics, Airing, and Ghosts. Output flows to Discord/Zulip. Memory flows to GitHub. The cycle rests until the next cron ping.

🏆 GAMERSCORE EXAMPLES
Anime Delta: +5 Eps = +50 G

Manga Delta: +15 Chp = +30 G

Completion: +100 G

📺 AIRING EXAMPLE
10,800 Seconds Remaining -> 3h Warning.
3,600 Seconds Remaining -> 1h Final Warning.

👻 GHOST EXAMPLE
Media missing on AniList is stored with current score/progress in JSON. Once AniList approves the media, the engine discovers it, submits a mutation restoring progress automatically, and logs "GHOST ASSIMILATED."

🧹 PURGE EXAMPLE
Discord Log message_id is created at T0.
At T+172,800 seconds, the message is vaporized via a silent DELETE API call.

🧩 COMPONENT RELATIONSHIPS
The engine centralizes execution inside execute_master_sync(). That conductor queries sub-routines (Airing, Ghost, Hologram, Purge) in sequence before initiating file write actions.

🔬 DEBUGGING STRATEGY
Isolate the subsystem. An API failure does not mean a JSON failure. If the hologram doesn't show, verify the exact duration math. If Zulip fails, check the auth strings. Follow the chain step-by-step.

🧪 VALIDATION STRATEGY
Run workflow_dispatch. Track the Actions log trace. Validate Discord drops. Check the pushed commit on the main branch to ensure db_sync.json and performance/ files were mutated.

🧠 MEMORY MODEL
Live Memory (AniList fetch) + Persistent Memory (JSON Vaults) = Automated Intelligent Decision Making.

🛰️ WHY GITHUB ACTIONS
Zero server maintenance. Background execution. Secure secret management. Native file mutation via bots.

🪶 WHY JSON
Zero database hosting costs. Human-readable logs. Easily auditable Git commit histories showing exact progress updates line-by-line.

🧱 WHY MODULAR SUBSYSTEMS
Keeps the Python execution manageable, testable, and strictly bound to individual responsibilities.

🎨 WHY DYNAMIC COLORS
Aesthetic harmony. Discord side-borders perfectly mirror the vibrant primary colors of the attached anime/manga thumbnail art via native GraphQL hex values.

📚 WHY MULTIPLE DISCORD CHANNELS
Prevents notification fatigue. Keeps log noise out of the premium, S-Tier alert channels.

🗺️ FUTURE EXPANSION
Potential migration toward relational analytics, complex web UIs, and expanded priority franchise tracking parameters.

🧪 DEVELOPMENT NOTES
Back up *.json files before any major .py structural rewrites to avoid corrupting the Master Sync matrix tracking progress histories.

🛠️ RECOMMENDED DEVELOPMENT WORKFLOW
Modify Code -> Test Payloads -> Manual GitHub Dispatch -> Verify Logs -> Confirm JSON Git Push -> Leave on Cron Auto-Pilot.

🧯 RECOVERY PROCEDURE
If corruption occurs: Halt Cron -> Back up repo -> Identify corrupt file -> Restore via Git History -> Run Manual Dispatch.

📈 PERFORMANCE MODEL
The current 850-item library processes exceptionally well within GitHub's free-tier Actions compute time limits.

🧮 SCALING CONSIDERATIONS
As your library balloons, API pagination increases. Throttling mechanisms remain critical to avoid rate-limiting triggers on the AniList servers.

🕹️ COMPLETIONIST DESIGN
Maximum Overdrive actively pushes users to fully complete series via the +100 G bonus, preventing list stagnation and perpetual "Watching/Reading" backlogs.

🏅 RPG INTERPRETATION
Your entire watch history transforms into a gamified progression matrix. Every chapter feeds the engine.

🧠 COMMAND CENTER MENTAL MODEL
AniList = Inventory

JSON = Memory

Python = Brain

GitHub Actions = Clock

Discord = Command Center

Hologram = Analytics

🧭 SYSTEM STATUS MODEL
The engine remains dormant until GitHub Actions kicks the workflow into gear, running sequence tracking checks before immediately powering down to conserve resources.

📦 BACKUP STRATEGY
Your GitHub repository is the backup. Retaining the .json and .xml files safely preserves the historical matrix indefinitely.

🔒 PRIVATE REPOSITORY RECOMMENDATION
Do not expose this repository to the public. It houses highly localized identity variables, read histories, and webhook endpoints.

✅ DEPLOYMENT COMPLETION TEST
If workflow_dispatch yields green checks in the Actions tab, and Discord/Zulip receives correctly formatted embeds, the architecture is structurally sound.

🧪 MANUAL EXECUTION
Used strictly for on-demand sync testing or immediately forcing a Live Performance Hologram update outside of the standard cron hours.

📜 LOGGING PHILOSOPHY
Keep operations separated from the fun. Let the engine output telemetry into #anilist-log while you enjoy the #anilist-anime tracking feed.

🧹 LOG RETENTION
Keeping log retention to 48 hours acts as an automatic vacuum cleaner, maintaining channel hygiene over years of continuous operation.

🛰️ AUTOMATION PHILOSOPHY
Set it, forget it, and let the command center run the analytics in the background seamlessly.

🏗️ ARCHITECTURAL SUMMARY
External Data: AniList + MAL

Processing: Python Engine

State: JSON Vaults & Performance Directories

Presentation: Discord & Zulip Webhooks

Automation: GitHub Actions

📊 FEATURE MATRIX
Feature	Purpose	State
AniList GraphQL	Media synchronization	✅
Anime Progress	Progress tracking	✅
Manga Progress	Progress tracking	✅
Chameleon UI	Artwork-based embed color	✅
Gamerscore	RPG scoring	✅
Performance Hologram	Live Daily/Weekly/Monthly/Yearly Tracking	✅
Temporal Vault	Dynamic runtime folder analytics	✅
Completion Bonus	Series completion reward	✅
Weekly Wipe	Weekly score rollover	✅
Milestones	Weekly achievement thresholds	✅
Prestige Override	Lifetime milestone identity	✅
Airing Radar	Upcoming episode monitoring	✅
3-Hour Alert	Early warning	✅
1-Hour Alert	Final warning	✅
Dynamic Timestamps	Discord countdown display	✅
Ghost Radar	MAL anomaly recovery	✅
Ghost Vault	Persistent unresolved entries	✅
Ghost Assimilation	Automatic AniList restoration	✅
API Armor	Retry / backoff	✅
Discord Pipeline	Multi-channel routing	✅
Auto-Purge	48-hour cleanup	✅
JSON Persistence	Local state memory	✅
GitHub Actions	Scheduled execution	✅
🧩 FEATURE RESPONSIBILITY MAP
Component	Input	Output
Master Sync	AniList GraphQL	Media inventory
Gamerscore	Progress delta	G points
Performance Vault	Duration & Progress Delta	JSON Ledgers & Hologram
Airing Radar	Airing timestamp	Discord warning
Ghost Radar	MAL XML	Ghost records
Assimilation	Ghost record + AniList match	AniList update
Discord Layer	Event data	Webhook message
Auto-Purge	Message state	Delete request
JSON Vault	Runtime state	Persistent state
GitHub Actions	Schedule	Engine execution
🏁 FINAL SYSTEM LOOP
Plaintext
                 START
                   │
                   ▼
          GitHub Actions Run
                   │
                   ▼
           Load Repository
                   │
                   ▼
           Load JSON Memory
                   │
                   ▼
           Query AniList API
                   │
                   ▼
           Build Inventory
                   │
                   ▼
          Compare Previous State
                   │
                   ▼
            Detect Changes
                   │
          ┌────────┼─────────┬─────────┐
          │        │         │         │
          ▼        ▼         ▼         ▼
       Gamerscore Airing   Ghosts  Performance
          │        │         │         │
          └────────┼─────────┴─────────┘
                   │
                   ▼
             Discord Alerts
                   │
                   ▼
            Purge Old Logs
                   │
                   ▼
            Save JSON State
                   │
                   ▼
              Git Commit
                   │
                   ▼
               Git Push
                   │
                   ▼
                  END
                   │
                   ▼
              NEXT RUN
🏆 PROJECT STATUS
AniList Maximum Overdrive 4.1.0 — Apex Build

The documented architecture currently includes:

Plaintext
✓ AniList synchronization
✓ GraphQL data retrieval
✓ Gamerscore tracking
✓ Weekly Gamerscore rollover
✓ Live Temporal Hologram Updates
✓ Dynamic JSON Analytics Folders
✓ Completion rewards
✓ Achievement milestones
✓ Prestige threshold
✓ Airing Radar
✓ 3-hour warning
✓ 1-hour warning
✓ Dynamic Discord timestamps
✓ MAL XML ingestion
✓ Ghost Radar
✓ Ghost Vault
✓ Ghost Assimilation
✓ API retry protection
✓ Discord webhook routing
✓ Persistent JSON state
✓ Discord log retention
✓ Automatic 48-hour purge
✓ GitHub Actions automation
🧠 THE MAXIMUM OVERDRIVE MANIFESTO
This project is not designed to be another passive tracking script.

It is designed around the idea that personal media data can become an active system.

Plaintext
Anime
↓
Data

Manga
↓
Data

Data
↓
State

State
↓
Events

Events
↓
Gamerscore

Events
↓
Analytics

Events
↓
Alerts

Alerts
↓
Discord

Discord
↓
Command Center
The end result is a personal media ecosystem that watches the tracker alongside you.

🧭 THE BROAD OBJECTIVE
The long-term architectural direction is to make the system increasingly autonomous while maintaining a lightweight deployment model.

The fundamental constraints remain:

Plaintext
Minimal infrastructure
Persistent state
Automated execution
Human-readable memory
Discord visibility
AniList integration
MAL recovery
Temporal Tracking
🗺️ FUTURE EXPANSION IDEAS
The architecture could later be extended with additional components such as:

Plaintext
Historical Gamerscore analytics
Gamerscore leaderboards
More detailed completion statistics
Expanded priority-franchise logic
Additional notification categories
Web dashboard
Visual progress charts
Database migration option
Improved title matching
Extended recovery logic
More detailed execution reports
These are architectural possibilities and should be implemented only when they fit the project's goals.

📚 DOCUMENTATION PRINCIPLE
The README intentionally documents not only what the system does, but also how the systems relate to each other.

The goal is for a future maintainer to understand:

Plaintext
What runs
Why it runs
Where the data comes from
Where state is stored
Where alerts go
How state persists
How failures are handled
How analytics compute
🧪 MAINTENANCE PRINCIPLE
When modifying Maximum Overdrive:

Plaintext
Preserve state
Preserve secrets
Preserve webhook routing
Preserve workflow permissions
Preserve JSON compatibility
Test API requests
Test Discord output
Test state persistence
A small change in one subsystem can affect another because the engine operates as a coordinated pipeline.

🔥 MAXIMUM OVERDRIVE CHECKPOINT
Before considering a major version complete:

Plaintext
[ ] Master Sync verified
[ ] Gamerscore verified
[ ] Weekly rollover verified
[ ] Temporal Math verified
[ ] Hologram API trigger verified
[ ] Completion bonus verified
[ ] Airing Radar verified
[ ] Airing state verified
[ ] Ghost Radar verified
[ ] Ghost Vault verified
[ ] Ghost Assimilation verified
[ ] Retry logic verified
[ ] Discord routing verified
[ ] Message storage verified
[ ] Auto-Purge verified
[ ] GitHub Actions verified
[ ] JSON persistence verified
🧬 VERSION IDENTITY
Current release:

Plaintext
4.1.0
Codename:

Plaintext
APEX BUILD
Project identity:

Plaintext
ANILIST MAXIMUM OVERDRIVE
Author identity:

Plaintext
HARI (OREWATOKYO)
🛸 FINAL STATUS
Plaintext
╔══════════════════════════════════════════╗
║      ANILIST MAXIMUM OVERDRIVE           ║
║                                          ║
║              APEX BUILD 4.1.0            ║
║                                          ║
║       SYNC ................. ONLINE      ║
║       GAMERSCORE ........... ONLINE      ║
║       PERFORMANCE MATRIX ... ONLINE      ║
║       AIRING RADAR ......... ONLINE      ║
║       GHOST RADAR .......... ONLINE      ║
║       API ARMOR ............ ONLINE      ║
║       DISCORD .............. ONLINE      ║
║       JSON MEMORY .......... ONLINE      ║
║       AUTO-PURGE ........... ONLINE      ║
║       GITHUB ACTIONS ....... ONLINE      ║
║                                          ║
║           MAXIMUM OVERDRIVE              ║
║                IS ONLINE                 ║
╚══════════════════════════════════════════╝
👑 HARI (OREWATOKYO)
Built for the completionist.

Built for the obsessive tracker.

Built for the person who doesn't just want a list.

Built for the person who wants the list to become a system.

Track everything.

Remember everything.

Automate everything.

Maximum Overdrive. ⚡

📜 CREDITS
Author: Hari (Orewatokyo)

Primary Technologies:

Plaintext
Python 3.10
AniList GraphQL
GitHub Actions
Discord Webhooks
JSON
MyAnimeList XML exports
⭐ PROJECT TAGLINE
From passive tracking to an autonomous Otaku Command Center.

⚡ END OF SYSTEM DOCUMENT
Plaintext
Maximum Overdrive
Apex Build 4.1.0

System Document Compiled.
Automation Layer Active.
Persistent Memory Active.
Command Center Active.
Performance Analytics Initialized.

END.


                    │   Scheduled Execution   │
                    └────────────────────────┘](https://gemini.google.com/u/1/app/866c9aa52836cb9f?hl=en-IN&pageId=none)
