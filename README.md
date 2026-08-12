# ⚡ ANILIST MAXIMUM OVERDRIVE ⚡

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
                    │     GitHub Actions      │
                    │   Scheduled Execution   │
                    └────────────────────────┘

```
🔄 SYSTEM DATA FLOWThe engine follows a synchronized operational sequence.PlaintextGitHub Actions starts
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


🧩 CORE SYSTEMSMaximum Overdrive is divided into seven major operational systems.

| System | Purpose |
|---|---|
| Master Sync | Synchronizes AniList media state |
| Gamerscore | Converts media activity into RPG-style points |
| Performance Vault | Tracks daily/weekly/monthly/yearly time consumption |
| Airing Radar | Tracks upcoming episode releases |
| Ghost Radar | Resolves missing MAL entries |
| Titanium Armor | Handles temporary API/network failures |
| Auto-Purge | Removes old Discord engine logs |


Each subsystem has a focused responsibility.

The systems are designed to operate together without requiring a separate database server.

1. HIGH-DENSITY MASTER SYNC
The Master Sync is the core synchronization layer.

It executes a paginated GraphQL sweep against the AniList media-list API.

The engine retrieves the tracked inventory and extracts information required by the downstream systems.

The synchronization layer is responsible for:

The synchronization layer is responsible for:

- Anime progress.
- Manga progress.
- Episode counts.
- Chapter counts.
- Volume counts.
- Media status.
- Exact media runtime (duration).
- Romaji titles.
- English titles.
- Season information.
- Season year.
- Cover artwork.
- Cover artwork color.
- Upcoming airing information.


The inventory is then compared against the locally stored synchronization matrix.

🎨 CHAMELEON UI
The Chameleon UI uses the color returned by AniList's media cover information.

The engine reads:

Plaintext
coverImage.color
The returned color is converted into the format required by Discord embeds.

The Discord message can therefore visually match the artwork associated with the media entry.

This provides dynamic presentation without requiring manually selected colors.

2. RPG GAMERSCORE SYSTEM

3. 
Maximum Overdrive includes a custom RPG-style scoring layer.

Every tracked action can contribute Gamerscore.

The current scoring model is:

| Activity | Reward |
|---|---:|
| Anime episode watched | +10 G |
| Manga chapter read | +2 G |
| Fully completed series | +100 G |

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

👑 PRESTIGE OVERRIDE
The project includes a prestige system tied to lifetime Gamerscore.

The configured threshold is:

Plaintext
10,000 Lifetime G

After crossing the threshold, the webhook identity is configured to use the:

Plaintext
Orewatokyo
identity for future alerts.

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

completionist reward.

