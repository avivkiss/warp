
from common_tools import *
from client_udt_manager import ClientUDTManager
import os
from multiprocessing.pool import ThreadPool
from file_transfer_agent import FileTransferAgent


class ClientTransferController:
  def __init__(self, server_channel, hostname, file_src, file_dest, recursive, tcp_mode, disable_verify, parallelism, follow_links):
    self.server_channel = server_channel
    self.hostname = hostname
    self.file_src = file_src
    self.file_root_dest = file_dest
    self.file_dest = file_dest
    self.recursive = recursive
    self.verify = not disable_verify
    self.tcp_mode = tcp_mode
    self.parallelism = parallelism
    self.follow_links = follow_links
    self.transfer_agents = []


  def start(self):
    if os.path.isdir(self.file_src) and not self.recursive:
      fail(str(self.file_src) + " is a directory")
    if os.path.isfile(self.file_src) and self.recursive:
      fail(str(self.file_src) + " is a file")
    if not os.path.isfile(self.file_src) and not os.path.isdir(self.file_src):
      fail("Source file not found")

    pool = ThreadPool(processes=self.parallelism)
    if not self.recursive:
      transfer_agent = FileTransferAgent(ClientUDTManager(self.server_channel, self.hostname, self.tcp_mode), self.server_channel, self.file_src, self.file_dest, self.verify)
      self.transfer_agents.append(transfer_agent)
      pool.apply_async(transfer_agent.send_file)
    else:
      transfer_manager = self.server_channel.root.get_transfer_manager()
      transfer_manager.create_dir(self.file_dest)
      for directory, subdirs, files in os.walk(self.file_src, followlinks=self.follow_links):
        # Make sure the directory we use on the server starts where we want it to
        # Instead of having the same path the client has
        server_directory = os.path.relpath(directory, self.file_src)
        if(str(server_directory) == "."):
          server_directory = ""
        transfer_manager.create_dir(os.path.join(self.file_root_dest, server_directory))
        for f in files:
          file_dest = os.path.join(self.file_root_dest, server_directory, f)
          file_src = os.path.join(directory, f)

          transfer_agent = FileTransferAgent(ClientUDTManager(self.server_channel, self.hostname, self.tcp_mode), self.server_channel, file_src, file_dest, self.verify)

          self.transfer_agents.append(transfer_agent)

          pool.apply_async(transfer_agent.send_file)

    return pool

  def get_server_received_size(self):
    pool = ThreadPool(processes=20)

    res = pool.map(lambda x: x.get_progress(), self.transfer_agents)

    pool.close()

    return reduce(lambda x, y: x + y, res, 0)

  def get_total_transfer_size(self):
    pool = ThreadPool(processes=20)

    res = pool.map(lambda x: x.file_size, self.transfer_agents)

    pool.close()

    return reduce(lambda x, y: x + y, res, 0)
  transfer_size = property(get_total_transfer_size)


  def is_transfer_finished(self):
    for i in self.transfer_agents:
      if not i.transfer_finished:
        return False
    return True

  def is_transfer_success(self):
    return reduce(lambda y, x: 0 + y if x.transfer_success is True else 1 + y, self.transfer_agents, 0) == 0

  def close(self):
    """
    Cleanup goes here, we probably have to close some connections...
    """
    pass

