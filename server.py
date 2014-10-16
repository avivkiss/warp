#!/usr/bin/env python


"""
This is the server script that will be started by client over SSH, it takes
two arguments...
"""

from config import *
from rpyc.utils.server import ThreadedServer
from common_tools import *
import plac
from server_transfer_controller import ServerTransferController

logger.propagate = True


def main():
  server = ThreadedServer(ServerTransferController, hostname='localhost', port=PORT, protocol_config={"allow_public_attrs": True})
  server.start()


if __name__ == '__main__':
  plac.call(main)
