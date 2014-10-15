
from common_tools import *
from client_udt_manager import ClientUDTManager
import os


class ClientTransferController:
  def __init__(self, server_channel, hostname, file_src, file_dest, recursive, tcp_mode, disable_verify):
    self.server_channel = server_channel
    self.hostname = hostname
    self.file_src = file_src
    self.file_dest = file_dest
    self.recursive = recursive

    global TCP_MODE
    TCP_MODE = tcp_mode

  def start(self):
    udt = ClientUDTManager(self.server_channel, self.hostname)
    transfer_manager = self.server_channel.root.get_transfer_manager()

    file_path = transfer_manager.validate_filepath(self.file_src, self.file_dest)
    file_hash, block_count = transfer_manager.get_hash_and_blocks(file_path)

    if not verify_partial_hash(self.file_src, file_hash, block_count):
      transfer_manager.overwrite_file(file_path)
      block_count = 0

    udt.connect()
    udt.send_file(self.file_src, file_path, block_count, os.path.getsize(file_src))

  def close(self):
    """
    Cleanup goes here, we probably have to close some connections...
    """
    pass

  def verify_partial_hash(self, file_src, partial_hash, block_count):
    """
    Takes a file source and hashes the file up to block count and then compares
    it with the partial hash passed in, fails if they do not match.
    """
    my_hash = getHash(file_src, block_count)
    if partial_hash != my_hash:
      return False
