# ⚡ ANILIST MAXIMUM OVERDRIVE SYNC — V2 ENGINE DOCUMENTATION ⚡

```text
███╗   ███╗ █████╗ ██╗  ██╗██╗███╗   ███╗██╗   ██╗███╗   ███╗
████╗ ████║██╔══██╗╚██╗██╔╝██║████╗ ████║██║   ██║████╗ ████║
██╔████╔██║███████║ ╚███╔╝ ██║██╔████╔██║██║   ██║██╔████╔██║
██║╚██╔╝██║██╔══██║ ██╔██╗ ██║██║╚██╔╝██║██║   ██║██║╚██╔╝██║
██║ ╚═╝ ██║██║  ██║██╔╝ ██╗██║██║ ╚═╝ ██║╚██████╔╝██║ ╚═╝ ██║
╚═╝     ╚═╝╚═╝  ╚═╝╚═╝  ╚═╝╚═╝╚═╝     ╚═╝ ╚═════╝ ╚═╝     ╚═╝
        V 2   T E L E M E T R Y   &   A N A L Y T I C S
```

> **Source of truth:** this README documents the currently uploaded
> `anilist_engine.py` implementation, including its current behavior,
> file names, environment variables, data flow, and known implementation notes.

---

# 📌 PROJECT IDENTITY

**Project:** AniList Maximum Overdrive Sync  
**Engine:** Maximum Overdrive V2  
**Runtime:** Python  
**Primary API:** AniList GraphQL  
**Automation:** GitHub Actions compatible  
**Primary Output:** Discord Webhooks  
**Direct Alert Output:** Telegram  
**Archive Output:** Zulip  
**State:** JSON files  
**Source Reconciliation:** MyAnimeList XML exports  
**Performance:** Daily / Weekly / Monthly / Yearly / Lifetime vaults  
**Telemetry:** Discord Performance Hologram + README injection

The engine is designed as a scheduled personal anime and manga synchronization system.

It does not only synchronize progress.

It also maintains:

```text
Gamerscore
Weekly Grind
Performance Time
Airing Alerts
MAL Ghosts
Deep Void Entries
Discord Messages
Achievement Milestones
README Telemetry
```

---

# 📑 TABLE OF CONTENTS

