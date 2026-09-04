import json
import os
import time
from typing import Any, Dict, Optional, Tuple

import requests

# ============================================================
# MAL <- ANILIST SHORT DELTA SYNC v2
# ============================================================
# Source : AniList user "Orewatokyo"
# Target : MyAnimeList
# Mode   : Manual GitHub Actions only
#
# The previous deep run is assumed to have synchronized the existing
# library. This engine therefore uses a persistent per-media timestamp
# baseline and only writes AniList entries whose updatedAt changed.
#
# GitHub Actions secrets required:
#   ANILIST_TARGET_TOKEN
#   MAL_CLIENT_ID
#   MAL_CLIENT_SECRET
#   MAL_REFRESH_TOKEN
#
# Persistent repository state:
#   mal_delta_state.json
#
# IMPORTANT:
# The workflow commits mal_delta_state.json after successful processing.
# This is required because GitHub-hosted runners are temporary.
# ============================================================

SOURCE_USERNAME = "Orewatokyo"

ANILIST_TOKEN = os.environ.get("ANILIST_TARGET_TOKEN", "").strip()
MAL_CLIENT_ID = os.environ.get("MAL_CLIENT_ID", "").strip()
MAL_CLIENT_SECRET = os.environ.get("MAL_CLIENT_SECRET", "").strip()
MAL_REFRESH_TOKEN = os.environ.get("MAL_REFRESH_TOKEN", "").strip()

STATE_FILE = "mal_delta_state.json"

ANILIST_URL = "https://graphql.anilist.co"
MAL_TOKEN_URL = "https://myanimelist.net/v1/oauth2/token"
MAL_ME_URL = "https://api.myanimelist.net/v2/users/@me"
MAL_ANIME_DETAILS_URL = "https://api.myanimelist.net/v2/anime/{anime_id}"
MAL_UPDATE_URL = "https://api.myanimelist.net/v2/anime/{anime_id}/my_list_status"

ANILIST_HEADERS = {
    "Authorization": f"Bearer {ANILIST_TOKEN}" if ANILIST_TOKEN else "",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

MAL_STATUS_MAP = {
    "CURRENT": "watching",
    "REPEATING": "watching",
    "PLANNING": "plan_to_watch",
    "COMPLETED": "completed",
    "PAUSED": "on_hold",
    "DROPPED": "dropped",
}

ANILIST_QUERY = """
query ($userName: String, $page: Int) {
  Page(page: $page, perPage: 50) {
    pageInfo { hasNextPage }
    mediaList(
      userName: $userName,
      type: ANIME,
      sort: [UPDATED_TIME_DESC]
    ) {
      updatedAt
      status
      score(format: POINT_100)
      progress
      startedAt { year month day }
      completedAt { year month day }
      media {
        id
        idMal
        title { romaji english }
        episodes
      }
    }
  }
}
"""


def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {}

    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception as exc:
        print(f"⚠️ Could not read {STATE_FILE}: {exc}")
        return {}


def save_state(state: dict) -> None:
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2, sort_keys=True)
    os.replace(tmp, STATE_FILE)


def require_config() -> None:
    missing = []

    if not ANILIST_TOKEN:
        missing.append("ANILIST_TARGET_TOKEN")
    if not MAL_CLIENT_ID:
        missing.append("MAL_CLIENT_ID")
    if not MAL_CLIENT_SECRET:
        missing.append("MAL_CLIENT_SECRET")
    if not MAL_REFRESH_TOKEN:
        missing.append("MAL_REFRESH_TOKEN")

    if missing:
        raise SystemExit(
            "❌ Missing GitHub Secrets: " + ", ".join(missing)
        )


