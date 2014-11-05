from config import *
from common_tools import *
import os

class FileTransferAgent:
  def __init__(self, udt, server_channel, file_name, file_dest, verify, createDirs):
    self.file_dest = file_dest
    self.file_name = file_name
    self.verify = verify
    self.is_transfering = False
    self.transfer_finished = False
    self.transfer_success = False
    self.udt = udt
    self.server_channel = server_channel
    self.transfer_manager = self.server_channel.root.get_transfer_manager()
    self.createDirs = createDirs

  def get_progress(self):
    if self.is_transfering is False and self.transfer_finished is False:
      return self.base_server_file_size
    elif self.is_transfering is False and self.transfer_finished is True:
      return self.file_size
    elif self.is_transfering is True and self.transfer_finished is False:
      return self.transfer_manager.get_size(self.server_file_path)

    return 0

  def get_server_file_size(self):
    if not hasattr(self, "_base_server_file_size"):
      self._base_server_file_size = self.transfer_manager.get_size_and_init_file_path(self.server_file_path)

    return self._base_server_file_size
  base_server_file_size = property(get_server_file_size)

  def get_server_file_path(self):
    if not hasattr(self, "_server_file_path"):
      result = self.transfer_manager.validate_filepath(self.file_dest, self.file_name, self.createDirs)
      self.validate_success = result[0]
      self._server_file_path = result[1]

    return self._server_file_path
  server_file_path = property(get_server_file_path)

  def get_total_size(self):
    if not hasattr(self, "_file_size"):
      self._file_size = os.path.getsize(self.file_name)

    return self._file_size
  file_size = property(get_total_size)

  def send_file(self):
    self.is_transfering = True

    logger.debug("Source " + self.file_name + " Dest: " + self.file_dest)

    logger.debug("Saving to... " + self.server_file_path)

    if(not self.validate_success):
      self.is_transfering = False
      self.transfer_finished = True
      self.transfer_success = False
      return

    block_count = 0

    if(self.base_server_file_size > 0):
      block_count = 0
      if(self.base_server_file_size != self.file_size):
        block_count = self.transfer_manager.get_blocks(self.server_file_path)
      file_hash = self.transfer_manager.get_file_hash(self.server_file_path, block_count)
      if not self.verify_partial_hash(self.file_name, file_hash, block_count):
        logger.debug("Client and server side partial hash differ.")
        self.transfer_manager.overwrite_file(self.server_file_path)
        block_count = 0
      elif block_count == 0:
        logger.debug("File already transfered")
        self.transfer_finished = True
        self.transfer_success = True
        self.is_transfering = False
        return
    else:
      # This will create the file on the server side
      self.transfer_manager.overwrite_file(self.server_file_path)

    self.udt.connect()
    self.udt.send_file(self.file_name, self.server_file_path, block_count, self.file_size)

    self.is_transfering = False

    if self.verify:
      if self.verify_partial_hash(self.file_name, self.transfer_manager.get_file_hash(self.server_file_path)):
        self.transfer_success = True
        self.transfer_finished = True
      else:
        logger.debug("File failed validation check.")
        self.transfer_success = False
        self.transfer_finished = True
    else:
      self.transfer_success = True
      self.transfer_finished = True

  def file_block_count(self, file_src):
    return (os.path.getsize(file_src) / CHUNK_SIZE)

  def verify_partial_hash(self, file_src, partial_hash, block_count=0):
    """
    Takes a file source and hashes the file up to block count and then compares
    it with the partial hash passed in, fails if they do not match.
    """
    my_hash = getHash(file_src, block_count)
    return partial_hash == my_hash
