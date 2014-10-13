#!/usr/bin/env python

"""
This is the main driver script that will run on the client.
"""

from config import *
from common_tools import *
import os.path
from connection import Connection
import plac

@plac.annotations(
    tcp_mode=('TCP mode', 'flag', 't'),
    recursive = ('prints', 'flag', 'r'),
    disable_verify = ('Disable verify', 'flag', 'v'))
def main(remote_host, recursive, file_src, file_dest, tcp_mode, disable_verify):
  (head, tail) = os.path.split(file_src)
  username, hostname, ssh_port = Connection.unpack_remote_host(remote_host)

  connection = Connection(username, hostname, ssh_port)
  connection.connect()

  channel = connection.getChannel()

  controller = ClientTransferController(channel, file_src, file_dest, recursive, tcp_mode, disable_verify)

  controller.start()
  controller.close()

  connection.close()


if __name__ == '__main__':
  plac.call(main)
