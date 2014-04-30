"""
This is the main driver script that will run on the client.
"""

import socket, sys
from config import *

def main(remote_host, file_src, file_dest):
  s = connect_to_server(remote_host)
  f = open(file_src, 'r')
  data = f.read(CHUNK_SIZE)
  while data :
    s.sendall(data)
    data = f.read(CHUNK_SIZE)
  # print "Sent " + str(sent) + " bytes." 
  s.close()

def connect_to_server(remote_host):
  HOST = remote_host    # The remote host
  PORT = 54321              # random port number, will be changed
  s = None
  for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC, socket.SOCK_STREAM):
    af, socktype, proto, canonname, sa = res
    try:
      s = socket.socket(af, socktype, proto)
    except socket.error as msg:
      s = None
      continue
    try:
      s.connect(sa)
    except socket.error as msg:
      #print msg
      s.close()
      s = None
      continue
    break
  if s is None:
    print 'Could not connect to', remote_host
    sys.exit(1)

  return s

if __name__ == '__main__':
  import plac; plac.call(main)
