# ⚡ ANILIST MAXIMUM OVERDRIVE ⚡

<!-- BADGES_START -->
![Gamerscore](https://img.shields.io/badge/Lifetime_Gamerscore-4894%20G-FFD700?style=for-the-badge&logo=epic-games&logoColor=black)
![Weekly](https://img.shields.io/badge/Weekly_Grind-528%20G-FF4500?style=for-the-badge&logo=graphql&logoColor=white)
<!-- BADGES_END -->
---

## 🧬 PROJECT IDENTITY

**Project:** AniList Maximum Overdrive  
**Version:** 4.0.0 — Apex Build  
**Author:** Orewatokyo  
**Architecture:** Python 3.10 + AniList GraphQL + GitHub Actions + Discord Webhooks + JSON State Vaults

AniList Maximum Overdrive is an autonomous AniList synchronization and monitoring engine designed for heavy anime and manga tracking workflows.

It transforms passive media tracking into an automated command center.

The engine synchronizes AniList progress, calculates a custom Gamerscore system, monitors upcoming anime episodes, processes MyAnimeList exports, maintains persistent local state, distributes information through multiple Discord webhook channels, and performs automatic cleanup of historical engine messages.

The project is designed around a lightweight flat-file architecture.

There is no SQL database requirement.

There is no continuously running server requirement.

There is no manual synchronization requirement.

The system is designed to run through scheduled GitHub Actions executions and persist its memory through JSON state files.

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
- [3. Dual-Stage Airing Intelligence](#3-dual-stage-airing-intelligence)
- [4. Bimodal Ghost Radar](#4-bimodal-ghost-radar)
- [5. Titanium Armor](#5-titanium-armor)
- [6. 48-Hour Auto-Purge](#6-48-hour-auto-purge)
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
5. Calculates Gamerscore.
6. Generates Discord embed payloads.
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
                 ┌───────────────┼────────────────┐
                 │               │                │
                 ▼               ▼                ▼
          Gamerscore        Airing Radar      Ghost Radar
                 │               │                │
                 └───────────────┼────────────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │     Discord Pipeline   │
                    └────────────┬───────────┘
                                 │
          ┌──────────────────────┼───────────────────────┐
          │                      │                       │
          ▼                      ▼                       ▼
     Anime Channel         Achievement Channel      Airing Channel
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │      JSON Vaults        │
                    │      Persistent State   │
                    └────────────┬───────────┘
                                 │
                                 ▼
                    ┌────────────────────────┐
                    │     GitHub Actions      │
                    │   Scheduled Execution   │
                    └────────────────────────┘
```

---

## 🔄 SYSTEM DATA FLOW

The engine follows a synchronized operational sequence.

```text
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
Gamerscore calculated
        ↓
Discord embeds generated
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
JSON vaults updated
        ↓
Repository state committed
        ↓
GitHub Actions execution ends
```

---

## 🧩 CORE SYSTEMS

Maximum Overdrive is divided into six major operational systems.

| System | Purpose |
|---|---|
| Master Sync | Synchronizes AniList media state |
| Gamerscore | Converts media activity into RPG-style points |
| Airing Radar | Tracks upcoming episode releases |
| Ghost Radar | Resolves missing MAL entries |
| Titanium Armor | Handles temporary API/network failures |
| Auto-Purge | Removes old Discord engine logs |

Each subsystem has a focused responsibility.

The systems are designed to operate together without requiring a separate database server.

---

## 1. HIGH-DENSITY MASTER SYNC

The Master Sync is the core synchronization layer.

It executes a paginated GraphQL sweep against the AniList media-list API.

The engine retrieves the tracked inventory and extracts information required by the downstream systems.

The synchronization layer is responsible for:

- Anime progress.
- Manga progress.
- Episode counts.
- Chapter counts.
- Volume counts.
- Media status.
- Romaji titles.
- English titles.
- Season information.
- Season year.
- Cover artwork.
- Cover artwork color.
- Upcoming airing information.

The inventory is then compared against the locally stored synchronization matrix.

### 🎨 CHAMELEON UI

The Chameleon UI uses the color returned by AniList's media cover information.

The engine reads:

```text
coverImage.color
```

The returned color is converted into the format required by Discord embeds.

The Discord message can therefore visually match the artwork associated with the media entry.

This provides dynamic presentation without requiring manually selected colors.

### 🧮 HIGH-DENSITY MEDIA DATA

The standard media payload contains information such as:

```text
Romaji Title
English Title
Status
Consumed Progress
Remaining Progress
Episode Count
Chapter Count
Volume Count
Season
Season Year
```

This creates a compact but information-dense Discord representation.

---

## 2. RPG GAMERSCORE SYSTEM

Maximum Overdrive includes a custom RPG-style scoring layer.

Every tracked action can contribute Gamerscore.

The current scoring model is:

| Activity | Reward |
|---|---:|
| Anime episode watched | +10 G |
| Manga chapter read | +2 G |
| Fully completed series | +100 G |

The system separates weekly activity from lifetime progress.

### 🎮 LIFETIME GAMERSCORE

Lifetime Gamerscore represents the permanently accumulated score.

Once weekly Gamerscore is transferred into the lifetime vault, it becomes part of the persistent total.

Example:

```json
{
  "lifetime_g": 12450
}
```

### 📆 WEEKLY GAMERSCORE

Weekly Gamerscore tracks activity during the current calendar week.

Example:

```json
{
  "weekly_g": 840,
  "current_week": 32
}
```

The engine determines the current ISO calendar week using UTC time.

### 🧹 WEEKLY WIPE

At the beginning of a new weekly cycle, the engine performs the weekly rollover.

```text
Weekly Gamerscore
        ↓
Bank into Lifetime Gamerscore
        ↓
Reset Weekly Gamerscore
        ↓
Advance Calendar Week
        ↓
Generate Weekly Report
```

The weekly score is temporary.

The lifetime score is persistent.

### 🏆 COMPLETIONIST BONUS

A completed series can trigger an additional:

```text
+100 G
```

completionist reward.

This gives completed media a distinct value beyond ordinary episode or chapter consumption.

### 🥇 WEEKLY MILESTONES

The achievement system includes special milestone thresholds.

Configured milestone examples include:

```text
1,000 G
5,000 G
```

When a weekly threshold is crossed, the engine can generate specialized achievement embeds.

### 👑 PRESTIGE OVERRIDE

The project includes a prestige system tied to lifetime Gamerscore.

The configured threshold is:

```text
10,000 Lifetime G
```

After crossing the threshold, the webhook identity is configured to use the:

```text
Orewatokyo
```

identity for future alerts.

This acts as the project's highest Gamerscore prestige layer.

---

## 3. DUAL-STAGE AIRING INTELLIGENCE

Maximum Overdrive monitors anime entries containing upcoming airing information.

The system is designed around two warning stages.

### 🕒 PHASE 1 — THREE-HOUR WARNING

When an episode reaches the configured three-hour threshold:

```text
10,800 seconds
```

the engine produces a:

```text
🕒 3-HOUR WARNING
```

alert.

The warning is routed to the dedicated airing webhook.

### 🚨 PHASE 2 — ONE-HOUR WARNING

When the remaining time falls below:

```text
3,600 seconds
```

the engine produces a:

```text
🚨 FINAL 1-HOUR WARNING
```

alert.

This is the final configured pre-release warning.

### ⏱️ DYNAMIC DISCORD TIMESTAMPS

Discord supports UNIX-based timestamp tags.

Maximum Overdrive uses:

```text
<t:TIME:R>
```

to create relative timestamps.

This means Discord can display a dynamic representation of the remaining time.

### 🧠 AIRING STATE MACHINE

The engine stores warning state inside:

```text
db_airing.json
```

Example:

```json
{
  "21456_ep1067": "3h",
  "21456_ep1068": "1h",
  "99876_ep12": "none"
}
```

This prevents the same warning stage from being repeatedly dispatched.

---

## 4. BIMODAL GHOST RADAR

Ghost Radar exists to handle media that appears in MAL exports but cannot currently be matched against the AniList title inventory.

The system is designed around a local recovery workflow.

### 👻 WHY GHOSTS EXIST

MyAnimeList and AniList do not always contain perfectly identical databases.

Differences can occur because of:

- Different titles.
- Different naming conventions.
- Missing entries.
- Unapproved media.
- Recently added submissions.
- Naming collisions.

When the engine cannot confidently resolve an imported entry, it stores the item instead of discarding it.

### 📦 DUAL XML PROCESSING

Ghost Radar processes two files:

```text
mal_export.xml
mal_anime.xml
```

The two files represent manga and anime export data respectively.

The engine processes both inputs in the same execution cycle.

### 🌐 BILINGUAL TITLE MATRIX

The engine creates a lowercase matching pool using known AniList titles.

The matching matrix can include:

```text
Romaji titles
English titles
```

Titles are normalized for case-insensitive comparison.

This helps reduce false negatives caused purely by capitalization.

### 🗃️ GHOST VAULT

Unresolved entries are stored in:

```text
db_ghosts.json
```

Example:

```json
{
  "Obscure Light Novel Name": {
    "progress": 45,
    "score": 8,
    "type": "MANGA"
  }
}
```

The unresolved entry remains available for future recovery.

### 🔎 CONTINUOUS SEARCH

Ghost Radar checks unresolved items during subsequent engine executions.

```text
Ghost Found
      ↓
Store in db_ghosts.json
      ↓
Next engine execution
      ↓
Search AniList
      ↓
Entry still unavailable?
      │
      ├── YES → Keep ghost
      │
      └── NO → Assimilate
```

### 🟢 GHOST ASSIMILATION

When an unresolved entry eventually becomes available through AniList, the engine can:

1. Detect the newly available media.
2. Match the entry.
3. Read the stored progress.
4. Read the stored score.
5. Submit an AniList mutation.
6. Restore the corresponding progress.
7. Remove or update the unresolved state.
8. Report the successful assimilation to Discord.

The configured Discord event is:

```text
🟢 GHOST ASSIMILATED
```

---

## 5. TITANIUM ARMOR

AniList API calls can encounter temporary failures.

Maximum Overdrive therefore wraps network operations inside a retry layer.

The central helper is:

```python
fetch_with_armor(url, payload, headers, retries)
```

The function is designed to provide resilience against temporary API and network failures.

### 🛡️ EXPONENTIAL BACKOFF

The documented retry pattern is:

```text
Attempt 1
   ↓
Failure
   ↓
Sleep 3 seconds
   ↓
Attempt 2
   ↓
Failure
   ↓
Sleep 6 seconds
   ↓
Attempt 3
```

This reduces unnecessary repeated requests during temporary service instability.

### 🚦 API RATE CONSIDERATION

The project incorporates deliberate request throttling.

Ghost Radar additionally introduces spacing between searches.

The configured Ghost Radar delay is:

```python
time.sleep(1.5)
```

---

## 6. 48-HOUR AUTO-PURGE

The command center includes a cleanup mechanism.

The engine records Discord message identifiers associated with its log output.

These records are stored inside:

```text
db_messages.json
```

Example:

```json
{
  "112233445566778899": {
    "timestamp": 1691600000.5,
    "delete_url": "https://discord.com/api/webhooks/.../messages/112233445566778899"
  }
}
```

### 🧹 PURGE PROCESS

```text
Discord Message Created
        ↓
Message ID Stored
        ↓
Timestamp Stored
        ↓
Next Engine Execution
        ↓
Age Calculated
        ↓
Older than 172,800 seconds?
        ↓
YES
        ↓
DELETE request
```

The configured retention period is:

```text
48 hours
```

or:

```text
172,800 seconds
```

---

## 📡 DISCORD COMMAND CENTER

Maximum Overdrive uses multiple Discord webhooks.

Each webhook is responsible for a distinct class of information.

This prevents the command center from becoming a single noisy feed.

### 📋 DISCORD PIPELINE MAP

| Environment Variable | Target Channel | Purpose |
|---|---|---|
| `DISCORD_ANILIST_ANIME_WEBHOOK` | `#anilist-anime` | Anime progress |
| `DISCORD_ANILIST_MANGA_WEBHOOK` | `#anilist-manga` | Manga progress |
| `DISCORD_ACHIEVEMENTS_WEBHOOK` | `#achievements` | Gamerscore and milestones |
| `DISCORD_AIRING_WEBHOOK` | `#anime-airing-alerts` | Upcoming episode alerts |
| `DISCORD_GHOST_RADAR_WEBHOOK` | `#ghost-archive` | Ghost assimilation |
| `DISCORD_FAVORITES_WEBHOOK` | `#priority-favorites` | Priority franchise alerts |
| `DISCORD_ANILIST_LOG_WEBHOOK` | `#anilist-log` | Engine telemetry |

### 🎨 ANIME FEED

The anime webhook is responsible for standard anime synchronization notifications.

Typical information includes:

```text
Title
Status
Progress
Episodes
Remaining Episodes
Gamerscore
Artwork
Dynamic Color
```

### 📚 MANGA FEED

The manga webhook performs the equivalent role for manga updates.

Typical information includes:

```text
Title
Status
Chapter Progress
Remaining Chapters
Volume Progress
Gamerscore
Artwork
Dynamic Color
```

### 🏆 ACHIEVEMENT FEED

The achievement channel is reserved for major Gamerscore events.

Examples include:

```text
Series Completion
Weekly Wipe
1,000 G Milestone
5,000 G Milestone
Prestige Events
```

### 📺 AIRING FEED

The airing channel focuses exclusively on upcoming episode warnings.

Configured stages:

```text
🕒 3-HOUR WARNING
🚨 FINAL 1-HOUR WARNING
```

### 👻 GHOST ARCHIVE

Ghost Radar events are routed into the ghost archive.

The archive provides visibility into automatic recovery.

Configured success notification:

```text
🟢 GHOST ASSIMILATED
```

### ⭐ PRIORITY FAVORITES

The favorite webhook provides a dedicated destination for S-Tier priority franchises.

The original configuration identifies franchises such as:

```text
One Piece
```

as an example of a high-priority franchise.

### 📜 ENGINE LOG

The log channel receives the engine's operational telemetry.

The system records Discord message IDs so they can be evaluated by the 48-hour cleanup process.

---

## 🧠 JSON MEMORY VAULT

Maximum Overdrive deliberately uses lightweight JSON files instead of an external SQL database.

The memory architecture currently consists of five JSON vaults:

```text
db_sync.json
db_achievements.json
db_airing.json
db_ghosts.json
db_messages.json
```

Each file has a distinct responsibility.

### 1. `db_sync.json`

The core synchronization matrix.

It tracks the previous progress state associated with AniList media entries.

Conceptually:

```json
{
  "mediaId": {
    "progress": 12
  }
}
```

The synchronization layer uses this state to determine whether the user's current progress differs from the previous recorded state.

### 2. `db_achievements.json`

The RPG vault.

It stores:

```text
Lifetime Gamerscore
Weekly Gamerscore
Current Week
```

Example:

```json
{
  "lifetime_g": 12450,
  "weekly_g": 840,
  "current_week": 32
}
```

### 3. `db_airing.json`

The Airing Radar state machine.

It records which warning stage has already been dispatched.

Example:

```json
{
  "21456_ep1067": "3h",
  "21456_ep1068": "1h",
  "99876_ep12": "none"
}
```

### 4. `db_ghosts.json`

The unresolved MAL entry vault.

Example:

```json
{
  "Obscure Light Novel Name": {
    "progress": 45,
    "score": 8,
    "type": "MANGA"
  }
}
```

The data remains available until the entry can be resolved.

### 5. `db_messages.json`

The Discord cleanup vault.

It stores:

```text
Message ID
Timestamp
Delete endpoint
```

Example:

```json
{
  "112233445566778899": {
    "timestamp": 1691600000.5,
    "delete_url": "https://discord.com/api/webhooks/.../messages/112233445566778899"
  }
}
```

---

## 📁 REPOSITORY STRUCTURE

A typical repository can be organized as:

```text
.
├── anilist_engine.py
│
├── db_sync.json
├── db_achievements.json
├── db_airing.json
├── db_ghosts.json
├── db_messages.json
│
├── mal_export.xml
├── mal_anime.xml
│
└── .github/
    └── workflows/
        └── sync_engine.yml
```

The primary engine is:

```text
anilist_engine.py
```

The JSON files act as persistent memory.

The MAL XML files act as local source data for Ghost Radar.

The GitHub Actions workflow acts as the execution scheduler.

---

## 🚀 INSTALLATION

### Step 1 — Create the Repository

Create a private GitHub repository.

The engine is intended to operate as a private personal automation system.

Add the primary engine:

```text
anilist_engine.py
```

to the repository root.

### Step 2 — Add JSON Memory Vaults

Create the required state files:

```text
db_sync.json
db_achievements.json
db_airing.json
db_ghosts.json
db_messages.json
```

These files should be committed to the repository so GitHub Actions can read and update persistent state.

### Step 3 — Add MAL Exports

Export the required MAL data.

The configured filenames are:

```text
mal_export.xml
mal_anime.xml
```

Place both files in the repository root.

### Step 4 — Configure Discord

Create the required Discord channels.

Create the corresponding webhooks.

The webhook roles are described in the Discord pipeline section.

### Step 5 — Configure GitHub Secrets

Open:

```text
Repository
→ Settings
→ Secrets and variables
→ Actions
→ New repository secret
```

Create the required secrets.

---

## 📦 MAL EXPORT PREPARATION

The Ghost Radar expects two XML files.

The configured manga export filename is:

```text
mal_export.xml
```

The configured anime export filename is:

```text
mal_anime.xml
```

The files should be placed at:

```text
Repository Root/
```

rather than inside the workflow directory.

---

## 🔐 GITHUB SECRETS

The engine configuration currently expects eight repository secrets.

```text
ANILIST_TARGET_TOKEN

DISCORD_ANILIST_ANIME_WEBHOOK

DISCORD_ANILIST_MANGA_WEBHOOK

DISCORD_AIRING_WEBHOOK

DISCORD_ANILIST_LOG_WEBHOOK

DISCORD_FAVORITES_WEBHOOK

DISCORD_GHOST_RADAR_WEBHOOK

DISCORD_ACHIEVEMENTS_WEBHOOK
```

### 🔑 ANILIST TARGET TOKEN

```text
ANILIST_TARGET_TOKEN
```

This is the AniList authentication token used by the engine.

The token must remain private.

Do not place it directly inside:

```text
anilist_engine.py
```

Do not commit it to the repository.

Use GitHub Actions Secrets instead.

---

## 📡 DISCORD WEBHOOK CONFIGURATION

The project assumes separate Discord destinations.

A recommended logical layout is:

```text
#anilist-anime
#anilist-manga
#achievements
#anime-airing-alerts
#ghost-archive
#priority-favorites
#anilist-log
```

Each channel has a specific role.

This separation allows important messages to remain visible without mixing every event into a single stream.

---

## ⚙️ GITHUB ACTIONS

The engine is designed to execute through GitHub Actions.

The workflow file is:

```text
.github/workflows/sync_engine.yml
```

The workflow provides:

- Repository checkout.
- Python setup.
- Dependency installation.
- Secret injection.
- Engine execution.
- JSON state persistence.
- Repository synchronization.

### 🕒 EXECUTION SCHEDULE

The configured cron expression is:

```yaml
- cron: '30 2-17 * * *'
```

This schedules sixteen executions per day at the 30-minute mark during the specified UTC hours.

The workflow also supports manual execution through:

```yaml
workflow_dispatch:
```

This allows the engine to be manually triggered from GitHub Actions.

### 🧵 CONCURRENCY

The workflow defines:

```yaml
concurrency:
  group: anilist-engine
  cancel-in-progress: true
```

This prevents overlapping engine executions from operating against the same persistent state at the same time.

### 🐍 PYTHON ENVIRONMENT

The workflow uses:

```yaml
python-version: '3.10'
```

### 📦 DEPENDENCIES

The current workflow installs:

```text
requests
```

through:

```yaml
pip install requests
```

Additional Python functionality used by the documented implementation includes modules such as:

```text
datetime
time
xml.etree.ElementTree
```

where applicable.

---

## 🛠️ WORKFLOW CONFIGURATION

The core workflow structure is:

```yaml
name: AniList Maximum Overdrive

on:
  schedule:
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
```

The master engine is then executed with environment variables supplied through GitHub Secrets.

### 🔐 SECRET INJECTION

The workflow passes secrets through the environment.

```yaml
env:
  ANILIST_TARGET_TOKEN: ${{ secrets.ANILIST_TARGET_TOKEN }}
  DISCORD_ANIME_WEBHOOK: ${{ secrets.DISCORD_ANILIST_ANIME_WEBHOOK }}
  DISCORD_MANGA_WEBHOOK: ${{ secrets.DISCORD_ANILIST_MANGA_WEBHOOK }}
  DISCORD_AIRING_WEBHOOK: ${{ secrets.DISCORD_AIRING_WEBHOOK }}
  DISCORD_LOG_WEBHOOK: ${{ secrets.DISCORD_ANILIST_LOG_WEBHOOK }}
  DISCORD_FAVORITES_WEBHOOK: ${{ secrets.DISCORD_FAVORITES_WEBHOOK }}
  DISCORD_GHOST_RADAR_WEBHOOK: ${{ secrets.DISCORD_GHOST_RADAR_WEBHOOK }}
  DISCORD_ACHIEVEMENTS_WEBHOOK: ${{ secrets.DISCORD_ACHIEVEMENTS_WEBHOOK }}
```

The engine is then launched with:

```yaml
run: python anilist_engine.py
```

---

## 💾 AUTOMATIC STATE PERSISTENCE

At the end of the workflow, the JSON vaults are synchronized back into the repository.

The workflow configures the GitHub Actions identity:

```bash
git config --global user.name 'github-actions[bot]'
git config --global user.email 'github-actions[bot]@users.noreply.github.com'
```

The workflow then performs a pull, stages JSON files, creates a commit when changes exist, and pushes the updated state.

### 🔄 STATE COMMIT FLOW

```text
Engine starts
      ↓
JSON loaded
      ↓
Engine modifies state
      ↓
Execution ends
      ↓
git add *.json
      ↓
Changes detected?
      │
      ├── NO → No state commit
      │
      └── YES
            ↓
       Git commit
            ↓
       Git push
```

This is the mechanism that allows future executions to remember earlier runs.

---

## 🔍 GRAPHQL ARCHITECTURE

Maximum Overdrive uses AniList GraphQL queries to retrieve the information necessary for synchronization.

### 📡 HIGH-DENSITY FETCH QUERY

```graphql
query ($userName: String, $page: Int) {
  Page(page: $page, perPage: 50) {
    pageInfo {
      hasNextPage
    }

    mediaList(userName: $userName) {
      mediaId
      progress
      progressVolumes
      score
      status

      media {
        title {
          romaji
          english
        }

        type
        episodes
        chapters
        volumes
        season
        seasonYear

        coverImage {
          extraLarge
          color
        }

        nextAiringEpisode {
          airingAt
          episode
        }
      }
    }
  }
}
```

### 📄 PAGINATION

The query requests:

```text
50 entries per page
```

The engine checks:

```text
pageInfo.hasNextPage
```

to determine whether another page needs to be fetched.

Conceptually:

```text
Page 1
 ↓
hasNextPage?
 ↓ YES
Page 2
 ↓
hasNextPage?
 ↓ YES
Page 3
 ↓
...
 ↓ NO
Synchronization complete
```

### 📚 MEDIA DATA

The query retrieves:

```text
mediaId
progress
progressVolumes
score
status
```

and media metadata such as:

```text
title
type
episodes
chapters
volumes
season
seasonYear
coverImage
nextAiringEpisode
```

---

## 🧬 ASSIMILATION MUTATION

When Ghost Radar successfully resolves an unresolved media entry, the engine can submit the documented AniList mutation:

```graphql
mutation ($id: Int, $prog: Int, $score: Int) {
  SaveMediaListEntry(
    mediaId: $id
    progress: $prog
    scoreRaw: $score
  ) {
    id
  }
}
```

The mutation is used to restore the locally stored progress and score.

---

## 🔄 ANILIST SYNCHRONIZATION

The Master Sync compares two states:

```text
Live AniList State
        vs
Stored Local State
```

The difference is used to identify progress changes.

### 🧮 DELTA DETECTION

A conceptual synchronization calculation is:

```text
Current Progress
        -
Previous Progress
        =
Progress Delta
```

The delta becomes the basis for Gamerscore calculation.

### 🎮 ANIME DELTA

For anime:

```text
Episode Delta × 10 G
```

Example:

```text
Previous: 100 episodes
Current: 103 episodes

Delta = 3

3 × 10 G = 30 G
```

### 📚 MANGA DELTA

For manga:

```text
Chapter Delta × 2 G
```

Example:

```text
Previous: 50 chapters
Current: 56 chapters

Delta = 6

6 × 2 G = 12 G
```

### 🏁 COMPLETION DETECTION

When the engine recognizes that a series has been completely consumed, the completionist bonus can be applied:

```text
+100 G
```

---

## 📺 AIRING RADAR ARCHITECTURE

Airing Radar reads:

```text
nextAiringEpisode
```

from the AniList media payload.

The relevant values include:

```text
airingAt
episode
```

The engine compares the airing timestamp against the current UTC time.

### ⏱️ AIRING TIME CALCULATION

Conceptually:

```text
airingAt
-
current_time
=
remaining_seconds
```

The remaining value is compared against the configured thresholds.

### 🕒 THREE-HOUR THRESHOLD

Configured threshold:

```text
10,800 seconds
```

Equivalent to:

```text
3 hours
```

### 🚨 ONE-HOUR THRESHOLD

Configured threshold:

```text
3,600 seconds
```

Equivalent to:

```text
1 hour
```

### 🗂️ AIRING STATE

The system uses:

```text
db_airing.json
```

as an event state machine.

This prevents the engine from repeatedly sending the same warning every time it runs.

---

## 👻 GHOST RADAR ARCHITECTURE

Ghost Radar begins with local MAL XML ingestion.

The documented Python implementation uses:

```python
xml.etree.ElementTree
```

to parse the XML structure.

### 📥 MAL DATA INGESTION

The radar reads:

```text
mal_export.xml
mal_anime.xml
```

and extracts relevant media information.

The resulting records are normalized before comparison.

### 🔡 TITLE NORMALIZATION

The matching process converts titles into a lowercase representation.

Conceptually:

```text
Original:
One Piece

Normalized:
one piece
```

The same normalization is applied to the known AniList title pool.

### 🌐 TITLE MATCHING POOL

The known title pool is built from:

```text
AniList Romaji Title
AniList English Title
```

This provides multiple ways for a MAL title to match an AniList media entry.

### 👻 UNRESOLVED ENTRY FLOW

```text
MAL Export
    ↓
Title Normalization
    ↓
Known AniList Pool
    ↓
Match?
    │
    ├── YES → Normal processing
    │
    └── NO → Ghost Vault
```

---

## 🛡️ API RESILIENCE

Network requests are routed through the retry layer.

The documented helper is:

```python
fetch_with_armor(...)
```

Its purpose is to reduce failures caused by temporary API errors.

### 🔁 RETRY MODEL

Documented retry sequence:

```text
Attempt 1
Failure
Sleep 3s

Attempt 2
Failure
Sleep 6s

Attempt 3
```

### ⏳ GHOST RADAR THROTTLE

Ghost searches use a deliberate delay:

```python
time.sleep(1.5)
```

This reduces the rate at which repeated AniList searches are made.

---

## 🧹 AUTOMATIC STATE MAINTENANCE

Maximum Overdrive maintains more than media progress.

It also maintains operational state.

The engine remembers:

```text
Synchronization state
Achievement state
Airing state
Ghost state
Discord message state
```

This turns the repository into a persistent memory layer.

### 🧠 STATE MACHINE CONCEPT

```text
SYNC STATE
Previous progress → Current progress

ACHIEVEMENT STATE
Weekly score → Lifetime score

AIRING STATE
No alert → 3h alert → 1h alert

GHOST STATE
Unresolved → Searching → Assimilated

MESSAGE STATE
Created → Stored → Expired → Deleted
```

---

## 💻 CODEBASE COMPONENTS

The documented codebase is organized around several major functions.

### `fetch_with_armor()`

```python
fetch_with_armor(url, payload, headers, retries)
```

Responsible for resilient HTTP requests.

Responsibilities include:

- Sending API requests.
- Detecting temporary failures.
- Retrying requests.
- Waiting between attempts.

### `send_discord_alert()`

```python
send_discord_alert(...)
```

Responsible for Discord webhook payload generation.

The function can handle:

- Dynamic colors.
- Custom thumbnails.
- Username overrides.
- Author blocks.
- Gamerscore presentation.
- Log webhook handling.

When routed to the log webhook, the engine can capture the Discord message ID for future cleanup.

### `manage_achievements_and_weekly()`

```python
manage_achievements_and_weekly(points_earned)
```

Responsible for the RPG system.

The function handles:

- Progress-derived points.
- Weekly Gamerscore.
- Lifetime Gamerscore.
- Calendar-week tracking.
- Weekly rollover.
- Achievement thresholds.

The documented week calculation uses:

```python
datetime.now(timezone.utc).isocalendar()[1]
```

### `process_airing_countdowns()`

```python
process_airing_countdowns(inventory)
```

Responsible for airing alerts.

The function:

1. Scans inventory.
2. Looks for `nextAiringEpisode`.
3. Calculates remaining time.
4. Checks the three-hour threshold.
5. Checks the one-hour threshold.
6. Reads/writes airing state.
7. Prevents duplicate alerts.

### `sweep_mal_xml()`

```python
sweep_mal_xml(known_titles_pool)
```

Responsible for local MAL ingestion.

The function uses XML parsing to identify media entries that are not currently represented in the known AniList title pool.

### `execute_master_sync()`

```python
execute_master_sync(inventory)
```

Acts as the orchestration layer.

It coordinates:

```text
AniList inventory
↓
State comparison
↓
Gamerscore
↓
Chameleon UI
↓
Discord embeds
↓
Favorites
↓
Airing checks
↓
Ghost Radar
↓
State persistence
```

This function effectively acts as the conductor for the engine.

---

## 📊 SYSTEM METRICS

The current project documentation describes the following operational targets.

### DATABASE SIZE

The flat-file architecture is documented as tested for approximately:

```text
10,000 tracked media entries
```

The intended use case is therefore a large personal media library without requiring a traditional SQL server.

### EXECUTION TIME

The engine documentation states that a full sweep of an approximately:

```text
850+ item database
```

is optimized to complete in under:

```text
3 minutes
```

including Ghost Radar search throttling.

Actual runtime can vary based on network performance, API response times, and the number of entries processed.

### GITHUB ACTIONS USAGE

The current schedule executes:

```text
16 times per day
```

The project documentation estimates approximately:

```text
48 minutes/day
```

of compute time.

This corresponds to approximately:

```text
1,440 minutes/month
```

under the documented runtime assumptions.

---

## ⚠️ LIMITATIONS

Maximum Overdrive is designed around a lightweight architecture.

That architecture comes with trade-offs.

### JSON IS NOT A RELATIONAL DATABASE

The project intentionally avoids SQL.

Advantages include:

```text
Simple deployment
No database server
Easy backup
Human-readable state
Git history
```

The trade-off is that very large or highly concurrent datasets are not the primary target.

### GITHUB ACTIONS IS NOT A PERMANENT SERVER

The engine executes only when the workflow runs.

There is no continuously running process.

Therefore:

```text
No workflow execution
=
No engine execution
```

Manual triggering is available through:

```text
workflow_dispatch
```

### EXTERNAL API DEPENDENCY

The system depends on AniList for live GraphQL information.

Temporary API problems can therefore affect execution.

Titanium Armor provides retry handling, but it cannot eliminate external service outages.

### DISCORD WEBHOOK DEPENDENCY

Discord notification functionality depends on valid webhook endpoints.

A deleted or invalid webhook can prevent the associated channel from receiving messages.

### MAL EXPORT DEPENDENCY

Ghost Radar requires correctly named MAL XML files:

```text
mal_export.xml
mal_anime.xml
```

Invalid, missing, or outdated exports can reduce Ghost Radar accuracy.

---

## 🔐 SECURITY

The repository handles credentials and potentially private media-tracking data.

Treat the repository as private.

### NEVER COMMIT TOKENS

Do not place your AniList token inside:

```text
anilist_engine.py
```

Use:

```text
GitHub Actions Secrets
```

instead.

### NEVER COMMIT WEBHOOK URLS

Discord webhook URLs should be treated as credentials.

Do not publish them in:

```text
README.md
source code
screenshots
issues
public logs
```

### MAL EXPORTS MAY CONTAIN PERSONAL DATA

MAL XML files represent personal tracking information.

They should therefore be treated as private data.

If the repository is public, carefully review the export contents before committing it.

### 🧯 SECRET LEAK RESPONSE

If a token or webhook is accidentally exposed:

```text
1. Revoke or rotate the credential.
2. Remove it from the repository.
3. Replace the GitHub Secret.
4. Check commit history.
5. Verify that the old credential no longer works.
```

Deleting a secret from the latest commit does not necessarily remove it from Git history.

---

## 🛠️ TROUBLESHOOTING

### GitHub Action Does Not Start

Check:

```text
GitHub Actions enabled
Workflow file path correct
Workflow YAML valid
Repository permissions available
Schedule configured correctly
```

The workflow should exist at:

```text
.github/workflows/sync_engine.yml
```

### ❌ ACTION FAILS DURING PYTHON SETUP

Check:

```text
Python version
setup-python action
Workflow YAML indentation
Runner availability
```

The current workflow targets:

```text
Python 3.10
```

### ❌ ANILIST REQUEST FAILS

Check:

```text
ANILIST_TARGET_TOKEN
Network connectivity
AniList API availability
GraphQL payload
Request rate
```

Titanium Armor will retry supported temporary failures.

Persistent authentication or request errors require configuration correction.

### ❌ DISCORD MESSAGE DOES NOT APPEAR

Check:

```text
Correct webhook secret
Webhook still exists
Correct Discord channel
GitHub Actions environment variables
Engine logs
```

A webhook failure in one channel should be investigated separately from the rest of the pipeline.

### ❌ AIRING ALERT DOES NOT APPEAR

Check:

```text
nextAiringEpisode exists
Airing timestamp is valid
Current time is calculated correctly
db_airing.json state
Airing webhook
```

### ❌ GHOST ENTRY DOES NOT ASSIMILATE

Check:

```text
db_ghosts.json
MAL XML title
AniList title availability
Romaji title
English title
AniList authentication
GraphQL mutation
```

A ghost remains in the vault until the engine can resolve it.

### ❌ JSON STATE IS NOT UPDATED

Check:

```text
Workflow contents permission
GitHub Actions write permission
git add *.json
git commit
git push
```

The workflow requires:

```yaml
permissions:
  contents: write
```

---

## ✅ OPERATIONAL CHECKLIST

Before running the system:

```text
[ ] anilist_engine.py exists
[ ] Python 3.10 configured
[ ] db_sync.json exists
[ ] db_achievements.json exists
[ ] db_airing.json exists
[ ] db_ghosts.json exists
[ ] db_messages.json exists
[ ] mal_export.xml exists
[ ] mal_anime.xml exists
[ ] Discord webhooks created
[ ] AniList token configured
[ ] GitHub secrets configured
[ ] GitHub Actions enabled
[ ] contents: write permission enabled
```

### FIRST RUN CHECKLIST

After configuration:

```text
[ ] Trigger workflow_dispatch
[ ] Confirm repository checkout
[ ] Confirm Python setup
[ ] Confirm dependencies
[ ] Confirm environment variables
[ ] Confirm AniList GraphQL request
[ ] Confirm Discord output
[ ] Confirm JSON state changes
[ ] Confirm Git commit
[ ] Confirm Git push
```

### POST-RUN VERIFICATION

After the workflow finishes:

Check the GitHub Actions logs.

Then inspect:

```text
db_sync.json
db_achievements.json
db_airing.json
db_ghosts.json
db_messages.json
```

Finally verify the expected Discord channels.

---

## 🎯 DESIGN PRINCIPLES

Maximum Overdrive follows several practical design principles.

### 1. STATE SHOULD PERSIST

The engine should remember previous executions.

This is why JSON state is committed back into the repository.

### 2. AUTOMATION SHOULD BE IDEMPOTENT

Repeated executions should not repeatedly perform the same alert action when the state already indicates that the action occurred.

This principle is especially important for:

```text
Airing Radar
Discord logs
Gamerscore calculations
Ghost processing
```

### 3. FAILURES SHOULD BE RECOVERABLE

Temporary network failures should trigger retries rather than immediately terminating the whole process.

### 4. DATA SHOULD REMAIN HUMAN-READABLE

JSON was selected because the memory layer can be inspected without specialized database software.

### 5. DISCORD SHOULD BE THE VISUAL COMMAND CENTER

The repository contains the machine state.

Discord presents the machine state in a human-friendly way.

---

## 🧭 OPERATIONAL PHILOSOPHY

Maximum Overdrive can be understood as a personal automation loop:

```text
TRACK
↓
COMPARE
↓
CALCULATE
↓
ALERT
↓
REMEMBER
↓
REPEAT
```

The system does not simply synchronize data.

It interprets changes.

---

## ⚡ MAXIMUM OVERDRIVE LOOP

```text
       ┌──────────────┐
       │    AniList   │
       └──────┬───────┘
              │
              ▼
       ┌──────────────┐
       │     Sync     │
       └──────┬───────┘
              │
              ▼
       ┌──────────────┐
       │    Detect    │
       │    Delta     │
       └──────┬───────┘
              │
      ┌───────┼────────┐
      ▼       ▼        ▼
    Score   Airing   Ghost
      │       │        │
      └───────┼────────┘
              ▼
       ┌──────────────┐
       │   Discord    │
       └──────┬───────┘
              │
              ▼
       ┌──────────────┐
       │ JSON Memory  │
       └──────┬───────┘
              │
              ▼
       ┌──────────────┐
       │ GitHub Push  │
       └──────┬───────┘
              │
              └──────► NEXT RUN
```

---

## 🏆 GAMERSCORE EXAMPLES

### Example 1 — Anime Progress

```text
Previous Progress: 100
Current Progress: 105
```

Progress delta:

```text
5 episodes
```

Gamerscore:

```text
5 × 10 = 50 G
```

### Example 2 — Manga Progress

```text
Previous Progress: 80
Current Progress: 95
```

Progress delta:

```text
15 chapters
```

Gamerscore:

```text
15 × 2 = 30 G
```

### Example 3 — Completion

A series becomes fully completed.

Completion bonus:

```text
+100 G
```

The completion reward is independent of ordinary episode/chapter scoring.

### 📊 SCORE PIPELINE

```text
Media Change
     ↓
Progress Delta
     ↓
Media Type
     ↓
Score Multiplier
     ↓
Gamerscore Earned
     ↓
Weekly G
     ↓
Lifetime G
```

---

## 📺 AIRING EXAMPLE

Suppose an episode is scheduled three hours in the future.

The engine calculates:

```text
Remaining Time ≈ 10,800 seconds
```

The state becomes:

```text
3h
```

The Discord notification:

```text
🕒 3-HOUR WARNING
```

is generated.

Later, when the remaining time reaches the one-hour threshold, the engine transitions to:

```text
1h
```

and sends:

```text
🚨 FINAL 1-HOUR WARNING
```

---

## 👻 GHOST EXAMPLE

Suppose MAL contains:

```text
Obscure Light Novel Name
```

but the corresponding AniList entry is unavailable.

The engine stores:

```json
{
  "Obscure Light Novel Name": {
    "progress": 45,
    "score": 8,
    "type": "MANGA"
  }
}
```

A future execution searches AniList again.

Once the media becomes available, the engine can restore the saved state through the documented mutation.

---

## 🧹 PURGE EXAMPLE

A log message is generated at:

```text
T0
```

The timestamp is stored.

After:

```text
172,800 seconds
```

the message qualifies for cleanup.

The next maintenance cycle can send the corresponding Discord delete request.

---

## 🧩 COMPONENT RELATIONSHIPS

```text
anilist_engine.py
│
├── fetch_with_armor()
│
├── execute_master_sync()
│   │
│   ├── Gamerscore
│   │
│   ├── Chameleon UI
│   │
│   ├── Favorites
│   │
│   ├── Airing Radar
│   │
│   └── Discord
│
├── process_airing_countdowns()
│
├── sweep_mal_xml()
│
├── manage_achievements_and_weekly()
│
└── send_discord_alert()
```

### 🗃️ STATE RELATIONSHIPS

```text
db_sync.json
    │
    └── Detect progress changes

db_achievements.json
    │
    └── Track Gamerscore

db_airing.json
    │
    └── Prevent duplicate warnings

db_ghosts.json
    │
    └── Preserve unresolved MAL entries

db_messages.json
    │
    └── Track Discord cleanup targets
```

### 📡 WEBHOOK RELATIONSHIPS

```text
Master Sync
    ├── Anime Webhook
    ├── Manga Webhook
    ├── Favorites Webhook
    └── Log Webhook

Achievement System
    └── Achievement Webhook

Airing System
    └── Airing Webhook

Ghost Radar
    └── Ghost Webhook
```

---

## 🔬 DEBUGGING STRATEGY

When troubleshooting the engine, identify the failing subsystem first.

```text
AniList failure
    → Authentication / GraphQL / API

Discord failure
    → Webhook / payload / channel

Airing failure
    → nextAiringEpisode / time / state

Ghost failure
    → XML / title matching / mutation

Gamerscore failure
    → previous state / delta / week

Persistence failure
    → JSON / Git / permissions
```

This makes debugging significantly easier than treating the application as one large undifferentiated script.

---

## 🧪 VALIDATION STRATEGY

The most important validation points are:

```text
AniList fetch succeeds
        ↓
Inventory populated
        ↓
State loaded
        ↓
Delta calculated
        ↓
Discord payload generated
        ↓
Airing state processed
        ↓
Ghost state processed
        ↓
JSON saved
        ↓
Git state persisted
```

Each layer depends on the previous one.

---

## 🧠 MEMORY MODEL

Maximum Overdrive effectively has two levels of memory.

### Live Memory

Data retrieved from AniList during the current execution.

### Persistent Memory

Data stored inside the JSON vaults and committed back to GitHub.

The combination provides:

```text
Live Data
+
Historical State
=
Automated Decision Making
```

---

## 🛰️ WHY GITHUB ACTIONS

The architecture uses GitHub Actions because the engine does not require a continuously running local process.

The scheduler can:

```text
Start environment
↓
Run Python
↓
Call APIs
↓
Process data
↓
Save state
↓
Exit
```

This makes the system suitable for automated periodic execution.

---

## 🪶 WHY JSON

JSON keeps the deployment lightweight.

Benefits include:

```text
Easy inspection
Easy backup
Git-friendly
Human-readable
No database server
Simple Python integration
```

The system therefore remains portable.

---

## 🧱 WHY MODULAR SUBSYSTEMS

Instead of treating the project as one enormous synchronization operation, Maximum Overdrive divides responsibilities.

```text
Synchronization
Gamerscore
Airing
Ghosts
Notifications
Persistence
Cleanup
```

Each layer can be reasoned about independently.

---

## 🎨 WHY DYNAMIC COLORS

AniList already exposes cover artwork colors.

Maximum Overdrive uses that information to create a Discord presentation that reflects the source artwork.

This means the interface naturally changes with the media.

---

## 📚 WHY MULTIPLE DISCORD CHANNELS

Different notification classes have different urgency.

For example:

```text
Anime update
=
Routine

Achievement
=
Milestone

Airing warning
=
Time-sensitive

Ghost assimilation
=
Recovery event

Log
=
Operational
```

Separating them keeps the command center organized.

---

## 🗺️ FUTURE EXPANSION

The architecture leaves room for future expansion.

Possible future directions include:

```text
Historical Gamerscore analytics
Gamerscore leaderboards
More detailed completion statistics
Expanded priority-franchise logic
Additional notification categories
Web dashboard
Visual progress charts
Database-backed storage option
Improved title matching
Extended recovery logic
More detailed execution reports
```

These are conceptual expansion paths rather than guarantees of currently implemented functionality.

---

## 🧪 DEVELOPMENT NOTES

When modifying the engine, maintain compatibility with the existing state files whenever possible.

State migration is especially important for:

```text
db_sync.json
db_achievements.json
db_airing.json
db_ghosts.json
db_messages.json
```

Changing the schema without migration logic can cause the engine to lose historical state or interpret it incorrectly.

### ⚠️ STATE SCHEMA WARNING

Before changing a JSON structure:

```text
1. Back up the existing JSON file.
2. Document the old structure.
3. Update the engine.
4. Test migration.
5. Verify the resulting state.
6. Commit only after validation.
```

The JSON files are not merely configuration.

They are the engine's persistent memory.

---

## 🛠️ RECOMMENDED DEVELOPMENT WORKFLOW

```text
Modify code
     ↓
Run local validation
     ↓
Inspect JSON behavior
     ↓
Test Discord payloads
     ↓
Test workflow manually
     ↓
Inspect GitHub Actions logs
     ↓
Verify persistent state
     ↓
Deploy scheduled execution
```

---

## 🧯 RECOVERY PROCEDURE

If the engine's state becomes corrupted:

```text
1. Stop scheduled executions.
2. Back up current JSON files.
3. Identify the corrupted state file.
4. Restore the last known-good version.
5. Run a manual workflow.
6. Verify state reconciliation.
7. Re-enable scheduled execution.
```

Git history provides an additional historical record for committed JSON state.

---

## 📈 PERFORMANCE MODEL

The major contributors to runtime are expected to include:

```text
AniList API latency
Number of media pages
Ghost Radar searches
Discord webhook responses
GitHub repository operations
```

The documented configuration is optimized for a personal library containing hundreds to thousands of entries.

---

## 🧮 SCALING CONSIDERATIONS

As the media library increases:

```text
More entries
     ↓
More pagination
     ↓
More comparison work
     ↓
Potentially more Discord events
     ↓
More JSON state
```

Ghost Radar can become one of the more noticeable contributors to runtime because it intentionally throttles searches.

---

## 🕹️ COMPLETIONIST DESIGN

The Gamerscore system intentionally rewards both:

```text
Ongoing consumption
```

and:

```text
Full completion
```

This means the project does not exclusively reward high-volume activity.

It also rewards finishing series.

---

## 🏅 RPG INTERPRETATION

The media library effectively becomes a progression system.

```text
Watch
↓
Earn G
↓
Complete Series
↓
Earn Bonus
↓
Reach Weekly Milestone
↓
Bank Lifetime Score
↓
Reach Prestige Threshold
```

This transforms ordinary tracking into a persistent progression loop.

---

## 🧠 COMMAND CENTER MENTAL MODEL

Think of the project as a private Otaku operations center.

```text
AniList
   =
Inventory

JSON
   =
Memory

Python
   =
Brain

GitHub Actions
   =
Clock

Discord
   =
Command Center

Gamerscore
   =
Progression System

Ghost Radar
   =
Recovery Unit

Airing Radar
   =
Early Warning System

Auto-Purge
   =
Maintenance Unit
```

---

## 🧭 SYSTEM STATUS MODEL

At any point, the engine may be processing one or more of these states:

```text
SYNCING
TRACKING
CALCULATING
ALERTING
SEARCHING
ASSIMILATING
PURGING
PERSISTING
```

The system returns to an idle state after the GitHub Actions execution completes.

---

## 📦 BACKUP STRATEGY

The most important persistent files are:

```text
db_sync.json
db_achievements.json
db_airing.json
db_ghosts.json
db_messages.json
```

Backups of these files preserve the engine's memory.

The MAL XML files should also be retained when they are required for Ghost Radar recovery.

---

## 🔒 PRIVATE REPOSITORY RECOMMENDATION

Because the project may contain:

```text
AniList authentication
Discord webhook endpoints
MAL tracking exports
Personal media history
```

a private repository is the safest deployment model for the documented configuration.

---

## ✅ DEPLOYMENT COMPLETION TEST

The deployment can be considered operational when all of the following succeed:

```text
✓ GitHub Actions launches
✓ Python environment initializes
✓ Dependencies install
✓ Secrets load
✓ AniList GraphQL succeeds
✓ Media inventory is retrieved
✓ Discord webhook works
✓ Gamerscore state updates
✓ Airing Radar evaluates entries
✓ Ghost Radar parses XML
✓ JSON state is written
✓ Git commit succeeds
✓ Git push succeeds
```

---

## 🧪 MANUAL EXECUTION

The workflow includes:

```yaml
workflow_dispatch:
```

This allows a manual run from GitHub Actions.

Manual execution is useful for:

```text
Testing
Debugging
State recovery
Configuration verification
Post-update validation
```

---

## 📜 LOGGING PHILOSOPHY

The project separates operational telemetry from user-facing notifications.

Routine state messages can go into:

```text
#anilist-log
```

while meaningful events can go into their dedicated channels.

This provides a cleaner user experience.

---

## 🧹 LOG RETENTION

The documented retention period is:

```text
48 hours
```

The purpose is to keep the operational channel from growing indefinitely.

---

## 🛰️ AUTOMATION PHILOSOPHY

The ideal execution requires no manual interaction.

Once configuration is complete:

```text
GitHub Actions
    ↓
Engine
    ↓
AniList
    ↓
Discord
    ↓
JSON
    ↓
GitHub
```

The following execution begins with the previous execution's state already available.

---

## 🏗️ ARCHITECTURAL SUMMARY

Maximum Overdrive can be summarized as five layers:

```text
LAYER 1
External Data
AniList + MAL

LAYER 2
Processing
Python Engine

LAYER 3
State
JSON Vaults

LAYER 4
Presentation
Discord Webhooks

LAYER 5
Automation
GitHub Actions
```

Together they form the complete personal media automation stack.

---

## 📊 FEATURE MATRIX

| Feature | Purpose | State |
|---|---|---|
| AniList GraphQL | Media synchronization | ✅ |
| Anime Progress | Progress tracking | ✅ |
| Manga Progress | Progress tracking | ✅ |
| Chameleon UI | Artwork-based embed color | ✅ |
| Gamerscore | RPG scoring | ✅ |
| Completion Bonus | Series completion reward | ✅ |
| Weekly Wipe | Weekly score rollover | ✅ |
| Milestones | Weekly achievement thresholds | ✅ |
| Prestige Override | Lifetime milestone identity | ✅ |
| Airing Radar | Upcoming episode monitoring | ✅ |
| 3-Hour Alert | Early warning | ✅ |
| 1-Hour Alert | Final warning | ✅ |
| Dynamic Timestamps | Discord countdown display | ✅ |
| Ghost Radar | MAL anomaly recovery | ✅ |
| Ghost Vault | Persistent unresolved entries | ✅ |
| Ghost Assimilation | Automatic AniList restoration | ✅ |
| API Armor | Retry / backoff | ✅ |
| Discord Pipeline | Multi-channel routing | ✅ |
| Auto-Purge | 48-hour cleanup | ✅ |
| JSON Persistence | Local state memory | ✅ |
| GitHub Actions | Scheduled execution | ✅ |

---

## 🧩 FEATURE RESPONSIBILITY MAP

| Component | Input | Output |
|---|---|---|
| Master Sync | AniList GraphQL | Media inventory |
| Gamerscore | Progress delta | G points |
| Airing Radar | Airing timestamp | Discord warning |
| Ghost Radar | MAL XML | Ghost records |
| Assimilation | Ghost record + AniList match | AniList update |
| Discord Layer | Event data | Webhook message |
| Auto-Purge | Message state | Delete request |
| JSON Vault | Runtime state | Persistent state |
| GitHub Actions | Schedule | Engine execution |

---

## 🏁 FINAL SYSTEM LOOP

```text
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
          ┌────────┼─────────┐
          │        │         │
          ▼        ▼         ▼
       Gamerscore Airing   Ghosts
          │        │         │
          └────────┼─────────┘
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
```

---

## 🏆 PROJECT STATUS

**AniList Maximum Overdrive 4.0.0 — Apex Build**

The documented architecture currently includes:

```text
✓ AniList synchronization
✓ GraphQL data retrieval
✓ Gamerscore tracking
✓ Weekly Gamerscore rollover
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
```

---

## 🧠 THE MAXIMUM OVERDRIVE MANIFESTO

This project is not designed to be another passive tracking script.

It is designed around the idea that personal media data can become an active system.

```text
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
Alerts

Alerts
↓
Discord

Discord
↓
Command Center
```

The end result is a personal media ecosystem that watches the tracker alongside you.

---

## 🧭 THE BROAD OBJECTIVE

The long-term architectural direction is to make the system increasingly autonomous while maintaining a lightweight deployment model.

The fundamental constraints remain:

```text
Minimal infrastructure
Persistent state
Automated execution
Human-readable memory
Discord visibility
AniList integration
MAL recovery
```

---

## 🗺️ FUTURE EXPANSION IDEAS

The architecture could later be extended with additional components such as:

```text
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
```

These are architectural possibilities and should be implemented only when they fit the project's goals.

---

## 📚 DOCUMENTATION PRINCIPLE

The README intentionally documents not only what the system does, but also how the systems relate to each other.

The goal is for a future maintainer to understand:

```text
What runs
Why it runs
Where the data comes from
Where state is stored
Where alerts go
How state persists
How failures are handled
```

---

## 🧪 MAINTENANCE PRINCIPLE

When modifying Maximum Overdrive:

```text
Preserve state
Preserve secrets
Preserve webhook routing
Preserve workflow permissions
Preserve JSON compatibility
Test API requests
Test Discord output
Test state persistence
```

A small change in one subsystem can affect another because the engine operates as a coordinated pipeline.

---

## 🔥 MAXIMUM OVERDRIVE CHECKPOINT

Before considering a major version complete:

```text
[ ] Master Sync verified
[ ] Gamerscore verified
[ ] Weekly rollover verified
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
```

---

## 🧬 VERSION IDENTITY

Current release:

```text
4.0.0
```

Codename:

```text
APEX BUILD
```

Project identity:

```text
ANILIST MAXIMUM OVERDRIVE
```

Author identity:

```text
OREWATOKYO
```

---

## 🛸 FINAL STATUS

```text
╔══════════════════════════════════════════╗
║      ANILIST MAXIMUM OVERDRIVE           ║
║                                          ║
║              APEX BUILD 4.0.0            ║
║                                          ║
║       SYNC ................. ONLINE      ║
║       GAMERSCORE ........... ONLINE      ║
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
```

---

## 👑 OREWATOKYO

Built for the completionist.

Built for the obsessive tracker.

Built for the person who doesn't just want a list.

Built for the person who wants the list to become a system.

**Track everything.**

**Remember everything.**

**Automate everything.**

**Maximum Overdrive. ⚡**

---

## 📜 CREDITS

**Author:** Orewatokyo

**Primary Technologies:**

```text
Python 3.10
AniList GraphQL
GitHub Actions
Discord Webhooks
JSON
MyAnimeList XML exports
```

---

## ⭐ PROJECT TAGLINE

> **From passive tracking to an autonomous Otaku Command Center.**

---

# ⚡ END OF SYSTEM DOCUMENT

```text
Maximum Overdrive
Apex Build 4.0.0

System Document Compiled.
Automation Layer Active.
Persistent Memory Active.
Command Center Active.

END.
```
