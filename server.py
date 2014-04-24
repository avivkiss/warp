"""
This is the server script that will be started by client over SSH, it takes 
two arguments...
"""

import socket

def main(nonce, port):
  pass


if __name__ == '__main__':
  import plac; plac.call(main)