1. [Executive Overview](#1-executive-overview)
2. [Engine Responsibilities](#2-engine-responsibilities)
3. [Configuration](#3-configuration)
4. [Environment Variables](#4-environment-variables)
5. [JSON State Files](#5-json-state-files)
6. [Performance Vault](#6-performance-vault)
7. [Telemetry Hub](#7-telemetry-hub)
8. [CLI Performance Board](#8-cli-performance-board)
9. [Live Performance Hologram](#9-live-performance-hologram)
10. [Titanium Armor](#10-titanium-armor)
11. [Discord Communication](#11-discord-communication)
12. [Zulip Archive](#12-zulip-archive)
13. [Telegram Alerts](#13-telegram-alerts)
14. [48-Hour Purge](#14-48-hour-purge)
15. [Gamerscore Engine](#15-gamerscore-engine)
16. [Achievement Milestones](#16-achievement-milestones)
17. [AniList GraphQL Core](#17-anilist-graphql-core)
18. [Airing Intelligence](#18-airing-intelligence)
19. [MAL Ghost Radar](#19-mal-ghost-radar)
20. [Deep Void Protocol](#20-deep-void-protocol)
21. [Master Sync](#21-master-sync)
22. [README Telemetry Injection](#22-readme-telemetry-injection)
23. [Execution Order](#23-execution-order)
24. [Data Flow](#24-data-flow)
25. [Scoring Model](#25-scoring-model)
26. [Performance Model](#26-performance-model)
27. [Repository Structure](#27-repository-structure)
28. [Deployment](#28-deployment)
29. [Required Secrets](#29-required-secrets)
30. [GitHub Actions](#30-github-actions)
31. [Operational Checks](#31-operational-checks)
32. [Known Implementation Notes](#32-known-implementation-notes)
33. [Known Failure Modes](#33-known-failure-modes)
34. [Security Notes](#34-security-notes)
35. [Future Hardening](#35-future-hardening)
36. [Final System Status](#36-final-system-status)

---

# 1. EXECUTIVE OVERVIEW

AniList Maximum Overdrive Sync V2 is a state-aware media tracking engine.

The program starts by loading configuration and JSON state.

It then:

```text
1. Purges old Discord log messages.
2. Fetches the complete AniList inventory.
3. Builds a title pool from English and Romaji titles.
4. Processes airing countdowns.
5. Processes synchronization deltas.
6. Processes MAL Ghost entries.
7. Processes Deep Void entries.
8. Injects current performance data into README.md.
9. Ends the cycle.
```

The central implementation is one Python script.

The script uses:

```text
requests
json
time
random
re
xml.etree.ElementTree
datetime
requests.auth.HTTPBasicAuth
```

The current source imports `random`, although the shown engine does not use it directly.

The engine is deliberately built from standard Python facilities plus the `requests`
library.

---

# 1.1 PRIMARY DESIGN

The source is divided into numbered sections:

```text
1. System Configuration & Secrets
2. V2 Telemetry Hub
3. Titanium Armor
4. Communication Protocols
5. RPG Engine
6. AniList GraphQL Core
7. Airing Intelligence
8. MAL Ghost Radar
9. Deep Void Protocol
10. Master Sync Engine
11. Live Telemetry Injector
12. Initiation Sequence
```

This section ordering is also a useful map for maintaining the script.

---

# 1.2 CORE PRINCIPLE

The system treats an AniList progress change as a trigger.

Conceptually:

```text
AniList
   ↓
Inventory
   ↓
Progress comparison
   ↓
Delta
   ↓
Gamerscore
   ↓
Performance
   ↓
Notifications
   ↓
Persistence
```

This makes the engine more than a notification bot.

---

# 1.3 PERSISTENCE MODEL

The workflow is designed around JSON files.

The code does not require a persistent SQL service.

Instead, persistent state is written to:

```text
db_sync.json
db_messages.json
db_ghosts.json
db_void.json
db_airing.json
db_achievements.json
db_performance_msg.json
performance/*.json
```

This makes the system easy to inspect through Git.

---

# 1.4 EXTERNAL SERVICES

The current code interacts with:

```text
AniList GraphQL
Discord Webhooks
Telegram Bot API
Zulip API
GitHub repository files
MyAnimeList XML exports
```

Each service has a separate role.

---

# 2. ENGINE RESPONSIBILITIES

The engine currently performs these major functions.

## 2.1 AniList Inventory

It retrieves the target user's media list from AniList.

The account username is configured in the script as:

```python
SOURCE_USERNAME = "Orewatokyo"
```

---

## 2.2 Synchronization

The engine remembers previous progress in:

```text
db_sync.json
```

It compares the remote progress to the saved value.

---

## 2.3 Gamerscore

The engine calculates Gamerscore from progress deltas and completion status.

---

## 2.4 Performance

The engine records:

```text
Episodes
Chapters
Anime minutes
Manga minutes
Gamerscore
Completions
```

into multiple time buckets.

---

## 2.5 Airing

The engine checks `nextAiringEpisode` and can send:

```text
3-hour warning
1-hour warning
```

---

## 2.6 Ghost Radar

The engine reads:

```text
mal_export.xml
mal_anime.xml
```

and searches AniList for unresolved entries.

---

## 2.7 Deep Void

The engine also searches manually staged entries in:

```text
db_void.json
```

---

## 2.8 Discord

The engine uses multiple webhook channels.

---

## 2.9 Telegram

The engine can send a direct one-hour airing alert.

---

## 2.10 Zulip

The engine archives anime and manga synchronization events into separate streams.

---

## 2.11 README

The engine generates a CLI-style performance board and injects it into a marked
README region.

---

# 3. CONFIGURATION

The configuration block is the first operational section of the source.

The script defines:

```python
SOURCE_USERNAME = "Orewatokyo"
```

This is the AniList username queried by the inventory function.

---

# 3.1 TOKEN LOADING

The AniList token is read from:

```text
ANILIST_TARGET_TOKEN
```

using:

```python
os.environ.get('ANILIST_TARGET_TOKEN')
```

The script therefore does not hard-code the actual AniList token.

---

# 3.2 DISCORD WEBHOOKS

The script loads eight Discord-related variables:

```text
DISCORD_ANIME_WEBHOOK
DISCORD_MANGA_WEBHOOK
DISCORD_AIRING_WEBHOOK
DISCORD_LOG_WEBHOOK
DISCORD_FAVORITES_WEBHOOK
DISCORD_GHOST_RADAR_WEBHOOK
DISCORD_ACHIEVEMENTS_WEBHOOK
DISCORD_PERFORMANCE_WEBHOOK
```

These are mapped internally to:

```text
WEBHOOK_ANIME
WEBHOOK_MANGA
WEBHOOK_AIRING
WEBHOOK_LOG
WEBHOOK_VIP
WEBHOOK_GHOST
WEBHOOK_ACHIEVEMENTS
WEBHOOK_PERFORMANCE
```

---

# 3.3 TELEGRAM CONFIGURATION

The engine reads:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

These are required for direct Telegram alerts.

If either value is missing, the Telegram function returns without sending.

---

# 3.4 ZULIP CONFIGURATION

The engine reads:

```text
ZULIP_SERVER_URL
ZULIP_BOT_EMAIL
ZULIP_API_KEY
```

The values are used with `HTTPBasicAuth`.

---

# 3.5 DATABASE FILE NAMES

The source defines:

```text
db_sync.json
db_messages.json
db_ghosts.json
db_void.json
db_airing.json
db_achievements.json
db_performance_msg.json
```

These file names form part of the engine's configuration contract.

---

# 3.6 MAL SOURCE

The configured primary XML path is:

```text
mal_export.xml
```

The code separately checks:

```text
mal_anime.xml
```

during the anime portion of the Ghost Radar.

---

# 3.7 PRIORITY FAVORITES

The current hard-coded priority list is:

```text
One Piece
Detective Conan
JoJo's Bizarre Adventure
Dragon Ball Z
```

These are matched against English and Romaji title values.

---

# 3.8 API HEADERS

The AniList headers are created as:

```text
Authorization: Bearer <target token>
Content-Type: application/json
Accept: application/json
```

If no token exists, the Authorization value becomes an empty string.

---

# 4. ENVIRONMENT VARIABLES

The following variables are referenced directly by the source.

| Variable | Function |
|---|---|
| `ANILIST_TARGET_TOKEN` | AniList authentication |
| `DISCORD_ANIME_WEBHOOK` | Anime progress |
| `DISCORD_MANGA_WEBHOOK` | Manga progress |
| `DISCORD_AIRING_WEBHOOK` | Airing warnings |
| `DISCORD_LOG_WEBHOOK` | Logs and rejected ghosts |
| `DISCORD_FAVORITES_WEBHOOK` | Priority franchise updates |
| `DISCORD_GHOST_RADAR_WEBHOOK` | Ghost assimilation |
| `DISCORD_ACHIEVEMENTS_WEBHOOK` | Gamerscore milestones |
| `DISCORD_PERFORMANCE_WEBHOOK` | Performance Hologram |
| `TELEGRAM_BOT_TOKEN` | Telegram bot authentication |
| `TELEGRAM_CHAT_ID` | Telegram destination |
| `ZULIP_SERVER_URL` | Zulip endpoint |
| `ZULIP_BOT_EMAIL` | Zulip bot identity |
| `ZULIP_API_KEY` | Zulip authentication |

---

# 4.1 REQUIRED VS OPTIONAL

The code gracefully returns from several communication functions when credentials are absent.

Therefore not every integration is mandatory for every execution.

However, AniList data retrieval requires the target token for authenticated operations.

---

# 4.2 SECRET NAMING

Secret names must match the workflow mapping.

For example:

```text
DISCORD_ANIME_WEBHOOK
```

is what the Python source reads.

A GitHub secret named:

```text
DISCORD_ANILIST_ANIME_WEBHOOK
```

will only work if the workflow maps it into:

```text
DISCORD_ANIME_WEBHOOK
```

---

# 5. JSON STATE FILES

The generic database loader is:

```python
load_db(filepath)
```

It:

1. Checks if the file exists.
2. Attempts JSON parsing.
3. Returns `{}` if parsing fails.
4. Returns `{}` if the file does not exist.

---

# 5.1 SAVE FUNCTION

The generic writer is:

```python
save_db(filepath, data)
```

It writes:

```text
JSON
indent=4
```

This keeps generated state readable.

---

# 5.2 ERROR RECOVERY

The current loader catches any exception during reading and returns an empty object.

This prevents a malformed file from immediately crashing the loader.

However, it also means malformed JSON can silently appear as empty state.

That behavior should be understood before debugging state loss.

---

# 6. PERFORMANCE VAULT

The V2 Telemetry Hub is implemented through:

```python
update_performance_vault(...)
```

The function calculates current time buckets.

It creates:

```text
daily
weekly
monthly
yearly
lifetime
```

paths.

---

# 6.1 DAILY PATH

Example:

```text
performance/daily/2026-08-13.json
```

The exact date is generated from UTC time.

---

# 6.2 WEEKLY PATH

Example:

```text
performance/weekly/2026-W33.json
```

The script uses ISO calendar week values.

---

# 6.3 MONTHLY PATH

Example:

```text
performance/monthly/2026-08.json
```

---

# 6.4 YEARLY PATH

Example:

```text
performance/yearly/2026.json
```

---

# 6.5 LIFETIME PATH

Lifetime data is written to:

```text
performance/lifetime.json
```

Unlike the other buckets, the lifetime file lives directly under `performance`.

---

# 6.6 DIRECTORY CREATION

The engine automatically creates:

```text
performance/daily
performance/weekly
performance/monthly
performance/yearly
```

when required.

---

# 6.7 PERFORMANCE FIELDS

Every performance file receives:

```text
episodes
chapters
anime_minutes
manga_minutes
g_score
```

The lifetime file additionally receives:

```text
completed
```

---

# 6.8 ANIME COUNTER

For anime:

```python
ep_add = delta
ch_add = 0
```

Therefore the detected episode delta increments the `episodes` field.

---

# 6.9 MANGA COUNTER

For manga:

```python
ep_add = 0
ch_add = delta
```

Therefore the detected chapter delta increments the `chapters` field.

---

# 6.10 ANIME MINUTES

The source calculates:

```text
delta × max(1, duration - 2)
```

This means each anime episode uses its retrieved duration minus two minutes,
with a minimum effective duration of one minute.

---

# 6.11 MANGA MINUTES

The source uses:

```text
delta × 5
```

So each manga chapter contributes five estimated minutes.

---

# 6.12 COMPLETION COUNTER

A local completion increment is:

```text
1 if is_completed
0 otherwise
```

But the `completed` field is only written for the lifetime file.

---

# 6.13 GAMERSCORE IN PERFORMANCE

Every performance bucket receives:

```text
g_score += g_earned
```

This means the performance vault keeps a score total in addition to time and media counts.

---

# 6.14 IMPORTANT PERFORMANCE BEHAVIOR

The master sync only calls `update_performance_vault()` when:

```text
delta > 0
```

This means performance files do not grow merely because the workflow executes.

They grow when new progress is detected.

---

# 7. TELEMETRY HUB

The Telemetry Hub consists of three main pieces:

```text
update_performance_vault()
get_performance_stats()
generate_cli_board()
```

The Hologram and README injector both consume the generated board.

---

# 7.1 STATISTICS LOADER

`get_performance_stats()` loads:

```text
today
this week
lifetime
```

It does not directly load monthly or yearly data for the CLI board.

---

# 7.2 TODAY

Today is determined using the UTC date.

---

# 7.3 THIS WEEK

The current ISO week is used.

---

# 7.4 ALL TIME

All-time statistics come from:

```text
performance/lifetime.json
```

---

# 7.5 TELEMETRY ARCHITECTURE

The output flow is:

```text
Performance Vault
      ↓
get_performance_stats()
      ↓
generate_cli_board()
      ↓
      ├──► Discord Hologram
      └──► README
```

This is one of the most important architectural relationships in V2.

---

# 8. CLI PERFORMANCE BOARD

The function:

```python
generate_cli_board()
```

creates the textual dashboard.

It contains:

```text
TODAY
THIS WEEK
ALL TIME
```

---

# 8.1 TODAY FORMAT

The current implementation displays:

```text
Anime       N eps
Manga       N ch
Time        N min
Gamerscore  N G
```

---

# 8.2 THIS WEEK FORMAT

The weekly block has the same metric style.

---

# 8.3 ALL TIME FORMAT

The lifetime block displays:

```text
Episodes
Chapters
Minutes
Gamerscore
Completed
```

---

# 8.4 TIME TOTAL

The CLI board combines:

```text
anime_minutes
+
manga_minutes
```

into one total.

---

# 8.5 COMPLETION COUNT

Only the lifetime block reads:

```text
completed
```

because that field is only stored in lifetime data.

---

# 8.6 EMPTY DATA BEHAVIOR

If a performance file does not exist, `load_db()` returns `{}`.

The CLI board then shows zeros.

This is the current reason a freshly created performance vault can display:

```text
TODAY
Anime 0 eps
Manga 0 ch
```

until progress events have populated it.

---

# 9. LIVE PERFORMANCE HOLOGRAM

The function:

```python
refresh_performance_hologram()
```

updates a dedicated Discord performance message.

It is intentionally separate from normal anime/manga notification webhooks.

---

# 9.1 Hologram WEBHOOK

The source uses:

```text
WEBHOOK_PERFORMANCE
```

loaded from:

```text
DISCORD_PERFORMANCE_WEBHOOK
```

---

# 9.2 MESSAGE MEMORY

The previous Discord message ID is stored in:

```text
db_performance_msg.json
```

---

# 9.3 DELETE OLD MESSAGE

If a previous message ID exists, the engine sends:

```text
DELETE <webhook>/messages/<message_id>
```

---

# 9.4 BUILD NEW BOARD

After deleting the previous message, it calls:

```python
generate_cli_board()
```

---

# 9.5 EMBED

The Hologram title is:

```text
⚡ LIVE PERFORMANCE MONITOR
```

The CLI board is placed inside a fenced text block.

---

# 9.6 EMBED COLOR

The current Hologram embed color is:

```text
3447003
```

---

# 9.7 TIMESTAMP

The Hologram includes the current UTC ISO timestamp.

---

# 9.8 FOOTER

The footer text is:

```text
V2 Telemetry Hub Synced
```

---

# 9.9 MESSAGE POST

The engine posts with:

```text
?wait=true
```

so it can receive the created message ID.

---

# 9.10 SUCCESS STATUS

The source accepts:

```text
200
204
```

as successful Hologram response statuses.

---

# 9.11 MESSAGE ID SAVE

If a response ID exists:

```text
db_performance_msg.json
```

is replaced with:

```json
{
    "message_id": "..."
}
```

---

# 9.12 RECOVERY

If deleting the old Hologram message fails, the exception is ignored.

The engine can still create a new dashboard afterward.

---

# 9.13 Hologram TRIGGER

The Master Sync uses:

```text
hologram_trigger = True
```

when an event has:

```text
delta > 0
```

The refresh occurs after the inventory loop.

---

# 10. TITANIUM ARMOR

The network retry layer is:

```python
fetch_with_armor(...)
```

It is primarily used for the paginated AniList inventory query.

---

# 10.1 RETRY COUNT

Default:

```text
3 attempts
```

---

# 10.2 TIMEOUT

Each request uses:

```text
15 seconds
```

---

# 10.3 RETRY DELAY

After each failed attempt:

```text
3 seconds
6 seconds
9 seconds
```

because the code sleeps:

```python
(attempt + 1) * 3
```

---

# 10.4 SUCCESS CONDITION

A request is treated as successful when:

```text
HTTP 200
```

is returned.

---

# 10.5 FAILURE

After all attempts fail:

```text
None
```

is returned.

The caller can then stop processing that request.

---

# 10.6 LIMITATION

The retry wrapper does not inspect HTTP 429 retry headers.

It uses a fixed incremental delay.

That is a current implementation detail.

---

# 11. DISCORD COMMUNICATION

The general Discord sender is:

```python
send_discord_alert(...)
```

It accepts:

```text
webhook_url
title
description
color
image_url
fields
author
override_name
```

---

# 11.1 TITLE LIMIT

The title is truncated to:

```text
256 characters
```

---

# 11.2 DESCRIPTION LIMIT

Descriptions are truncated to:

```text
4096 characters
```

---

# 11.3 FIELD LIMIT

The provided field list is limited to:

```text
25 fields
```

---

# 11.4 IMAGE

If an image URL is provided, it is added as an embed image.

---

# 11.5 AUTHOR

An optional author block can be attached.

---

# 11.6 OVERRIDE USERNAME

The sender can override the webhook username.

The source truncates the override name to:

```text
80 characters
```

---

# 11.7 LOG MESSAGE STORAGE

If the webhook being used equals:

```text WEBHOOK_LOG
```

and Discord returns a successful response, the message ID is stored in:

```text
db_messages.json
```

with:

```text timestamp
delete_url
```

---

# 12. ZULIP ARCHIVE

The function:

```python
fire_zulip_archive(...)
```

archives synchronization events.

---

# 12.1 REQUIRED VALUES

If any of these are missing:

```text
ZULIP_URL
ZULIP_EMAIL
ZULIP_API_KEY
```

the function returns without sending.

---

# 12.2 STREAM SELECTION

Anime uses:

```text
Anime-Vault
```

Manga uses:

```text
Manga-Vault
```

---

# 12.3 ACTION TEXT

Anime:

```text
📺 Watched Episode
```

Manga:

```text
📖 Read Chapter
```

---

# 12.4 ARCHIVE CONTENT

The message contains:

```text
Sync Log Executed
Watched/Read progress
Current score
```

---

# 12.5 TOPIC

The title is used as the Zulip topic.

---

# 12.6 AUTHENTICATION

The source uses:

```python
HTTPBasicAuth(ZULIP_EMAIL, ZULIP_API_KEY)
```

---

# 12.7 ERROR BEHAVIOR

Exceptions are caught and ignored.

This means Zulip failure does not stop the main synchronization loop.

---

# 13. TELEGRAM ALERTS

The Telegram function is:

```python
send_telegram_alert(message, image_url=None)
```

---

# 13.1 TWO MODES

Without an image:

```text
sendMessage
```

With an image:

```text
sendPhoto
```

---

# 13.2 PARSE MODE

The message uses:

```text
Markdown
```

---

# 13.3 DESTINATION

The destination is:

```text
TELEGRAM_CHAT_ID
```

---

# 13.4 AIRING USE

Telegram is currently invoked by the one-hour airing warning.

The message identifies:

```text
Title
Episode number
Under 60 minutes
```

and may include the cover image.

---

# 14. 48-HOUR PURGE

The engine contains an automatic log cleanup routine:

```python
execute_48hr_purge()
```

---

# 14.1 RETENTION

The retention period is:

```text
172800 seconds
```

which equals:

```text
48 hours
```

---

# 14.2 SOURCE DATA

The purge reads:

```text
db_messages.json
```

---

# 14.3 TIMESTAMP COMPARISON

For each stored message:

```text
current_time - message_timestamp
```

is compared against:

```text
172800
```

---

# 14.4 DELETE

Old messages are deleted through their stored:

```text
delete_url
```

---

# 14.5 CLEANUP DELAY

The engine sleeps:

```text
1 second
```

between deletions.

---

# 14.6 STATE SAVE

After cleanup, the remaining message database is saved.

---

# 15. GAMERSCORE ENGINE

The RPG subsystem is:

```python
manage_achievements_and_weekly(...)
```

It loads:

```text
db_achievements.json
```

---

# 15.1 DEFAULT STATE

If no valid achievement state exists:

```json
{
    "lifetime_g": 0,
    "weekly_g": 0,
    "current_week": <current week>
}
```

is created in memory.

---

# 15.2 WEEK DETECTION

Current week is derived from:

```python
datetime.now(timezone.utc).isocalendar()[1]
```

---

# 15.3 WEEK RESET

When the stored week differs from the current week:

```text
weekly_g = 0
current_week = current_week
```

---

# 15.4 POINT ADDITION

Every invocation adds:

```text
points_earned
```

to:

```text
weekly_g
lifetime_g
```

---

# 15.5 1K MILESTONE

The engine checks:

```text
old weekly < 1000
new weekly >= 1000
```

If true:

```text
hit_1k = True
```

---

# 15.6 5K MILESTONE

The engine checks:

```text
old weekly < 5000
new weekly >= 5000
```

If true:

```text
hit_5k = True
```

---

# 15.7 PRESTIGE

Prestige becomes true when:

```text
lifetime_g >= 10000
```

The Master Sync can then use:

```text
Orewatokyo
```

as the webhook override name.

---

# 15.8 CLASSIFIED UI

The milestone function sends:

```text
1,000 G REACHED
5,000 G: OVERDRIVE
```

to the achievement webhook.

---

# 16. ACHIEVEMENT MILESTONES

The source currently implements two weekly milestones.

---

# 16.1 1,000 G

Title:

```text
💠 1,000 G REACHED
```

Description:

```text
>> CLASS-A MILESTONE CLEARED <<
```

---

# 16.2 5,000 G

Title:

```text
🔥 5,000 G: OVERDRIVE
```

Description:

```text
>> SYSTEM MAXIMIZED. APEX TIER REACHED <<
```

---

# 16.3 IMAGE PAYLOADS

Both milestones include external GIF URLs.

Those URLs are part of the current source implementation.

---

# 17. ANILIST GRAPHQL CORE

The primary inventory function is:

```python
fetch_anilist_inventory(username)
```

---

# 17.1 QUERY

The query requests:

```text
mediaId
progress
score
status
title.romaji
title.english
type
episodes
chapters
duration
coverImage
nextAiringEpisode
```

---

# 17.2 PAGE SIZE

The source uses:

```text
perPage: 50
```

---

# 17.3 PAGE LOOP

The engine starts at:

```text
page = 1
```

and continues while:

```text
hasNextPage
```

is true.

---

# 17.4 INVENTORY KEY

The local inventory dictionary uses:

```text
English title
```

when available.

Otherwise:

```text
Romaji title
```

is used.

---

# 17.5 STORED MEDIA RECORD

Each inventory record contains:

```text
mediaId
progress
status
scoreRaw
type
cover
color
duration
nextAiring
romaji
english
total_episodes
total_chapters
```

---

# 17.6 COVER

The source reads:

```text
coverImage.extraLarge
```

---

# 17.7 COLOR

The source reads:

```text
coverImage.color
```

---

# 17.8 DURATION FALLBACK

If AniList does not provide duration:

```text
24 minutes
```

is used as the fallback.

---

# 17.9 TITLE NORMALIZATION

The inventory primary key prefers:

```text
English
```

then:

```text
Romaji
```

---

# 17.10 INTER-PAGE DELAY

After each page:

```text
1 second
```

of sleep is applied.

---

# 18. AIRING INTELLIGENCE

The airing subsystem is:

```python
process_airing_countdowns(inventory)
```

---

# 18.1 CURRENT TIME

Current UNIX time is generated from:

```python
int(time.time())
```

---

# 18.2 NEXT AIRING

If:

```text
nextAiring
```

is missing, that title is skipped.

---

# 18.3 TIME DIFFERENCE

The calculation is:

```text
airingAt - current_time
```

---

# 18.4 AIRING DATABASE KEY

The key is:

```text
<mediaId>_ep<episode>
```

Example:

```text
21456_ep1067
```

---

# 18.5 THREE-HOUR WINDOW

When:

```text
3600 < time_until <= 10800
```

and the current state is:

```text
none
```

the engine sends a 3-hour warning.

---

# 18.6 ONE-HOUR WINDOW

When:

```text
0 < time_until <= 3600
```

and the current state is:

```text
none
```

or:

```text
3h
```

the engine sends the final warning.

---

# 18.7 AIRING DISCORD FIELDS

The warning contains:

```text
Romaji
Telecast Time
Live Countdown
```

---

# 18.8 TELECAST TIME

The Discord field uses:

```text
<t:airingAt:F>
```

---

# 18.9 RELATIVE COUNTDOWN

The Discord field uses:

```text
<t:airingAt:R>
```

---

# 18.10 AIRING STATE SAVE

After processing, the full airing database is saved.

---

# 19. MAL GHOST RADAR

The Ghost Radar is divided into:

```text
sweep_mal_xml()
execute_ghost_radar()
```

---

# 19.1 MANGA EXPORT

The manga export path is:

```text
mal_export.xml
```

---

# 19.2 MANGA TITLE

The engine reads:

```text
manga_title
```

---

# 19.3 MANGA PROGRESS

The engine reads:

```text
my_read_chapters
```

---

# 19.4 MANGA SCORE

The engine reads:

```text
my_score
```

---

# 19.5 ANIME EXPORT

The anime export path is:

```text
mal_anime.xml
```

---

# 19.6 ANIME TITLE

The engine reads:

```text
series_title
```

---

# 19.7 ANIME PROGRESS

The engine reads:

```text
my_watched_episodes
```

---

# 19.8 ANIME SCORE

The engine reads:

```text
my_score
```

---

# 19.9 GHOST DETECTION

An entry becomes a Ghost candidate if:

```text
title.lower()
```

is not in the supplied known title pool.

The entry must also not already exist in the Ghost database.

---

# 19.10 GHOST RECORD

The Ghost record contains:

```text
progress
score
type
```

---

# 19.11 GHOST STORAGE

Ghost state is stored in:

```text
db_ghosts.json
```

---

# 20. GHOST ASSIMILATION

`execute_ghost_radar()` processes stored Ghost entries.

---

# 20.1 SEARCH

Each Ghost generates an AniList Media search query.

Variables include:

```text
search
type
```

---

# 20.2 MEDIA TYPE

The current stored type is:

```text
MANGA
```

or:

```text
ANIME
```

---

# 20.3 SUCCESS CONDITION

A Ghost is considered found if:

```text
HTTP 200
```

and a Media object is returned.

---

# 20.4 SAVE MUTATION

When a token exists, the script sends:

```text
SaveMediaListEntry
```

with:

```text
mediaId
progress
scoreRaw
```

---

# 20.5 SCORE CONVERSION

Ghost score is multiplied by:

```text
10
```

before being sent as `scoreRaw`.

This is a current implementation behavior.

---

# 20.6 ASSIMILATION ALERT

Success sends:

```text
🟢 GHOST ASSIMILATED
```

to the Ghost webhook.

---

# 20.7 REJECTION ALERT

Failure sends:

```text
🔴 GHOST REJECTED / NOT FOUND
```

to the log webhook.

---

# 20.8 GHOST DELAY

Each Ghost search is followed by:

```text
1.5 seconds
```

of sleep.

---

# 20.9 GHOST CLEANUP

Successfully assimilated titles are removed from:

```text
ghost_db
```

and the remaining dictionary is returned.

---

# 21. DEEP VOID PROTOCOL

The Deep Void is implemented by:

```python
execute_void_radar()
```

---

# 21.1 VOID FILE

The engine reads:

```text
db_void.json
```

---

# 21.2 EMPTY VOID

If the Void database is empty:

```text
return
```

and no searches are performed.

---

# 21.3 SEARCH

Each entry is searched through the AniList GraphQL API.

---

# 21.4 ASSIMILATION

If a Media object is found:

```text
progress
score
```

are saved through a mutation if the AniList token exists.

---

# 21.5 VOID SCORE

Void score is also multiplied by:

```text
10
```

before becoming `scoreRaw`.

---

# 21.6 VOID ALERT

Success sends:

```text
🌌 VOID ENTITY ASSIMILATED
```

to the log webhook.

---

# 21.7 VOID CLEANUP

Successfully assimilated Void titles are deleted from:

```text
db_void.json
```

when the returned dictionary is saved by the main sequence.

---

# 21.8 VOID DELAY

The current engine waits:

```text
1.5 seconds
```

between entries.

---

# 22. MASTER SYNC

The main progress engine is:

```python
execute_master_sync(inventory)
```

This is the orchestration layer for progress changes.

---

# 22.1 SYNC DATABASE

The Master Sync loads:

```text
db_sync.json
```

---

# 22.2 MEDIA ID

The progress state key is the media ID converted to string.

---

# 22.3 CHANGE DETECTION

The engine checks:

```text
stored progress != current progress
```

---

# 22.4 DELTA

The delta is:

```text
current progress - stored progress
```

---

# 22.5 NEGATIVE DELTA

If the delta is negative:

```text
delta = 0
```

This prevents negative progress from generating negative Gamerscore.

---

# 22.6 ANIME SCORE

For anime:

```text
delta × 10
```

---

# 22.7 MANGA SCORE

For manga:

```text
delta × 2
```

---

# 22.8 COMPLETION BONUS

If the current status is:

```text
COMPLETED
```

the engine adds:

```text
+100 G
```

to `g_earned`.

---

# 22.9 PERFORMANCE TRIGGER

Performance is updated only when:

```text
delta > 0
```

---

# 22.10 Hologram TRIGGER

When a positive delta occurs:

```text
hologram_trigger = True
```

---

# 22.11 ACHIEVEMENT UPDATE

The engine calls:

```text
manage_achievements_and_weekly(g_earned)
```

---

# 22.12 PRESTIGE OVERRIDE

If lifetime Gamerscore reaches:

```text
10,000
```

then:

```text
override_tag = "Orewatokyo"
```

---

# 22.13 DISCORD COLOR

The embed color is derived through:

```text
hex_to_int(data["color"])
```

---

# 22.14 STANDARD FIELDS

Progress update fields include:

```text
Romaji
Status
Progress
Left
```

---

# 22.15 LEFT CALCULATION

For anime:

```text
total_episodes - progress
```

For manga:

```text
total_chapters - progress
```

If total is unavailable:

```text
?
```

---

# 22.16 NORMAL WEBHOOK

Anime uses:

```text
WEBHOOK_ANIME
```

Manga uses:

```text
WEBHOOK_MANGA
```

---

# 22.17 ZULIP

Every accepted progress event also calls:

```text
fire_zulip_archive(...)
```

---

# 22.18 VIP MATCH

The title is checked against:

```text
PRIORITY_FAVORITES
```

using both English and Romaji.

---

# 22.19 VIP ALERT

If matched, the engine sends:

```text
⭐ VIP UPDATE: <title>
```

to the VIP webhook.

---

# 22.20 MILESTONE ALERTS

If:

```text
hit_1k
```

the 1K UI drop is sent.

If:

```text
hit_5k
```

the 5K UI drop is sent.

---

# 22.21 ANILIST SAVE

After processing, the engine calls:

```text
SaveMediaListEntry
```

with:

```text
mediaId
progress
score
```

where the score is the stored AniList score field.

---

# 22.22 STATE COMMIT

The sync database is updated:

```text
sync_db[media_id] = progress
```

---

# 22.23 FINAL SAVE

After all media have been processed:

```text
db_sync.json
```

is saved.

---

# 22.24 FINAL HOLOGRAM

If at least one positive delta occurred:

```text
refresh_performance_hologram()
```

is called.

---

# 23. README TELEMETRY INJECTION

The final live output function is:

```python
update_readme_telemetry()
```

---

# 23.1 BOARD SOURCE

It calls:

```python
generate_cli_board()
```

So the README does not calculate independent performance numbers.

---

# 23.2 TELEMETRY MARKERS

The source expects:

```html
<!-- TELEMETRY_START -->
```text
TODAY
─────────────────────────
Manga             0 ch
Time              0 min
Gamerscore       0 G

THIS WEEK
─────────────────────────
Manga         8,919 ch
Time         44,595 min
Gamerscore  28,796 G

ALL TIME
─────────────────────────
Chapters      8,898
Minutes      44,490
Gamerscore  28,796 G
Completed       109

```
<!-- TELEMETRY_END -->
```

in the README.

---

# 23.3 GENERATED BLOCK

The inserted block has this structure:

```html
<!-- TELEMETRY_START -->
```text
TODAY
─────────────────────────
Manga             0 ch
Time              0 min
Gamerscore       0 G

THIS WEEK
─────────────────────────
Manga         8,919 ch
Time         44,595 min
Gamerscore  28,796 G

ALL TIME
─────────────────────────
Chapters      8,898
Minutes      44,490
Gamerscore  28,796 G
Completed       109

```
<!-- TELEMETRY_END -->
```

---

# 23.4 REGEX REPLACEMENT

The replacement uses a DOTALL regular expression:

```text
<!-- TELEMETRY_START -->
```text
TODAY
─────────────────────────
Manga             0 ch
Time              0 min
Gamerscore       0 G

THIS WEEK
─────────────────────────
Manga         8,919 ch
Time         44,595 min
Gamerscore  28,796 G

ALL TIME
─────────────────────────
Chapters      8,898
Minutes      44,490
Gamerscore  28,796 G
Completed       109

```
<!-- TELEMETRY_END -->
```

This replaces everything between the two markers.

---

# 23.5 FILE NAME BEHAVIOR

The Python source currently opens:

```text
README.md
```

with uppercase letters.

This is important on case-sensitive environments.

If the repository contains only:

```text
readme.md
```

instead of:

```text
README.md
```

the telemetry injector can fail.

---

# 23.6 WINDOWS VS GITHUB

Case-insensitive local filesystems can make filename case differences harder to notice.

GitHub's Linux runners use a case-sensitive filesystem.

Therefore the safest deployment convention is:

```text
README.md
```

exactly as the script expects.

---

# 23.7 TELEMETRY FAILURE

If file reading or writing fails, the source prints:

```text
[SYSTEM] Telemetry Injection Failed: ...
```

---

# 23.8 IMPORTANT LIMITATION

The current README injector does not create the marker block if it is missing.

It only replaces an existing marker block.

Therefore the README must contain:

```html
<!-- TELEMETRY_START -->
```text
TODAY
─────────────────────────
Manga             0 ch
Time              0 min
Gamerscore       0 G

THIS WEEK
─────────────────────────
Manga         8,919 ch
Time         44,595 min
Gamerscore  28,796 G

ALL TIME
─────────────────────────
Chapters      8,898
Minutes      44,490
Gamerscore  28,796 G
Completed       109

```
<!-- TELEMETRY_END -->
```

before the automation can inject telemetry.

---

# 24. EXECUTION ORDER

The `__main__` block defines the full lifecycle.

---

# 24.1 START MESSAGE

The program prints:

```text
=== MAXIMUM OVERDRIVE V2 ENGINE: SPINNING UP ===
```

---

# 24.2 STEP 1

The engine executes:

```text
execute_48hr_purge()
```

---

# 24.3 STEP 2

The engine fetches:

```text
live_inventory
```

from AniList.

---

# 24.4 STEP 3

The known title pool is built.

Both:

```text
Romaji
English
```

are inserted when available.

---

# 24.5 STEP 4

The engine processes:

```text
process_airing_countdowns(live_inventory)
```

---

# 24.6 STEP 5

The engine processes:

```text
execute_master_sync(live_inventory)
```

---

# 24.7 STEP 6

The engine performs the MAL sweep and Ghost Radar:

```text
sweep_mal_xml()
execute_ghost_radar()
```

---

# 24.8 STEP 7

The engine performs:

```text
execute_void_radar()
```

---

# 24.9 STEP 8

The engine injects telemetry:

```text
update_readme_telemetry()
```

---

# 24.10 END MESSAGE

The program prints:

```text
=== MAXIMUM OVERDRIVE V2 ENGINE: CYCLE COMPLETE ===
```

---

# 25. DATA FLOW

The full cycle can be visualized as:

```text
                 ┌──────────────┐
                 │   AniList    │
                 └──────┬───────┘
                        │
                        ▼
               ┌─────────────────┐
               │ Inventory Fetch │
               └────────┬────────┘
                        │
              ┌─────────┼─────────┐
              ▼         ▼         ▼
           Airing     Sync      Titles
              │         │         │
              ▼         ▼         ▼
          Discord    Game Core  Ghost Radar
              │         │         │
              │         ▼         ▼
              │      Performance  Void
              │         │
              └─────────┼────────────┐
                        ▼            │
                 Hologram            │
                        │            │
                        ▼            ▼
                     README      Zulip / Telegram
```

---

# 25.1 EVENT PIPELINE

For a new episode:

```text
AniList progress +1
        ↓
delta = 1
        ↓
+10 G
        ↓
performance +1 episode
        ↓
performance +duration-2 minutes
        ↓
Discord update
        ↓
Zulip archive
        ↓
README telemetry
        ↓
GitHub commit
```

---

# 25.2 MANGA PIPELINE

For a new chapter:

```text
AniList progress +1
        ↓
delta = 1
        ↓
+2 G
        ↓
performance +1 chapter
        ↓
performance +5 minutes
        ↓
Discord update
        ↓
Zulip archive
        ↓
README telemetry
        ↓
GitHub commit
```

---

# 25.3 AIRING PIPELINE

```text
nextAiringEpisode
        ↓
seconds remaining
        ↓
3H or 1H
        ↓
Discord
        ↓
Telegram for 1H
        ↓
db_airing.json
```

---

# 25.4 GHOST PIPELINE

```text
MAL XML
   ↓
Known title pool
   ↓
Missing title
   ↓
db_ghosts.json
   ↓
AniList search
   ↓
Found?
 / \
YES NO
 |   |
 ▼   ▼
Save  Log rejection
 |
 ▼
Delete ghost
```

---

# 25.5 VOID PIPELINE

```text
db_void.json
       ↓
AniList search
       ↓
Found?
 /     \
YES     NO
 |       |
 ▼       ▼
Save    Keep waiting
 |
 ▼
Delete void item
```

---

# 26. SCORING MODEL

Current source scoring is straightforward.

---

# 26.1 ANIME

```text
+10 G / new episode
```

---

# 26.2 MANGA

```text
+2 G / new chapter
```

---

# 26.3 COMPLETION

```text
+100 G
```

when the current media status equals:

```text
COMPLETED
```

during a processed synchronization state change.

---

# 26.4 TOTAL

For:

```text
3 anime episodes
5 manga chapters
1 completion
```

the current calculation is:

```text
30 G
+ 10 G
+ 100 G
= 140 G
```

---

# 27. PERFORMANCE MODEL

The current performance model is:

```text
Anime:
(delta × (duration - 2))

Manga:
(delta × 5)
```

with a minimum anime duration expression of one minute:

```text
max(1, duration - 2)
```

---

# 27.1 DAILY

Daily performance is stored by UTC date.

---

# 27.2 WEEKLY

Weekly performance is stored by ISO year/week.

---

# 27.3 MONTHLY

Monthly performance is stored by UTC month.

---

# 27.4 YEARLY

Yearly performance is stored by UTC year.

---

# 27.5 LIFETIME

Lifetime is stored in one persistent JSON file.

---

# 28. REPOSITORY STRUCTURE

Recommended structure based on the source:

```text
📦 Repository
 ┣ 📂 .github/
 ┃ ┗ 📂 workflows/
 ┃    ┗ 📜 sync_engine.yml
 ┣ 📂 performance/
 ┃ ┣ 📂 daily/
 ┃ ┣ 📂 weekly/
 ┃ ┣ 📂 monthly/
 ┃ ┣ 📂 yearly/
 ┃ ┗ 📜 lifetime.json
 ┣ 📜 anilist_engine.py
 ┣ 📜 db_sync.json
 ┣ 📜 db_messages.json
 ┣ 📜 db_ghosts.json
 ┣ 📜 db_void.json
 ┣ 📜 db_airing.json
 ┣ 📜 db_achievements.json
 ┣ 📜 db_performance_msg.json
 ┣ 📜 mal_export.xml
 ┣ 📜 mal_anime.xml
 ┗ 📜 README.md
```

---

# 28.1 WORKFLOW

The workflow is responsible for:

```text
Scheduling
Environment injection
Python setup
Engine execution
State persistence
Git commit
```

The supplied Python source itself does not contain a Git command.

---

# 28.2 ENGINE

The main source file is:

```text
anilist_engine.py
```

---

# 28.3 PERFORMANCE

Performance records live under:

```text
performance/
```

---

# 28.4 STATE

State files live at repository root.

---

# 28.5 SOURCE EXPORTS

MAL XML exports are also expected in the repository.

---

# 29. DEPLOYMENT

A practical deployment sequence is:

```text
1. Create repository.
2. Add anilist_engine.py.
3. Add JSON state files.
4. Add performance directories.
5. Add MAL XML files if needed.
6. Add README.md with telemetry markers.
7. Configure GitHub secrets.
8. Configure GitHub Actions.
9. Run manually.
10. Inspect output.
11. Verify repository changes.
```

---

# 29.1 PRIVATE REPOSITORY

A private repository is recommended when storing personal tracking exports and webhook
configuration.

---

# 29.2 INITIAL STATE

Empty or first-run JSON files can start as:

```json
{}
```

The engine initializes missing achievement state internally.

---

# 29.3 PERFORMANCE DIRECTORIES

The engine can create the standard performance directories itself.

---

# 29.4 README PREPARATION

Before the engine can inject telemetry, include:

```html
<!-- TELEMETRY_START -->
```text
TODAY
─────────────────────────
Manga             0 ch
Time              0 min
Gamerscore       0 G

THIS WEEK
─────────────────────────
Manga         8,919 ch
Time         44,595 min
Gamerscore  28,796 G

ALL TIME
─────────────────────────
Chapters      8,898
Minutes      44,490
Gamerscore  28,796 G
Completed       109

```
<!-- TELEMETRY_END -->
```

This is the expected marker contract.

---

# 30. REQUIRED SECRETS

## AniList

```text
ANILIST_TARGET_TOKEN
```

---

## Discord

```text
DISCORD_ANIME_WEBHOOK
DISCORD_MANGA_WEBHOOK
DISCORD_AIRING_WEBHOOK
DISCORD_LOG_WEBHOOK
DISCORD_FAVORITES_WEBHOOK
DISCORD_GHOST_RADAR_WEBHOOK
DISCORD_ACHIEVEMENTS_WEBHOOK
DISCORD_PERFORMANCE_WEBHOOK
```

---

## Telegram

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

---

## Zulip

```text
ZULIP_SERVER_URL
ZULIP_BOT_EMAIL
ZULIP_API_KEY
```

---

# 30.1 WORKFLOW MAPPING

The Python script reads the internal names above.

The GitHub Actions workflow can map differently named secrets into these environment
variables.

Example:

```yaml
env:
  DISCORD_ANIME_WEBHOOK: ${{ secrets.DISCORD_ANILIST_ANIME_WEBHOOK }}
```

The YAML is therefore the bridge between repository secret naming and Python naming.

---

# 31. GITHUB ACTIONS

The source assumes it will run on a scheduled automation runner.

The expected workflow responsibilities are:

```text
Checkout
↓
Python Setup
↓
Dependencies
↓
Secrets
↓
python anilist_engine.py
↓
git add
↓
git commit
↓
git push
```

---

# 31.1 MANUAL DISPATCH

A manual workflow trigger is recommended so the engine can be tested without waiting
for the schedule.

---

# 31.2 WRITE PERMISSION

Because the engine changes JSON files and README telemetry, the workflow normally needs:

```yaml
permissions:
  contents: write
```

---

# 31.3 CONCURRENCY

A concurrency group is recommended so multiple runs do not simultaneously modify the
same JSON state.

---

# 31.4 DEPENDENCY

The engine requires the `requests` package.

The other imports come from Python's standard library.

---

# 32. OPERATIONAL CHECKS

A healthy run should show:

```text
Engine starts
AniList responds
Inventory is populated
Airing scan executes
Master Sync executes
Ghost Radar executes
Void Radar executes
README telemetry executes
Engine completes
```

---

# 32.1 GAMERSCORE CHECK

Confirm that:

```text
db_achievements.json
```

contains updated:

```text
lifetime_g
weekly_g
```

after a positive progress event.

---

# 32.2 PERFORMANCE CHECK

Confirm that:

```text
performance/daily/<date>.json
```

contains:

```text
episodes
chapters
anime_minutes
manga_minutes
g_score
```

---

# 32.3 Hologram CHECK

Confirm that:

```text
db_performance_msg.json
```

contains a current message ID.

---

# 32.4 AIRING CHECK

Confirm that:

```text
db_airing.json
```

records the warning stage.

---

# 32.5 GHOST CHECK

Confirm that:

```text
db_ghosts.json
```

contains unresolved entries when appropriate.

---

# 32.6 VOID CHECK

Confirm that:

```text
db_void.json
```

is reduced when an entry is successfully found.

---

# 32.7 README CHECK

Confirm that the following markers remain intact:

```text
TELEMETRY_START
TELEMETRY_END
```

and that the generated board appears between them.

---

# 33. KNOWN IMPLEMENTATION NOTES

This section documents behavior visible directly in the supplied source.

---

# 33.1 README CASE SENSITIVITY

The source opens:

```text
README.md
```

not:

```text
readme.md
```

On a Linux GitHub runner, those are different paths.

For the current script, the safest repository filename is:

```text
README.md
```

---

# 33.2 PERFORMANCE IS DELTA-DRIVEN

Performance vault updates happen only when:

```text
delta > 0
```

Therefore a no-change engine run does not add new performance counts.

---

# 33.3 FRESH PERFORMANCE FILES START AT ZERO

Because performance files are created on demand and loaded as empty dictionaries when
missing, the CLI board shows zeroes until new delta events are recorded.

---

# 33.4 LIFETIME BACKFILL IS NOT PRESENT

The supplied source does not include a historical backfill routine.

`performance/lifetime.json` grows through calls to:

```text
update_performance_vault()
```

triggered by the Master Sync when a positive delta occurs.

There is no separate migration that reconstructs lifetime performance from the full
AniList inventory.

---

# 33.5 GAMERSCORE BACKFILL IS NOT PRESENT

The `db_achievements.json` file contains Gamerscore state.

The code does not reconstruct historical Gamerscore from the entire inventory.

This means a fresh `db_achievements.json` can start from zero.

---

# 33.6 COMPLETION ACCOUNTING NOTE

The current Master Sync checks:

```text
is_completed = data["status"] == "COMPLETED"
```

and adds:

```text
+100 G
```

whenever a synchronization state change is processed for that title and the title is
currently completed.

The code does not maintain a separate per-title completion ledger.

This is important when modifying the completion logic.

---

# 33.7 ANILIST MUTATION NOTE

After an update, the engine sends a `SaveMediaListEntry` mutation using the currently
stored AniList score value.

The source therefore treats AniList as an actively writable target when the token exists.

---

# 33.8 GHOST SCORE NOTE

MAL Ghost score is multiplied by ten before being sent as `scoreRaw`.

This is different from merely copying the raw MAL score.

---

# 33.9 XML FILE NOTE

`mal_export.xml` is used for the manga XML scan.

`mal_anime.xml` is separately used for anime scanning.

---

# 33.10 SILENT EXCEPTIONS

Several communication functions catch exceptions broadly and do not re-raise them.

This makes the engine resilient to some output failures.

It can also make debugging harder without explicit logs.

---

# 33.11 RETRY SCOPE

The `fetch_with_armor()` wrapper is used by the main AniList inventory query.

Ghost and Void search requests use direct `requests.post()` calls rather than routing
through the retry wrapper.

---

# 33.12 HOLOGRAM DELETE

The Hologram deletion request is performed without an explicit timeout in the delete call.

The POST creating the new Hologram uses a ten-second timeout.

---

# 33.13 AIRING TELEGRAM

Only the one-hour warning explicitly calls Telegram from the airing system.

The three-hour warning is Discord-only in the current source.

---

# 33.14 PERFORMANCE BOARD SCOPE

The generated CLI board includes:

```text
Daily
Weekly
Lifetime
```

but does not directly display monthly or yearly figures.

Those figures are still written into their performance JSON files.

---

# 33.15 MONTHLY AND YEARLY DATA

Monthly and yearly files are written by the Telemetry Hub but are not loaded by
`get_performance_stats()`.

That is current source behavior.

---

# 34. KNOWN FAILURE MODES

## Missing AniList Token

Symptoms:

```text
No authenticated AniList operation
```

Potential result:

```text
No useful inventory
```

---

## Missing Discord Webhook

The Discord function immediately returns.

---

## Missing Telegram Credentials

Telegram function returns.

---

## Missing Zulip Credentials

Zulip function returns.

---

## Missing README Marker

The regex replacement has no matching block.

The source does not create the markers automatically.

---

## Wrong README Case

Using:

```text
readme.md
```

while the script expects:

```text
README.md
```

can break telemetry on case-sensitive runners.

---

## Corrupt JSON

`load_db()` returns `{}` instead of exposing the parse error.

This may make a corrupt state file look like a fresh state.

---

## AniList Request Failure

The main inventory function may return an empty or partial inventory depending on where
the fetch fails.

---

## Ghost API Failure

Ghost requests are not protected by `fetch_with_armor()`.

---

## Void API Failure

Void requests are not protected by `fetch_with_armor()`.

---

# 35. SECURITY NOTES

## 35.1 TOKENS

Never commit:

```text
ANILIST_TARGET_TOKEN
TELEGRAM_BOT_TOKEN
ZULIP_API_KEY
```

---

## 35.2 WEBHOOKS

Discord webhook URLs are secrets.

---

## 35.3 SOURCE EXPORTS

MAL XML files can contain personal tracking history.

A private repository is recommended.

---

## 35.4 BOT IDENTIFIERS

Telegram chat IDs and Zulip bot information should be treated as private configuration.

---

## 35.5 REPOSITORY HISTORY

Removing a secret from the latest commit does not guarantee removal from Git history.

If a credential is exposed:

```text
Revoke
↓
Regenerate
↓
Update secret
↓
Check repository history
```

---

# 36. FUTURE HARDENING

The current script can be improved without abandoning the Python architecture.

---

# 36.1 CENTRALIZED CONFIG

Move scoring and timing constants into a dedicated configuration object.

Potential values:

```text
ANIME_G
MANGA_G
COMPLETION_G
ANIME_DEDUCTION
MANGA_MINUTES
GHOST_DELAY
RETRY_COUNT
```

---

# 36.2 STRUCTURED LOGGING

Replace silent exception blocks with categorized diagnostics:

```text
[ANIList]
[DISCORD]
[TELEGRAM]
[ZULIP]
[GHOST]
[VOID]
[README]
[STATE]
```

---

# 36.3 EVENT IDS

Introduce deterministic event IDs such as:

```text
anime:<mediaId>:<progress>
manga:<mediaId>:<progress>
completion:<mediaId>
```

---

# 36.4 IDEMPOTENCY

Keep a processed-event ledger so the same event cannot award points twice.

---

# 36.5 COMPLETION LEDGER

Store completed media IDs independently.

This would make the +100 G rule safer.

---

# 36.6 HISTORICAL BACKFILL

Add a dedicated one-time migration mode for:

```text
Lifetime episodes
Lifetime chapters
Lifetime estimated minutes
Historical score
```

without double-awarding Gamerscore.

---

# 36.7 README BOOTSTRAP

If the telemetry markers are missing, future versions can insert them once rather than
silently failing.

---

# 36.8 GRAPHQL ERROR CHECKING

Inspect both:

```text
HTTP response
GraphQL errors
```

because GraphQL can return an error payload even when HTTP transport succeeds.

---

# 36.9 RATE LIMIT HANDLING

Use AniList response headers when available rather than relying only on fixed sleeps.

---

# 36.10 REQUEST TIMEOUTS

Apply explicit timeouts consistently to all external network calls.

---

# 36.11 MODULARIZATION

Potential future module tree:

```text
src/
├── core.py
├── anilist.py
├── performance.py
├── gamerscore.py
├── airing.py
├── ghosts.py
├── void.py
├── discord.py
├── telegram.py
├── zulip.py
└── telemetry.py
```

---

# 36.12 SQLITE OPTION

Only migrate from JSON if the project becomes large enough that:

```text
Git diffs
Schema growth
Complex queries
Concurrency
```

make JSON uncomfortable.

---

# 36.13 TYPESCRIPT OPTION

A future TypeScript dashboard could visualize the existing JSON telemetry.

Python can remain the automation core.

---

# 36.14 TEST SUITE

Future tests should cover:

```text
progress delta
Gamerscore
weekly rollover
completion
performance
airing
ghosts
void
README injection
```

---

# 36.15 DRY RUN

A future environment flag could allow:

```text
DRY_RUN=true
```

to inspect the pipeline without mutations.

---

# 36.16 READ ONLY

Another useful mode:

```text
READ_ONLY=true
```

would inspect the state without modifying AniList.

---

# 36.17 BACKFILL MODE

A dedicated:

```text
BACKFILL=true
```

could populate historical performance without generating new Gamerscore awards.

---

# 37. FINAL SYSTEM STATUS

```text
╔══════════════════════════════════════════════╗
║      ANILIST MAXIMUM OVERDRIVE V2           ║
╠══════════════════════════════════════════════╣
║ AniList Inventory     : ONLINE               ║
║ Master Sync            : ONLINE               ║
║ Gamerscore Core        : ONLINE               ║
║ Performance Vault      : ONLINE               ║
║ Performance Hologram   : ONLINE               ║
║ Airing Intelligence    : ONLINE               ║
║ MAL Ghost Radar        : ARMED                ║
║ Deep Void Protocol     : ARMED                ║
║ Discord Pipelines      : READY                ║
║ Telegram Alerts        : READY                ║
║ Zulip Archive          : READY                ║
║ README Telemetry       : ACTIVE               ║
║ JSON Memory             : ACTIVE              ║
║ 48H Purge              : ACTIVE               ║
╚══════════════════════════════════════════════╝
```

---

# 37.1 LIVE PIPELINE

```text
ANIList
   │
   ▼
FETCH
   │
   ▼
INVENTORY
   │
   ├───────────────┐
   ▼               ▼
AIRING          MASTER SYNC
                   │
             ┌─────┼─────┐
             ▼     ▼     ▼
           SCORE  PERF  DISCORD
             │     │      │
             └─────┼──────┘
                   ▼
                 ZULIP
                   │
                   ▼
               GIT STATE
                   │
                   ▼
              README TELEMETRY
```

---

# 38. AUTHOR

**Orewa Tokyo**

Project class:

```text
Personal Automation Engine
Completionist Tracking System
Anime/Manga Telemetry Hub
```

The project identity is centered around:

```text
Logic
Structure
Automation
Persistence
Completion
```

---

# 38.1 PROJECT TAGLINE

> **From passive tracking to an autonomous Otaku Command Center.**

---

# 38.2 OPERATING PHILOSOPHY

> **Execute the master sync. Leave no data behind.**

---

# 39. FINAL PRINCIPLE

```text
WATCH
  ↓
UPDATE
  ↓
DETECT
  ↓
CALCULATE
  ↓
SCORE
  ↓
MEASURE
  ↓
NOTIFY
  ↓
ARCHIVE
  ↓
PERSIST
  ↓
REPEAT
```

The engine is designed so that media progress becomes structured telemetry.

Gamerscore measures progression.

Performance measures estimated consumption.

Discord provides visualization.

Telegram provides direct alerts.

Zulip provides structured archive output.

JSON provides machine memory.

GitHub provides scheduled execution and repository persistence.

README telemetry provides a public-facing status surface.

---

# ⚡ MAXIMUM OVERDRIVE V2

```text
ENGINE STATUS      : ONLINE
SYNC STATUS        : ACTIVE
GAME CORE          : LIVE
PERFORMANCE CORE   : LIVE
HOLOGRAM           : LIVE
AIRING RADAR       : LIVE
GHOST RADAR        : ARMED
DEEP VOID          : ARMED
README TELEMETRY   : ACTIVE
VAULT              : SECURED
AUTOMATION         : ARMED

INITIATING NEXT CYCLE...
```

---

# 📜 END OF SYSTEM DOCUMENT

**AniList Maximum Overdrive Sync — V2**

`State-driven • Automated • Persistent • Gamified • Analytical • Live`

> **One source. One event. One calculation. Many synchronized outputs.**

---

# 📘 APPENDIX 01 — CONFIGURATION CONTRACT

This appendix section records the source-level contract for **Configuration Contract**.

```text
SOURCE → Configuration Contract
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 02 — ENVIRONMENT CONTRACT

This appendix section records the source-level contract for **Environment Contract**.

```text
SOURCE → Environment Contract
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 03 — STATE FILE CONTRACT

This appendix section records the source-level contract for **State File Contract**.

```text
SOURCE → State File Contract
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 04 — PERFORMANCE FIELD CONTRACT

This appendix section records the source-level contract for **Performance Field Contract**.

```text
SOURCE → Performance Field Contract
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 05 — DAILY BUCKET

This appendix section records the source-level contract for **Daily Bucket**.

```text
SOURCE → Daily Bucket
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 06 — WEEKLY BUCKET

This appendix section records the source-level contract for **Weekly Bucket**.

```text
SOURCE → Weekly Bucket
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 07 — MONTHLY BUCKET

This appendix section records the source-level contract for **Monthly Bucket**.

```text
SOURCE → Monthly Bucket
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 08 — YEARLY BUCKET

This appendix section records the source-level contract for **Yearly Bucket**.

```text
SOURCE → Yearly Bucket
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 09 — LIFETIME BUCKET

This appendix section records the source-level contract for **Lifetime Bucket**.

```text
SOURCE → Lifetime Bucket
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 10 — CLI BOARD

This appendix section records the source-level contract for **CLI Board**.

```text
SOURCE → CLI Board
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 11 — HOLOGRAM STATE

This appendix section records the source-level contract for **Hologram State**.

```text
SOURCE → Hologram State
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 12 — DISCORD PAYLOAD

This appendix section records the source-level contract for **Discord Payload**.

```text
SOURCE → Discord Payload
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 13 — ZULIP PAYLOAD

This appendix section records the source-level contract for **Zulip Payload**.

```text
SOURCE → Zulip Payload
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 14 — TELEGRAM PAYLOAD

This appendix section records the source-level contract for **Telegram Payload**.

```text
SOURCE → Telegram Payload
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 15 — AIRING STATE

This appendix section records the source-level contract for **Airing State**.

```text
SOURCE → Airing State
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 16 — GHOST STATE

This appendix section records the source-level contract for **Ghost State**.

```text
SOURCE → Ghost State
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 17 — VOID STATE

This appendix section records the source-level contract for **Void State**.

```text
SOURCE → Void State
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 18 — SYNC STATE

This appendix section records the source-level contract for **Sync State**.

```text
SOURCE → Sync State
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 19 — TITLE POOL

This appendix section records the source-level contract for **Title Pool**.

```text
SOURCE → Title Pool
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 20 — PROGRESS DELTA

This appendix section records the source-level contract for **Progress Delta**.

```text
SOURCE → Progress Delta
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 21 — ANIME SCORE

This appendix section records the source-level contract for **Anime Score**.

```text
SOURCE → Anime Score
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 22 — MANGA SCORE

This appendix section records the source-level contract for **Manga Score**.

```text
SOURCE → Manga Score
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 23 — COMPLETION BONUS

This appendix section records the source-level contract for **Completion Bonus**.

```text
SOURCE → Completion Bonus
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 24 — WEEKLY RESET

This appendix section records the source-level contract for **Weekly Reset**.

```text
SOURCE → Weekly Reset
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 25 — 1K MILESTONE

This appendix section records the source-level contract for **1K Milestone**.

```text
SOURCE → 1K Milestone
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 26 — 5K MILESTONE

This appendix section records the source-level contract for **5K Milestone**.

```text
SOURCE → 5K Milestone
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 27 — 10K PRESTIGE

This appendix section records the source-level contract for **10K Prestige**.

```text
SOURCE → 10K Prestige
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 28 — ANILIST PAGINATION

This appendix section records the source-level contract for **AniList Pagination**.

```text
SOURCE → AniList Pagination
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 29 — ANILIST DURATION

This appendix section records the source-level contract for **AniList Duration**.

```text
SOURCE → AniList Duration
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 30 — COVER COLOR

This appendix section records the source-level contract for **Cover Color**.

```text
SOURCE → Cover Color
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 31 — AIRING TIMESTAMP

This appendix section records the source-level contract for **Airing Timestamp**.

```text
SOURCE → Airing Timestamp
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 32 — GHOST SEARCH

This appendix section records the source-level contract for **Ghost Search**.

```text
SOURCE → Ghost Search
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 33 — GHOST MUTATION

This appendix section records the source-level contract for **Ghost Mutation**.

```text
SOURCE → Ghost Mutation
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 34 — VOID SEARCH

This appendix section records the source-level contract for **Void Search**.

```text
SOURCE → Void Search
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 35 — VOID MUTATION

This appendix section records the source-level contract for **Void Mutation**.

```text
SOURCE → Void Mutation
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 36 — README REGEX

This appendix section records the source-level contract for **README Regex**.

```text
SOURCE → README Regex
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 37 — MAIN SEQUENCE

This appendix section records the source-level contract for **Main Sequence**.

```text
SOURCE → Main Sequence
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 38 — PURGE SEQUENCE

This appendix section records the source-level contract for **Purge Sequence**.

```text
SOURCE → Purge Sequence
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 39 — DEPLOYMENT CHECK

This appendix section records the source-level contract for **Deployment Check**.

```text
SOURCE → Deployment Check
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.



---

# 📘 APPENDIX 40 — TROUBLESHOOTING CHECK

This appendix section records the source-level contract for **Troubleshooting Check**.

```text
SOURCE → Troubleshooting Check
```

The current implementation should be treated as the authoritative behavior.

The engine favors simple state files, explicit function boundaries, and direct API
operations.

The surrounding README explains the intended purpose, while the Python source remains
the final authority for exact runtime behavior.

Operational sequence:

```text
LOAD
 ↓
PROCESS
 ↓
VALIDATE
 ↓
SAVE
 ↓
OUTPUT
```

When modifying this subsystem, verify its neighboring state files and notification
paths before changing the shared behavior.