def request_with_retry(
    method: str,
    url: str,
    *,
    headers: Optional[Dict[str, str]] = None,
    retries: int = 4,
    **kwargs: Any,
) -> requests.Response:
    last_error: Optional[str] = None

    for attempt in range(retries):
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                timeout=30,
                **kwargs,
            )

            if response.status_code in (429, 500, 502, 503, 504):
                last_error = (
                    f"HTTP {response.status_code}: "
                    f"{response.text[:300]}"
                )
                retry_after = response.headers.get("Retry-After")
                try:
                    delay = max(2, int(float(retry_after))) if retry_after else 0
                except ValueError:
                    delay = 0
                time.sleep(delay or (2 + attempt * 2))
                continue

            return response

        except requests.RequestException as exc:
            last_error = str(exc)
            time.sleep(2 + attempt * 2)

    raise RuntimeError(last_error or "HTTP request failed after retries.")


def refresh_mal_token() -> Tuple[str, str]:
    print("🔐 Refreshing MAL OAuth token...")

    response = request_with_retry(
        "POST",
        MAL_TOKEN_URL,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        data={
            "client_id": MAL_CLIENT_ID,
            "client_secret": MAL_CLIENT_SECRET,
            "grant_type": "refresh_token",
            "refresh_token": MAL_REFRESH_TOKEN,
        },
    )

    if response.status_code != 200:
        print("❌ MAL token refresh failed.")
        print("HTTP:", response.status_code)
        try:
            body = response.json()
            print("Error:", body.get("error", "unknown"))
            print("Message:", body.get("message", "unknown"))
        except Exception:
            print(response.text[:500])
        raise SystemExit(1)

    body = response.json()
    access_token = body.get("access_token")
    new_refresh_token = body.get("refresh_token") or MAL_REFRESH_TOKEN

    if not access_token:
        raise SystemExit("❌ MAL returned no access token.")

    print("✅ MAL access token ready.")
    return access_token, new_refresh_token


def verify_mal(access_token: str) -> None:
    response = request_with_retry(
        "GET",
        MAL_ME_URL,
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
    )

    if response.status_code == 401:
        raise PermissionError("MAL access token rejected.")

    if response.status_code != 200:
        raise RuntimeError(
            f"MAL account test failed: HTTP {response.status_code} "
            f"{response.text[:300]}"
        )

    username = response.json().get("name", "unknown")
    print(f"✅ MAL account authenticated: {username}")


def fetch_anilist_changes(previous_updates: dict) -> Tuple[list[dict], dict]:
    """Inspect AniList newest-first and return only changed entries."""
    changed: list[dict] = []
    current_updates: dict[str, int] = {}
    page = 1
    page_count = 0

    while True:
        response = request_with_retry(
            "POST",
            ANILIST_URL,
            headers=ANILIST_HEADERS,
            json={
                "query": ANILIST_QUERY,
                "variables": {
                    "userName": SOURCE_USERNAME,
                    "page": page,
                },
            },
        )

        if response.status_code != 200:
            print("❌ AniList request failed.")
            print("HTTP:", response.status_code)
            print(response.text[:500])
            raise SystemExit(1)

        payload = response.json()
        if payload.get("errors"):
            print("❌ AniList GraphQL errors:")
            print(payload["errors"])
            raise SystemExit(1)

        page_data = payload.get("data", {}).get("Page", {})
        batch = page_data.get("mediaList", [])
        if not batch:
            break

        page_count += 1

        for entry in batch:
            media = entry.get("media") or {}
            media_id = media.get("id")
            if media_id is None:
                continue

            updated_at = int(entry.get("updatedAt") or 0)
            media_key = str(media_id)
            current_updates[media_key] = updated_at

            previous = int(previous_updates.get(media_key, 0) or 0)
            if updated_at > previous:
                changed.append(entry)

        if not page_data.get("pageInfo", {}).get("hasNextPage"):
            break

        page += 1
        time.sleep(0.15)

    print(
        f"✅ AniList checked: {len(current_updates)} anime "
        f"across {page_count} page(s)."
    )
    return changed, current_updates


def anilist_score_to_mal(score: Any) -> Optional[int]:
    if score is None:
        return None

    try:
        value = float(score)
    except (TypeError, ValueError):
        return None

    if value <= 0:
        return None

    return max(1, min(10, int(round(value / 10.0))))


