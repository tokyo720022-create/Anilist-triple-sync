# ⚡ ANILIST MAXIMUM OVERDRIVE SYNC ⚡

```text
███╗   ███╗ █████╗ ██╗  ██╗██╗███╗   ███╗██╗   ██╗███╗   ███╗
████╗ ████║██╔══██╗╚██╗██╔╝██║████╗ ████║██║   ██║████╗ ████║
██╔████╔██║███████║ ╚███╔╝ ██║██╔████╔██║██║   ██║██╔████╔██║
██║╚██╔╝██║██╔══██║ ██╔██╗ ██║██║╚██╔╝██║██║   ██║██║╚██╔╝██║
██║ ╚═╝ ██║██║  ██║██╔╝ ██╗██║██║ ╚═╝ ██║╚██████╔╝██║ ╚═╝ ██║
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝     ╚═╝
            O V E R D R I V E   A R C H I T E C T U R E
```

<!-- BADGES_START -->
![Gamerscore](https://img.shields.io/badge/Lifetime_Gamerscore-5024%20G-FFD700?style=for-the-badge&logo=epic-games&logoColor=black)
![Weekly](https://img.shields.io/badge/Weekly_Grind-658%20G-FF4500?style=for-the-badge&logo=graphql&logoColor=white)
<!-- BADGES_END -->

<!-- PERFORMANCE_START -->
![Daily Eps](https://img.shields.io/badge/Daily_Eps-0-blue?style=for-the-badge&logo=youtube&logoColor=white)
![Daily Chp](https://img.shields.io/badge/Daily_Chp-0-green?style=for-the-badge&logo=bookmeter&logoColor=white)
<!-- PERFORMANCE_END -->

---

# ⚡  PROJECT OVERVIEW

**AniList Maximum Overdrive Sync** is an automated AniList tracking, synchronization,
gamification, performance-analysis, notification, and archival engine.

It is designed around a simple idea:

> Your AniList account should not merely record progress.
> It should become the central input for an entire personal tracking system.

The engine watches for meaningful changes in anime and manga progress.

When a new episode or chapter is detected, the system can process the event through
multiple independent subsystems.

Those subsystems can update synchronization state, calculate Gamerscore, calculate
consumption time, update Discord dashboards, send Telegram alerts, archive events,
and preserve state for future workflow executions.

This project is intentionally built for completionists.

It treats progress as data.

It treats data as state.

It treats state as history.

And it turns that history into a live personal dashboard.

---

# 📑 TABLE OF CONTENTS

- [Project Overview](#-0-project-overview)
- [Core Philosophy](#-1-core-philosophy)
- [Design Goals](#-2-design-goals)
- [System Architecture](#-3-system-architecture)
- [Execution Model](#-4-execution-model)
- [State Machine](#-5-state-machine)
- [Anime Synchronization](#-6-anime-synchronization)
- [Manga Synchronization](#-7-manga-synchronization)
- [Airing Intelligence Radar](#-8-airing-intelligence-radar)
- [MAL Ghost Radar](#-9-mal-ghost-radar)
- [Live Game Core](#-10-live-game-core)
- [Gamerscore Rules](#-11-gamerscore-rules)
- [Achievement System](#-12-achievement-system)
- [Live Performance Hologram](#-13-live-performance-hologram)
- [Anime Time Calculation](#-14-anime-time-calculation)
- [Manga Time Calculation](#-15-manga-time-calculation)
- [Performance Vault](#-16-performance-vault)
- [Discord Integration](#-17-discord-integration)
- [Telegram Integration](#-18-telegram-integration)
- [Zulip Integration](#-19-zulip-integration)
- [Repository Structure](#-20-repository-structure)
- [Database Files](#-21-database-files)
- [README Live Badges](#-22-readme-live-badges)
- [GitHub Actions](#-23-github-actions)
- [Secrets](#-24-secrets)
- [Deployment](#-25-deployment)
- [Zulip Configuration](#-26-zulip-configuration)
- [Workflow Lifecycle](#-27-workflow-lifecycle)
- [Error Handling](#-28-error-handling)
- [Troubleshooting](#-29-troubleshooting)
- [Data Safety](#-30-data-safety)
- [Operational Philosophy](#-31-operational-philosophy)
- [Future Expansion](#-32-future-expansion)
- [Author](#-33-author)
- [Final Status](#-34-final-status)

---

# 🧠 1. CORE PHILOSOPHY

> "Progress comes from questioning and reform. Systems should be judged based on fairness and logic."

The standard AniList experience is intentionally simple.

You watch something.

You update your progress.

AniList stores the result.

Maximum Overdrive asks a different question:

> What else can be done with that progress event?

A single progress change can become an event that drives several systems.

```text
AniList Change
      │
      ▼
State Detection
      │
      ├── Synchronization
      │
      ├── Gamerscore
      │
      ├── Achievement
      │
      ├── Performance
      │
      ├── Airing Intelligence
      │
      ├── Discord
      │
      ├── Telegram
      │
      ├── Zulip
      │
      └── Persistent Archive
```

The system therefore follows an event-driven philosophy.

A progress change is not just a number.

It is an event.

---

# 🎯 2. DESIGN GOALS

## 2.1 Automation

The engine should perform repetitive tracking work automatically.

The goal is to avoid manually calculating:

- Episodes watched
- Chapters read
- Minutes consumed
- Gamerscore earned
- Weekly grind
- Completion bonuses
- Airing warnings
- Ghost entries
- Historical statistics

---

## 2.2 Persistence

The engine must remember previous executions.

GitHub Actions runners are temporary.

The repository therefore acts as persistent storage for the engine's state.

JSON files preserve important information between workflow executions.

---

## 2.3 Duplicate Prevention

The system should not repeatedly announce the same progress.

State comparison is used to determine whether a meaningful change happened.

This prevents notification spam.

---

## 2.4 Multi-Platform Broadcasting

Different services have different purposes.

Discord is the visual dashboard.

Telegram is the direct alert channel.

Zulip is the archival communication layer.

GitHub Actions is the execution layer.

AniList is the primary tracking source.

---

## 2.5 Gamification

Tracking becomes more interesting when progress has measurable rewards.

The Live Game Core therefore turns consumption into Gamerscore.

---

## 2.6 Live Analytics

The system should show current activity rather than only historical totals.

The Live Performance Hologram exists for this purpose.

---

# 🏗️ 3. SYSTEM ARCHITECTURE

The project can be understood as several cooperating layers.

```text
┌─────────────────────────────────────────────┐
│                 ANILIST                     │
│             Primary Data Source             │
└──────────────────┬──────────────────────────┘
                   │
                   ▼
┌─────────────────────────────────────────────┐
│              CORE ENGINE                    │
│           anilist_engine.py                 │
└──────────────────┬──────────────────────────┘
                   │
        ┌──────────┼──────────┐
        ▼          ▼          ▼
   State Layer  Game Core  Performance
        │          │          │
        ▼          ▼          ▼
      Sync     Gamerscore   Hologram
        │          │          │
        └──────────┼──────────┘
                   ▼
        ┌─────────────────────┐
        │ Notification Layer  │
        ├─────────────────────┤
        │ Discord             │
        │ Telegram            │
        │ Zulip               │
        └─────────────────────┘
```

---

# ⏱️ 4. EXECUTION MODEL

The engine is designed to run through GitHub Actions.

The workflow acts as the scheduler and execution environment.

The current design uses an hourly operating window from approximately:

**08:00 → 23:00**

The exact behavior is controlled by the workflow configuration.

Each execution performs a fresh processing cycle.

---

## 4.1 Execution Cycle

A normal cycle can be understood as:

```text
1. Start GitHub runner
2. Load repository state
3. Load secrets
4. Contact AniList
5. Read current progress
6. Compare previous state
7. Calculate deltas
8. Process anime events
9. Process manga events
10. Process airing intelligence
11. Process MAL ghosts
12. Update Gamerscore
13. Update performance statistics
14. Update Discord
15. Send Telegram alerts
16. Archive to Zulip
17. Save JSON state
18. Update README badges
19. Commit state changes
20. Finish workflow
```

---

# 🧠 5. STATE MACHINE

The state machine is one of the most important parts of the project.

The engine does not simply ask:

> "What is the current AniList progress?"

It also asks:

> "What was the previous known progress?"

The difference between those values determines whether an event exists.

---

## 5.1 Example

Previous:

```text
Episode = 12
```

Current:

```text
Episode = 13
```

Delta:

```text
+1
```

The engine can therefore process the new episode.

---

## 5.2 No Delta

Previous:

```text
Episode = 13
```

Current:

```text
Episode = 13
```

Delta:

```text
0
```

No new episode event exists.

The engine intentionally avoids sending another normal progress notification.

---

## 5.3 Multiple Episode Delta

If the state changes from:

```text
10 → 13
```

the delta is:

```text
+3
```

The engine can use the delta as the basis for downstream calculations.

This is important because users may update AniList after watching several episodes.

---

# 🔄 6. ANIME SYNCHRONIZATION

Anime synchronization is one of the primary engine functions.

The system reads anime progress from AniList and compares it against its stored synchronization state.

When progress changes, the engine can trigger:

- Anime update notification
- Gamerscore calculation
- Performance calculation
- Achievement processing
- Archive event
- State update

---

## 6.1 Anime Event

Conceptually:

```text
Anime Progress
      │
      ▼
Compare State
      │
      ▼
Episode Delta
      │
      ├── G-Score
      │
      ├── Minutes
      │
      ├── Discord
      │
      ├── Zulip
      │
      └── Database
```

---

# 📖 7. MANGA SYNCHRONIZATION

Manga progress follows the same general state-driven model.

The system compares the previous chapter state against the current chapter state.

A chapter delta can trigger:

- Manga notification
- Gamerscore
- Performance minutes
- Achievement processing
- Zulip archive
- State persistence

---

## 7.1 Manga Example

Previous:

```text
Chapter = 40
```

Current:

```text
Chapter = 45
```

Delta:

```text
+5
```

Gamerscore contribution:

```text
5 × 2 G
```

Performance contribution:

```text
5 × 5 minutes
```

The values are then incorporated into the relevant tracking systems.

---

# 📡 8. AIRING INTELLIGENCE RADAR

The Airing Intelligence Radar watches the user's active anime list for currently airing titles.

Its purpose is to provide useful reminders without requiring manual checking.

---

## 8.1 Three-Hour Warning

The system can send a warning approximately three hours before an expected episode.

The warning is primarily intended for Discord.

---

## 8.2 One-Hour Warning

The final warning is approximately one hour before airing.

This can be sent to:

- Discord
- Telegram

Telegram is particularly useful because it provides a direct mobile notification.

---

## 8.3 Duplicate Protection

Airing notifications use persistent state.

This prevents the same episode from generating repeated warnings during multiple hourly executions.

---

# 👻 9. MAL GHOST RADAR

The MAL Ghost Radar exists for a specific problem:

> An entry may exist in MAL data but not exist in the active AniList account.

These are treated as "ghost" entries.

---

## 9.1 Input Files

The engine can process:

```text
mal_export.xml
mal_anime.xml
```

The files act as external source data.

---

## 9.2 Ghost Detection

Conceptually:

```text
MAL Dataset
    │
    ▼
Extract Titles
    │
    ▼
Compare with AniList
    │
    ▼
Missing Entry?
   / \
 YES  NO
  │    │
  ▼    └── Ignore
Assimilate
```

---

## 9.3 Assimilation

When a valid missing entry is identified, the engine can attempt to create or update the corresponding AniList record using GraphQL mutations.

Successful assimilation can be reported through the Ghost Radar Discord channel.

---

## 9.4 Rejected Entries

AniList may reject certain entries because the corresponding work does not exist in its database.

Examples may include highly specific:

- Doujinshi
- Ecchi entries
- Unregistered works
- Other unsupported database records

The engine should not endlessly retry entries that AniList itself cannot resolve.

---

# 🎮 10. LIVE GAME CORE

The Live Game Core is a permanent part of Maximum Overdrive.

It transforms anime and manga consumption into an RPG-like progression system.

The important distinction is:

**Gamerscore is not a temporary display.**

It is persistent tracking data.

---

## 10.1 Lifetime Gamerscore

Lifetime Gamerscore represents the permanent accumulated score.

Example:

```text
Lifetime Gamerscore
       │
       ├── Episode rewards
       ├── Chapter rewards
       └── Completion bonuses
```

Lifetime score does not represent only the current week.

It represents the overall progression history recorded by the engine.

---

## 10.2 Weekly Grind

Weekly Gamerscore measures current activity.

It provides a second metric:

```text
Lifetime = Long-Term Progress
Weekly   = Current Grind
```

The weekly cycle can reset independently while lifetime progression remains intact.

---

# 🏆 11. GAMERSCORE RULES

Current scoring rules:

| Activity | Reward |
|---|---:|
| Anime episode | +10 G |
| Manga chapter | +2 G |
| Series completion | +100 G |

---

## 11.1 Anime

If:

```text
Episodes = 3
```

Then:

```text
3 × 10 G = 30 G
```

---

## 11.2 Manga

If:

```text
Chapters = 10
```

Then:

```text
10 × 2 G = 20 G
```

---

## 11.3 Completion Bonus

A completed series can provide:

```text
+100 G
```

This is separate from normal episode or chapter rewards.

---

## 11.4 Weekly Reset

The weekly score is designed to represent the current grind.

The lifetime score remains the permanent record.

---

# 🥇 12. ACHIEVEMENT SYSTEM

The Gamerscore system is paired with milestone tracking.

Current milestone examples include:

```text
1,000 G
5,000 G
```

When an important threshold is crossed, the engine can send an achievement notification.

Achievement processing can be delivered through Discord.

---

## 12.1 Why Milestones Exist

A raw number is useful.

A milestone is memorable.

The achievement layer turns large amounts of accumulated tracking data into recognizable progression events.

---

# ⚡ 13. LIVE PERFORMANCE HOLOGRAM

The Live Performance Hologram is another core system and must remain active alongside the Live Game Core.

It is the engine's live consumption analytics dashboard.

The Hologram answers questions such as:

- How many episodes were consumed today?
- How many chapters were consumed today?
- How much estimated time was spent?
- What does the current performance look like?
- What is the current daily grind?

---

## 13.1 Discord Dashboard

The Hologram is designed around a dedicated Discord message.

The message is continuously refreshed.

Instead of endlessly posting new dashboard messages, the engine tracks the existing message ID.

---

## 13.2 Refresh Process

```text
Find Existing Message
        │
        ▼
Delete / Replace
        │
        ▼
Calculate Current Stats
        │
        ▼
Generate Dashboard
        │
        ▼
Post Fresh Message
        │
        ▼
Save New Message ID
```

---

## 13.3 Why a Message ID Is Stored

Discord messages have unique identifiers.

The engine stores the current performance message ID in:

```text
db_performance_msg.json
```

This allows later workflow executions to locate the dashboard.

---

# ⏱️ 14. ANIME TIME CALCULATION

Anime performance is calculated using episode duration information obtained from AniList.

The engine can calculate estimated viewing time rather than simply counting episodes.

---

## 14.1 Opening and Ending Deduction

The system automatically deducts approximately:

```text
2 minutes
```

from the listed episode duration.

This attempts to represent effective content consumption rather than counting the full listed runtime.

---

## 14.2 Example

If an episode duration is:

```text
24 minutes
```

Effective calculation:

```text
24 - 2 = 22 minutes
```

For:

```text
5 episodes
```

the estimated consumption becomes:

```text
5 × 22 = 110 minutes
```

---

# 📖 15. MANGA TIME CALCULATION

Manga does not provide the same standardized duration metadata as anime.

The engine therefore uses a fixed estimate:

```text
1 chapter = 5 minutes
```

---

## 15.1 Example

For:

```text
8 chapters
```

Estimated time:

```text
8 × 5 = 40 minutes
```

This is an analytical estimate rather than a measurement of the reader's literal time.

---

# 📊 16. PERFORMANCE VAULT

Performance information is stored in a dedicated directory.

```text
performance/
├── daily/
├── weekly/
├── monthly/
└── yearly/
```

---

## 16.1 Daily Vault

Daily records use a date-based filename.

Example:

```text
performance/daily/2026-08-12.json
```

The daily record can contain:

- Episode count
- Chapter count
- Estimated minutes
- Other engine performance values

---

## 16.2 Weekly Vault

Weekly data groups daily activity into a larger period.

This is useful for understanding short-term consistency.

---

## 16.3 Monthly Vault

Monthly data provides a broader view of consumption.

---

## 16.4 Yearly Vault

Yearly data provides long-term historical tracking.

---

# 🎨 17. DISCORD INTEGRATION

Discord acts as the main visual output layer.

Different webhooks can be assigned to different purposes.

---

## 17.1 Anime Updates

Anime progress events can be delivered to the anime update webhook.

---

## 17.2 Manga Updates

Manga progress events can be delivered to the manga update webhook.

---

## 17.3 Airing Alerts

Airing warnings use a dedicated webhook.

---

## 17.4 Diagnostics

System errors and diagnostics use a dedicated logging webhook.

---

## 17.5 Favorites

Priority franchise updates can use a dedicated favorites webhook.

---

## 17.6 Ghost Radar

Ghost assimilation events can use a dedicated Ghost Radar webhook.

---

## 17.7 Achievements

Gamerscore milestones and weekly cycles can use the achievement webhook.

---

## 17.8 Performance

The Live Performance Hologram uses:

```text
DISCORD_PERFORMANCE_WEBHOOK
```

This keeps the performance dashboard separate from normal progress spam.

---

# 📱 18. TELEGRAM INTEGRATION

Telegram is the direct-alert layer.

The system uses a Telegram bot to send high-priority messages.

---

## 18.1 Typical Use

Telegram is useful for:

- One-hour airing warnings
- Direct personal alerts
- Important automated notifications

---

## 18.2 Required Values

The engine requires:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

The bot token is generated through BotFather.

The chat ID identifies the intended destination.

---

# 🗄️ 19. ZULIP INTEGRATION

Zulip functions as an archival and structured communication layer.

The system can organize information into dedicated stream topics.

Example architecture:

```text
Anime Vault
   ├── progress
   ├── logs
   └── history

Manga Vault
   ├── progress
   ├── logs
   └── history
```

The exact topic structure depends on the implementation.

---

# 📂 20. REPOSITORY STRUCTURE

The core repository is organized around the engine, workflow, performance vault,
state databases, and source data.

```text
Anilist-Triple-Sync/
│
├── .github/
│   └── workflows/
│       └── sync_engine.yml
│
├── performance/
│   ├── daily/
│   ├── weekly/
│   ├── monthly/
│   └── yearly/
│
├── anilist_engine.py
├── db_achievements.json
├── db_airing.json
├── db_ghosts.json
├── db_messages.json
├── db_performance_msg.json
├── db_sync.json
├── mal_anime.xml
├── mal_export.xml
└── README.md
```

---

# 🗃️ 21. DATABASE FILES

## `db_sync.json`

Master synchronization ledger.

It stores information required to compare previous and current progress.

---

## `db_achievements.json`

Gamerscore and achievement state.

It tracks lifetime and weekly Gamerscore information.

---

## `db_airing.json`

Airing notification state.

It helps prevent duplicate warnings.

---

## `db_ghosts.json`

Ghost Radar processing ledger.

It helps remember which MAL-derived entries have already been processed.

---

## `db_messages.json`

Discord message cleanup queue.

It supports management of temporary Discord messages.

---

## `db_performance_msg.json`

Stores the Live Performance Hologram message identifier.

This is essential for dashboard refresh behavior.

---

# 🏷️ 22. README LIVE BADGES

The README itself is treated as a live status surface.

Two main badge groups are maintained.

---

## 22.1 Gamerscore Badges

```text
<!-- BADGES_START -->
![Gamerscore](https://img.shields.io/badge/Lifetime_Gamerscore-5024%20G-FFD700?style=for-the-badge&logo=epic-games&logoColor=black)
![Weekly](https://img.shields.io/badge/Weekly_Grind-658%20G-FF4500?style=for-the-badge&logo=graphql&logoColor=white)
<!-- BADGES_END -->
```

These represent:

- Lifetime Gamerscore
- Weekly Grind

---

## 22.2 Performance Badges

```text
<!-- PERFORMANCE_START -->
...
<!-- PERFORMANCE_END -->
```

These represent:

- Daily episodes
- Daily chapters

The engine can update these values automatically.

---

## 22.3 Why Use Badges?

The repository homepage becomes a quick status screen.

Instead of opening Discord or inspecting JSON files, the current headline statistics can be visible directly from GitHub.

---

# ⚙️ 23. GITHUB ACTIONS

GitHub Actions is the automation layer.

The workflow is responsible for launching the engine according to its configured schedule.

---

## 23.1 Workflow Responsibilities

The workflow can:

- Start the Python engine
- Provide secrets
- Execute scheduled cycles
- Preserve repository state
- Commit generated state
- Update README badges

---

## 23.2 Cron Scheduling

The workflow uses a cron schedule.

The intended operating window is approximately:

```text
08:00 → 23:00
```

with hourly execution according to the workflow's cron configuration.

---

## 23.3 Repository State

After processing, generated state can be committed back to the repository.

This is important because GitHub-hosted runners are ephemeral.

---

# 🔐 24. SECRETS

All credentials must be stored through GitHub Actions Secrets.

Required secrets include:

| Secret | Purpose |
|---|---|
| `ANILIST_TARGET_TOKEN` | AniList authentication |
| `DISCORD_ANILIST_ANIME_WEBHOOK` | Anime updates |
| `DISCORD_ANILIST_MANGA_WEBHOOK` | Manga updates |
| `DISCORD_AIRING_WEBHOOK` | Airing alerts |
| `DISCORD_ANILIST_LOG_WEBHOOK` | Diagnostics |
| `DISCORD_FAVORITES_WEBHOOK` | Favorite franchise updates |
| `DISCORD_GHOST_RADAR_WEBHOOK` | Ghost Radar |
| `DISCORD_ACHIEVEMENTS_WEBHOOK` | Gamerscore |
| `DISCORD_PERFORMANCE_WEBHOOK` | Performance Hologram |
| `TELEGRAM_BOT_TOKEN` | Telegram authentication |
| `TELEGRAM_CHAT_ID` | Telegram destination |
| `ZULIP_BOT_EMAIL` | Zulip bot identity |
| `ZULIP_API_KEY` | Zulip authentication |
| `ZULIP_SERVER_URL` | Zulip endpoint |

---

## 🚨 Secret Rule

Never place real tokens directly into:

```text
anilist_engine.py
sync_engine.yml
README.md
JSON databases
```

Secrets belong in GitHub's secret manager.

---

# 🚀 25. DEPLOYMENT

A basic deployment process is:

```text
1. Create repository
2. Add Python engine
3. Add workflow
4. Add performance directories
5. Add JSON state files
6. Add MAL XML source files
7. Configure GitHub Secrets
8. Configure Discord webhooks
9. Configure Telegram bot
10. Configure Zulip bot
11. Test workflow manually
12. Verify generated state
13. Verify notifications
14. Verify README badges
15. Enable scheduled execution
```

---

# 🧪 25.1 INITIAL TEST

Before relying on scheduled execution, run the workflow manually.

Check:

```text
✓ AniList authentication
✓ Discord connectivity
✓ Telegram connectivity
✓ Zulip connectivity
✓ JSON state loading
✓ Performance calculation
✓ Gamerscore calculation
✓ README badge update
✓ Git commit behavior
```

---

# 🟢 25.2 PRODUCTION TEST

After a successful manual run, allow the scheduled workflow to execute.

Monitor the GitHub Actions logs for the first several cycles.

---

# 🧩 26. ZULIP CONFIGURATION

Zulip has an important domain requirement.

The bot email domain and server URL must correspond to the same Zulip server.

---

## Step 1 — Create Bot

Open the Zulip server settings.

Navigate to:

```text
Settings
   ↓
Personal settings
   ↓
Bots
```

Create an Incoming Webhook bot.

---

## Step 2 — Verify Bot Email

Example:

```text
matrix-engine-bot@tokyo.zulipchat.com
```

The domain is:

```text
tokyo.zulipchat.com
```

---

## Step 3 — Match Server URL

Correct:

```text
https://tokyo.zulipchat.com/api/v1/messages
```

Incorrect:

```text
https://orewatokyo.zulipchat.com/api/v1/messages
```

The domain mismatch can produce:

```text
401 UNAUTHORIZED
```

---

## Step 4 — API Key

Copy the complete API key.

Avoid:

- Trailing spaces
- Extra line breaks
- Partial tokens
- Accidental quotation marks

---

# 🔁 27. WORKFLOW LIFECYCLE

A complete engine cycle can be visualized as:

```text
┌───────────────┐
│ GitHub Action │
│    Starts     │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Load Secrets  │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Load State    │
└───────┬───────┘
        │
        ▼
┌───────────────┐
│ Query AniList │
└───────┬───────┘
        │
        ▼
┌────────────────┐
│ Calculate Delta│
└───────┬────────┘
        │
   ┌────┼────┐
   ▼    ▼    ▼
 Anime Manga Airing
   │    │    │
   └────┼────┘
        ▼
┌────────────────┐
│ Live Game Core │
└───────┬────────┘
        │
        ▼
┌───────────────────┐
│ Performance Core  │
└───────┬───────────┘
        │
        ▼
┌────────────────────┐
│ Notification Layer │
└───────┬────────────┘
        │
   ┌────┼─────┐
   ▼    ▼     ▼
Discord Telegram Zulip
        │
        ▼
┌──────────────────┐
│ Save State       │
└───────┬──────────┘
        │
        ▼
┌──────────────────┐
│ Update README    │
└───────┬──────────┘
        │
        ▼
┌──────────────────┐
│ Commit Changes   │
└──────────────────┘
```

---

# 🛡️ 28. ERROR HANDLING

The engine includes diagnostic behavior designed to expose failures through logs.

A failed external request should be investigated through GitHub Actions first.

The objective is:

```text
Failure
  ↓
Diagnostic Output
  ↓
Identify Component
  ↓
Fix Configuration
  ↓
Retry
```

---

# 🧰 29. TROUBLESHOOTING

## Error: Discord Webhook Missing

Example:

```text
Discord Webhook missing for: UPDATE
```

### Cause

The secret name in the workflow does not exactly match the GitHub Secret.

### Fix

Check the spelling of:

```text
DISCORD_ANILIST_ANIME_WEBHOOK
DISCORD_ANILIST_MANGA_WEBHOOK
```

and the corresponding workflow variables.

---

## Error: Zulip 401

Example:

```text
Zulip Status [401]
```

### Cause

Domain mismatch.

### Check

```text
ZULIP_BOT_EMAIL
ZULIP_SERVER_URL
```

Both must reference the same Zulip server.

---

## Error: Discord Has No New Update

### Cause

The state machine detected zero progress delta.

Example:

```text
Previous = 20
Current  = 20
Delta    = 0
```

This is expected behavior.

The engine is preventing duplicate spam.

---

## Error: Hologram Did Not Delete

### Cause

The stored message ID may be invalid.

Possible reasons:

- Message manually deleted
- Message ID lost
- Discord rejected the request
- Webhook configuration changed

### Recovery

The engine can create a new dashboard and store the new message ID.

---

## Error: README Badge Not Updated

### Possible Causes

- Workflow permission issue
- Git push failure
- Badge replacement markers changed
- Script could not locate the expected block

Verify that these markers remain intact:

```text
<!-- BADGES_START -->
![Gamerscore](https://img.shields.io/badge/Lifetime_Gamerscore-5024%20G-FFD700?style=for-the-badge&logo=epic-games&logoColor=black)
![Weekly](https://img.shields.io/badge/Weekly_Grind-658%20G-FF4500?style=for-the-badge&logo=graphql&logoColor=white)
<!-- BADGES_END -->

<!-- PERFORMANCE_START -->
<!-- PERFORMANCE_END -->
```

Do not casually rename or remove these markers.

---

# 🧹 29.1 MESSAGE CLEANUP

Discord can become noisy when automated systems produce large numbers of messages.

The engine therefore maintains message-related state.

The cleanup queue is associated with:

```text
db_messages.json
```

This allows the engine to track messages that may require later cleanup.

---

# 💾 29.2 STATE RECOVERY

If the engine loses a temporary Discord dashboard message, the core tracking data should remain separate.

This is an intentional architectural principle:

```text
Temporary UI State
        ≠
Permanent Tracking State
```

The performance message can be recreated.

The historical performance vault remains the important record.

---

# 🔒 30. DATA SAFETY

The repository may contain personal tracking data.

Treat the repository accordingly.

---

## Never Commit

Do not commit:

```text
AniList OAuth tokens
Discord webhook URLs
Telegram bot tokens
Zulip API keys
Private credentials
```

---

## Source Data

MAL XML files may contain personal watch-history information.

If the repository is public, consider whether these files should remain private.

---

## Repository Visibility

A private repository is strongly recommended when the project contains:

- Personal tracking history
- Private webhook configuration
- Personal identifiers
- Detailed consumption statistics

---

# 🧠 31. OPERATIONAL PHILOSOPHY

Maximum Overdrive is intentionally excessive.

A normal tracker might answer:

> "What episode am I on?"

Maximum Overdrive wants to answer:

> "What did I consume, how much did it contribute to my Gamerscore,
> how much estimated time did it represent, was it airing,
> was it synchronized, was it archived, and what should the dashboard show?"

That is the point.

---

# ⚡ 31.1 LIVE MEANS LIVE

The project has two major live systems.

## 🎮 Live Game Core

Tracks:

- Lifetime Gamerscore
- Weekly Gamerscore
- Episode rewards
- Chapter rewards
- Completion bonuses
- Milestones

## ⚡ Live Performance Hologram

Tracks:

- Daily episodes
- Daily chapters
- Estimated minutes
- Performance history
- Discord dashboard state

Neither system should be treated as decorative.

They are part of the engine's core functionality.

---

# 🏆 31.2 COMPLETIONIST ARCHITECTURE

The project is designed around completionist behavior.

The system rewards activity.

It preserves activity.

It visualizes activity.

It archives activity.

This produces a loop:

```text
Consume
  ↓
Update AniList
  ↓
Engine Detects Progress
  ↓
Earn G
  ↓
Calculate Time
  ↓
Update Dashboard
  ↓
Archive
  ↓
Continue
```

---

# 🔥 31.3 WHY GITHUB ACTIONS?

GitHub Actions provides:

- Scheduled execution
- Linux runners
- Secret management
- Workflow logs
- Repository integration
- Automated commits
- Manual workflow dispatch

This makes the repository capable of functioning as a small autonomous tracking service.

---

# 🧬 31.4 WHY JSON STATE?

JSON is simple, inspectable, portable, and Git-friendly.

A state file can be viewed directly without requiring a database server.

For this personal-scale system, that simplicity is valuable.

---

# 📚 31.5 WHY ZULIP?

Zulip provides structured conversations through streams and topics.

This makes it useful as an archival communication layer.

Instead of one endless chat history, engine events can be separated into logical categories.

---

# 📡 31.6 WHY TELEGRAM?

Telegram provides a direct personal notification channel.

Discord is excellent for dashboards.

Telegram is better suited to immediate mobile alerts.

The architecture therefore gives each platform a specific responsibility.

---

# 🎨 31.7 WHY DISCORD?

Discord provides the visual presentation layer.

It can display:

- Rich embeds
- Cover art
- Achievement announcements
- Performance dashboards
- Airing alerts
- Sync events
- Ghost Radar activity

The result feels closer to a live control room than a traditional tracker.

---

# 🧪 31.8 TESTING PHILOSOPHY

Every subsystem should be testable independently.

Suggested testing order:

```text
1. AniList
2. State
3. Anime
4. Manga
5. Gamerscore
6. Performance
7. Discord
8. Telegram
9. Zulip
10. README
11. Git commit
```

This makes failures easier to isolate.

---

# 🧭 32. FUTURE EXPANSION

Maximum Overdrive is intentionally modular.

Potential future components can be added without redesigning the entire system.

Possible expansion areas include:

- More achievement tiers
- Additional performance metrics
- More detailed weekly reports
- Monthly reports
- Yearly reports
- Advanced completion statistics
- Additional notification platforms
- Expanded MAL reconciliation
- More dashboard visualizations
- More archive categories
- Additional README statistics

The architecture should continue to separate:

```text
Input
→ Processing
→ State
→ Analytics
→ Output
```

---

# 🧱 32.1 MODULARITY

The engine should avoid turning every feature into one giant block of tightly coupled logic.

A useful conceptual separation is:

```text
AniList
  ↓
Core State
  ↓
Feature Engines
  ├── Sync
  ├── Airing
  ├── Ghost Radar
  ├── Game Core
  └── Performance
  ↓
Output Services
  ├── Discord
  ├── Telegram
  └── Zulip
```

This makes future changes safer.

---

# 🔄 32.2 SELF-HEALING PRINCIPLE

Temporary output failures should not destroy permanent tracking state.

For example:

```text
Discord dashboard missing
        ↓
Recreate dashboard
        ↓
Save new message ID
```

rather than:

```text
Discord dashboard missing
        ↓
Destroy tracking system
```

The engine should favor recovery over catastrophic failure.

---

# 📈 32.3 HISTORICAL DATA

Historical performance matters because current activity does not tell the entire story.

A user may have:

```text
Slow Day
Busy Week
Massive Month
Huge Year
```

The performance vault exists to preserve that history.

---

# 🏁 33. AUTHOR

**Orewa Tokyo**

- 🇮🇳 Tamil Nadu, India
- 🧠 Rationalist
- 🎌 Otaku
- 🏆 S-Tier Completionist

## Favorite Protagonists

- Roronoa Zoro
- Edward Kenway
- Nathan Drake

---

# 💬 33.1 AUTHOR PHILOSOPHY

> "No sugar-coating. Just logic, structure, and maximum energy."

The project is intentionally built around automation, persistence, transparency, and measurable progress.

---

# 🛰️ 34. FINAL STATUS

```text
╔══════════════════════════════════════════════╗
║          MAXIMUM OVERDRIVE STATUS            ║
╠══════════════════════════════════════════════╣
║ Engine Status      : ONLINE                   ║
║ State Machine      : ACTIVE                   ║
║ AniList Sync       : ARMED                    ║
║ MAL Ghost Radar    : ARMED                    ║
║ Airing Radar       : ARMED                    ║
║ Live Game Core     : ONLINE                   ║
║ Gamerscore Engine  : ONLINE                   ║
║ Performance Core   : ONLINE                   ║
║ Live Hologram      : ONLINE                   ║
║ Discord Layer      : CONNECTED                ║
║ Telegram Layer     : CONNECTED                ║
║ Zulip Archive      : CONNECTED                ║
║ Vault Connection   : SECURED                  ║
║ README Telemetry   : ACTIVE                   ║
║ Synchronization    : ARMED                    ║
╚══════════════════════════════════════════════╝
```

```text
                 SYSTEM READY

       ██████╗ ██╗   ██╗███████╗██████╗
      ██╔═══██╗██║   ██║██╔════╝██╔══██╗
      ██║   ██║██║   ██║█████╗  ██████╔╝
      ██║▄▄ ██║██║   ██║██╔══╝  ██╔══██╗
      ╚██████╔╝╚██████╔╝███████╗██║  ██║
       ╚══▀▀═╝  ╚═════╝ ╚══════╝╚═╝  ╚═╝

             MAXIMUM OVERDRIVE

          SYNCHRONIZATION ARMED
             PERFORMANCE LIVE
             GAME CORE LIVE
             VAULT SECURED

              INITIATING CYCLE...
```

---

# 📜 PROJECT PRINCIPLE

> Track everything.
>
> Archive everything.
>
> Automate everything.
>
> Calculate everything.
>
> And when the numbers go up...
>
> **LET THE GAMERSCORE KNOW.** ⚡🎮

---

# 🔥 END OF README

**AniList Maximum Overdrive Sync**

`State-driven • Automated • Persistent • Gamified • Live`

```text
ENGINE STATUS: ONLINE
MAXIMUM OVERDRIVE: ENGAGED
```


---

# 📘 APPENDIX A — COMPONENT REFERENCE

| Component | Primary Responsibility |
|---|---|
| AniList | Primary anime/manga progress source |
| `anilist_engine.py` | Core processing engine |
| GitHub Actions | Scheduled execution |
| `db_sync.json` | Synchronization memory |
| `db_achievements.json` | Gamerscore memory |
| `db_airing.json` | Airing alert memory |
| `db_ghosts.json` | Ghost Radar memory |
| `db_messages.json` | Discord message queue |
| `db_performance_msg.json` | Hologram message memory |
| `performance/` | Historical performance vault |
| Discord | Visual notification layer |
| Telegram | Direct alert layer |
| Zulip | Archive layer |
| README.md | Human-readable status surface |

---

# 📘 APPENDIX B — EVENT TYPES

The engine conceptually processes several event classes.

## Anime Progress Event

Triggered when anime progress increases.

Possible outputs:

- Gamerscore
- Performance
- Discord
- Archive
- State update

## Manga Progress Event

Triggered when manga progress increases.

Possible outputs:

- Gamerscore
- Performance
- Discord
- Archive
- State update

## Completion Event

Triggered when a tracked title reaches completion.

Possible output:

- Completion bonus
- Achievement notification
- Archive event

## Airing Event

Triggered by proximity to an expected airing time.

Possible outputs:

- Three-hour warning
- One-hour warning
- Telegram alert

## Ghost Event

Triggered when MAL data identifies an entry absent from the target AniList account.

Possible outputs:

- Assimilation attempt
- Ghost Radar notification
- Ghost ledger update

---

# 📘 APPENDIX C — GAMERSCORE REFERENCE

### Episode

```text
1 episode = 10 G
```

### Chapter

```text
1 chapter = 2 G
```

### Completion

```text
1 completed series = 100 G
```

### Example

```text
4 episodes
+
15 chapters
+
1 completion

= 4 × 10
+ 15 × 2
+ 100

= 170 G
```

The exact final behavior depends on how the engine detects the associated events.

---

# 📘 APPENDIX D — PERFORMANCE REFERENCE

### Anime

```text
Effective Minutes
=
Episode Duration
-
Opening/Ending Deduction
```

The current deduction is approximately two minutes per episode.

### Manga

```text
Estimated Minutes
=
Chapter Count × 5
```

These values are estimates intended for consistent analytics.

They are not claims about exact real-world reading or viewing duration.

---

# 📘 APPENDIX E — LIVE DASHBOARD CONCEPT

The Live Performance Hologram can be thought of as a continuously regenerated status panel.

```text
┌─────────────────────────────────────┐
│       LIVE PERFORMANCE HOLOGRAM     │
├─────────────────────────────────────┤
│ Daily Episodes      : XX            │
│ Daily Chapters      : XX            │
│ Estimated Minutes   : XXX           │
│                                     │
│ Gamerscore          : XXXX G        │
│ Weekly Grind        : XXX G         │
└─────────────────────────────────────┘
```

The exact visual formatting belongs to the Discord implementation.

The README documents the architecture rather than locking the dashboard to one visual design.

---

# 📘 APPENDIX F — REPOSITORY MEMORY MODEL

The repository effectively has several memory layers.

## Immediate State

Used for current synchronization.

```text
db_sync.json
```

## Achievement State

Used for Gamerscore progression.

```text
db_achievements.json
```

## Alert State

Used for airing notifications.

```text
db_airing.json
```

## Ghost State

Used for MAL reconciliation.

```text
db_ghosts.json
```

## UI State

Used for Discord message management.

```text
db_messages.json
db_performance_msg.json
```

## Historical State

Used for performance records.

```text
performance/
```

This separation reduces the risk that one subsystem's temporary failure destroys unrelated data.

---

# 📘 APPENDIX G — BADGE CONTRACT

The engine expects the README badge markers to remain stable.

Do not remove:

```text
<!-- BADGES_START -->
![Gamerscore](https://img.shields.io/badge/Lifetime_Gamerscore-5024%20G-FFD700?style=for-the-badge&logo=epic-games&logoColor=black)
![Weekly](https://img.shields.io/badge/Weekly_Grind-658%20G-FF4500?style=for-the-badge&logo=graphql&logoColor=white)
<!-- BADGES_END -->
```

Do not remove:

```text
<!-- PERFORMANCE_START -->
<!-- PERFORMANCE_END -->
```

These markers act as machine-readable anchors.

The surrounding human-readable README can evolve without changing the automation contract.

---

# 📘 APPENDIX H — OPERATING CHECKLIST

Before first deployment:

- [ ] Repository exists
- [ ] Workflow exists
- [ ] Python engine exists
- [ ] Performance directories exist
- [ ] State JSON files exist
- [ ] MAL source files are available
- [ ] AniList token is configured
- [ ] Discord webhooks are configured
- [ ] Telegram bot is configured
- [ ] Zulip bot is configured
- [ ] Workflow permissions are correct
- [ ] Manual test succeeds
- [ ] README badge update succeeds
- [ ] State commit succeeds

---

# 📘 APPENDIX I — MAINTENANCE CHECKLIST

When changing the engine:

- [ ] Preserve state-file compatibility
- [ ] Preserve README markers
- [ ] Preserve Live Game Core
- [ ] Preserve Live Performance Hologram
- [ ] Preserve secret names unless intentionally migrated
- [ ] Test AniList requests
- [ ] Test Discord requests
- [ ] Test Telegram requests
- [ ] Test Zulip requests
- [ ] Test GitHub Actions
- [ ] Inspect generated JSON
- [ ] Inspect README changes
- [ ] Verify no credentials were committed

---

# 📘 APPENDIX J — DEBUGGING ORDER

When something breaks, investigate in this order:

```text
1. GitHub Actions run status
2. Authentication
3. AniList request
4. State loading
5. Delta calculation
6. Feature processing
7. External webhook
8. State saving
9. Git commit
10. README update
```

This order follows the approximate execution lifecycle.

---

# 📘 APPENDIX K — PRINCIPLE OF SEPARATION

The engine intentionally separates:

```text
DATA
PROCESSING
STATE
OUTPUT
ARCHIVE
```

For example:

AniList is data.

Python is processing.

JSON is state.

Discord is output.

Zulip is archive.

GitHub is execution and persistence infrastructure.

This separation makes the system easier to reason about.

---

# 📘 APPENDIX L — NORMAL EXECUTION EXAMPLE

Imagine an anime moves from episode 7 to episode 8.

The engine detects:

```text
Previous = 7
Current  = 8
Delta    = 1
```

The event can then produce:

```text
+10 G
+Episode Performance
+Estimated Viewing Minutes
+Discord Update
+Archive Event
```

The state is then saved as:

```text
Current = 8
```

On the next run, the engine sees:

```text
Previous = 8
Current  = 8
Delta    = 0
```

No duplicate episode reward should be generated from the unchanged state.

---

# 📘 APPENDIX M — MULTI-EPISODE EXAMPLE

Suppose the stored state says:

```text
Episode = 20
```

AniList now reports:

```text
Episode = 23
```

The detected delta is:

```text
3
```

The Game Core contribution is:

```text
3 × 10 G = 30 G
```

The Performance Core processes the corresponding three episodes.

The Discord layer can report the progress.

The state ledger is updated to:

```text
23
```

---

# 📘 APPENDIX N — MULTI-CHAPTER EXAMPLE

Suppose the stored manga state is:

```text
Chapter = 100
```

Current AniList state:

```text
Chapter = 108
```

Delta:

```text
8
```

Gamerscore:

```text
8 × 2 G = 16 G
```

Estimated reading time:

```text
8 × 5 = 40 minutes
```

The event can then flow through the notification and archive systems.

---

# 📘 APPENDIX O — FAILURE ISOLATION

A notification failure should not automatically imply a tracking failure.

For example:

```text
AniList ✓
State ✓
Gamerscore ✓
Performance ✓
Discord ✗
```

This is different from:

```text
AniList ✗
State ?
Gamerscore ?
Performance ?
```

The diagnostic system exists to make such distinctions visible.

---

# 📘 APPENDIX P — LIVE GAME CORE VS PERFORMANCE CORE

These systems are intentionally different.

## Live Game Core

Measures:

```text
PROGRESSION
```

Examples:

- G earned
- Weekly grind
- Lifetime score
- Completion rewards

## Performance Core

Measures:

```text
CONSUMPTION
```

Examples:

- Episodes
- Chapters
- Estimated minutes
- Daily activity
- Historical activity

A user can therefore have:

```text
High Performance
Low Gamerscore
```

or:

```text
High Gamerscore
Low Current Performance
```

because the systems answer different questions.

---

# 📘 APPENDIX Q — AIRING RADAR VS PROGRESS SYNC

These are also separate systems.

Airing Radar asks:

> "When should I expect an episode?"

Progress Sync asks:

> "What progress has already happened?"

They can operate simultaneously without being the same feature.

---

# 📘 APPENDIX R — GHOST RADAR VS NORMAL SYNC

Ghost Radar is reconciliation.

Normal synchronization is ongoing progress tracking.

Ghost Radar asks:

> "What should exist but does not?"

Normal synchronization asks:

> "What changed since the last run?"

This distinction prevents the core sync engine from becoming responsible for every possible data-recovery scenario.

---

# 📘 APPENDIX S — ARCHIVE PHILOSOPHY

The system uses multiple layers of persistence because different information has different purposes.

JSON is useful for machine state.

Performance files are useful for historical statistics.

Zulip is useful for human-readable logs.

Git history provides an additional timeline of repository changes.

Together they form a layered archive.

---

# 📘 APPENDIX T — README AS A CONTROL SURFACE

The README is not only documentation.

Because the engine updates its badge sections, the README also acts as a lightweight public-facing status surface.

This creates a useful split:

```text
README
  ↓
Quick Status

Discord
  ↓
Live Visual Dashboard

JSON
  ↓
Machine State

Performance Vault
  ↓
Historical Data

Zulip
  ↓
Communication Archive
```

---

# 📘 APPENDIX U — SECURITY PRINCIPLE

Credentials are infrastructure secrets.

Tracking statistics are data.

The README is documentation.

These should not be mixed together.

The engine should therefore keep:

```text
Secrets → GitHub Secret Manager
State   → JSON
Stats   → Performance Vault
Docs    → README
```

---

# 📘 APPENDIX V — REPRODUCIBILITY

A good automation system should be understandable after it has been running for a long time.

The repository therefore stores enough state and documentation to explain:

- What the engine does
- What files it uses
- What each state file means
- What credentials are required
- What external services are connected
- How the workflow operates
- How failures can be diagnosed

---

# 📘 APPENDIX W — COMPLETIONIST LOOP

The complete philosophy can be summarized as:

```text
WATCH
  ↓
TRACK
  ↓
SYNC
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

This is the Maximum Overdrive loop.

---

# 📘 APPENDIX X — SYSTEM IDENTITY

The project is not merely:

```text
AniList Sync Script
```

It is better described as:

```text
Personal Anime & Manga Tracking Automation Engine
```

with:

```text
Synchronization
+
Gamification
+
Performance Analytics
+
Notifications
+
Archival
```

---

# 📘 APPENDIX Y — FINAL ARCHITECTURE MAP

```text
                         ┌───────────────┐
                         │    AniList    │
                         └───────┬───────┘
                                 │
                                 ▼
                     ┌─────────────────────┐
                     │ anilist_engine.py   │
                     └──────────┬──────────┘
                                │
              ┌─────────────────┼─────────────────┐
              │                 │                 │
              ▼                 ▼                 ▼
        ┌──────────┐      ┌───────────┐     ┌─────────────┐
        │   Sync   │      │ Game Core │     │ Performance │
        └────┬─────┘      └─────┬─────┘     └──────┬──────┘
             │                  │                  │
             ▼                  ▼                  ▼
        db_sync.json     db_achievements    performance/
                              .json
             │                  │                  │
             └──────────────────┼──────────────────┘
                                │
                                ▼
                     ┌─────────────────────┐
                     │ Notification Layer  │
                     └──────────┬──────────┘
                                │
                    ┌───────────┼───────────┐
                    ▼           ▼           ▼
                 Discord     Telegram     Zulip
                    │           │           │
                    └───────────┼───────────┘
                                ▼
                     ┌─────────────────────┐
                     │ Persistent Archive  │
                     └──────────┬──────────┘
                                │
                                ▼
                         GitHub Repository
```

---

# 📘 APPENDIX Z — MAXIMUM OVERDRIVE COMMANDMENT

```text
Do not manually calculate what a machine can calculate.

Do not repeatedly process what state can remember.

Do not throw away what historical data can preserve.

Do not hide progress that can be visualized.

Do not let a tracker remain merely a tracker.

Turn progress into information.
Turn information into history.
Turn history into progression.

MAXIMUM OVERDRIVE.
```

