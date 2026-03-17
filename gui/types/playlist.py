from random import shuffle
from gui.types.result import Result
from gui.types.song import Song

class Playlist:
  def __init__(self, songs: list[Song]=[]):
    self.songs = songs

  def from_dicts(songs: list[dict]):
    sb = []
    for song in songs:
      result = Song.from_dict(song)
      if result.ok:
        sb.append(result.value)
    
    return Result.ok(Playlist(sb))
