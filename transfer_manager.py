
from config import *
import json
from common_tools import *

class TransferManager:
  def __init__(self):
    pass

  def __del__(self):
    pass

  def is_file(self, filepath):
    return os.path.isfile(filepath)

  def get_hash_and_blocks(self, filepath):
    file_hash = getHash(filepath)
    block_count = (os.path.getsize(old_path)) / CHUNK_SIZE

    return file_hash, block_count 

  def get_block_and_init_file_path(self, filepath, old_path):

    block_count = 0

    if old_path:
      block_count = (os.path.getsize(old_path)) / CHUNK_SIZE
      if not os.path.isfile(filepath) or not os.path.samefile(old_path, filepath):
        output_file = open(filepath, "w")
        shutil.copyfile(old_path, filepath)
      else:
        output_file = open(filepath, "r+")
    else:
      output_file = open(filepath, "w")

    output_file.close()

    return block_count

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
