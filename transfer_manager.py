
from config import *
from common_tools import *


class TransferManager:
  def __init__(self):
    pass

  def __del__(self):
    pass

  def is_file(self, filepath):
    return os.path.isfile(filepath)

  def get_file_hash(self, filepath, block_count=0):
    return getHash(filepath, block_count)

  def get_blocks(self, filepath):
    return os.path.getsize(filepath) / CHUNK_SIZE

  def create_dir(self, directory):
    if not os.path.exists(directory):
      os.makedirs(directory)

  def overwrite_file(self, filepath):
    open(filepath, "w").close()

  def get_size_and_init_file_path(self, filepath):
    if not os.path.isfile(filepath):
      output_file = open(filepath, "w")
    else:
      output_file = open(filepath, "r+")

    output_file.close()

    return os.path.getsize(filepath)

  def total_size(self, files):
    size = 0
    for path in files:
      if os.path.isfile(path):
        size += os.path.getsize(path)
    return size

  def validate_filepath(self, filepath, client_path):
    """
    Validates the filepath, and returns the correct path
    """
    (head, tail) = os.path.split(filepath)
    if not tail:
      if not os.path.exists(head):
        # TODO add error support for warp.py
        fail("Directory " + head + " does not exist.")
      else:
          (client_head, client_tail) = os.path.split(client_path)
          return os.path.join(head, client_tail)

    elif head != "" and not os.path.exists(head):
      fail(filepath + ": No such file or directory")

    elif not head and os.path.isdir(tail):
      (client_head, client_tail) = os.path.split(client_path)
      return os.path.join(tail, client_tail)

    return filepath
