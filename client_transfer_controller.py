
from common_tools import *
from client_udt_manager import ClientUDTManager
import os, threading
from multiprocessing.pool import ThreadPool


class ClientTransferController:
  def __init__(self, server_channel, hostname, file_src, file_dest, recursive, tcp_mode, disable_verify, parallelism):
    self.server_channel = server_channel
    self.hostname = hostname
    self.file_src = file_src
    self.file_root_dest = file_dest
    self.file_dest = file_dest
    self.recursive = recursive
    self.verify = not disable_verify
    self.tcp_mode = tcp_mode
    self.transfer_size = 0
    self.transfer_pool_results = []
    self.parallelism = parallelism
    self.transfer_status = []

  def start(self):
    if os.path.isdir(self.file_src) and not self.recursive:
      fail(str(self.file_src) + " is a directory")
    if os.path.isfile(self.file_src) and self.recursive:
      fail(str(self.file_src) + " is a file")
    if not os.path.isfile(self.file_src) and not os.path.isdir(self.file_src):
      fail("Source file not found")

    pool = ThreadPool(processes=self.parallelism)
    if not self.recursive:
      self.transfer_size = os.path.getsize(self.file_src)
      self.transfer_pool_results.append(pool.apply_async(self.send_file_with_status, args=(self.file_src, self.file_dest)))
    else:
      transfer_manager = self.server_channel.root.get_transfer_manager()
      transfer_manager.create_dir(self.file_dest)
      for directory, subdirs, files in os.walk(self.file_src):
        # Make sure the directory we use on the server starts where we want it to
        # Instead of having the same path the client has
        server_directory = os.path.relpath(directory, self.file_src)
        if(str(server_directory) == "."):
          server_directory = ""
        transfer_manager.create_dir(os.path.join(self.file_root_dest, server_directory))
        for f in files:
          file_dest = os.path.join(self.file_root_dest, server_directory, f)
          file_src = os.path.join(directory, f)
          self.transfer_size += os.path.getsize(file_src)
          self.transfer_pool_results.append(pool.apply_async(self.send_file_with_status, args=(file_src, file_dest)))

    return pool

  def is_transfer_finished(self):
    for i in self.transfer_pool_results:
      if not i.ready():
        return False

    return True
    
  def is_transfer_success(self):
    return self.transfer_status.count(False) == 0
      
  def send_file_with_status(self, file_name, file_dest):
    self.transfer_status.append(self.send_file(file_name, file_dest))

  def send_file(self, file_name, file_dest):
    udt = ClientUDTManager(self.server_channel, self.hostname, self.tcp_mode)
    transfer_manager = self.server_channel.root.get_transfer_manager()

    logger.debug("Source " + file_name + " Dest: " + file_dest)

    file_path = transfer_manager.validate_filepath(file_dest, file_name)
    logger.debug("Saving to... " + file_path)

    block_count = 0

    #TODO: figure out what to do if the file you are trying to send is a folder on the server
    server_file_size = transfer_manager.get_size_and_init_file_path(file_path)
    if(server_file_size > 0):
      block_count = 0
      if(server_file_size != os.path.getsize(file_name)):
        block_count = transfer_manager.get_blocks(file_path)
      file_hash = transfer_manager.get_file_hash(file_path, block_count)
      if not self.verify_partial_hash(file_name, file_hash, block_count):
        logger.debug("Client and server side partial hash differ.")
        transfer_manager.overwrite_file(file_path)
        block_count = 0
      elif block_count == 0:
        logger.debug("File already transfered")
        return True
    else:
      # This will create the file on the server side
      transfer_manager.overwrite_file(file_path)

    udt.connect()
    udt.send_file(file_name, file_path, block_count, os.path.getsize(file_name))

    if self.verify:
      if self.verify_partial_hash(file_name, transfer_manager.get_file_hash(file_path)):
        return True
      else:
        logger.debug("File failed validation check.")
        return False
    return True

  def file_block_count(self, file_src):
    return (os.path.getsize(file_src) / CHUNK_SIZE)

  def close(self):
    """
    Cleanup goes here, we probably have to close some connections...
    """
    pass

  def verify_partial_hash(self, file_src, partial_hash, block_count=0):
    """
    Takes a file source and hashes the file up to block count and then compares
    it with the partial hash passed in, fails if they do not match.
    """
    my_hash = getHash(file_src, block_count)
    return partial_hash == my_hash
