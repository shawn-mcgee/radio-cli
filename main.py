import os
import shutil
import gapi
import ffmpeg
import pygame
import random

from ytmusicapi     import YTMusic
from  pytubefix     import YouTube
from  pytubefix.cli import on_progress

pygame.mixer.init()


def clear():
  os.system("cls" if os.name == "nt" else "clear")

def main_menu():
  while True:
    clear()
    print("******************")
    print("* PTEC/radio-cli *")
    print("******************")
    print()
    print("Select an option:")
    print()
    print("  d. Download")
    print("  c. Convert ")
    print("  s. Shuffle ")
    print("  q. Quit")
    print()

    while True:
      choice = input("> ")
      if   choice == "q":
        return clear()
      elif choice == "d":
        download_playlists_menu()
        break
      elif choice == "c":
        convert_playlists_menu()
        break
      elif choice == "s":
        shuffle_playlists_menu()
        break
      else:
        input("Invalid option, press Enter to continue...")

def download_playlists_menu():
  while True:
    clear()
    print("Fetching playlists...")

    playlist_ids = gapi.get_playlist_ids()

    clear()
    print("Download Playlist")
    print("-----------------")
    print()
    print("  b. Return to the previous menu")
    for i, playlist_id in enumerate(playlist_ids):
      print(f"{str(i+1).rjust(3)}. Download '{playlist_id}'")
    print()
    
    while True:
      choice = input("> ")
      if   choice == "b":
        return
      else:
        try:
          choice = int(choice)
          if choice > 0 and choice <= len(playlist_ids):
            return download_playlist(playlist_ids[choice-1])
          else:
            input("Invalid option, press Enter to continue...")
        except ValueError:
            input("Invalid option, press Enter to continue...")

def convert_playlists_menu():
  while True:
    clear()

    playlist_ids = os.listdir("./playlist")

    print("Convert Playlist")
    print("----------------")
    print()
    print("  b. Return to the previous menu")
    print("  d. Download a playlist online")
    for i, playlist_id in enumerate(playlist_ids):
      print(f"{str(i+1).rjust(3)}. Convert '{playlist_id}'")
    print()

    while True:
      choice = input("> ")

      if   choice == "b":
        return
      elif choice == "d":
        download_playlists_menu()
        break
      else:
        try:
          choice = int(choice)
          if choice > 0 and choice <= len(playlist_ids):
            return convert_playlist(playlist_ids[choice-1])
          else:
            input("Invalid option, press Enter to continue...")
        except ValueError:
            input("Invalid option, press Enter to continue...")


def shuffle_playlists_menu():
  while True:
    clear()

    playlist_ids = os.listdir("./playlist")

    print("Shuffle Playlist")
    print("----------------")
    print()
    print("  b. Return to the previous menu")
    print("  d. Download a playlist online")
    for i, playlist_id in enumerate(playlist_ids):
      oggs = [f for f in os.listdir(f"./playlist/{playlist_id}") if f.endswith(".ogg")]
      print(f"{str(i+1).rjust(3)}. Shuffle '{playlist_id}' ({len(oggs)} songs)")
    print()

    while True:
      choice = input("> ")

      if   choice == "b":
        return
      elif choice == "d":
        download_playlists_menu()
        break
      else:
        try:
          choice = int(choice)
          if choice > 0 and choice <= len(playlist_ids):
            return shuffle_playlist(playlist_ids[choice-1])
          else:
            input("Invalid option, press Enter to continue...")
        except ValueError:
            input("Invalid option, press Enter to continue...")