def format_date(value: Optional[dict]) -> Optional[str]:
    if not value:
        return None

    year = value.get("year")
    month = value.get("month")
    day = value.get("day")

    if not year or not month or not day:
        return None

    return f"{year:04d}-{month:02d}-{day:02d}"


def title_for(entry: dict) -> str:
    media = entry.get("media") or {}
    titles = media.get("title") or {}
    return (
        titles.get("english")
        or titles.get("romaji")
        or f"MAL ID {media.get('idMal', '?')}"
    )


def fetch_mal_entry(access_token: str, mal_id: int) -> dict:
    """Fetch only the one MAL anime corresponding to a changed AniList entry."""
    response = request_with_retry(
        "GET",
        MAL_ANIME_DETAILS_URL.format(anime_id=mal_id),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Accept": "application/json",
        },
        params={
            "fields": "my_list_status"
        },
    )

    if response.status_code == 401:
        raise PermissionError("MAL access token rejected.")

    if response.status_code == 404:
        return {}

    if response.status_code != 200:
        raise RuntimeError(
            f"MAL lookup failed for {mal_id}: HTTP {response.status_code} "
            f"{response.text[:300]}"
        )

    return response.json().get("my_list_status") or {}


def build_mal_update(entry: dict, current: dict) -> dict:
    desired_status = MAL_STATUS_MAP.get(entry.get("status"))
    desired_progress = int(entry.get("progress") or 0)
    desired_score = anilist_score_to_mal(entry.get("score"))

    current_status = current.get("status")
    current_progress = int(current.get("num_watched_episodes") or 0)
    current_score = int(current.get("score") or 0)

    update: dict[str, Any] = {}

    if desired_status and desired_status != current_status:
        update["status"] = desired_status

    if desired_progress != current_progress:
        update["num_watched_episodes"] = desired_progress

    if desired_score is not None and desired_score != current_score:
        update["score"] = desired_score

    desired_start = format_date(entry.get("startedAt"))
    desired_finish = format_date(entry.get("completedAt"))

    if desired_start and desired_start != current.get("start_date"):
        update["start_date"] = desired_start

    if (
        desired_finish
        and desired_status == "completed"
        and desired_finish != current.get("finish_date")
    ):
        update["finish_date"] = desired_finish

    return update


def update_mal_entry(
    access_token: str,
    entry: dict,
    current: dict,
) -> bool:
    media = entry.get("media") or {}
    mal_id = media.get("idMal")

    if not mal_id:
        return False

    update = build_mal_update(entry, current)
    if not update:
        return False

    title = title_for(entry)
    print(f"🔄 {title} -> MAL {mal_id}")
    print("   Fields:", ", ".join(update.keys()))

    response = request_with_retry(
        "PUT",
        MAL_UPDATE_URL.format(anime_id=int(mal_id)),
        headers={
            "Authorization": f"Bearer {access_token}",
            "Content-Type": "application/x-www-form-urlencoded",
            "Accept": "application/json",
        },
        data=update,
    )

    if response.status_code == 401:
        raise PermissionError("MAL access token rejected.")

    if response.status_code not in (200, 201):
        print(
            f"   ❌ MAL update failed: HTTP {response.status_code}"
        )
        print(response.text[:500])
        return False

    print("   ✅ MAL updated.")
    return True


