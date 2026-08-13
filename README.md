# ⚡ ANILIST MAXIMUM OVERDRIVE SYNC: V2 ⚡

<!-- TELEMETRY_START -->
<!-- Telemetry Hub will inject live CLI data here -->
<!-- TELEMETRY_END -->
---

```text
███╗   ███╗ █████╗ ██╗  ██╗██╗███╗   ███╗██╗   ██╗███╗   ███╗
████╗ ████║██╔══██╗╚██╗██╔╝██║████╗ ████║██║   ██║████╗ ████║
██╔████╔██║███████║ ╚███╔╝ ██║██╔████╔██║██║   ██║██╔████╔██║
██║╚██╔╝██║██╔══██║ ██╔██╗ ██║██║╚██╔╝██║██║   ██║██║╚██╔╝██║
██║ ╚═╝ ██║██║  ██║██╔╝ ██╗██║██║ ╚═╝ ██║╚██████╔╝██║ ╚═╝ ██║
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝     ╚═╝
      V 2   T E L E M E T R Y   &   A N A L Y T I C S   H U B
```

# ⚡ V2 PROJECT IDENTITY

**Project:** AniList Maximum Overdrive Sync  
**Version:** 2.0 — Telemetry & Analytics Hub  
**Codename:** Maximum Overdrive V2  
**Architecture:** Python + AniList GraphQL + GitHub Actions + JSON Vaults  
**Primary Interface:** Discord  
**Direct Alert Layer:** Telegram  
**Archive Layer:** Zulip  
**Source Reconciliation:** MyAnimeList XML  
**State Persistence:** Git-backed JSON  
**Performance Surface:** Discord Hologram + GitHub README

Welcome to **AniList Maximum Overdrive Sync V2**.

This is not a conventional webhook script.

It is a serverless, state-aware, automated personal media command center designed for
people who want to track anime and manga with completionist-level precision.

V2 is built around one central idea:

> **One mathematical event should produce one consistent set of statistics everywhere.**

When the engine detects:

```text
+1 anime episode
```

or:

```text
+1 manga chapter
```

the event can propagate through the same canonical calculation pipeline.

```text
AniList
   │
   ▼
Delta Detection
   │
   ├───────────────┬────────────────┬─────────────────┐
   ▼               ▼                ▼                 ▼
Gamerscore     Performance       Discord          Archive
   │               │                │                 │
   ▼               ▼                ▼                 ▼
Lifetime/     Daily Minutes    Hologram /        Zulip / JSON
Weekly G      Daily Eps/Chp    Progress Feed      Vaults
   │               │
   └───────┬───────┘
           ▼
      README Telemetry
```

No fragmented calculations.

No separate number for Discord and another number for GitHub.

No unnecessary database server.

No permanent cloud machine.

Just a scheduled engine, persistent state, and a growing history of what was consumed.

---

# 📑 TABLE OF CONTENTS

