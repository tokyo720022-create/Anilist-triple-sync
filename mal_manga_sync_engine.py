import hashlib
import json
import os
import time
from typing import Any, Dict, Optional, Tuple

import requests

SOURCE_USERNAME = "Orewatokyo"
ANILIST_TOKEN = os.environ.get("ANILIST_TARGET_TOKEN", "").strip()
MAL_CLIENT_ID = os.environ.get("MAL_CLIENT_ID", "").strip()
MAL_CLIENT_SECRET = os.environ.get("MAL_CLIENT_SECRET", "").strip()
MAL_REFRESH_TOKEN = os.environ.get("MAL_REFRESH_TOKEN", "").strip()

STATE_FILE = "mal_manga_delta_state.json"
ANILIST_URL = "https://graphql.anilist.co"
MAL_TOKEN_URL = "https://myanimelist.net/v1/oauth2/token"
MAL_ME_URL = "https://api.myanimelist.net/v2/users/@me"
MAL_MANGA_DETAILS_URL = "https://api.myanimelist.net/v2/manga/{manga_id}"
MAL_UPDATE_URL = "https://api.myanimelist.net/v2/manga/{manga_id}/my_list_status"

ANILIST_HEADERS = {
    "Authorization": f"Bearer {ANILIST_TOKEN}" if ANILIST_TOKEN else "",
    "Content-Type": "application/json",
    "Accept": "application/json",
}

