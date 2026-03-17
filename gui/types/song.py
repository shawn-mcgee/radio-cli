from gui.types.result import Result

TITLE  = "title" 
ARTIST = "artist"
STATUS = "status"

APPROVED = "approved"
REJECTED = "rejected"
PENDING  = "pending"

class Song:
  def __init__(self, 
    title : str, 
    artist: str,
    status: str
  ):
    self.title  = title .strip()
    self.artist = artist.strip()
    self.status = status.strip().lower()

  def is_approved(self):
    return self.status == APPROVED
  
  def is_rejected(self):
    return self.status == REJECTED
  
  def is_pending(self):
    return self.status == PENDING

  def from_dict(song: dict):
    try:
      title  = song[TITLE ].strip()
    except:
      return Result.error(f"[Song.from_dict] Unable to get 'title' from song '{song}'")
    
    try:
      artist = song[ARTIST].strip()
    except:
      return Result.error(f"[Song.from_dict] Unable to get 'artist' from song '{song}'")
    
    try:
      status = song[STATUS].strip()
    except:
      return Result.error(f"[Song.from_dict] Unable to get 'status' from song '{song}'")
    
    return Result.ok(Song(title, artist, status))

  def __str__(self):
    sb = ""
    
    if self.title:
      sb += f"{self.title}"

    if self.artist:
      if sb:
        sb += " by "
      sb += f"{self.artist}"

    return sb