1. [Core System Philosophy](#1-core-system-philosophy)
2. [V2 Telemetry Hub](#2-v2-telemetry-hub)
3. [System Architecture](#3-system-architecture)
4. [State Machine](#4-state-machine)
5. [Master AniList Sync](#5-master-anilist-sync)
6. [Anime Progress Engine](#6-anime-progress-engine)
7. [Manga Progress Engine](#7-manga-progress-engine)
8. [Live Game Core](#8-live-game-core)
9. [Gamerscore Rules](#9-gamerscore-rules)
10. [Achievement System](#10-achievement-system)
11. [Weekly Grind](#11-weekly-grind)
12. [Live Performance Core](#12-live-performance-core)
13. [Anime Time Calculation](#13-anime-time-calculation)
14. [Manga Time Calculation](#14-manga-time-calculation)
15. [Performance Vault](#15-performance-vault)
16. [README Telemetry](#16-readme-telemetry)
17. [Live Performance Hologram](#17-live-performance-hologram)
18. [Airing Intelligence Radar](#18-airing-intelligence-radar)
19. [MAL Ghost Radar](#19-mal-ghost-radar)
20. [Deep Void Protocol](#20-deep-void-protocol)
21. [Discord Command Center](#21-discord-command-center)
22. [Telegram Direct Alerts](#22-telegram-direct-alerts)
23. [Zulip Grand Archive](#23-zulip-grand-archive)
24. [JSON Memory Vaults](#24-json-memory-vaults)
25. [Repository Structure](#25-repository-structure)
26. [Deployment](#26-deployment)
27. [Secrets](#27-secrets)
28. [Zulip Configuration](#28-zulip-configuration)
29. [GitHub Actions](#29-github-actions)
30. [GraphQL Architecture](#30-graphql-architecture)
31. [API Resilience](#31-api-resilience)
32. [Diagnostics](#32-diagnostics)
33. [Troubleshooting](#33-troubleshooting)
34. [Data Safety](#34-data-safety)
35. [Backup and Recovery](#35-backup-and-recovery)
36. [Testing Strategy](#36-testing-strategy)
37. [Performance and Scaling](#37-performance-and-scaling)
38. [V2 Architecture Improvements](#38-v2-architecture-improvements)
39. [Future V3 Roadmap](#39-future-v3-roadmap)
40. [Maintenance](#40-maintenance)
41. [Release Strategy](#41-release-strategy)
42. [Operational Checklists](#42-operational-checklists)
43. [System Status](#43-system-status)
44. [Author](#44-author)
45. [Final Principle](#45-final-principle)

---

# 1. CORE SYSTEM PHILOSOPHY

> *"Systems should be judged based on fairness, structure, and pure logic."*

The standard media-tracking experience is passive.

You watch an episode.

You update a number.

The website stores the number.

Maximum Overdrive treats that action as an event.

The event can then drive:

- Gamerscore
- Performance statistics
- Notifications
- Historical records
- Achievement checks
- Repository telemetry
- Archive entries
- Airing intelligence
- Reconciliation workflows

The project follows a strict cause-and-effect philosophy.

```text
USER ACTION
    │
    ▼
ANIList CHANGE
    │
    ▼
STATE DELTA
    │
    ▼
CANONICAL EVENT
    │
    ├──► GAME CORE
    ├──► PERFORMANCE
    ├──► DISCORD
    ├──► TELEGRAM
    ├──► ZULIP
    ├──► ACHIEVEMENT
    └──► README
```

The purpose is not complexity for its own sake.

The purpose is consistency.

---

# 1.1 DATA SOVEREIGNTY

Maximum Overdrive is designed around user-controlled state.

Important tracking information is persisted into files owned by the repository rather than
being dependent on a single chat message or ephemeral execution.

The system therefore separates:

```text
Remote Source
      │
      ▼
Local State
      │
      ▼
Derived Statistics
      │
      ▼
Human Presentation
```

This makes the project more resilient to temporary service outages.

---

# 1.2 LOGICAL TIME PARSING

Anime time is not treated as a random hardcoded number.

The engine can retrieve episode duration from AniList.

The effective time model is:

```text
Listed Episode Duration
          │
          ▼
     - 2 minutes
          │
          ▼
Estimated Consumed Time
```

The two-minute deduction represents an approximate opening/ending allowance.

Manga uses a fixed analytical estimate:

```text
1 chapter = 5 minutes
```

These are statistics, not stopwatch measurements.

---

# 1.3 RPG GAMIFICATION

Tracking becomes a progression system.

The current V2 scoring rules are:

```text
Anime Episode    +10 G
Manga Chapter    +2 G
Completion       +100 G
```

The result is a personal RPG layer built on top of ordinary media consumption.

---

# 1.4 COMPLETIONIST DESIGN

The system is designed for users who care about:

```text
Progress
Consistency
Completion
History
Statistics
Milestones
```

The repository is therefore treated as more than code.

It is:

```text
ENGINE
+
MEMORY
+
ANALYTICS
+
DASHBOARD
+
ARCHIVE
```

---

# 1.5 NO-BLOAT PRINCIPLE

V2 intentionally continues the lightweight architecture.

No continuously running server is required.

No SQL server is required.

No external database service is required.

The system can operate through:

```text
GitHub Actions
+
Python
+
JSON
+
APIs
```

This keeps deployment straightforward.

---

# 2. THE V2 TELEMETRY HUB

The central V2 upgrade is the **Telemetry Hub**.

The engine does not calculate a daily number separately for every output.

Instead, it creates a canonical performance state.

That canonical state can then feed:

```text
Discord Hologram
Daily JSON
Weekly JSON
Monthly JSON
Yearly JSON
README badges
```

This prevents the classic problem:

```text
Discord says: 4 episodes
README says: 3 episodes
JSON says: 5 episodes
```

V2 wants:

```text
Canonical value: 4

Discord  → 4
README   → 4
JSON     → 4
```

---

# 2.1 SINGLE CALCULATION PRINCIPLE

The Telemetry Hub follows:

```text
ONE EVENT
   ↓
ONE CALCULATION
   ↓
MANY OUTPUTS
```

That is the core V2 architecture.

---

# 2.2 TELEMETRY OUTPUTS

A single progress event can update:

1. Lifetime Gamerscore.
2. Weekly Gamerscore.
3. Daily episode count.
4. Daily chapter count.
5. Estimated minutes.
6. Discord progress message.
7. Performance Hologram.
8. README telemetry.
9. Zulip archive.
10. Local JSON state.

---

# 2.3 WHY THIS MATTERS

If output calculations are duplicated, a bug can cause inconsistent numbers.

If calculations are centralized, every display has the same source.

This is one of the most important upgrades in V2.

---

# 2.4 TELEMETRY FLOW

```text
AniList
   │
   ▼
Delta
   │
   ▼
Event Object
   │
   ▼
Telemetry Processor
   │
   ├── Gamerscore
   ├── Episodes
   ├── Chapters
   ├── Minutes
   └── Completion
           │
           ▼
    Canonical Snapshot
           │
      ┌────┼────┬─────┐
      ▼    ▼    ▼     ▼
   Discord JSON README Zulip
```

---

# 3. SYSTEM ARCHITECTURE

The engine is divided into multiple cooperating subsystems.

```text
┌──────────────────────────────────────────┐
│                 AniList                  │
│             SOURCE OF TRUTH              │
└─────────────────────┬────────────────────┘
                      │
                      ▼
┌──────────────────────────────────────────┐
│            MASTER PYTHON ENGINE          │
│              V2 TELEMETRY HUB            │
└─────────────────────┬────────────────────┘
                      │
          ┌───────────┼────────────┐
          │           │            │
          ▼           ▼            ▼
       SYNC CORE   GAME CORE   PERFORMANCE
          │           │            │
          ▼           ▼            ▼
       db_sync     G-Score       Metrics
                      │            │
                      └────┬───────┘
                           ▼
                  ┌──────────────────┐
                  │ OUTPUT DISPATCH  │
                  └────────┬─────────┘
                           │
              ┌────────────┼────────────┐
              ▼            ▼            ▼
           Discord       Telegram     Zulip
              │
              ▼
      Performance Hologram
              │
              ▼
       GitHub README
```

---

# 3.1 ENGINE RESPONSIBILITIES

The engine is responsible for:

- Fetching AniList data.
- Normalizing media records.
- Comparing state.
- Creating progress deltas.
- Calculating scoring.
- Calculating performance.
- Checking airing information.
- Processing MAL ghosts.
- Processing Deep Void entries.
- Sending notifications.
- Saving state.
- Refreshing telemetry.
- Committing repository changes.

---

# 3.2 SEPARATION OF RESPONSIBILITIES

The following conceptual separation is preferred:

```text
AniList       = source
State files   = memory
Game Core     = progression
Perf Core     = analytics
Discord       = visual output
Telegram      = urgent output
Zulip         = archive
GitHub        = execution + persistence
README        = dashboard
```

---

# 4. STATE MACHINE

The state machine is the memory of Maximum Overdrive.

The engine compares:

```text
CURRENT REMOTE VALUE
```

against:

```text
PREVIOUS LOCAL VALUE
```

and derives:

```text
DELTA
```

---

# 4.1 POSITIVE DELTA

Example:

```text
Previous = 12
Current  = 13
Delta    = +1
```

The engine can interpret this as one newly observed episode.

---

# 4.2 MULTI-DELTA

Example:

```text
Previous = 12
Current  = 15
Delta    = +3
```

The system can process three episodes.

The scoring contribution becomes:

```text
3 × 10 G = 30 G
```

The performance contribution is calculated across those newly observed episodes.

---

# 4.3 ZERO DELTA

Example:

```text
Previous = 15
Current  = 15
Delta    = 0
```

No normal progress event is generated.

This prevents repeated hourly notifications.

---

# 4.4 NEGATIVE DELTA

Example:

```text
Previous = 15
Current  = 14
Delta    = -1
```

A negative delta usually represents manual correction or rollback.

The engine should treat this as reconciliation rather than automatically removing earned
Gamerscore unless a deliberate accounting policy says otherwise.

---

# 4.5 STATE UPDATE ORDER

Recommended state flow:

```text
Read
 ↓
Compare
 ↓
Calculate
 ↓
Persist
 ↓
Notify
```

Future idempotency improvements can make this even safer.

---

# 5. MASTER ANILIST SYNC

The Master Sync is the conductor.

It performs a paginated GraphQL sweep over the target account.

It collects the information required by:

```text
Sync
Airing
Gamerscore
Performance
Discord
Ghost comparison
```

---

# 5.1 PAGINATED FETCH

Conceptual process:

```text
Page 1
  ↓
Page 2
  ↓
Page 3
  ↓
...
  ↓
Final Page
```

The engine checks `hasNextPage`.

It continues until the complete inventory is loaded.

---

# 5.2 MEDIA DATA

The engine is designed to work with fields such as:

```text
mediaId
progress
progressVolumes
score
status
title.romaji
title.english
type
episodes
chapters
volumes
season
seasonYear
coverImage.extraLarge
coverImage.color
nextAiringEpisode
```

Not every field is relevant to every media type.

---

# 5.3 MEDIA TYPE SAFETY

Anime logic should focus on:

```text
episodes
duration
airing
```

Manga logic should focus on:

```text
chapters
volumes
```

The engine should not assume that every object has every field.

---

# 5.4 TITLE FALLBACK

A robust title formatter can use:

```text
English
   ↓
Romaji
   ↓
Native
```

when one display field is unavailable.

The actual implementation can define the exact preference order.

---

# 5.5 CHAMELEON COLOR

AniList can provide a cover color.

The engine may use that value to create Discord embeds that visually match the artwork.

Flow:

```text
Cover
 ↓
Color
 ↓
Validate
 ↓
Discord Embed
```

A safe fallback color should be used when AniList does not return a valid color.

---

# 6. ANIME PROGRESS ENGINE

The anime subsystem detects progress changes for anime entries.

When an episode delta is found, it can trigger:

```text
Gamerscore
Performance
Discord
Achievement
Favorite check
Archive
State update
```

---

# 6.1 ANIME REWARD

Current V2 rule:

```text
1 episode = +10 G
```

---

# 6.2 ANIME PERFORMANCE

The performance system uses AniList duration data where available.

Example:

```text
Duration = 24 minutes
Deduction = 2 minutes
Effective = 22 minutes
```

---

# 6.3 MULTI-EPISODE PERFORMANCE

For a delta of three episodes:

```text
22 + 22 + 22
=
66 estimated minutes
```

If actual episode durations differ, each episode may be calculated separately.

---

# 6.4 COMPLETION

If the status transitions to completed, the completion subsystem can award:

```text
+100 G
```

The completion event should be protected from duplication.

---

# 7. MANGA PROGRESS ENGINE

The manga subsystem tracks chapter progress using the same state-machine philosophy.

---

# 7.1 MANGA REWARD

Current V2 rule:

```text
1 chapter = +2 G
```

---

# 7.2 MANGA PERFORMANCE

Current estimate:

```text
1 chapter = 5 minutes
```

For ten chapters:

```text
10 × 5 = 50 estimated minutes
```

---

# 7.3 MANGA COMPLETION

A completed manga entry can trigger the same completion bonus policy if the engine detects
the title-level transition.

---

# 7.4 MANGA VOLUMES

Volume data can be retained for information and display.

Volumes should not automatically be confused with chapter progress.

---

# 8. LIVE GAME CORE

The **Live Game Core** remains a first-class V2 subsystem.

This is not merely a decorative badge.

It is a persistent progression system.

The Game Core tracks:

```text
Lifetime G
Weekly G
Episode rewards
Chapter rewards
Completion rewards
Milestones
```

---

# 8.1 LIFETIME GAMERSCORE

Lifetime Gamerscore is permanent progression.

It represents cumulative scoring across the engine's recorded history.

---

# 8.2 WEEKLY GAMERSCORE

Weekly Gamerscore measures current activity.

It can reset after the weekly cycle while lifetime score continues to grow.

---

# 8.3 LIFETIME VS WEEKLY

```text
LIFETIME
   ↓
Permanent
   ↓
Never intentionally erased

WEEKLY
   ↓
Current grind
   ↓
Reset by weekly cycle
```

---

# 8.4 GAME CORE EVENT

A progress event creates a score transaction.

Conceptual:

```text
Event
 │
 ├── Anime +1 → +10 G
 ├── Manga +1 → +2 G
 └── Completion → +100 G
```

---

# 8.5 SCORE CONSISTENCY

The same score calculation should feed:

```text
Discord
README
JSON
Achievements
Weekly report
```

No output should independently calculate Gamerscore.

---

# 9. GAMERSCORE RULES

Current rules:

| Event | Reward |
|---|---:|
| Anime episode | +10 G |
| Manga chapter | +2 G |
| Series completion | +100 G |

---

# 9.1 EXAMPLE

```text
2 Anime Episodes = 20 G
8 Manga Chapters = 16 G
1 Completion      = 100 G
```

Total:

```text
136 G
```

---

# 9.2 GAMERSCORE LEDGER

A future ledger could store:

```json
{
    "event": "anime:21456:1067",
    "points": 10,
    "type": "EPISODE"
}
```

This would make every reward auditable.

---

# 9.3 DUPLICATE SCORE PROTECTION

A mature implementation should ensure the same event cannot grant score twice.

Possible event key:

```text
anime:<mediaId>:episode:<number>
```

The state ledger can be extended to recognize processed event IDs.

---

# 10. ACHIEVEMENT SYSTEM

Achievements convert major scoring events into milestones.

Current milestone examples:

```text
1,000 G
5,000 G
```

The architecture leaves room for larger thresholds.

---

# 10.1 MILESTONE DETECTION

The engine should detect a threshold crossing rather than checking only whether the
current score is above the threshold.

Example:

```text
Previous = 995 G
Current  = 1005 G
```

The 1,000 G milestone was crossed.

---

# 10.2 NO DUPLICATE MILESTONES

Once a milestone has been delivered, it should be recorded.

A future achievement ledger may contain:

```text
1000G = unlocked
5000G = locked
```

---

# 10.3 COMPLETION ACHIEVEMENTS

Series completion can also create achievement output.

The system can distinguish:

```text
Progress Reward
Completion Reward
Milestone Reward
```

---

# 11. WEEKLY GRIND

The weekly grind is the current activity scoreboard.

The engine uses the active week to decide when a rollover occurs.

---

# 11.1 WEEK RESET

Conceptual:

```text
Previous Week = 32
Current Week  = 33
```

The engine can:

1. Archive the previous weekly score.
2. Preserve lifetime score.
3. Reset weekly score.
4. Set the new active week.
5. Send a weekly report.
6. Continue normal processing.

---

# 11.2 WEEKLY REPORT

A report can contain:

```text
Weekly Gamerscore
Episodes
Chapters
Completions
Estimated Minutes
Milestones
```

---

# 11.3 WEEKLY DATA SAFETY

Weekly reset should never delete the lifetime total.

The operation is:

```text
Bank
 ↓
Reset
 ↓
Continue
```

not:

```text
Delete everything
```

---

# 12. LIVE PERFORMANCE CORE

The **Live Performance Core** is the second major pillar of V2.

The Game Core measures:

```text
progression
```

The Performance Core measures:

```text
consumption
```

This distinction must remain explicit.

---

# 12.1 PERFORMANCE METRICS

The V2 performance layer can track:

```text
Daily Episodes
Daily Chapters
Daily Minutes
Weekly Episodes
Weekly Chapters
Weekly Minutes
Monthly Episodes
Monthly Chapters
Monthly Minutes
Yearly Episodes
Yearly Chapters
Yearly Minutes
```

---

# 12.2 DAILY TELEMETRY

Daily telemetry is designed to answer:

> "What did I consume today?"

Example:

```text
Episodes = 4
Chapters = 12
Estimated Minutes = 148
```

---

# 12.3 WEEKLY TELEMETRY

Weekly telemetry answers:

> "How hard did I grind this week?"

Example:

```text
Episodes = 24
Chapters = 81
Minutes = 810
```

---

# 12.4 MONTHLY TELEMETRY

Monthly telemetry gives a broader view of consistency.

It can help answer:

```text
Was this a heavy month?
Which medium dominated?
How many titles were completed?
```

---

# 12.5 YEARLY TELEMETRY

Yearly telemetry becomes a historical record.

Potential values include:

```text
Total episodes
Total chapters
Total estimated minutes
Total Gamerscore
Total completions
Active days
```

---

# 13. ANIME TIME CALCULATION

The anime calculation uses AniList duration information.

Model:

```text
Effective Minutes
=
Duration
-
2
```

The two-minute adjustment is an estimate for opening/ending content.

---

# 13.1 EXAMPLE

```text
Episode Duration = 24
Effective        = 22
```

---

# 13.2 MULTIPLE EPISODES

If five episodes have 24-minute durations:

```text
5 × (24 - 2)
=
110 minutes
```

---

# 13.3 MIXED DURATIONS

If three episodes have:

```text
24
23
25
```

then:

```text
(24 - 2)
+
(23 - 2)
+
(25 - 2)
=
66 minutes
```

This is more accurate than assuming every anime episode has the same duration.

---

# 13.4 MISSING DURATION

If AniList returns no usable duration:

```text
Duration unavailable
      ↓
Use configured fallback
      ↓
Log fallback usage
```

The fallback should be clearly documented if implemented.

---

# 14. MANGA TIME CALCULATION

The manga estimate uses:

```text
5 minutes per chapter
```

This makes daily analytics consistent.

---

# 14.1 EXAMPLE

```text
20 chapters
× 5 minutes
=
100 estimated minutes
```

---

# 14.2 STATISTICAL DISCLAIMER

Five minutes is not a measurement of the user's real reading speed.

It is an analytical normalization value.

A future configurable profile could allow different reading estimates.

---

# 15. PERFORMANCE VAULT

The performance directory stores historical telemetry.

Recommended structure:

```text
performance/
├── daily/
├── weekly/
├── monthly/
└── yearly/
```

---

# 15.1 DAILY FILE

Example:

```text
performance/daily/2026-08-13.json
```

Potential fields:

```json
{
    "date": "2026-08-13",
    "anime_episodes": 4,
    "manga_chapters": 12,
    "estimated_minutes": 148
}
```

---

# 15.2 WEEKLY FILE

Example:

```text
performance/weekly/2026-W33.json
```

Potential fields:

```json
{
    "week": "2026-W33",
    "anime_episodes": 24,
    "manga_chapters": 81,
    "estimated_minutes": 810
}
```

---

# 15.3 MONTHLY FILE

Example:

```text
performance/monthly/2026-08.json
```

---

# 15.4 YEARLY FILE

Example:

```text
performance/yearly/2026.json
```

---

# 15.5 LIFETIME FILE

A lifetime aggregate can live at:

```text
performance/lifetime.json
```

This can provide a stable summary independent of daily files.

---

# 16. README TELEMETRY

The README itself becomes a live dashboard.

The existing machine-readable markers are:

```html
<!-- BADGES_START -->
<!-- BADGES_END -->
```

and:

```html
<!-- PERFORMANCE_START -->
<!-- PERFORMANCE_END -->
```

These markers should be considered part of the automation contract.

---

# 16.1 LIFETIME BADGE

The Lifetime badge represents:

```text
lifetime_g
```

It should be updated from the canonical Gamerscore state.

---

# 16.2 WEEKLY BADGE

The Weekly badge represents:

```text
weekly_g
```

It should be updated from the same state used by the Discord achievement system.

---

# 16.3 DAILY EPS BADGE

The Daily Eps badge should represent the canonical daily anime counter.

It should not be hardcoded.

Desired architecture:

```text
Daily Performance
      │
      ▼
Canonical anime_episodes
      │
      ├──► JSON
      ├──► Discord
      └──► README
```

---

# 16.4 DAILY CHP BADGE

The Daily Chp badge should represent the canonical daily chapter counter.

Again:

```text
One value
Many outputs
```

---

# 16.5 README SAFETY

If the markers are missing, the engine should stop the README update and log an error.

It should never silently rewrite the entire README.

---

# 16.6 README TELEMETRY FAILURE

A telemetry failure should not delete:

```text
Gamerscore
Performance Vault
Discord Hologram
State
```

The README is a presentation layer.

---

# 17. LIVE PERFORMANCE HOLOGRAM

The Performance Hologram is the live Discord representation of the Performance Core.

It can display:

```text
Daily Episodes
Daily Chapters
Estimated Minutes
Gamerscore
Weekly Grind
Last Sync
```

---

# 17.1 Hologram Refresh

Conceptual process:

```text
Load previous message ID
       │
       ▼
Fetch canonical telemetry
       │
       ▼
Build new embed
       │
       ▼
Delete previous message
       │
       ▼
Post new message
       │
       ▼
Save new message ID
```

---

# 17.2 MESSAGE ID MEMORY

The Hologram uses:

```text
db_performance_msg.json
```

to remember the previous dashboard message.

---

# 17.3 Hologram Recovery

If the previous message no longer exists:

```text
Delete fails
   │
   ▼
Ignore missing message
   │
   ▼
Post new dashboard
   │
   ▼
Save new message ID
```

---

# 17.4 Hologram IS NOT THE DATABASE

The Hologram is only a display.

Permanent performance data remains in the performance vault.

This is important.

Deleting a Discord message must not delete historical statistics.

---

# 17.5 Hologram DESIGN

A CLI-style layout can resemble:

```text
╔══════════════════════════════════════╗
║       LIVE PERFORMANCE HOLOGRAM      ║
╠══════════════════════════════════════╣
║ DAILY EPS       : 04                 ║
║ DAILY CHP       : 12                 ║
║ EST. MINUTES    : 148                ║
║ WEEKLY G         : 662 G             ║
║ LIFETIME G       : 5028 G            ║
╚══════════════════════════════════════╝
```

The actual Discord formatting can be richer.

---

# 18. AIRING INTELLIGENCE RADAR

The Airing Radar is designed for currently airing anime.

The engine reads:

```text
nextAiringEpisode
```

from AniList.

---

# 18.1 THREE-HOUR WARNING

At approximately:

```text
10,800 seconds
```

remaining:

```text
🕒 3-HOUR WARNING
```

is generated.

---

# 18.2 ONE-HOUR WARNING

At approximately:

```text
3,600 seconds
```

remaining:

```text
🚨 FINAL 1-HOUR WARNING
```

can be delivered.

---

# 18.3 TELEGRAM OVERRIDE

The one-hour warning can also be routed directly to Telegram.

This makes it a mobile alert rather than a Discord-only message.

---

# 18.4 AIRING STATE LOCK

`db_airing.json` prevents repeated notifications.

Conceptual state:

```json
{
    "21456_ep1067": "3h",
    "21456_ep1068": "1h"
}
```

---

# 18.5 DISCORD TIMESTAMP

The engine can use:

```text
<t:UNIX:R>
```

to allow Discord to render a dynamic relative time.

---

# 18.6 AIRING NULL SAFETY

Not every anime has a next airing episode.

If no value exists:

```text
Skip airing calculation.
```

This is normal.

---

# 19. MAL GHOST RADAR

The Ghost Radar detects gaps between MAL source data and AniList target state.

It can parse:

```text
mal_export.xml
mal_anime.xml
```

---

# 19.1 TITLE CROSS-REFERENCE

The engine can build a known title pool from:

```text
AniList Romaji
AniList English
```

and compare normalized MAL titles against it.

---

# 19.2 NORMALIZATION

Typical normalization:

```text
Lowercase
Trim whitespace
Normalize known punctuation
```

The goal is to reduce false mismatches.

---

# 19.3 GHOST STORAGE

Unresolved entries are stored in:

```text
db_ghosts.json
```

---

# 19.4 GHOST ASSIMILATION

If an unresolved title becomes available later:

```text
Ghost
  ↓
AniList Search
  ↓
Match Found
  ↓
SaveMediaListEntry
  ↓
Progress Imported
  ↓
GamerScore Applied
  ↓
Ghost Resolved
```

---

# 19.5 GHOST REJECTION

If AniList cannot resolve an item:

```text
🔴 GHOST REJECTED
```

The reason can be logged.

This prevents infinite blind retries without visibility.

---

# 19.6 GHOST THROTTLE

The Ghost Radar can introduce a delay between searches.

Example:

```python
time.sleep(1.5)
```

The value should ideally remain configurable.

---

# 20. DEEP VOID PROTOCOL

The Deep Void Protocol extends the Ghost Radar philosophy.

It is intended for titles that are known to the user but not currently indexed by AniList.

Examples may include:

```text
Obscure manga
Indie web novels
Unlisted publications
Highly specific works
```

---

# 20.1 VOID FILE

The dedicated state file is:

```text
db_void.json
```

---

# 20.2 VOID EXAMPLE

```json
{
    "Unlisted Manga Title Here": {
        "progress": 15,
        "score": 9,
        "type": "MANGA"
    }
}
```

---

# 20.3 VOID LIFECYCLE

```text
Manual Entry
     │
     ▼
db_void.json
     │
     ▼
Periodic Search
     │
     ▼
AniList Match?
   /       \
 NO        YES
 │          │
 ▼          ▼
Wait     Assimilate
            │
            ▼
       Remove from Void
```

---

# 20.4 VOID SAFETY

The Deep Void should not automatically create random media entries from weak title
matches.

A confidence check is strongly recommended for future implementation.

---

# 20.5 VOID PRIORITY

Future versions could store:

```text
priority
last_attempt
attempt_count
match_confidence
```

This would make the Deep Void easier to manage.

---

# 21. DISCORD COMMAND CENTER

Discord is the primary visual layer.

The V2 architecture uses separate webhooks for logical categories.

---

# 21.1 ANIME WEBHOOK

```text
DISCORD_ANILIST_ANIME_WEBHOOK
```

Used for standard anime progress.

---

# 21.2 MANGA WEBHOOK

```text
DISCORD_ANILIST_MANGA_WEBHOOK
```

Used for manga progress.

---

# 21.3 AIRING WEBHOOK

```text
DISCORD_AIRING_WEBHOOK
```

Used for:

```text
3-hour warning
1-hour warning
```

---

# 21.4 LOG WEBHOOK

```text
DISCORD_ANILIST_LOG_WEBHOOK
```

Used for diagnostics and engine telemetry.

---

# 21.5 FAVORITES WEBHOOK

```text
DISCORD_FAVORITES_WEBHOOK
```

Used for priority franchise alerts.

---

# 21.6 GHOST WEBHOOK

```text
DISCORD_GHOST_RADAR_WEBHOOK
```

Used for Ghost Radar activity.

---

# 21.7 ACHIEVEMENTS WEBHOOK

```text
DISCORD_ACHIEVEMENTS_WEBHOOK
```

Used for:

```text
Milestones
Completion
Weekly reports
Gamerscore events
```

---

# 21.8 PERFORMANCE WEBHOOK

```text
DISCORD_PERFORMANCE_WEBHOOK
```

Used exclusively by the Live Performance Hologram.

---

# 22. TELEGRAM DIRECT ALERTS

Telegram provides a direct mobile notification route.

Required values:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

---

# 22.1 WHY TELEGRAM

Discord is the command center.

Telegram is the direct alert channel.

This division keeps notification purpose clear.

---

# 22.2 TYPICAL TELEGRAM EVENTS

Examples:

```text
1-hour airing warning
Critical engine warning
Manual recovery result
High-priority franchise alert
```

---

# 23. ZULIP GRAND ARCHIVE

Zulip provides structured long-term event communication.

Suggested topic structure:

```text
Anime-Vault
Manga-Vault
Achievements
Airing
Performance
Ghost-Radar
System-Logs
```

---

# 23.1 ANIME VAULT

Anime progress events can be archived under an anime-specific stream topic.

---

# 23.2 MANGA VAULT

Manga progress can be archived independently.

---

# 23.3 PERFORMANCE ARCHIVE

Performance reports can be preserved separately from individual progress notifications.

---

# 23.4 ZULIP DOMAIN RULE

The bot email domain must match the server URL domain.

Example:

```text
Bot:
matrix-engine-bot@tokyo.zulipchat.com

Server:
https://tokyo.zulipchat.com/api/v1/messages
```

---

# 23.5 ZULIP 401

If domains differ:

```text
401 UNAUTHORIZED
```

can occur.

This is a configuration problem, not an AniList problem.

---

# 24. JSON MEMORY VAULTS

V2 continues to use readable JSON.

Current files:

```text
db_achievements.json
db_airing.json
db_ghosts.json
db_void.json
db_messages.json
db_performance_msg.json
db_sync.json
```

---

# 24.1 db_sync.json

Master synchronization state.

It stores previous known progress.

---

# 24.2 db_achievements.json

Gamerscore and weekly cycle state.

Possible fields:

```text
lifetime_g
weekly_g
current_week
milestones
```

---

# 24.3 db_airing.json

Airing alert state.

---

# 24.4 db_ghosts.json

Ghost reconciliation ledger.

---

# 24.5 db_void.json

Deep Void storage.

---

# 24.6 db_messages.json

Discord cleanup queue.

---

# 24.7 db_performance_msg.json

Performance Hologram message ID.

---

# 24.8 WHY JSON

JSON is:

```text
Readable
Portable
Git-friendly
Easy to inspect
Easy to back up
Easy to process with Python
```

---

# 24.9 JSON LIMITATIONS

JSON becomes less attractive as a system grows because:

```text
Concurrent writes are awkward
Complex queries are limited
Large files produce bigger Git diffs
Schema changes need care
```

For the current personal-scale system, these trade-offs remain manageable.

---

# 25. REPOSITORY STRUCTURE

Recommended V2 structure:

```text
📦 Anilist-Triple-Sync
 ┣ 📂 .github/workflows
 ┃ ┗ 📜 sync_engine.yml
 ┣ 📂 performance
 ┃ ┣ 📂 daily
 ┃ ┃ ┗ 📜 YYYY-MM-DD.json
 ┃ ┣ 📂 monthly
 ┃ ┣ 📂 weekly
 ┃ ┣ 📂 yearly
 ┃ ┗ 📜 lifetime.json
 ┣ 📜 anilist_engine.py
 ┣ 📜 db_achievements.json
 ┣ 📜 db_airing.json
 ┣ 📜 db_ghosts.json
 ┣ 📜 db_void.json
 ┣ 📜 db_messages.json
 ┣ 📜 db_performance_msg.json
 ┣ 📜 db_sync.json
 ┣ 📜 mal_anime.xml
 ┣ 📜 mal_export.xml
 ┗ 📜 README.md
```

---

# 25.1 FILE RESPONSIBILITIES

```text
sync_engine.yml
    Scheduler

anilist_engine.py
    Master engine

performance/
    Analytics history

db_achievements.json
    Gamerscore state

db_airing.json
    Airing alert state

db_ghosts.json
    MAL anomalies

db_void.json
    Deep Void

db_messages.json
    Discord cleanup

db_performance_msg.json
    Hologram message state

db_sync.json
    Progress memory

README.md
    Documentation + telemetry
```

---

# 26. DEPLOYMENT

Deploying V2 should be done in controlled stages.

---

# 26.1 STEP 1 — PRIVATE REPOSITORY

Create a private GitHub repository if personal tracking data is stored.

---

# 26.2 STEP 2 — ENGINE

Upload:

```text
anilist_engine.py
```

---

# 26.3 STEP 3 — WORKFLOW

Create:

```text
.github/workflows/sync_engine.yml
```

---

# 26.4 STEP 4 — STATE FILES

Initialize:

```text
db_achievements.json
db_airing.json
db_ghosts.json
db_void.json
db_messages.json
db_performance_msg.json
db_sync.json
```

Use valid empty/default state.

---

# 26.5 STEP 5 — PERFORMANCE DIRECTORIES

Create:

```text
performance/daily
performance/weekly
performance/monthly
performance/yearly
```

---

# 26.6 STEP 6 — MAL DATA

Place:

```text
mal_export.xml
mal_anime.xml
```

into the repository if Ghost Radar is enabled.

---

# 26.7 STEP 7 — SECRETS

Configure all required repository secrets.

---

# 26.8 STEP 8 — MANUAL TEST

Run the workflow manually before enabling long-term automation.

---

# 26.9 STEP 9 — VERIFY

Check:

```text
AniList
Discord
Gamerscore
Performance
Airing
Ghost Radar
Telegram
Zulip
README
Git push
```

---

# 27. SECRETS

The engine requires names matching its workflow environment mapping.

Core secrets:

| Secret | Purpose |
|---|---|
| `ANILIST_TARGET_TOKEN` | AniList authentication |
| `DISCORD_ANILIST_ANIME_WEBHOOK` | Anime progress |
| `DISCORD_ANILIST_MANGA_WEBHOOK` | Manga progress |
| `DISCORD_AIRING_WEBHOOK` | Airing warnings |
| `DISCORD_ANILIST_LOG_WEBHOOK` | Diagnostics |
| `DISCORD_FAVORITES_WEBHOOK` | Priority franchise alerts |
| `DISCORD_GHOST_RADAR_WEBHOOK` | Ghost alerts |
| `DISCORD_ACHIEVEMENTS_WEBHOOK` | Achievements |
| `DISCORD_PERFORMANCE_WEBHOOK` | Performance Hologram |
| `TELEGRAM_BOT_TOKEN` | Telegram bot token |
| `TELEGRAM_CHAT_ID` | Telegram destination |
| `ZULIP_BOT_EMAIL` | Zulip bot identity |
| `ZULIP_API_KEY` | Zulip API token |
| `ZULIP_SERVER_URL` | Zulip endpoint |

---

# 27.1 SECRET RULE

Store secret values only in GitHub Secrets.

Do not place them in:

```text
README.md
Python source
JSON files
Workflow comments
Screenshots
```

---

# 27.2 SECRET NAME RULE

Secret names are part of the configuration contract.

A mismatch such as:

```text
DISCORD_MANGA_WEBHOOK
```

instead of:

```text
DISCORD_ANILIST_MANGA_WEBHOOK
```

can break an output pipeline.

---

# 27.3 TOKEN ROTATION

If a token leaks:

```text
Revoke
 ↓
Regenerate
 ↓
Update GitHub Secret
 ↓
Run manually
 ↓
Verify
```

---

# 28. ZULIP CONFIGURATION

Zulip configuration requires exact domain matching.

---

# 28.1 CREATE BOT

Navigate to:

```text
Settings
→ Personal settings
→ Bots
```

Create an Incoming Webhook bot.

---

# 28.2 CHECK BOT EMAIL

Example:

```text
matrix-engine-bot@tokyo.zulipchat.com
```

---

# 28.3 MATCH DOMAIN

Correct:

```text
https://tokyo.zulipchat.com/api/v1/messages
```

Incorrect:

```text
https://orewatokyo.zulipchat.com/api/v1/messages
```

---

# 28.4 API KEY

Paste the Zulip API key with:

```text
No trailing space
No accidental newline
No quotation marks
```

unless the secret system explicitly includes them.

---

# 29. GITHUB ACTIONS

GitHub Actions provides:

```text
Schedule
Runner
Secrets
Logs
Manual dispatch
Repository writes
```

---

# 29.1 WORKFLOW NAME

Suggested:

```yaml
name: AniList Maximum Overdrive V2
```

---

# 29.2 SCHEDULE

The exact cron schedule belongs in:

```text
sync_engine.yml
```

The README should describe the intention rather than become the schedule source.

---

# 29.3 MANUAL DISPATCH

Include:

```yaml
workflow_dispatch:
```

for testing and recovery.

---

# 29.4 PERMISSIONS

The workflow needs repository write permission if it commits telemetry/state.

Example:

```yaml
permissions:
  contents: write
```

---

# 29.5 CONCURRENCY

Recommended:

```yaml
concurrency:
  group: anilist-engine
  cancel-in-progress: true
```

This helps prevent overlapping runs.

---

# 29.6 PYTHON SETUP

A typical setup:

```yaml
- name: Set up Python
  uses: actions/setup-python@v5
  with:
    python-version: '3.10'
```

---

# 29.7 DEPENDENCIES

Install the dependencies actually required by the engine.

For a requests-based engine:

```yaml
- name: Install Dependencies
  run: pip install requests
```

---

# 29.8 ENGINE EXECUTION

Example:

```yaml
- name: Run Master Engine
  run: python anilist_engine.py
```

Environment variables should be provided through secrets.

---

# 29.9 STATE COMMIT

After the engine finishes:

```text
git add
git commit
git push
```

Only relevant generated files should be committed.

---

# 30. GRAPHQL ARCHITECTURE

AniList GraphQL is the main remote interface.

The V2 engine can request multiple data points in one query.

---

# 30.1 MASTER QUERY

Example architecture:

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

---

# 30.2 WHY ONE DENSE QUERY

A dense query reduces the need for many separate network requests.

One response can support:

```text
Sync
Airing
Gamerscore
Performance
Discord
```

---

# 30.3 GHOST MUTATION

Conceptual mutation:

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

---

# 30.4 GRAPHQL ERROR CHECKING

HTTP 200 does not automatically mean everything succeeded.

The engine should inspect:

```text
HTTP status
GraphQL errors
Required data
```

---

# 31. API RESILIENCE

The Titanium Armor system protects network requests.

---

# 31.1 RETRY

Conceptual:

```text
Attempt 1
   ↓ failure
Sleep
   ↓
Attempt 2
   ↓ failure
Sleep
   ↓
Attempt 3
```

---

# 31.2 EXPONENTIAL BACKOFF

A simple model:

```text
3s
6s
12s
24s
```

The actual implementation may cap the delay.

---

# 31.3 JITTER

Future versions may add a small random offset to reduce synchronized retry bursts.

---

# 31.4 RATE LIMIT

If the API returns a rate-limit response:

```text
429
```

the engine should delay and retry according to the server's guidance when available.

---

# 31.5 AUTH FAILURE

A permanent authentication problem should not be retried endlessly.

Example:

```text
401
 ↓
Log
 ↓
Stop safely
```

---

# 31.6 TIMEOUT

A network timeout may be transient.

The Titanium Armor should be capable of retrying bounded timeouts.

---

# 32. DIAGNOSTICS

The diagnostics layer exists to explain failures without turning every small external
problem into a silent crash.

Useful log prefixes:

```text
[SYNC]
[GAME]
[PERFORMANCE]
[AIRING]
[GHOST]
[VOID]
[DISCORD]
[TELEGRAM]
[ZULIP]
[STATE]
[README]
[GIT]
```

---

# 32.1 HEALTHY RUN EXAMPLE

```text
[SYNC] Inventory fetched
[SYNC] Delta detected
[GAME] +10 G
[PERFORMANCE] +22 minutes
[DISCORD] Progress delivered
[AIRING] Scan complete
[GHOST] Scan complete
[README] Telemetry refreshed
[STATE] JSON updated
[GIT] Changes pushed
```

---

# 32.2 RUN SUMMARY

A final run summary can contain:

```text
Media scanned
Events detected
Gamerscore earned
Episodes tracked
Chapters tracked
Estimated minutes
Airing notices
Ghosts found
Ghosts assimilated
Errors
Runtime
```

---

# 33. TROUBLESHOOTING

## Discord Webhook Missing

Error:

```text
Discord Webhook missing for: UPDATE
```

Cause:

```text
Secret mismatch
```

Fix:

```text
Check YAML environment name
Check GitHub Secret name
Check spelling
```

---

## Zulip 401

Error:

```text
Zulip Status [401]
```

Cause:

```text
Domain mismatch
```

Fix:

```text
Bot email domain == server URL domain
```

---

## No Discord Update

Cause:

```text
Delta = 0
```

The state machine intentionally skipped the event.

---

## Performance Hologram Did Not Delete

Cause:

```text
Stored message ID invalid
```

Recovery:

```text
Create new dashboard
Save new message ID
Continue
```

---

## README Daily Counters Stay at Zero

If:

```text
Daily Eps = 0
Daily Chp = 0
```

while Discord performance is updating, the README telemetry path may not be receiving
the canonical daily metrics.

Correct V2 design:

```text
Performance Core
     │
     ├──► JSON
     ├──► Hologram
     └──► README
```

The fix should be in the engine/output layer, not by manually editing the README every day.

---

## README Markers Missing

If these are removed:

```html
<!-- PERFORMANCE_START -->
<!-- PERFORMANCE_END -->
```

the updater must log the error and avoid damaging the document.

---

# 34. DATA SAFETY

The engine can contain highly personal media history.

A private repository is strongly recommended when storing:

```text
MAL exports
Daily history
Private webhooks
Telegram identifiers
Zulip configuration
```

---

# 34.1 MAL DATA

MAL exports may reveal extensive personal media history.

Do not publish them casually.

---

# 34.2 WEBHOOKS

Discord webhook URLs are credentials.

Treat them as secret.

---

# 34.3 TELEGRAM

Bot tokens must remain secret.

Chat IDs can also be sensitive depending on context.

---

# 34.4 ZULIP

Keep:

```text
API key
Bot email
```

protected.

---

# 35. BACKUP AND RECOVERY

The project should be recoverable from repository history.

Important files:

```text
db_sync.json
db_achievements.json
db_airing.json
db_ghosts.json
db_void.json
performance/
```

---

# 35.1 BACKUP STRATEGY

A basic strategy:

```text
Git repository
+
Periodic local backup
```

---

# 35.2 JSON BACKUP

Before major migration:

```text
copy JSON files
```

and retain the original versions.

---

# 35.3 RECOVERY

If state becomes corrupted:

```text
Stop workflow
 ↓
Restore previous commit
 ↓
Validate JSON
 ↓
Run manually
 ↓
Verify
```

---

# 35.4 PERFORMANCE RECOVERY

Historical performance files should not be rebuilt from Discord messages when avoidable.

The vault is the canonical historical layer.

---

# 36. TESTING STRATEGY

V2 should be tested by subsystem.

---

# 36.1 UNIT TESTS

Examples:

```text
1 anime episode → +10 G
5 manga chapters → +10 G
completion → +100 G
zero delta → +0 G
```

---

# 36.2 STATE TESTS

Test:

```text
New media
Progress increase
Progress unchanged
Progress rollback
Completion
```

---

# 36.3 AIRING TESTS

Test:

```text
3h
1h
30m
Already sent
New episode
No next airing
```

---

# 36.4 GHOST TESTS

Test:

```text
Exact title
Romaji title
English title
Case variation
Whitespace variation
Unknown title
Newly indexed title
```

---

# 36.5 PERFORMANCE TESTS

Test:

```text
1 episode
3 episodes
10 chapters
Mixed media
Different anime durations
Missing duration
```

---

# 36.6 README TESTS

Test:

```text
Badge markers present
Performance markers present
Daily Eps replaced
Daily Chp replaced
Gamerscore replaced
Weekly replaced
```

---

# 36.7 IDEMPOTENCY TESTS

Run the same event twice.

Expected:

```text
First run → processed
Second run → ignored as duplicate
```

This is an important future hardening goal.

---

# 37. PERFORMANCE AND SCALING

The current architecture is designed for a personal media inventory.

JSON remains practical for moderate scale.

---

# 37.1 CURRENT SCALE MODEL

The engine is expected to handle hundreds of media entries comfortably when the API and
Ghost Radar are properly throttled.

Actual runtime depends on:

```text
Inventory size
API latency
Number of Ghost entries
Number of notifications
GitHub runner performance
```

---

# 37.2 JSON SCALE LIMITATIONS

As history grows:

```text
JSON size increases
Git diffs grow
Search becomes less efficient
Schema complexity increases
```

This is the point where a future SQLite migration could become attractive.

---

# 37.3 SQLITE AS FUTURE OPTION

V2 intentionally remains JSON-based.

If the project grows dramatically, SQLite could provide:

```text
Transactions
Indexes
Historical event tables
Fast filtering
```

without requiring a separate database server.

---

# 37.4 WHY NOT SQL NOW

The current project values:

```text
Simplicity
Portability
Git readability
Low deployment overhead
```

JSON satisfies those goals.

---

# 38. V2 ARCHITECTURE IMPROVEMENTS

V2 introduces several important structural ideas beyond simple synchronization.

---

# 38.1 CANONICAL TELEMETRY

One performance calculation can feed every output.

---

# 38.2 LIVE GAME CORE

Gamerscore becomes an explicit engine subsystem.

---

# 38.3 LIVE PERFORMANCE CORE

Performance becomes an explicit analytics subsystem.

---

# 38.4 README AS OUTPUT

The README becomes a telemetry surface rather than static documentation alone.

---

# 38.5 DEEP VOID

Unlisted media can exist in a persistent local holding state.

---

# 38.6 MESSAGE MEMORY

The Performance Hologram can recover from message deletion.

---

# 38.7 OUTPUT SEPARATION

Discord, Telegram, and Zulip have separate responsibilities.

---

# 38.8 STATE PERSISTENCE

The workflow preserves memory between otherwise ephemeral GitHub runner sessions.

---

# 38.9 FAILURE ISOLATION

One output failure should not automatically destroy unrelated state.

---

# 38.10 FUTURE EVENT MODEL

A future V2.x or V3 engine could represent each progress change as an explicit event.

Example:

```json
{
    "type": "ANIME_PROGRESS",
    "media_id": 21456,
    "delta": 1,
    "progress": 1067
}
```

---

# 39. FUTURE V3 ROADMAP

V3 should focus on architecture rather than unnecessary language changes.

---

# 39.1 MODULAR PYTHON

Potential structure:

```text
src/
├── main.py
├── core/
├── anilist/
├── sync/
├── game/
├── performance/
├── radar/
└── output/
```

---

# 39.2 EVENT BUS

Future flow:

```text
Event
 │
 ├── Game Handler
 ├── Performance Handler
 ├── Discord Handler
 ├── Telegram Handler
 ├── Zulip Handler
 └── README Handler
```

---

# 39.3 SQLITE OPTION

Introduce SQLite only if JSON becomes a practical bottleneck.

---

# 39.4 TYPESCRIPT DASHBOARD

A TypeScript web dashboard could provide:

```text
Graphs
Live charts
Achievement browser
Historical statistics
Airing queue
```

Python can remain the core automation engine.

---

# 39.5 STRUCTURED LOGGING

Future logs can include:

```text
timestamp
run_id
event_id
type
status
duration
error
```

---

# 39.6 DRY RUN

A future:

```text
DRY_RUN=true
```

mode could calculate everything without mutating AniList.

---

# 39.7 READ-ONLY MODE

A future:

```text
READ_ONLY=true
```

mode could inspect and report state without applying mutations.

---

# 39.8 CONFIGURATION FILE

Future configurable values:

```text
anime_g
manga_g
completion_g
anime_time_deduction
manga_minutes_per_chapter
airing_warning_3h
airing_warning_1h
ghost_delay
retry_count
```

---

# 39.9 SCORE LEDGER

A future event ledger could make every point auditable.

---

# 39.10 PERFORMANCE LEDGER

A future event ledger could make every minute of estimated media consumption traceable.

---

# 39.11 ACHIEVEMENT TIERS

Potential future tiers:

```text
COMMON
UNCOMMON
RARE
EPIC
LEGENDARY
APEX
```

---

# 39.12 STREAK SYSTEM

Potential future metrics:

```text
Active Days
Current Streak
Longest Streak
Weekly Consistency
Monthly Consistency
```

---

# 40. MAINTENANCE

Maintenance should focus on:

```text
API compatibility
Workflow compatibility
State compatibility
Output compatibility
Documentation compatibility
```

---

# 40.1 API MAINTENANCE

Review:

```text
GraphQL fields
Authentication
Rate limits
Error structures
```

---

# 40.2 WORKFLOW MAINTENANCE

Review:

```text
actions/checkout
actions/setup-python
Python version
Permissions
Cron
Concurrency
```

---

# 40.3 STATE MAINTENANCE

Keep state schemas stable.

If they change:

```text
Migrate
Validate
Backup
```

---

# 40.4 README MAINTENANCE

Never casually remove:

```text
BADGES_START
BADGES_END
PERFORMANCE_START
PERFORMANCE_END
```

They are machine-readable hooks.

---

# 40.5 DOCUMENTATION MAINTENANCE

Keep implemented and planned features clearly separated.

The README should never claim that a future feature is already active.

---

# 41. RELEASE STRATEGY

V2 should use release tags.

Example:

```text
v2.0.0
```

for the main V2 release.

---

# 41.1 PATCH

Bug fixes:

```text
v2.0.1
```

---

# 41.2 MINOR

New non-breaking feature:

```text
v2.1.0
```

---

# 41.3 MAJOR

Breaking architecture change:

```text
v3.0.0
```

---

# 41.4 RELEASE NOTES

Each release should document:

```text
Added
Changed
Fixed
Removed
Security
Migration
```

---

# 41.5 RELEASE SAFETY

Do not attach:

```text
Real tokens
Webhook URLs
Private MAL exports
Private JSON histories
```

to a public release.

---

# 42. OPERATIONAL CHECKLISTS

## PRE-RELEASE

```text
[ ] AniList authentication tested
[ ] GraphQL pagination tested
[ ] Anime sync tested
[ ] Manga sync tested
[ ] Gamerscore tested
[ ] Completion bonus tested
[ ] Weekly reset tested
[ ] Achievement milestones tested
[ ] Airing 3H tested
[ ] Airing 1H tested
[ ] Telegram tested
[ ] MAL Ghost Radar tested
[ ] Deep Void tested
[ ] Discord routing tested
[ ] Performance Core tested
[ ] Performance Hologram tested
[ ] README telemetry tested
[ ] JSON validated
[ ] Git push tested
[ ] Secret names checked
```

---

# 42.1 FIRST DEPLOYMENT

```text
[ ] Create repository
[ ] Configure secrets
[ ] Add workflow
[ ] Add engine
[ ] Add state files
[ ] Add performance folders
[ ] Add MAL XML
[ ] Run manually
[ ] Inspect logs
[ ] Inspect Discord
[ ] Inspect README
[ ] Verify commit
```

---

# 42.2 RECOVERY

```text
[ ] Stop scheduled workflow
[ ] Identify failed subsystem
[ ] Inspect GitHub log
[ ] Validate state
[ ] Check API
[ ] Check secrets
[ ] Repair
[ ] Run manually
[ ] Verify
[ ] Re-enable schedule
```

---

# 42.3 DAILY HEALTH CHECK

The engine should normally be able to provide:

```text
Latest sync
Latest performance
Latest Gamerscore
Airings
Ghost state
Repository update
```

---

# 42.4 WEEKLY HEALTH CHECK

Review:

```text
Weekly G
Weekly performance
Weekly reset
Achievement events
Git history
Errors
```

---

# 42.5 MONTHLY HEALTH CHECK

Review:

```text
Performance totals
JSON growth
Action runtime
API failures
Ghost count
Repository size
```

---

# 43. SYSTEM STATUS

```text
╔══════════════════════════════════════════════╗
║       ANILIST MAXIMUM OVERDRIVE V2          ║
╠══════════════════════════════════════════════╣
║ Master Sync         : ONLINE                 ║
║ State Machine       : ACTIVE                 ║
║ Live Game Core      : ONLINE                 ║
║ Gamerscore Engine   : ONLINE                 ║
║ Achievement Core    : ONLINE                 ║
║ Live Performance    : ONLINE                 ║
║ Performance Vault   : ONLINE                 ║
║ Hologram            : ONLINE                 ║
║ Airing Radar        : ONLINE                 ║
║ Ghost Radar         : ONLINE                 ║
║ Deep Void           : ARMED                  ║
║ Discord             : CONNECTED              ║
║ Telegram            : READY                  ║
║ Zulip Archive       : READY                  ║
║ README Telemetry    : ACTIVE                 ║
║ JSON Memory         : SECURED                ║
║ GitHub Automation   : ACTIVE                 ║
╚══════════════════════════════════════════════╝
```

---

# 43.1 SYSTEM FLOW

```text
ANIList
   │
   ▼
MASTER SYNC
   │
   ▼
DELTA ENGINE
   │
   ├───────────────┬─────────────────┐
   ▼               ▼                 ▼
GAME CORE      PERF CORE          RADARS
   │               │                 │
   ▼               ▼                 ├── Airing
G-SCORE         Telemetry            ├── Ghost
   │               │                 └── Void
   └───────────────┼─────────────────────┐
                   ▼                     │
              OUTPUT LAYER               │
                   │                     │
         ┌─────────┼─────────┐           │
         ▼         ▼         ▼           │
      Discord   Telegram   Zulip         │
         │                                │
         ▼                                │
    Hologram                              │
         │                                │
         └──────────────┬─────────────────┘
                        ▼
                  README TELEMETRY
                        │
                        ▼
                  GIT COMMIT
                        │
                        ▼
                  NEXT SCHEDULE
```

---

# 44. AUTHOR

**Orewa Tokyo**

Project identity:

```text
Rationalist
S-Tier Completionist
Otaku
Automation Enthusiast
```

The broader project identity emphasizes:

```text
Logic
Structure
Self-reliance
Data ownership
Completion
```

Favorite protagonists documented in the project ecosystem include:

```text
Roronoa Zoro
Edward Kenway
Nathan Drake
```

Favorite franchise territory includes:

```text
One Piece
Tomb Raider
Assassin's Creed
```

---

# 44.1 AUTHOR PHILOSOPHY

> *"Execute the master sync. Leave no data behind."*

No sugar-coating.

No blind automation.

No silent failures.

Just:

```text
Logic
+
Structure
+
Maximum Energy
```

---

# 45. FINAL PRINCIPLE

Maximum Overdrive V2 is ultimately built around one loop:

```text
CONSUME
   ↓
TRACK
   ↓
DETECT
   ↓
CALCULATE
   ↓
SCORE
   ↓
MEASURE
   ↓
DISPLAY
   ↓
ARCHIVE
   ↓
REPEAT
```

The project does not stop at recording a number.

It turns that number into a system.

It turns the system into telemetry.

It turns telemetry into history.

And it turns history into progression.

---

# ⚡ MAXIMUM OVERDRIVE V2

```text
                 SYSTEM READY

       ██████╗ ██╗   ██╗███████╗██████╗
      ██╔═══██╗██║   ██║██╔════╝██╔══██╗
      ██║   ██║██║   ██║█████╗  ██████╔╝
      ██║▄▄ ██║██║   ██║██╔══╝  ██╔══██╗
      ╚██████╔╝╚██████╔╝███████╗██║  ██║
       ╚══▀▀═╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝

            MAXIMUM OVERDRIVE V2

        SYNCHRONIZATION ARMED
           GAME CORE LIVE
        PERFORMANCE CORE LIVE
          HOLOGRAM LIVE
          TELEMETRY LIVE
           VAULT SECURED

            INITIATING CYCLE...
```

---

# 📜 PROJECT COMMANDMENTS

> Track everything.
>
> Remember everything.
>
> Calculate everything.
>
> Automate everything.
>
> Archive everything.
>
> Keep the numbers consistent.
>
> Keep the state persistent.
>
> Keep the Live Game Core alive.
>
> Keep the Live Performance Core alive.
>
> And never let a zero in the README lie about a live metric.

---

# 🔥 END OF README

**AniList Maximum Overdrive Sync — V2**

`State-driven • Automated • Persistent • Gamified • Analytical • Live`

---

# 📘 EXTENDED REFERENCE A — V2 EVENT CATALOG

V2 treats important activity as recognizable event classes.

```text
ANIME_PROGRESS
MANGA_PROGRESS
COMPLETION
AIRING_3H
AIRING_1H
GHOST_FOUND
GHOST_ASSIMILATED
GHOST_REJECTED
VOID_DETECTED
VOID_ASSIMILATED
ACHIEVEMENT
WEEKLY_ROLLOVER
PERFORMANCE_REFRESH
README_REFRESH
SYSTEM_ERROR
```

Each event represents a distinct reason for the engine to perform an operation.

The event model is useful because it prevents unrelated actions from becoming entangled.

For example:

```text
ANIME_PROGRESS
```

should not require the full Ghost Radar to run again.

Likewise:

```text
AIRING_1H
```

should not modify Gamerscore.

---

# 📘 EXTENDED REFERENCE B — EVENT ID DESIGN

A future hardened event ledger can assign deterministic identifiers.

Examples:

```text
anime:21456:1067
manga:99876:12
completion:21456
airing:21456:1067:3h
airing:21456:1067:1h
ghost:obscure-light-novel-name
void:unlisted-manga-title
```

The advantage is simple:

```text
Same event ID
      ↓
Already processed?
      ↓
YES → ignore
NO  → process
```

This helps protect against duplicate workflow executions.

---

# 📘 EXTENDED REFERENCE C — CANONICAL METRIC OBJECT

A future telemetry object can conceptually look like:

```json
{
    "date": "2026-08-13",
    "anime_episodes": 4,
    "manga_chapters": 12,
    "estimated_minutes": 148,
    "gamerscore": 64,
    "completions": 0
}
```

This object can then become the source for:

```text
README
Discord
JSON
Weekly aggregation
Monthly aggregation
```

---

# 📘 EXTENDED REFERENCE D — DAILY READOUT

A CLI-style daily readout can use:

```text
╔══════════════════════════════════════╗
║          DAILY TELEMETRY             ║
╠══════════════════════════════════════╣
║ Episodes        : 04                 ║
║ Chapters        : 12                 ║
║ Minutes         : 148                ║
║ Gamerscore      : 64 G               ║
║ Completions     : 00                 ║
╚══════════════════════════════════════╝
```

This is a presentation format.

The underlying JSON remains the data source.

---

# 📘 EXTENDED REFERENCE E — WEEKLY READOUT

```text
╔══════════════════════════════════════╗
║          WEEKLY TELEMETRY            ║
╠══════════════════════════════════════╣
║ Episodes        : 24                 ║
║ Chapters        : 81                 ║
║ Minutes         : 810                ║
║ Gamerscore      : 462 G              ║
║ Completions     : 03                 ║
╚══════════════════════════════════════╝
```

Weekly values should aggregate daily canonical values.

---

# 📘 EXTENDED REFERENCE F — LIFETIME READOUT

A future lifetime dashboard can display:

```text
Episodes
Chapters
Minutes
Gamerscore
Completions
Active Days
```

The design can later be used by a web dashboard.

---

# 📘 EXTENDED REFERENCE G — SCORE INTEGRITY

The project should maintain the invariant:

```text
Lifetime Score
>=
Weekly Score
```

when weekly score represents a subset of lifetime scoring.

If that invariant breaks unexpectedly, diagnostics should report it.

---

# 📘 EXTENDED REFERENCE H — PERFORMANCE INTEGRITY

The project should maintain:

```text
Daily
→ Weekly
→ Monthly
→ Yearly
```

aggregation consistency.

A future validator can compare:

```text
sum(daily) == weekly
```

for the corresponding period.

---

# 📘 EXTENDED REFERENCE I — README INTEGRITY

The README telemetry block should be treated like a small API.

The updater should:

```text
Locate marker
Read canonical metric
Format badge
Replace badge
Validate marker
Write file
```

The updater should not:

```text
Guess values
Scrape Discord
Calculate independent totals
```

---

# 📘 EXTENDED REFERENCE J — Hologram INTEGRITY

The Hologram should use the same canonical metric snapshot as the README.

If:

```text
Daily Episodes = 4
```

then:

```text
README = 4
Hologram = 4
Daily JSON = 4
```

This is the central V2 consistency goal.

---

# 📘 EXTENDED REFERENCE K — GAMERSCORE AND PERFORMANCE DIFFERENCE

Gamerscore and Performance deliberately track different concepts.

Example:

```text
One anime episode:
+10 G
+22 estimated minutes
```

The first value is progression.

The second value is consumption.

They should never be merged into one statistic.

---

# 📘 EXTENDED REFERENCE L — COMPLETIONIST SCORE MODEL

Completion adds an additional reward layer.

Example:

```text
12 episodes
+
completion

= 120 G
+ 100 G
= 220 G
```

The achievement subsystem can then determine whether a milestone was crossed.

---

# 📘 EXTENDED REFERENCE M — WEEKLY RESET SAFETY

A weekly reset should be atomic from the engine's perspective.

Conceptually:

```text
Read old week
      ↓
Archive old weekly values
      ↓
Update lifetime
      ↓
Reset weekly
      ↓
Write state
```

If a failure occurs, the engine should not leave a half-reset state.

---

# 📘 EXTENDED REFERENCE N — AIRING EVENT SAFETY

Each warning phase should have a unique key.

Example:

```text
21456_ep1067_3h
21456_ep1067_1h
```

This makes duplicate prevention clear.

---

# 📘 EXTENDED REFERENCE O — GHOST EVENT SAFETY

Every Ghost Radar entry should preferably have:

```text
normalized title
original title
type
progress
score
last checked
attempt count
status
```

A more complete vault makes debugging easier.

---

# 📘 EXTENDED REFERENCE P — DEEP VOID RECORD

A future `db_void.json` record could be:

```json
{
    "Unlisted Manga": {
        "progress": 15,
        "score": 9,
        "type": "MANGA",
        "last_checked": "2026-08-13T08:00:00Z",
        "attempts": 14,
        "priority": "HIGH"
    }
}
```

The current minimal schema can remain simpler.

---

# 📘 EXTENDED REFERENCE Q — NOTIFICATION PRIORITY

Future outputs could use:

```text
CRITICAL
HIGH
NORMAL
LOW
```

Examples:

```text
1H AIRING = HIGH
NORMAL PROGRESS = NORMAL
DEBUG LOG = LOW
SYSTEM AUTH FAILURE = CRITICAL
```

---

# 📘 EXTENDED REFERENCE R — DISCORD CHANNEL DESIGN

A clean server may use:

```text
#anilist-anime
#anilist-manga
#performance-monitor
#achievements
#anime-airing-alerts
#ghost-archive
#priority-favorites
#anilist-log
```

Each channel exists for a specific information class.

---

# 📘 EXTENDED REFERENCE S — LOG CHANNEL

The log channel should not become the primary archive.

It is operational telemetry.

The 48-hour auto-purge keeps it focused on current problems.

---

# 📘 EXTENDED REFERENCE T — ARCHIVE CHANNEL

Zulip is better suited to long-term textual history.

This division keeps Discord clean while retaining historical context elsewhere.

---

# 📘 EXTENDED REFERENCE U — GITHUB HISTORY

Git commits can preserve:

```text
State changes
Daily telemetry
README updates
Version changes
```

This means the repository itself becomes a historical timeline.

---

# 📘 EXTENDED REFERENCE V — GIT SAFETY

Before committing generated state:

```text
Validate JSON
Validate README markers
Check diff
Commit
Push
```

A future workflow can include an explicit validation stage.

---

# 📘 EXTENDED REFERENCE W — JSON VALIDATION

Simple validation can verify:

```text
File exists
File is valid JSON
Expected object/array shape
Required fields exist
```

This reduces silent corruption.

---

# 📘 EXTENDED REFERENCE X — SCHEMA VERSIONING

Every state file may eventually contain:

```json
{
    "schema_version": 2
}
```

When V3 changes the schema:

```text
schema 1
   ↓
migration
   ↓
schema 2
```

This is safer than replacing state manually.

---

# 📘 EXTENDED REFERENCE Y — PYTHON MODULARIZATION

The current master script can eventually split into:

```text
core
anilist
game
performance
radar
output
storage
telemetry
```

This is the most useful future code-quality upgrade before changing programming languages.

---

# 📘 EXTENDED REFERENCE Z — TYPE SAFETY

A future Python version can introduce type hints.

Example:

```python
def calculate_episode_points(delta: int) -> int:
    return delta * 10
```

This makes contracts clearer.

---

# 📘 EXTENDED REFERENCE AA — LOGGING

Future structured logging can include:

```text
timestamp
level
event_id
media_id
event_type
duration
result
```

This makes large workflow logs easier to inspect.

---

# 📘 EXTENDED REFERENCE AB — RETRY POLICY

Not every request should have identical retry behavior.

Potential policy:

```text
401 → no retry
403 → no retry unless configured
404 → no retry
429 → retry after delay
500 → retry
502 → retry
503 → retry
504 → retry
timeout → retry
```

This is a future hardening model.

---

# 📘 EXTENDED REFERENCE AC — TIMEOUT POLICY

Every external request should ideally have an explicit timeout.

A request that waits forever is worse than a controlled failure.

---

# 📘 EXTENDED REFERENCE AD — TELEGRAM SAFETY

Telegram notifications should not block core state persistence indefinitely.

A failed Telegram request should be isolated.

---

# 📘 EXTENDED REFERENCE AE — ZULIP SAFETY

Zulip archive failure should not erase progress state.

Archive is an output.

Tracking state remains primary.

---

# 📘 EXTENDED REFERENCE AF — DISCORD SAFETY

Discord failure should not roll back AniList progress.

AniList is the source.

Discord is the presentation layer.

---

# 📘 EXTENDED REFERENCE AG — SOURCE-OF-TRUTH RULE

The engine should clearly distinguish:

```text
Source
Derived
Presentation
```

AniList is source.

Gamerscore is derived.

Discord embed is presentation.

---

# 📘 EXTENDED REFERENCE AH — NO DOUBLE CALCULATION

The same business rule should exist in one place.

For example:

```text
Anime = 10 G
```

should not be coded independently in:

```text
Discord
README
Achievements
Weekly report
```

It should be calculated once.

---

# 📘 EXTENDED REFERENCE AI — NO DOUBLE PERFORMANCE

Likewise:

```text
Manga = 5 min/chapter
```

should be defined once and reused.

---

# 📘 EXTENDED REFERENCE AJ — FUTURE CONFIG

A future `config.json` could contain:

```json
{
    "scoring": {
        "anime_episode": 10,
        "manga_chapter": 2,
        "completion": 100
    },
    "performance": {
        "anime_deduction": 2,
        "manga_minutes": 5
    }
}
```

This would make balancing easier.

---

# 📘 EXTENDED REFERENCE AK — VERSIONED CONFIG

Business rules can be versioned.

Example:

```text
SCORING_VERSION = 1
```

This allows future changes without corrupting historical interpretation.

---

# 📘 EXTENDED REFERENCE AL — HISTORICAL IMMUTABILITY

Historical events should ideally not change when current rules change.

Example:

```text
2026 event → scored under V2 rules
2027 event → scored under V3 rules
```

The record can retain which rule version was used.

---

# 📘 EXTENDED REFERENCE AM — DATABASE MIGRATION TRIGGER

Consider SQLite when:

```text
JSON becomes large
Queries become complex
Git diffs become painful
Concurrent state becomes difficult
```

Until then, JSON remains justified.

---

# 📘 EXTENDED REFERENCE AN — WEB DASHBOARD TRIGGER

Consider TypeScript when:

```text
README no longer provides enough visualization
Discord becomes too crowded
Historical charts are needed
Interactive filtering becomes useful
```

Python can continue running the engine.

---

# 📘 EXTENDED REFERENCE AO — LANGUAGE STRATEGY

The project does not need a language rewrite to become better.

The highest-value improvements are:

```text
Modularity
Idempotency
Canonical telemetry
Testing
State validation
Structured logs
```

Language changes come later if a specific subsystem needs them.

---

# 📘 EXTENDED REFERENCE AP — V2 SUCCESS CRITERIA

V2 can be considered successful when:

```text
Anime sync works
Manga sync works
Gamerscore works
Weekly reset works
Performance works
Hologram works
README telemetry works
Airing Radar works
Ghost Radar works
Deep Void works
State survives restarts
Duplicate processing is controlled
```

---

# 📘 EXTENDED REFERENCE AQ — V2 FAILURE CRITERIA

V2 should be considered unhealthy if:

```text
README counters disagree with canonical state
Gamerscore duplicates
Weekly score disappears
Performance history is lost
Airing alerts spam
Ghosts loop forever
Discord failure destroys state
Git commits corrupt JSON
```

These are architecture-level health indicators.

---

# 📘 EXTENDED REFERENCE AR — FINAL MAINTAINER RULE

When adding a new subsystem, ask:

```text
What is its input?
What state does it own?
What event triggers it?
What output does it create?
How is failure handled?
How is duplication prevented?
Where is its historical record?
```

If those questions have clear answers, the feature is ready for integration.

---

# 📘 EXTENDED REFERENCE AS — MAXIMUM OVERDRIVE TEST MATRIX

```text
ANIME +1
ANIME +3
MANGA +1
MANGA +10
COMPLETION
WEEK CHANGE
3H WARNING
1H WARNING
GHOST FOUND
GHOST REJECTED
VOID FOUND
VOID ASSIMILATED
DISCORD FAILURE
TELEGRAM FAILURE
ZULIP FAILURE
README FAILURE
JSON FAILURE
GIT FAILURE
```

Every one of these should have an expected recovery behavior.

---

# 📘 EXTENDED REFERENCE AT — FINAL V2 CHECK

```text
SYNC CORE             [ONLINE]
GAME CORE             [ONLINE]
PERFORMANCE CORE      [ONLINE]
README TELEMETRY      [ONLINE]
HOLOGRAM              [ONLINE]
AIRING RADAR          [ONLINE]
GHOST RADAR           [ONLINE]
DEEP VOID             [ARMED]
DISCORD               [ONLINE]
TELEGRAM              [READY]
ZULIP                 [READY]
JSON VAULT             [SECURED]
GITHUB ACTIONS         [ACTIVE]
```

---

# 📘 EXTENDED REFERENCE AU — FINAL DATA LOOP

```text
ANIList
  ↓
FETCH
  ↓
NORMALIZE
  ↓
COMPARE
  ↓
GENERATE EVENT
  ↓
CALCULATE
  ↓
PERSIST
  ↓
NOTIFY
  ↓
AGGREGATE
  ↓
TELEMETRY
  ↓
COMMIT
  ↓
WAIT
  ↓
NEXT RUN
```

---

# 📘 EXTENDED REFERENCE AV — FINAL V2 IDENTITY

```text
ANILIST MAXIMUM OVERDRIVE SYNC
              │
              ▼
       TELEMETRY HUB V2
              │
       ┌──────┼──────┐
       ▼      ▼      ▼
     SCORE   TIME   EVENTS
       │      │      │
       └──────┼──────┘
              ▼
          HISTORY
              │
              ▼
          PROGRESSION
```

---

# 📘 EXTENDED REFERENCE AW — CLOSING STATEMENT

Maximum Overdrive V2 is designed to make ordinary media tracking measurable,
persistent, visible, and fun.

The system is deliberately personal.

It does not attempt to become a general public service.

It exists to become a reliable machine for one very specific purpose:

```text
Know what happened.
Know why it happened.
Know what it earned.
Know how much it mattered.
Keep the record.
```

That is the V2 philosophy.


---

# 📎 V2 REFERENCE CARD 01

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 01

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 02

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 02

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 03

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 03

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 04

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 04

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 05

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 05

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 06

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 06

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 07

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 07

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 08

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 08

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 09

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 09

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 10

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 10

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 11

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 11

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 12

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 12

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 13

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 13

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 14

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 14

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 15

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 15

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 16

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 16

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 17

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 17

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 18

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 18

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 19

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 19

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 20

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 20

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 21

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 21

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 22

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 22

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 23

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 23

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 24

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 24

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 25

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 25

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 26

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 26

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 27

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 27

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 28

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 28

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 29

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 29

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 30

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 30

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 31

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 31

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 32

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 32

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 33

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 33

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 34

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 34

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 35

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 35

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 36

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 36

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 37

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 37

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 38

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 38

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 39

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 39

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 40

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 40

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 41

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 41

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 42

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 42

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 43

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 43

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 44

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 44

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 45

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 45

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 46

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 46

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 47

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 47

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 48

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 48

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 49

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 49

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 50

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 50

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 51

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 51

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 52

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 52

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 53

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 53

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 54

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 54

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 55

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 55

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 56

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 56

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 57

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 57

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 58

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 58

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 59

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 59

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 60

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 60

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 61

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 61

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 62

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 62

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 63

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 63

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 64

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 64

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 65

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 65

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 66

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 66

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 67

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 67

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 68

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 68

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 69

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 69

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 70

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 70

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 71

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 71

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 72

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 72

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 73

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 73

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 74

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 74

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 75

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 75

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 76

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 76

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 77

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 77

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 78

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 78

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 79

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 79

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 📎 V2 REFERENCE CARD 80

```text
MAXIMUM OVERDRIVE V2
REFERENCE CARD 80

SOURCE:
AniList GraphQL

STATE:
Git-backed JSON

GAME:
Live Gamerscore Core

PERFORMANCE:
Live Performance Core

OUTPUT:
Discord / Telegram / Zulip / README

AUTOMATION:
GitHub Actions

RULE:
One canonical calculation.
Many synchronized outputs.
```

The purpose of this reference card is to reinforce the V2 operating contract: remote
tracking data is converted into a controlled local event, the event is processed once,
and the resulting canonical metrics are distributed to the presentation and archive
layers without inventing separate calculations.

The Live Game Core remains responsible for progression.

The Live Performance Core remains responsible for consumption analytics.

The README remains a telemetry surface.

The Performance Hologram remains a live Discord presentation.

The JSON vault remains the persistent machine memory.

The repository remains the long-term operational checkpoint.


---

# 🧰 FINAL OPERATIONS MANUAL

## Launch

```text
GitHub Actions
     ↓
Workflow starts
     ↓
Python engine starts
     ↓
State loads
     ↓
AniList queried
     ↓
Telemetry generated
```

## Sync

```text
Current progress
-
Stored progress
=
New event
```

## Score

```text
Anime:
delta × 10

Manga:
delta × 2

Completion:
+100
```

## Performance

```text
Anime:
duration - 2 minutes

Manga:
chapter × 5 minutes
```

## Output

```text
Discord
Telegram
Zulip
README
```

## Persistence

```text
JSON
+
performance vault
+
Git commit
```

---

# 🚀 V2 DEPLOYMENT FINISH LINE

```text
╔══════════════════════════════════════════════╗
║     MAXIMUM OVERDRIVE V2 DEPLOYMENT         ║
╠══════════════════════════════════════════════╣
║ Repository           : READY                  ║
║ Secrets              : CONFIGURED             ║
║ Workflow             : READY                  ║
║ AniList              : CONNECTED              ║
║ Game Core            : LIVE                   ║
║ Performance Core     : LIVE                   ║
║ Hologram             : LIVE                   ║
║ README Telemetry     : LIVE                   ║
║ Airing Radar         : LIVE                   ║
║ Ghost Radar          : LIVE                   ║
║ Deep Void            : ARMED                  ║
║ Archive              : READY                  ║
║ State Vault          : SECURED                ║
╚══════════════════════════════════════════════╝
```

---

# ⚡ V2 FINAL MESSAGE

> **One source.**
>
> **One event.**
>
> **One calculation.**
>
> **Many synchronized outputs.**

That is the architectural heart of AniList Maximum Overdrive Sync V2.

---

# 🔥 MAXIMUM OVERDRIVE V2 — ONLINE

```text
ENGINE STATUS      : ONLINE
SYNC STATUS        : ACTIVE
GAME CORE          : LIVE
PERFORMANCE CORE   : LIVE
HOLOGRAM           : LIVE
README TELEMETRY   : ACTIVE
VAULT              : SECURED
AUTOMATION         : ARMED

BEGIN NEXT CYCLE.
```
