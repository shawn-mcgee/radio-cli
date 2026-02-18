# smarter way to handle this by only downloading what is needed

import os
import gapi
import random

from ytmusicapi import YTMusic


def clear():
  os.system("cls" if os.name == "nt" else "clear")

clear()
print("Fetching playlists...")
playlist_ids = gapi.get_playlist_ids()

clear()
print("Choose Playlist")
print("---------------")
print()
for i, playlist_id in enumerate(playlist_ids):
  print(f"{str(i+1).rjust(3)}. {playlist_id}")
print()

while True:
  try:
    choice = int(input("> "))
    if choice > 0 and choice <= len(playlist_ids):
      playlist_id = playlist_ids[choice-1]
      break
    else:
      print("Invalid choice, press Enter to continue...")
  except:
      print("Invalid choice, press Enter to continue...")

clear()

def is_approved(song: dict):
  try:
    return song["status"].strip().lower() == "approved"
  except:
    return False
  
# all approved songs
playlist = [song for song in gapi.get_playlist(playlist_id) if is_approved(song)]

def resolve(song: dict):
  try:
    yt = YTMusic()
    title  = song["title" ].strip()
    artist = song["artist"].strip()

    results = yt.search(f"{artist} {title}".strip(), filter="songs")

    if len(results) == 0:
      return None
    
    result = results[0]

    if result["isExplicit"]:
      return None
    
    return result["videoId"]
  
  except:
    return None
  
def resolve_next(playlist: list[dict], i: int):
  for j, song in enumerate(playlist):
    if j <= i:
      continue

    videoId = resolve(song)
    if videoId:
      return videoId
    
  random.shuffle(playlist)
  return resolve_next(playlist, 0)
    




while True:
  random.shuffle(playlist)
  this_video_id = None
  next_video_id = None

  for i, song in enumerate(playlist):
    pass


