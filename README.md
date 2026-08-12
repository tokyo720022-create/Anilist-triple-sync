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

SystemPurposeMaster SyncSynchronizes AniList media stateGamerscoreConverts media activity into RPG-style pointsPerformance VaultTracks daily/weekly/monthly/yearly time consumptionAiring RadarTracks upcoming episode releasesGhost RadarResolves missing MAL entriesTitanium ArmorHandles temporary API/network failuresAuto-PurgeRemoves old Discord engine logsEach subsystem has a focused responsibility.The systems are designed to operate together without requiring a separate database server.