def main() -> None:
    print("=" * 64)
    print("       MAL <- ANILIST SHORT DELTA SYNC v2")
    print("=" * 64)

    require_config()

    state = load_state()
    previous_updates = state.get("media_updates", {})
    if not isinstance(previous_updates, dict):
        previous_updates = {}

    if previous_updates:
        print("⚡ DELTA MODE ACTIVE")
        print(f"   Stored AniList media states: {len(previous_updates)}")
    else:
        print("🧭 INITIAL BASELINE MODE")
        print("   No MAL library scan will be performed.")
        print("   No MAL writes will be performed on this baseline run.")

    access_token, new_refresh_token = refresh_mal_token()
    verify_mal(access_token)

    print("📡 Checking AniList for new/updated entries...")
    changed_entries, current_updates = fetch_anilist_changes(previous_updates)

    # Initial baseline: record the complete AniList timestamp map only.
    if not previous_updates:
        save_state({
            "version": 2,
            "media_updates": current_updates,
        })

        print()
        print("=" * 64)
        print("✅ DELTA BASELINE CREATED")
        print("=" * 64)
        print("AniList entries remembered:", len(current_updates))
        print("MAL writes performed       : 0")
        print("Next run will process only entries whose AniList updatedAt changed.")

        if new_refresh_token != MAL_REFRESH_TOKEN:
            print("⚠️ MAL returned a new refresh token; update the GitHub Secret.")
        return

    print(f"✅ Changed/new AniList entries: {len(changed_entries)}")

    updated = 0
    unchanged = 0
    skipped_no_mal_id = 0
    failed = 0
    successful_media_ids: set[str] = set()

    for entry in changed_entries:
        media = entry.get("media") or {}
        media_id = media.get("id")
        mal_id = media.get("idMal")
        title = title_for(entry)

        if media_id is None:
            failed += 1
            print(f"❌ {title}: AniList media ID missing.")
            continue

        media_key = str(media_id)

        if not mal_id:
            skipped_no_mal_id += 1
            print(f"⏭️ {title}: no MAL ID; nothing to update.")
            successful_media_ids.add(media_key)
            continue

        try:
            current = fetch_mal_entry(access_token, int(mal_id))
            changed = update_mal_entry(access_token, entry, current)

            if changed:
                updated += 1
            else:
                unchanged += 1

            successful_media_ids.add(media_key)

        except PermissionError:
            print("🔄 MAL access token expired/rejected. Refreshing once...")

            access_token, new_refresh_token = refresh_mal_token()

            try:
                current = fetch_mal_entry(access_token, int(mal_id))
                changed = update_mal_entry(access_token, entry, current)

                if changed:
                    updated += 1
                else:
                    unchanged += 1

                successful_media_ids.add(media_key)

            except Exception as exc:
                failed += 1
                print(f"❌ Retry failed for {title}: {exc}")

        except Exception as exc:
            failed += 1
            print(f"❌ {title}: {exc}")

        time.sleep(0.4)

    # Merge only successfully handled entries into the persistent map.
    # Failed entries deliberately keep their previous timestamp so they
    # are detected and retried on the next manual run.
    merged_updates = dict(previous_updates)
    for entry in changed_entries:
        media = entry.get("media") or {}
        media_id = media.get("id")
        if media_id is None:
            continue

        media_key = str(media_id)
        if media_key in successful_media_ids:
            merged_updates[media_key] = int(entry.get("updatedAt") or 0)

    new_cursor = max(merged_updates.values(), default=0)
    save_state({
        "version": 2,
        "last_anilist_update": new_cursor,
        "media_updates": merged_updates,
    })

    print()
    print("=" * 64)
    print("⚡ MAL SHORT DELTA SYNC COMPLETE")
    print("=" * 64)
    print("AniList changed/new entries:", len(changed_entries))
    print("Updated on MAL             :", updated)
    print("Already synchronized       :", unchanged)
    print("No MAL ID                  :", skipped_no_mal_id)
    print("Failed                     :", failed)
    print("Stored AniList states      :", len(merged_updates))
    print("AniList cursor             :", new_cursor)

    if failed:
        print("⚠️ Failed entries were NOT advanced and will be retried next run.")

    if new_refresh_token != MAL_REFRESH_TOKEN:
        print("⚠️ MAL returned a new refresh token; update the GitHub Secret before the next run.")
    else:
        print("✅ MAL refresh token unchanged.")


if __name__ == "__main__":
    main()
