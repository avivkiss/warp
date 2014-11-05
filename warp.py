#!/usr/bin/env python

"""
This is the main driver script that will run on the client.
"""

from config import *
from common_tools import *
from connection import Connection
from client_transfer_controller import ClientTransferController
import plac
import sys, time, logging
from clint.textui import progress

@plac.annotations(
    tcp_mode=('TCP mode', 'flag', 't'),
    recursive = ('Transfer directory', 'flag', 'r'),
    parallelism = ('parallelism', 'option', 'p', int),
    disable_verify = ('Disable verify', 'flag', 'w'),
    verbose = ('Enable logging', 'flag', 'v'),
    follow_links = ('Follow symbolic links', 'flag', 'L'))
def main(remote_host, recursive, file_src, file_dest, tcp_mode, disable_verify, follow_links, verbose=False, custom_comm_port=PORT, parallelism=3):
  # Extract the username and hostname from the arguments,
  # the ssh_port does not need to be specified, will default to 22.
  username, hostname, ssh_port = Connection.unpack_remote_host(remote_host)

  if verbose:
    logger.setLevel(logging.DEBUG)

  # Start an ssh connection used by the xmlrpc connection,
  # the comm_port is used for port forwarding.
  connection = Connection(hostname=hostname, username=username, ssh_port=ssh_port, comm_port=custom_comm_port)
  connection.connect()

  # get the rpc channel
  channel = connection.channel

  controller = ClientTransferController(channel, hostname, file_src, file_dest, recursive, tcp_mode, disable_verify, parallelism, follow_links)

  logger.debug("Starting transfer")
  result = controller.start()
  if(result[0]):
    with progress.Bar(label="", expected_size=controller.transfer_size) as bar:
      while not controller.is_transfer_finished():
        bar.show(controller.get_server_received_size(), controller.transfer_size)
        time.sleep(0.1)

    if controller.is_transfer_success():
      logger.debug("Done with transfer.")
    else:
      logger.warn("Failed to send file.")

  controller.close()
  connection.close()
  channel.close()
  logger.debug("Closed connections.")

  sys.exit()


if __name__ == '__main__':
  plac.call(main)
