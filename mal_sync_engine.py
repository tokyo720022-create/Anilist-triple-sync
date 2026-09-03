import json
import os
import time
from typing import Dict, Any, Optional

import requests

# ============================================================
# MAL ← ANIList MANUAL SYNC ENGINE
# ============================================================
# Source: AniList
# Target: MyAnimeList
#
# Required GitHub Actions secrets:
#   ANILIST_TARGET_TOKEN
#   MAL_CLIENT_ID
#   MAL_CLIENT_SECRET
#   MAL_REFRESH_TOKEN
#
# The engine syncs current anime status, score and watched episodes.
# It does NOT modify AniList and does NOT touch manga.
# ============================================================

SOURCE_USERNAME = "Orewatokyo"

ANILIST_TOKEN = os.environ.get("ANILIST_TARGET_TOKEN", "").strip()
MAL_CLIENT_ID = os.environ.get("MAL_CLIENT_ID", "").strip()
MAL_CLIENT_SECRET = os.environ.get("MAL_CLIENT_SECRET", "").strip()
MAL_REFRESH_TOKEN = os.environ.get("MAL_REFRESH_TOKEN", "").strip()

ANILIST_URL = "https://graphql.anilist.co"
MAL_TOKEN_URL = "https://myanimelist.net/v1/oauth2/token"
MAL_ANIMELIST_URL = "https://api.myanimelist.net/v2/users/@me/animelist"
MAL_UPDATE_URL = "https://api.myanimelist.net/v2/anime/{anime_id}/my_list_status"
STATE_FILE = "mal_delta_state.json"

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



def load_state() -> dict:
    if not os.path.exists(STATE_FILE):
        return {}
    try:
        with open(STATE_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        return data if isinstance(data, dict) else {}
    except Exception:
        return {}


def save_state(state: dict) -> None:
    tmp = STATE_FILE + ".tmp"
    with open(tmp, "w", encoding="utf-8") as f:
        json.dump(state, f, indent=2)
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
            "❌ Missing required secrets: " + ", ".join(missing)
        )


def request_with_retry(
    method: str,
    url: str,
    *,
    headers: Optional[Dict[str, str]] = None,
    **kwargs: Any,
) -> requests.Response:
    last_error = None

    for attempt in range(3):
        try:
            response = requests.request(
                method,
                url,
                headers=headers,
                timeout=30,
                **kwargs,
            )

            if response.status_code not in (429, 500, 502, 503, 504):
                return response

            last_error = f"HTTP {response.status_code}: {response.text[:300]}"

        except requests.RequestException as exc:
            last_error = str(exc)

        time.sleep(2 + attempt * 2)

    raise RuntimeError(last_error or "Request failed after retries.")


def refresh_mal_token() -> tuple[str, str]:
    print("🔐 Refreshing MAL OAuth token...")

    response = request_with_retry(
        "POST",
        MAL_TOKEN_URL,
        headers={"Content-Type": "application/x-www-form-urlencoded"},
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


def fetch_anilist_delta(last_sync: int) -> tuple[list[dict], int]:
    query = """
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
            idMal
            title { romaji english }
            episodes
          }
        }
      }
    }
    """

    changed = []
    highest_seen = last_sync
    page = 1

    while True:
        response = request_with_retry(
            "POST",
            ANILIST_URL,
            headers=ANILIST_HEADERS,
            json={
                "query": query,
                "variables": {"userName": SOURCE_USERNAME, "page": page},
            },
        )

        if response.status_code != 200:
            print("❌ AniList request failed.")
            print("HTTP:", response.status_code)
            print(response.text[:500])
            raise SystemExit(1)

        payload = response.json()

        if payload.get("errors"):
            print("❌ AniList GraphQL error:")
            print(payload["errors"])
            raise SystemExit(1)

        page_data = payload.get("data", {}).get("Page", {})
        batch = page_data.get("mediaList", [])

        if not batch:
            break

        stop = False
        for entry in batch:
            updated_at = int(entry.get("updatedAt") or 0)
            highest_seen = max(highest_seen, updated_at)

            if last_sync and updated_at <= last_sync:
                stop = True
                break

            changed.append(entry)

        if stop or not page_data.get("pageInfo", {}).get("hasNextPage"):
            break

        page += 1
        time.sleep(0.25)

    return changed, highest_seen


def anilist_score_to_mal(score_100: Any) -> Optional[int]:
    if score_100 is None:
        return None

    try:
        score = float(score_100)
    except (TypeError, ValueError):
        return None

    if score <= 0:
        return None

    # AniList POINT_100 → MAL 1–10.
    converted = int(round(score / 10.0))
    return max(1, min(10, converted))


def format_date(date_obj: Optional[dict]) -> Optional[str]:
    if not date_obj:
        return None

    year = date_obj.get("year")
    month = date_obj.get("month")
    day = date_obj.get("day")

    if not year or not month or not day:
        return None

    return f"{year:04d}-{month:02d}-{day:02d}"


def sync_entry(
    access_token: str,
    anilist_entry: dict,
    mal_current: dict,
) -> bool:
    media = anilist_entry.get("media") or {}
    mal_id = media.get("idMal")

    if not mal_id:
        return False

    desired_status = MAL_STATUS_MAP.get(anilist_entry.get("status"))
    desired_progress = int(anilist_entry.get("progress") or 0)
    desired_score = anilist_score_to_mal(anilist_entry.get("score"))

    current_status = mal_current.get("status")
    current_progress = int(mal_current.get("num_episodes_watched") or 0)
    current_score = int(mal_current.get("score") or 0)

    # Only send fields that actually need changing.
    update_data: dict[str, Any] = {}

    if desired_status and desired_status != current_status:
        update_data["status"] = desired_status

    if desired_progress != current_progress:
        update_data["num_watched_episodes"] = desired_progress

    if desired_score is not None and desired_score != current_score:
        update_data["score"] = desired_score

    # Preserve AniList start/finish dates when present.
    start_date = format_date(anilist_entry.get("startedAt"))
    finish_date = format_date(anilist_entry.get("completedAt"))

    if start_date:
        update_data["start_date"] = start_date

    if finish_date and desired_status == "completed":
        update_data["finish_date"] = finish_date

    if not update_data:
        return False

    title = (
        media.get("title", {}).get("english")
        or media.get("title", {}).get("romaji")
        or f"MAL ID {mal_id}"
    )

    print(
        f"🔄 {title} | "
        f"status={current_status}->{desired_status} "
        f"episodes={current_progress}->{desired_progress} "
        f"score={current_score}->{desired_score}"
    )

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept": "application/json",
    }

    response = request_with_retry(
        "PUT",
        MAL_UPDATE_URL.format(anime_id=mal_id),
        headers=headers,
        data=update_data,
    )

    if response.status_code == 401:
        raise PermissionError("MAL access token expired or rejected.")

    if response.status_code not in (200, 201):
        print(
            f"   ❌ MAL update failed for {title}: "
            f"HTTP {response.status_code}"
        )
        print(response.text[:500])
        return False

    print("   ✅ MAL updated.")
    return True


