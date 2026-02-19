import os
import gapi
import random
import ffmpeg
import pygame

from ytmusicapi    import YTMusic
from pytubefix     import YouTube
from pytubefix.cli import on_progress


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

print("Fetching approved songs...")
playlist = [song for song in gapi.get_playlist(playlist_id) if is_approved(song)]

if len(playlist) == 0:
  print("No songs found, quitting...")
  quit()

pygame.mixer.init()

while True:
  random.shuffle(playlist)

  for i, song in enumerate(playlist):    
    title  = song["title" ].strip()
    artist = song["artist"].strip()

    print(f"Resolving '{title}' by '{artist}'...")

    yt = YTMusic()
    results = yt.search(f"{artist} {title}".strip(), filter="songs")

    if len(results) == 0:
      print(f"  No results for '{title}' by '{artist}', skipping...")
      continue

    result = results[0]

    if result["isExplicit"]:
      print(f"  Result(s) for '{title}' by '{artist}' are explicit, skipping...")
      continue

    video_id  = result["videoId"]
    video_url = f"https://www.youtube.com/watch?v={video_id}"

    if os.path.exists(f"./radio/{video_id}.m4a"):
      print(f"  './radio/{video_id}.m4a' already exists, advancing...")
    else:
      print(f"  Downloading './radio/{video_id}.m4a'...")
      try:
        (
          YouTube(video_url, on_progress_callback=on_progress)
            .streams
            .get_audio_only()
            .download(
              output_path="./radio",
              filename=f"{video_id}.m4a"          
            )
        )
      except:
        print(f"  Failed to download '{title}' by '{artist}', skipping...")
        continue
      finally:
        print()

    if os.path.exists(f"./radio/{video_id}.ogg"):
      print(f"  './radio/{video_id}.ogg' already exists, advancing...")
    else:
      print(f"  Converting './radio/{video_id}.m4a'...")
      try:
        (
          ffmpeg
            .input (f"./radio/{video_id}.m4a")
            .output(f"./radio/{video_id}.ogg")
            .run(quiet=True)
        )
      except:
        print(f"  Failed to convert './radio/{video_id}.m4a', skipping...")
        continue

    if pygame.mixer.music.get_busy():
      print(f"  Waiting for previous song to finish playing...")
      while pygame.mixer.music.get_busy():
        pygame.time.delay(100)

    print(f"  Playing '{title}' by '{artist}'...")
    pygame.mixer.music.load(f"./radio/{video_id}.ogg")
    pygame.mixer.music.play()