MAL_STATUS_MAP = {
    "CURRENT": "reading",
    "REPEATING": "reading",
    "PLANNING": "plan_to_read",
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
      type: MANGA,
      sort: [UPDATED_TIME_DESC]
    ) {
      updatedAt
      status
      score(format: POINT_100)
      progress
      progressVolumes
      startedAt { year month day }
      completedAt { year month day }
      media {
        id
        idMal
        title { romaji english }
        chapters
        volumes
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
    for name, value in (
        ("ANILIST_TARGET_TOKEN", ANILIST_TOKEN),
        ("MAL_CLIENT_ID", MAL_CLIENT_ID),
        ("MAL_CLIENT_SECRET", MAL_CLIENT_SECRET),
        ("MAL_REFRESH_TOKEN", MAL_REFRESH_TOKEN),
    ):
        if not value:
            missing.append(name)
    if missing:
        raise SystemExit("❌ Missing GitHub Secrets: " + ", ".join(missing))


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
                method, url, headers=headers, timeout=30, **kwargs
            )
            if response.status_code in (429, 500, 502, 503, 504):
                last_error = f"HTTP {response.status_code}: {response.text[:300]}"
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
    if new_refresh_token != MAL_REFRESH_TOKEN:
        print("⚠️ MAL rotated the refresh token.")
        print("   Update GitHub Secret: MAL_REFRESH_TOKEN")
    return access_token, new_refresh_token


def verify_mal(access_token: str) -> None:
    response = request_with_retry(
        "GET",
        MAL_ME_URL,
        headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
    )
    if response.status_code == 401:
        raise PermissionError("MAL access token rejected.")
    if response.status_code != 200:
        raise RuntimeError(
            f"MAL account test failed: HTTP {response.status_code} {response.text[:300]}"
        )
    print("✅ MAL account authenticated:", response.json().get("name", "unknown"))


def format_date(value: Optional[dict]) -> Optional[str]:
    if not value:
        return None
    year, month, day = value.get("year"), value.get("month"), value.get("day")
    if not year or not month or not day:
        return None
    return f"{year:04d}-{month:02d}-{day:02d}"


def title_for(entry: dict) -> str:
    media = entry.get("media") or {}
    titles = media.get("title") or {}
    return titles.get("english") or titles.get("romaji") or f"MAL ID {media.get('idMal', '?')}"


def entry_fingerprint(entry: dict) -> str:
    media = entry.get("media") or {}
    payload = {
        "status": entry.get("status"),
        "score": entry.get("score"),
        "progress": int(entry.get("progress") or 0),
        "progressVolumes": int(entry.get("progressVolumes") or 0),
        "startedAt": entry.get("startedAt"),
        "completedAt": entry.get("completedAt"),
        "idMal": media.get("idMal"),
    }
    raw = json.dumps(payload, sort_keys=True, separators=(",", ":"))
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def normalize_previous_state(state: dict) -> dict:
    raw = state.get("media")
    if isinstance(raw, dict):
        result = {}
        for key, value in raw.items():
            if isinstance(value, dict):
                result[str(key)] = {
                    "updated_at": int(value.get("updated_at") or 0),
                    "fingerprint": str(value.get("fingerprint") or ""),
                    "mal_id": value.get("mal_id"),
                }
        return result
    legacy = state.get("media_updates")
    if isinstance(legacy, dict):
        return {
            str(key): {"updated_at": int(value or 0), "fingerprint": "", "mal_id": None}
            for key, value in legacy.items()
        }
    return {}


def fetch_anilist_changes(previous_media: dict) -> Tuple[list[dict], dict, list[dict]]:
    changed: list[dict] = []
    current_media: dict[str, dict] = {}
    page = 1
    page_count = 0

    while True:
        response = request_with_retry(
            "POST",
            ANILIST_URL,
            headers=ANILIST_HEADERS,
            json={
                "query": ANILIST_QUERY,
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
            raise RuntimeError(f"AniList GraphQL errors: {payload['errors']}")

        page_data = payload.get("data", {}).get("Page", {})
        batch = page_data.get("mediaList", [])
        if not isinstance(batch, list):
            raise RuntimeError("AniList returned an invalid mediaList payload.")
        page_count += 1

        for entry in batch:
            media = entry.get("media") or {}
            media_id = media.get("id")
            if media_id is None:
                continue
            key = str(media_id)
            updated_at = int(entry.get("updatedAt") or 0)
            fingerprint = entry_fingerprint(entry)
            current_media[key] = {
                "updated_at": updated_at,
                "fingerprint": fingerprint,
                "mal_id": media.get("idMal"),
            }

            previous = previous_media.get(key) or {}
            previous_updated = int(previous.get("updated_at") or 0)
            previous_fingerprint = str(previous.get("fingerprint") or "")
            legacy_record = key in previous_media and not previous_fingerprint

            if key not in previous_media:
                changed.append(entry)
            elif updated_at > previous_updated:
                changed.append(entry)
            elif updated_at == previous_updated and previous_fingerprint:
                if fingerprint != previous_fingerprint:
                    changed.append(entry)
            elif updated_at == previous_updated and legacy_record:
                pass

        if not page_data.get("pageInfo", {}).get("hasNextPage"):
            break
        page += 1
        time.sleep(0.15)

    removed = [
        {"media_id": media_id, "mal_id": previous.get("mal_id")}
        for media_id, previous in previous_media.items()
        if media_id not in current_media
    ]

    legacy_count = sum(
        1
        for key, record in previous_media.items()
        if key in current_media and not str(record.get("fingerprint") or "")
    )

    print(f"✅ AniList checked: {len(current_media)} manga across {page_count} page(s).")
    if legacy_count:
        print(
            f"🔄 Legacy state migration: learned fingerprints for {legacy_count} "
            "existing entries without MAL writes."
        )
    return changed, current_media, removed


def anilist_score_to_mal(score: Any) -> int:
    try:
        value = float(score)
    except (TypeError, ValueError):
        return 0
    if value <= 0:
        return 0
    return max(1, min(10, int(round(value / 10.0))))


def fetch_mal_entry(access_token: str, mal_id: int) -> dict:
    response = request_with_retry(
        "GET",
        MAL_MANGA_DETAILS_URL.format(manga_id=mal_id),
        headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
        params={"fields": "my_list_status"},
    )
    if response.status_code == 401:
        raise PermissionError("MAL access token rejected.")
    if response.status_code == 404:
        return {}
    if response.status_code != 200:
        raise RuntimeError(
            f"MAL manga lookup failed for {mal_id}: HTTP {response.status_code} {response.text[:300]}"
        )
    return response.json().get("my_list_status") or {}


def build_mal_update(entry: dict, current: dict) -> dict:
    desired_status = MAL_STATUS_MAP.get(entry.get("status"))
    desired_chapters = int(entry.get("progress") or 0)
    desired_volumes = int(entry.get("progressVolumes") or 0)
    desired_score = anilist_score_to_mal(entry.get("score"))
    desired_start = format_date(entry.get("startedAt"))
    desired_finish = format_date(entry.get("completedAt"))
    desired_reread = entry.get("status") == "REPEATING"

    current_status = current.get("status")
    current_chapters = int(current.get("num_chapters_read") or 0)
    current_volumes = int(current.get("num_volumes_read") or 0)
    current_score = int(current.get("score") or 0)
    current_start = current.get("start_date") or ""
    current_finish = current.get("finish_date") or ""
    current_reread = bool(current.get("is_rereading"))

    update: dict[str, Any] = {}
    if desired_status and desired_status != current_status:
        update["status"] = desired_status
    if desired_chapters != current_chapters:
        update["num_chapters_read"] = desired_chapters
    if desired_volumes != current_volumes:
        update["num_volumes_read"] = desired_volumes
    if desired_score != current_score:
        update["score"] = desired_score
    if (desired_start or "") != current_start:
        update["start_date"] = desired_start or ""
    if (desired_finish or "") != current_finish:
        update["finish_date"] = desired_finish or ""
    if desired_reread != current_reread:
        update["is_rereading"] = "true" if desired_reread else "false"
    return update


def update_mal_entry(access_token: str, entry: dict, current: dict) -> bool:
    media = entry.get("media") or {}
    mal_id = media.get("idMal")
    if not mal_id:
        print(f"⏭️ {title_for(entry)}: no MAL ID; skipped.")
        return False

    update = build_mal_update(entry, current)
    if not update:
        return False

    print(f"🔄 {title_for(entry)} -> MAL {mal_id}")
    print("   Fields:", ", ".join(update.keys()))

    response = request_with_retry(
        "PUT",
        MAL_UPDATE_URL.format(manga_id=int(mal_id)),
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
        print(f"   ❌ MAL manga update failed: HTTP {response.status_code}")
        print(response.text[:500])
        return False
    print("   ✅ MAL manga added/updated.")
    return True


def remove_mal_entry(access_token: str, mal_id: int) -> bool:
    response = request_with_retry(
        "DELETE",
        MAL_UPDATE_URL.format(manga_id=int(mal_id)),
        headers={"Authorization": f"Bearer {access_token}", "Accept": "application/json"},
    )
    if response.status_code == 401:
        raise PermissionError("MAL access token rejected.")
    if response.status_code in (200, 204, 404):
        return True
    print(
        f"❌ MAL manga removal failed for {mal_id}: "
        f"HTTP {response.status_code} {response.text[:300]}"
    )
    return False


def main() -> None:
    print("=" * 68)
    print("        MAL <- ANILIST MANGA SHORT DELTA SYNC v1")
    print("=" * 68)

    require_config()
    state = load_state()
    previous_media = normalize_previous_state(state)

    if previous_media:
        print("⚡ MANGA DELTA MODE ACTIVE")
        print(f"   Stored AniList manga states: {len(previous_media)}")
    else:
        print("🧭 INITIAL MANGA BASELINE MODE")
        print("   No MAL library scan will be performed.")
        print("   No MAL writes/removals will be performed on this baseline run.")

    access_token, new_refresh_token = refresh_mal_token()
    verify_mal(access_token)

    print("📡 Checking AniList for new/updated manga...")
    changed_entries, current_media, removed_entries = fetch_anilist_changes(previous_media)

    if not previous_media:
        save_state({
            "version": 1,
            "last_anilist_update": max((item["updated_at"] for item in current_media.values()), default=0),
            "media": current_media,
        })
        print("\n" + "=" * 68)
        print("✅ MANGA DELTA BASELINE CREATED")
        print("=" * 68)
        print("AniList manga remembered:", len(current_media))
        print("MAL writes performed     : 0")
        print("Next run will process only changed/new manga.")
        return

    print(f"✅ Changed/new AniList manga: {len(changed_entries)}")
    print(f"🗑️ Removed from AniList      : {len(removed_entries)}")

    updated = 0
    unchanged = 0
    skipped_no_mal_id = 0
    removed = 0
    failed = 0
    successful_media_ids: set[str] = set()
    successful_removed_media_ids: set[str] = set()

    for entry in changed_entries:
        media = entry.get("media") or {}
        media_id = media.get("id")
        mal_id = media.get("idMal")
        title = title_for(entry)
        if media_id is None:
            failed += 1
            print(f"❌ {title}: AniList manga ID missing.")
            continue
        key = str(media_id)
        if not mal_id:
            skipped_no_mal_id += 1
            print(f"⏭️ {title}: no MAL ID; skipped.")
            continue

        try:
            current = fetch_mal_entry(access_token, int(mal_id))
            changed = update_mal_entry(access_token, entry, current)
            if changed:
                updated += 1
            else:
                unchanged += 1
            successful_media_ids.add(key)
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
                successful_media_ids.add(key)
            except Exception as exc:
                failed += 1
                print(f"❌ Retry failed for {title}: {exc}")
        except Exception as exc:
            failed += 1
            print(f"❌ {title}: {exc}")
        time.sleep(0.4)

    for item in removed_entries:
        media_key = str(item.get("media_id"))
        mal_id = item.get("mal_id")
        if not mal_id:
            print(
                f"⏭️ AniList manga {media_key} was removed, "
                "but no stored MAL ID is available."
            )
            successful_removed_media_ids.add(media_key)
            continue
        try:
            print(f"🗑️ AniList manga removal -> MAL removal (MAL {mal_id})")
            if remove_mal_entry(access_token, int(mal_id)):
                removed += 1
                successful_removed_media_ids.add(media_key)
        except PermissionError:
            print("🔄 MAL access token expired/rejected. Refreshing once...")
            access_token, new_refresh_token = refresh_mal_token()
            try:
                if remove_mal_entry(access_token, int(mal_id)):
                    removed += 1
                    successful_removed_media_ids.add(media_key)
            except Exception as exc:
                failed += 1
                print(f"❌ Retry failed removing MAL manga {mal_id}: {exc}")
        except Exception as exc:
            failed += 1
            print(f"❌ Failed removing MAL manga {mal_id}: {exc}")
        time.sleep(0.4)

    merged_media = dict(current_media)
    for entry in changed_entries:
        media_id = (entry.get("media") or {}).get("id")
        if media_id is None:
            continue
        key = str(media_id)
        if key not in successful_media_ids:
            previous = previous_media.get(key)
            if previous is not None:
                merged_media[key] = previous

    for item in removed_entries:
        key = str(item.get("media_id"))
        if key not in successful_removed_media_ids:
            previous = previous_media.get(key)
            if previous is not None:
                merged_media[key] = previous

    cursor = max((item["updated_at"] for item in merged_media.values()), default=0)
    save_state({"version": 1, "last_anilist_update": cursor, "media": merged_media})

    print("\n" + "=" * 68)
    print("⚡ MAL MANGA SHORT DELTA SYNC COMPLETE")
    print("=" * 68)
    print("AniList changed/new manga:", len(changed_entries))
    print("Added/updated on MAL      :", updated)
    print("Already synchronized      :", unchanged)
    print("No MAL ID                 :", skipped_no_mal_id)
    print("Removed from MAL          :", removed)
    print("Failed                    :", failed)
    print("Stored AniList manga     :", len(merged_media))
    print("AniList cursor            :", cursor)

    if failed:
        print("⚠️ Failed items were NOT advanced and will be retried next run.")
    if new_refresh_token != MAL_REFRESH_TOKEN:
        print(
            "⚠️ MAL refresh token rotated. "
            "Update GitHub Secret MAL_REFRESH_TOKEN before the next run."
        )
    else:
        print("✅ MAL refresh token unchanged.")


if __name__ == "__main__":
    main()