def main() -> None:
    require_config()

    state = load_state()
    last_sync = int(state.get("last_anilist_update", 0) or 0)

    if last_sync:
        print("⚡ SHORT DELTA MODE")
        print(f"   Last AniList cursor: {last_sync}")
    else:
        print("🧭 Creating initial delta baseline.")
        print("   The existing MAL library will NOT be downloaded again.")
        print("   The existing MAL data is assumed to be synchronized by the previous deep run.")

    access_token, new_refresh_token = refresh_mal_token()

    print("📡 Checking AniList for changes...")
    changed_entries, highest_seen = fetch_anilist_delta(last_sync)

    # First run of this version: only establish the cursor.
    if not last_sync:
        if highest_seen <= 0:
            raise SystemExit("❌ Could not establish AniList update cursor.")

        save_state({"last_anilist_update": highest_seen})

        print()
        print("=" * 64)
        print("✅ DELTA BASELINE CREATED")
        print("=" * 64)
        print("Changed entries processed:", 0)
        print("AniList cursor:", highest_seen)
        print("Future runs will process only NEW/UPDATED AniList entries.")
        return

    print(f"✅ AniList changes found: {len(changed_entries)}")

    updated = 0
    unchanged = 0
    skipped_no_mal_id = 0
    failed = 0

    for entry in changed_entries:
        media = entry.get("media") or {}
        mal_id = media.get("idMal")

        if not mal_id:
            skipped_no_mal_id += 1
            continue

        title_data = media.get("title") or {}
        title = title_data.get("english") or title_data.get("romaji") or f"MAL ID {mal_id}"

        try:
            mal_current = fetch_mal_entry(access_token, int(mal_id))
            changed = sync_entry(access_token, entry, mal_current)

            if changed:
                updated += 1
            else:
                unchanged += 1

        except PermissionError:
            print("🔄 MAL access token expired. Refreshing...")
            access_token, new_refresh_token = refresh_mal_token()

            try:
                mal_current = fetch_mal_entry(access_token, int(mal_id))
                changed = sync_entry(access_token, entry, mal_current)

                if changed:
                    updated += 1
                else:
                    unchanged += 1

            except Exception as exc:
                print(f"❌ Retry failed for {title}: {exc}")
                failed += 1

        except Exception as exc:
            print(f"❌ {title}: {exc}")
            failed += 1

        time.sleep(0.5)

    # Save the newest AniList timestamp after processing this batch.
    # Next run therefore starts strictly after this point.
    state["last_anilist_update"] = highest_seen
    save_state(state)

    print()
    print("=" * 64)
    print("⚡ MAL SHORT DELTA SYNC COMPLETE")
    print("=" * 64)
    print("AniList changed entries:", len(changed_entries))
    print("Updated on MAL         :", updated)
    print("Already synchronized   :", unchanged)
    print("No MAL ID              :", skipped_no_mal_id)
    print("Failed                 :", failed)
    print("New AniList cursor     :", highest_seen)

    if new_refresh_token != MAL_REFRESH_TOKEN:
        print()
        print(
            "⚠️ MAL returned a new refresh token. "
            "Update MAL_REFRESH_TOKEN before the next run."
        )
    else:
        print("✅ MAL refresh token unchanged.")


if __name__ == "__main__":
    main()