def download_playlist(playlist_id: str):
  clear()

  print(f"Fetching approved songs for playlist '{playlist_id}'")

  try:
    entries = gapi.get_playlist(playlist_id)
  except:
    print(f"Failed to fetch playlist '{playlist_id}'")
    input("Press Enter to continue...")
    return
  
  def is_approved(entry: dict):
    try:
      return entry["status"].strip().lower() == "approved"
    except:
      return False
  
  print(f"  Found {len(entries)}          songs in playlist '{playlist_id}'")
  entries = [entry for entry in entries if is_approved(entry)]
  print(f"  Found {len(entries)} approved songs in playlist '{playlist_id}'")
  print()

  # print(f"Preparing to download songs for playlist '{playlist_id}'")
  # if os.path.exists(f"./playlist/{playlist_id}"):
  #   shutil.rmtree(f"./playlist/{playlist_id}")
  # print()

  yt = YTMusic()
  for i, entry in enumerate(entries):
    print(f"Resolving {i+1} of {len(entries)}...")
    try:
      title  = entry["title" ].strip()
      artist = entry["artist"].strip()

      print(f"Searching YouTube Music for '{title}' by '{artist}'...")
      results = yt.search(f"{artist} {title}".strip(), filter="songs")

      if len(results) == 0:
        print(f"  No results found for '{title}' by '{artist}', skipping...")
        continue

      result = results[0]

      if result["isExplicit"]:
        print(f"  Result for '{title}' by '{artist}' is explicit, skipping...")
        continue

      print(f"  Discovered result for '{title}' by '{artist}'")
      url = f"https://www.youtube.com/watch?v={result['videoId']}"

      print(f"  Downloading {url}...")
      (
        YouTube(url, on_progress_callback=on_progress)
          .streams
          .get_audio_only()
          .download(
            filename=f"{result['videoId']}.m4a",
            output_path=f"./playlist/{playlist_id}"
          )
      )
      print()
    except Exception as e:
      print("  Failed to download, skipping...")
    finally:
      print()

  clear()
  print(f"Finished downloading songs for playlist '{playlist_id}'")
  print(f"Would you like to convert these songs now?")
  print()  
  print("  y. Convert these songs now")
  print("  n. Return to the previous menu")

  while True:
    choice = input("> ")
    if   choice == "y":
      return convert_playlist(playlist_id)
    elif choice == "n":
      return
    else:
      input("Invalid option, press Enter to continue...")

def convert_playlist(playlist_id: str):
  clear()

  print(f"Converting songs for playlist '{playlist_id}'")

  files = [f for f in os.listdir(f"./playlist/{playlist_id}") if f.endswith(".m4a")]

  print(f"  Found {len(files)} songs in playlist '{playlist_id}'")
  print()

  for i, file in enumerate(files):
    print(f"Resolving {i+1} of {len(files)}...")
    ipath = f"./playlist/{playlist_id}/{file}"
    opath = f"./playlist/{playlist_id}/{file.replace('.m4a', '.ogg')}"
  
    if os.path.exists(opath):
      print(f"  {ipath} already exists, skipping...")
    else:
      try:
        print(f"  Converting {ipath}...")
        (
          ffmpeg
            .input (ipath)
            .output(opath)
            .run(quiet=True)
        )
      except:
        print("  Failed to convert, skipping...")

  clear()
  print(f"Finished converting songs for playlist '{playlist_id}'")
  print(f"Would you like to shuffle these songs now?")
  print()  
  print("  y. Shuffle these songs now")
  print("  n. Return to the previous menu")

  while True:
    choice = input("> ")
    if   choice == "y":
      return shuffle_playlist(playlist_id)
    elif choice == "n":
      return
    else:
      input("Invalid option, press Enter to continue...")

def shuffle_playlist(playlist_id: str):
  clear()
  print(f"Shuffling songs for playlist '{playlist_id}'")

  files = [f for f in os.listdir(f"./playlist/{playlist_id}") if f.endswith(".ogg")]
  print(f"  Found {len(files)} songs in playlist '{playlist_id}'")
  print()

  while True:
    random.shuffle(files)
    for file in files:
      print(f"Playing {file}...")
      pygame.mixer.music.load(f"./playlist/{playlist_id}/{file}")
      pygame.mixer.music.play()

      while pygame.mixer.music.get_busy():
        pygame.time.delay(100)



if __name__ == "__main__":
  main_menu()