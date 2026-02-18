import os
import shutil
import gapi
import ffmpeg
import pygame
import random

from song import Song
from ytmusicapi import YTMusic
from  pytubefix import YouTube
from pytubefix.cli import on_progress

pygame.mixer.init()

playlist_ids = [ ]

def clear():
  os.system("clear")
  print("\n")

def refresh():
  global playlist_ids

  clear()
  print("Refreshing playlists...")
  playlist_ids = gapi.get_playlist_ids()

def menu():
  while True:
    clear()
    print("******************")
    print("*                *")
    print("* ptec/radio-cli *")
    print("*                *")
    print("******************")
    print()
    print("Select an option:")
    print()
    print("  q. Quit")
    print("  r. Refresh")

    if len(playlist_ids) > 0:
      print("     ----------")
      for i, playlist_id in enumerate(playlist_ids):
        print(f"{str(i+1).rjust(3)}. Download and play '{playlist_id}'")

    print()

    choice = input("> ")

    if choice == "q":
      break
    elif choice == "r":
      refresh()
    else:
      try:
        choice = int(choice)
        if choice > 0 and choice <= len(playlist_ids):
          download_and_play(playlist_ids[choice-1])
        else:
          input("Invalid choice. Press Enter to continue...")
      except Exception:
        input("Invalid choice. Press Enter to continue...")

def download_and_play(playlist_id: str):
  clear()
  print(f"Fetching approved songs for playlist '{playlist_id}'")
  songs = gapi.get_approved_songs(playlist_id)

  clear()
  print(f"Preparing to download {len(songs)} songs...")
  if os.path.exists("./playlist"):
    shutil.rmtree("./playlist")

  clear()
  print(f"Downloading {len(songs)} songs...")
  for song in songs:
    download(song)

  clear()
  print(f"Converting {len(os.listdir('./playlist'))} songs...")
  for file_name in os.listdir("./playlist"):
    convert(f"./playlist/{file_name}")

  clear()
  print(f"Playing '{playlist_id}' radio...")
  shuffle_play()

def resolve_url(song: Song):
  yt = YTMusic()
  results = yt.search(f"{song}", filter="songs")

  print(f"Searching YouTube Music for '{song}'...")
  if len(results) == 0:
    print(f"No results found for '{song}'")
    return None

  result = results[0]
  if result["isExplicit"]:
    print(f"Discovered explicit result for '{song}'")
    return None

  print(f"Discovered result for '{song}'")
  return f"https://www.youtube.com/watch?v={result['videoId']}"

def download(song: Song):
  url = resolve_url(song)
  if not url:
    print(f"Failed to resolve URL for '{song}'")
    return None

  try:
    file_name = f"{song}.m4a"
    print(f"Downloading '{file_name}'...\n")
    YouTube(url, on_progress_callback=on_progress).streams.get_audio_only().download(output_path="./playlist", filename=file_name)
  except Exception as e:
    print(f"Failed to download '{file_name}'")

def convert(file_name: str):
  print(f"Converting '{file_name}'...")
  ffmpeg.input(file_name).output(file_name.replace(".m4a", ".ogg")).run()

def shuffle_play():
  playlist = [f for f in os.listdir("./playlist") if f.endswith(".ogg")]

  while True:
    random.shuffle(playlist)
    for file_name in playlist:
      play(f"./playlist/{file_name}")

def play(file_name: str):
  print(f"Playing '{file_name}'...")
  pygame.mixer.music.load(file_name)
  pygame.mixer.music.play()

  while pygame.mixer.music.get_busy():
    pygame.time.delay(100)

def main():
  menu()

if __name__ == "__main__":
  main()