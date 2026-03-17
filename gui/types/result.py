class Result:
  def __init__(self, ok: bool, *, value=None, error=None):
    self.ok   = ok
    if value is not None:
      self.value = value
    if error is not None:
      self.error = error

  def ok   (value=None):
    return Result(True , value=value)
  
  def error(error=None):
    return Result(False, error=error)
  
  def __bool__(self):
    return self.ok