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


def fetch_anilist() -> list[dict]:
    query = """
    query ($userName: String, $page: Int) {
      Page(page: $page, perPage: 50) {
        pageInfo { hasNextPage }
        mediaList(
          userName: $userName,
          type: ANIME,
          sort: [UPDATED_TIME_DESC]
        ) {
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

    items: list[dict] = []
    page = 1

    while True:
        response = request_with_retry(
            "POST",
            ANILIST_URL,
            headers=ANILIST_HEADERS,
            json={
                "query": query,
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
            print("❌ AniList GraphQL error:")
            print(payload["errors"])
            raise SystemExit(1)

        page_data = payload.get("data", {}).get("Page", {})
        batch = page_data.get("mediaList", [])

        items.extend(batch)

        if not page_data.get("pageInfo", {}).get("hasNextPage"):
            break

        page += 1
        time.sleep(0.5)

    print(f"✅ AniList anime entries fetched: {len(items)}")
    return items


def fetch_mal_list(access_token: str) -> dict[int, dict]:
    print("📚 Fetching MAL anime list...")

    headers = {
        "Authorization": f"Bearer {access_token}",
        "Accept": "application/json",
    }

    result: dict[int, dict] = {}
    offset = 0
    limit = 1000

    while True:
        response = request_with_retry(
            "GET",
            MAL_ANIMELIST_URL,
            headers=headers,
            params={
                "limit": limit,
                "offset": offset,
                "fields": (
                    "status,score,num_episodes_watched,"
                    "start_date,finish_date"
                ),
                "sort": "list_updated_at",
            },
        )

        # If an access token expired before the first call, caller can refresh.
        if response.status_code == 401:
            return {}

        if response.status_code != 200:
            print("❌ MAL list request failed.")
            print("HTTP:", response.status_code)
            print(response.text[:500])
            raise SystemExit(1)

        body = response.json()
        batch = body.get("data", [])

        for row in batch:
            anime = row.get("node") or {}
            details = row.get("list_status") or {}
            anime_id = anime.get("id")

            if anime_id is not None:
                result[int(anime_id)] = details

        paging = body.get("paging") or {}
        next_link = paging.get("next")

        if not batch or not next_link:
            break

        offset += len(batch)
        time.sleep(0.5)

    print(f"✅ MAL anime entries fetched: {len(result)}")
    return result


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

    access_token, new_refresh_token = refresh_mal_token()

    anilist_entries = fetch_anilist()
    mal_entries = fetch_mal_list(access_token)

    if not mal_entries and anilist_entries:
        # A 401 from fetch_mal_list returns {}, while an actually empty
        # MAL list is possible too. Test the token directly.
        me = request_with_retry(
            "GET",
            "https://api.myanimelist.net/v2/users/@me",
            headers={
                "Authorization": f"Bearer {access_token}",
                "Accept": "application/json",
            },
        )

        if me.status_code == 401:
            print("⚠️ MAL token rejected. Refreshing once more...")
            access_token, new_refresh_token = refresh_mal_token()
            mal_entries = fetch_mal_list(access_token)

    updated = 0
    skipped_no_mal_id = 0
    unchanged = 0
    failed = 0

    print("\n🚀 Starting AniList → MAL synchronization...\n")

    for entry in anilist_entries:
        media = entry.get("media") or {}

        if not media.get("idMal"):
            skipped_no_mal_id += 1
            continue

        mal_id = int(media["idMal"])
        current = mal_entries.get(
            mal_id,
            {
                "status": None,
                "score": 0,
                "num_episodes_watched": 0,
            },
        )

        try:
            changed = sync_entry(access_token, entry, current)
        except PermissionError:
            # Refresh once and retry this entry.
            print("🔄 MAL access token expired. Refreshing...")
            access_token, new_refresh_token = refresh_mal_token()
            try:
                changed = sync_entry(access_token, entry, current)
            except PermissionError:
                print("   ❌ Token still rejected.")
                failed += 1
                continue
        except Exception as exc:
            print(f"   ❌ Unexpected error: {exc}")
            failed += 1
            continue

        if changed:
            updated += 1
            time.sleep(1.0)
        else:
            unchanged += 1

    print("\n" + "=" * 64)
    print("MAL SYNC COMPLETE")
    print("=" * 64)
    print("Updated entries       :", updated)
    print("Already synchronized  :", unchanged)
    print("No MAL ID on AniList  :", skipped_no_mal_id)
    print("Failed updates        :", failed)
    print()

    # Never print tokens. If MAL rotates the refresh token, the returned
    # token cannot be written back to a GitHub Actions secret automatically
    # without an additional secret-management mechanism.
    if new_refresh_token != MAL_REFRESH_TOKEN:
        print(
            "⚠️ MAL returned a new refresh token. "
            "Update the MAL_REFRESH_TOKEN GitHub Secret before the next run."
        )
    else:
        print("✅ Existing MAL refresh token remained unchanged.")


if __name__ == "__main__":
    main()
