#!/usr/bin/env python


"""
This is the server script that will be started by client over SSH, it takes
two arguments...
"""

from config import *
from rpyc.utils.server import OneShotServer
from common_tools import *
import plac
from server_transfer_controller import ServerTransferController
import os, sys
from os.path import expanduser

logger.propagate = True


def main():
  os.chdir(expanduser("~"))
  server = OneShotServer(ServerTransferController, hostname='localhost', port=0, protocol_config={"allow_public_attrs": True})
  sys.stderr.write(str(server.port))
  sys.stderr.write('     ')
  server.start()


if __name__ == '__main__':
  plac.call(main)
