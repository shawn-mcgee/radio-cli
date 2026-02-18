import json
import requests
from urllib.parse import quote

from song import Song

GOOGLE_APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwtfTgh_VX95AR3zYPokQODNzIwxfUf00uWS1wWS5hmCxCAxTtzbbk6PgCe9kPWWO8g/exec"

def wrap(content: dict) -> str:
    return quote(json.dumps(content))


def unwrap(response: requests.Response):
    try:
        data = response.json()
    except ValueError:
        raise Exception(f"[unwrap] Failed to parse JSON: {response.text}")

    if data and data.get("ok") is True:
        return data.get("content")
    elif data and data.get("ok") is False:
        raise Exception(f"[unwrap] {data.get('error')}")
    else:
        raise Exception(f"[unwrap] Failed to unwrap response '{data}'")


def get_playlist_ids():
    payload = {
        "action": "getPlaylistIds"
    }

    q = f"{GOOGLE_APPS_SCRIPT_URL}?q={wrap(payload)}"

    response = requests.post(
        q,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        allow_redirects=True
    )

    return unwrap(response)


def get_playlist(playlist_id: str):
    payload = {
        "action": "getPlaylist",
        "playlistId": playlist_id
    }

    q = f"{GOOGLE_APPS_SCRIPT_URL}?q={wrap(payload)}"

    response = requests.post(
        q,
        headers={
            "Content-Type": "application/x-www-form-urlencoded"
        },
        allow_redirects=True
    )

    return unwrap(response)

def is_approved(s: str):
    return s.strip().lower() == 'approved'

def is_rejected(s: str):
    return s.strip().lower() == 'rejected'

def get_playlist_songs(playlist_id: str):
    return [Song(result['title'], result['artist']) for result in get_playlist(playlist_id)]

def get_approved_songs(playlist_id: str):
    return [Song(result['title'], result['artist']) for result in get_playlist(playlist_id) if is_approved(result['status'])]
        