#!/usr/bin/env python 


"""
This is the server script that will be started by client over SSH, it takes 
two arguments...
"""

from config import *
from common_tools import *
from server_transfer_controller import ServerTransferControllerx
import plac

from SocketServer import ThreadingMixIn
from SimpleXMLRPCServer import SimpleXMLRPCServer

class XMLRPCServer(ThreadingMixIn, SimpleXMLRPCServer):
  pass

logger.propagate = False

def main():
  server = XMLRPCServer(('localhost', PORT))
  server.register_instance(ServerTransferController())
  server.serve_forever()


if __name__ == '__main__':
  plac.call(main)
