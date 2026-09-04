# ⚡ ANIME + MANGA MAXIMUM OVERDRIVE V2

> Split-engine AniList telemetry system for Anime and Manga.

![Status](https://img.shields.io/badge/status-active-success)
![Python](https://img.shields.io/badge/python-3.10+-blue)
![GitHub%20Actions](https://img.shields.io/badge/GitHub%20Actions-enabled-2088FF)
![AniList](https://img.shields.io/badge/AniList-GraphQL-02A9FF)
![Discord](https://img.shields.io/badge/Discord-webhooks-5865F2)

## 🧭 What Changed

V2 is now split into two focused engines.

- `anime_engine.py` handles Anime only.
- `manga_engine.py` handles Manga only.
- Anime and Manga use isolated memory databases.
- Anime and Manga have independent GitHub Actions workflows.
- Discord Forum routing is preserved.
- Special target lists get dedicated threads.
- Everything else goes to a stable `General Updates` thread.
- First-run data is silently baselined.
- Newly discovered media can be silently baselined.
- Forward progress generates activity.
- Rollbacks do not generate forward-progress rewards.
- GitHub Actions persists the engine memory.

---

## 📁 Repository Layout

```text
repository/
├── anime_engine.py
├── manga_engine.py
├── README.md
├── mal_export.xml
├── mal_anime.xml
├── .github/
│   └── workflows/
│       ├── anime_engine.yml
│       └── manga_engine.yml
├── db_anime_sync.json
├── db_anime_inventory.json
├── db_anime_timestamp.json
├── db_anime_threads.json
├── db_anime_messages.json
├── db_anime_ghosts.json
├── db_anime_void.json
├── db_anime_airing.json
├── db_anime_achievements.json
├── db_anime_performance_msg.json
├── db_manga_sync.json
├── db_manga_inventory.json
├── db_manga_timestamp.json
├── db_manga_threads.json
├── db_manga_messages.json
├── db_manga_ghosts.json
├── db_manga_void.json
├── db_manga_airing.json
├── db_manga_achievements.json
└── db_manga_performance_msg.json
```

---

## 🧠 Core Design

AniList is the live source.

The repository is persistent memory.

GitHub-hosted runners are temporary.

The JSON databases make each engine remember what it already saw.

The split architecture prevents Anime state and Manga state from colliding.

The engines follow this high-level pattern:

```text
AniList
  ↓
Isolated inventory
  ↓
Delta detection
  ↓
Notification routing
  ↓
Performance / achievements
  ↓
Persistent memory
```

---

## 🎯 Anime Engine

`anime_engine.py` is an Anime-only engine.

Its AniList GraphQL query uses:

```text
type: ANIME
```

The engine also verifies the media type before the master sync path accepts an entry.

Anime state uses files beginning with:

```text
db_anime_
```

The primary Discord endpoint is:

```text
DISCORD_ANILIST_ANIME_WEBHOOK
```

The Anime Zulip stream is:

```text
Anime-Vault
```

The Anime README telemetry block uses:

```text
<!-- ANIME_TELEMETRY_START -->
```text
TODAY
─────────────────────────
Anime             1 eps
Time             22 min
Gamerscore      10 G

THIS WEEK
─────────────────────────
Anime            19 eps
Time            418 min
Gamerscore     604 G

ALL TIME
─────────────────────────
Episodes         74
Minutes       1,547
Gamerscore  32,750 G
Completed       125

```
<!-- ANIME_TELEMETRY_END -->
```

---

## 📖 Manga Engine

`manga_engine.py` is a Manga-only engine.

Its AniList GraphQL query uses:

```text
type: MANGA
```

The engine also verifies the media type before the master sync path accepts an entry.

Manga state uses files beginning with:

```text
db_manga_
```

The primary Discord endpoint is:

```text
DISCORD_ANILIST_MANGA_WEBHOOK
```

The Manga Zulip stream is:

```text
Manga-Vault
```

The Manga README telemetry block should use:

```text
<!-- MANGA_TELEMETRY_START -->
<!-- MANGA_TELEMETRY_END -->
```

---

# 🧵 Discord Forum Routing

Discord Forum Channels require a thread for webhook posts.

The engines therefore create or reuse threads.

## 🎯 Target Lists

Current special-list vocabulary includes:

- `anime movies`
- `iseki`
- `isekai`
- `milf`
- `loli`
- `plan to continue`
- `hentai`
- `favourite`
- `fav`
- `planning`

## Dedicated Threads

A matching list gets its own thread.

Examples:

```text
[ANIME] Planning
[ANIME] Favourite
[ANIME] Hentai
[MANGA] Planning
[MANGA] Favourite
[MANGA] Hentai
```

## General Updates

Anything that does not match a target list goes to:

```text
[ANIME] General Updates
```

or:

```text
[MANGA] General Updates
```

This is intentional.

Normal AniList states such as `Watching`, `Completed`, or another custom list are not ignored.

## Thread Memory

Anime thread IDs are stored in:

```text
db_anime_threads.json
```

Manga thread IDs are stored in:

```text
db_manga_threads.json
```

The stored ID is reused on future runs.

## Forum Safety

If thread creation fails, the main engine skips the Forum notification.

It does not attempt an invalid direct Forum webhook post.

This prevents Discord error:

```text
Webhooks posted to forum channels must have a thread_name or thread_id
```

---

# 🔥 Progress System

The engines compare current AniList progress with persistent memory.

## Forward Progress

Example:

```text
Previous: 5
Current:  6
Delta:    1
```

The engine treats that as a real activity event.

## Anime G Score

Anime earns:

```text
10 G per forward episode
```

Completion adds the configured completion bonus.

## Manga G Score

Manga earns:

```text
2 G per forward chapter
```

Completion adds the configured completion bonus.

## No Change

If the progress is unchanged:

```text
No notification
No reward
No performance increment
```

## Rollback

If stored progress is higher than current progress:

```text
20 → 15
```

the engine updates memory but does not reward the negative change.

## New Media

When a new media ID is discovered after initial setup, the engine can establish its current progress silently.

Example:

```text
New Anime
Current progress: 12
Baseline: 12
Notification: none
```

The next real change:

```text
12 → 13
```

becomes a normal progress event.

---

# 🧪 First-Run Baseline

The first run is quiet by design.

A pre-existing list may contain hundreds of completed entries.

Treating every existing episode as newly watched would create fake telemetry.

The baseline prevents:

- Discord spam
- incorrect G totals
- false achievement jumps
- noisy Zulip archives
- inflated performance reports

The intended first-run sequence is:

```text
Empty memory
  ↓
Scan list
  ↓
Store current state
  ↓
No progress alerts
  ↓
Future runs become delta-driven
```

Do not delete the database just to fix a normal notification problem.

Deleting memory resets the baseline.

---

# 🔎 AniList GraphQL

Endpoint:

```text
https://graphql.anilist.co
```

The target token is read from:

```text
ANILIST_TARGET_TOKEN
```

The engines use a bearer authorization header when the token exists.

## Inventory Fields

The inventory stores the information needed by downstream modules.

Common values include:

- media ID
- progress
- score
- status
- custom list category
- media type
- cover URL
- cover color
- duration
- next airing information
- Romaji title
- English title
- total episodes
- total chapters

## Delta Timestamp

Anime:

```text
db_anime_timestamp.json
```

Manga:

```text
db_manga_timestamp.json
```

The timestamp is used to avoid repeatedly processing old entries once the initial inventory is known.

---

# 🏷️ Smart Categorization

Custom AniList lists are checked first.

If there is an active custom list, the first active category becomes the routing category.

Otherwise the engine can apply descriptor-based classification.

## Movie

Anime movie format can map to:

```text
Anime movies
```

## Isekai

Descriptors containing:

```text
isekai
```

can map to:

```text
Iseki
```

## Adult

Descriptors including:

```text
hentai
ecchi
adult
smut
```

can map to:

```text
Hentai
```

## MILF

Descriptors including:

```text
milf
older woman
mother
```

can map to:

```text
Milf
```

## Loli

The:

```text
loli
```

descriptor can map to:

```text
Loli
```

These classifications are routing hints.

They do not modify the AniList database taxonomy.

---

# ⏰ Airing Intelligence

The Anime engine includes airing logic using AniList `nextAiringEpisode`.

## Three-Hour Warning

An upcoming episode between three hours and one hour away can trigger a warning.

## One-Hour Warning

An upcoming episode within one hour can trigger a final warning.

## Telegram

The final warning can also be sent through Telegram.

## Discord Fields

Airing alerts can contain:

- Romaji title
- telecast timestamp
- relative countdown
- cover image

The Manga split keeps the compatibility structure, but Manga is not used as an Anime scraper.

---

# 👻 Ghost Radar

Ghost Radar looks for entries found in MAL exports but not present in the current AniList memory.

## Anime Source

```text
mal_anime.xml
```

## Manga Source

```text
mal_export.xml
```

## Recovery Flow

```text
MAL export
  ↓
Known title comparison
  ↓
Ghost candidate
  ↓
AniList search
  ↓
Optional list restoration
  ↓
Discord result
```

The Anime engine uses Anime media type.

The Manga engine uses Manga media type.

Keeping this media boundary avoids accidental cross-type recovery.

---

# 🌌 Deep Void

The Deep Void module handles stored recovery candidates.

Anime:

```text
db_anime_void.json
```

Manga:

```text
db_manga_void.json
```

Each candidate is resolved through AniList using its intended media type.

Successful recovery can write back to AniList when the target token exists.

The module also emits a Discord recovery log.

---

# 🏆 Achievement Engine

Each engine has an isolated achievement database.

Anime:

```text
db_anime_achievements.json
```

Manga:

```text
db_manga_achievements.json
```

The system tracks:

- weekly G
- lifetime G
- milestone thresholds
- prestige state

Current milestone examples include:

```text
1,000 G
5,000 G
```

The achievement system is triggered by forward progress.

Rollback events do not mint forward-progress rewards.

---

# 📈 Performance Telemetry

The performance layer tracks activity at multiple scopes.

```text
daily
weekly
monthly
yearly
lifetime
```

Anime performance tracks:

- episodes
- anime minutes
- G score
- completed series

Manga performance tracks:

- chapters
- manga minutes
- G score
- completed series

The performance webhook can maintain a live Discord board.

The previous performance message ID is stored in the engine-specific performance message database.

Anime:

```text
db_anime_performance_msg.json
```

Manga:

```text
db_manga_performance_msg.json
```

---

# 📟 GitHub Logs

The engines intentionally produce useful logs.

Typical Anime startup:

```text
=== MAXIMUM OVERDRIVE V2 ENGINE: ANIME CORE SPINNING UP ===
```

Typical delta mode:

```text
>>> [SYSTEM] ANIME DELTA-SYNC ENGAGED...
```

Typical baseline:

```text
[BASELINE] New Anime discovered: ...
```

Typical progress:

```text
[🔥 UPDATE DETECTED] ...
```

Typical rollback:

```text
[ROLLBACK] ...
```

Typical completion:

```text
=== MAXIMUM OVERDRIVE V2 ENGINE: ANIME CYCLE COMPLETE ===
```

The Manga engine follows the same operational pattern.

---

# 💬 Discord Communication

The common Discord sender supports:

- title
- description
- embed color
- fields
- image
- author
- username override
- thread ID

## Main Update

Main Anime/Manga updates use their respective Forum webhook.

## VIP Update

Priority franchises can receive a secondary notification through:

```text
DISCORD_FAVORITES_WEBHOOK
```

Current priorities are:

- One Piece
- Detective Conan
- Kono Suba
- Dragon Ball Z

The VIP route is independent of the normal target-list category.

---

# 📡 Telegram

Telegram requires:

```text
TELEGRAM_BOT_TOKEN
TELEGRAM_CHAT_ID
```

If either value is missing, Telegram alerts safely become no-ops.

The implementation can send either text messages or cover images with captions.

Telegram is intended for concise alert delivery rather than primary state storage.

---

# 🛰️ Zulip

Zulip requires:

```text
ZULIP_SERVER_URL
ZULIP_BOT_EMAIL
ZULIP_API_KEY
```

Anime stream:

```text
Anime-Vault
```


---

