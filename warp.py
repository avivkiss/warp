"""
This is the main driver script that will run on the client.
"""

import socket, sys

def main(remote_host, file_src, file_dest):
  s = connect_to_server(remote_host)
  f = open(file_src, 'r')
  sent = s.sendall(f.read())
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
      print msg
      s.close()
      s = None
      continue
    break
  if s is None:
    print 'could not open socket'
    sys.exit(1)

  return s

if __name__ == '__main__':
  import plac; plac.call(main)
