import json
import requests
from urllib.parse import quote

from gui.types.playlist import Playlist
from gui.types.result import Result

GOOGLE_APPS_SCRIPT_URL = "https://script.google.com/macros/s/AKfycbwtfTgh_VX95AR3zYPokQODNzIwxfUf00uWS1wWS5hmCxCAxTtzbbk6PgCe9kPWWO8g/exec"

def wrap(content: dict) -> str:
  return quote(json.dumps(content))

def unwrap(response: requests.Response):
  try:
    data = response.json()
  except ValueError:
    return Result.error(f"[unwrap] Unable to parse JSON: {response.text}")
  
  if data and data.get("ok"):
    return Result.ok(data.get("content"))
  elif data and data.get("error"):
    return Result.error(data.get("error"))
  else:
    return Result.error(f"[unwrap] Unable to unwrap response '{data}'")


def fetch_playlist_ids():
  payload = {
    "action": "getPlaylistIds"
  }

  q = f"{GOOGLE_APPS_SCRIPT_URL}?q={wrap(payload)}"

  
  try:
    return unwrap(requests.post(
      q,
      headers={
        "Content-Type": "application/x-www-form-urlencoded"
      },
      allow_redirects=True
    ))
  except:
    return Result.error(f"[gs.fetch_playlist_ids] Unable to fetch playlist ids")


def fetch_playlist(playlist_id: str):
  payload = {
    "action"  : "getPlaylist",
    "playlistId": playlist_id
  }

  q = f"{GOOGLE_APPS_SCRIPT_URL}?q={wrap(payload)}"

  try:
    songs = unwrap(requests.post(
        q,
        headers={
        "Content-Type": "application/x-www-form-urlencoded"
        },
        allow_redirects=True
    ))
    return Playlist.from_dicts(songs.value) if songs.ok else songs
  except Exception as e:
    print(e)
    return Result.error(f"[gs.fetch_playlist] Unable to fetch playlist '{playlist_id}'")