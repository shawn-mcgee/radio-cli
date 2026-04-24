from gui.types.result import Result
from gui.types.song   import Song

from ytmusicapi import YTMusic
from pytubefix  import YouTube
import ffmpeg
import os

def resolve_video_id(song: Song):
  if not song.is_approved():
    return Result.error(f"[yt.resolve_video_id] Song '{song}' is not approved")
  
  yt = YTMusic()
  query = f"{song.artist} {song.title}".strip()
  results = yt.search(query, filter="songs")

  if len(results) == 0:
    return Result.error(f"[yt.resolve_video_id] No results for '{song}'")
  
  result = results[0]

  if result["isExplicit"]:
    return Result.error(f"[yt.resolve_video_id] Result(s) for '{song}' are explicit")
  
  return Result.ok(result["videoId"])

def download_audio(video_id: str):
  video_url = f"https://www.youtube.com/watch?v={video_id}"

  if os.path.exists(f"./radio/{video_id}.m4a"):
    return Result.ok()
  else:
      try:
        (
          YouTube(video_url)
            .streams
            .get_audio_only()
            .download(
              output_path="./radio",
              filename=f"{video_id}.m4a"
            )
        )
      except:
        return Result.error(f"[yt.download_video] Unable to download '{video_id}'")
      return Result.ok()
  
def convert_audio(video_id: str):
  if os.path.exists(f"./radio/{video_id}.ogg"):
    return Result.ok()
  else:
    try:
      (
        ffmpeg
          .input (f"./radio/{video_id}.m4a")
          .output(f"./radio/{video_id}.ogg")
          .run(quiet=True)
      )
    except:
      return Result.error(f"[yt.convert_video] Unable to convert './radio/{video_id}.m4a'")
    return Result.ok()