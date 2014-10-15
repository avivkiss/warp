#!/usr/bin/env python

"""
This is the main driver script that will run on the client.
"""

from config import *
from common_tools import *
import os.path
from connection import Connection
from client_transfer_controller import ClientTransferController
import plac

@plac.annotations(
    tcp_mode=('TCP mode', 'flag', 't'),
    recursive = ('prints', 'flag', 'r'),
    disable_verify = ('Disable verify', 'flag', 'v'))
def main(remote_host, recursive, file_src, file_dest, tcp_mode, disable_verify, custom_comm_port=PORT):
  (head, tail) = os.path.split(file_src)
  # Extract the username and hostname from the arguments,
  # the ssh_port does not need to be specified, will default to 22.
  username, hostname, ssh_port = Connection.unpack_remote_host(remote_host)

  # Start an ssh connection used by the xmlrpc connection,
  # the comm_port is used for port forwarding.
  connection = Connection(hostname=hostname, username=username, ssh_port=ssh_port, comm_port=custom_comm_port)
  connection.connect()

  # get the rpc channel
  channel = connection.getChannel()

  controller = ClientTransferController(channel, hostname, file_src, file_dest, recursive, tcp_mode, disable_verify)

  controller.start()
  controller.close()

  connection.close()


if __name__ == '__main__':
  plac.call(main)
