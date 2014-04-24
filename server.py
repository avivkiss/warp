"""
This is the server script that will be started by client over SSH, it takes 
two arguments...
"""

import socket
import sys

CHUNK_SIZE = 4096

def main(nonce, port, filename):
  """
  Open a port and wait for connection, write to data to filename.
  """
  conn, addr, = wait_and_accept(port)
  
  ouput_file = open(filename, 'w')

  print 'Connected by', addr
  while 1:
    data = conn.recv(CHUNK_SIZE)
    ouput_file.write(data)
    if not data: break

  ouput_file.close()
  conn.close()

def wait_and_accept(port):
  """
  Opens a connection on the port and waits returns a conn and address.
  """
  HOST = None               # Symbolic name meaning all available interfaces
  PORT = port              # Arbitrary non-privileged port
  s = None
  for res in socket.getaddrinfo(HOST, PORT, socket.AF_UNSPEC,
                                socket.SOCK_STREAM, 0, socket.AI_PASSIVE):
    af, socktype, proto, canonname, sa = res
    try:
        s = socket.socket(af, socktype, proto)
    except socket.error as msg:
        s = None
        continue
    try:
        s.bind(sa)
        s.listen(1)
    except socket.error as msg:
        s.close()
        print msg
        s = None
        continue
    break
  if s is None:
    print 'could not open socket'
    sys.exit(1)

  conn, addr = s.accept()
  return conn, addr

if __name__ == '__main__':
  import plac; plac.call(main)
