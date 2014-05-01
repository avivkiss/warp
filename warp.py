#!/usr/bin/env python

"""
This is the main driver script that will run on the client.
"""

import socket, sys, hashlib, random
from config import *
from handshake import handshake

def main(remote_host, file_src, file_dest):
  username, hostname, ssh_port = unpack_remote_host(remote_host)
  nonce = generate_nonce();
  hash = getHash(file_src)
  port = handshake(username=username, hostname=hostname, nonce=nonce, file_dest=file_dest, hash=hash)

  print port, hostname

  send_data(hostname, file_src, file_dest, port)

def send_data(hostname, file_src, file_dest, tcp_port):
  s = connect_to_server(hostname, tcp_port)
  f = open(file_src, 'r')
  data = f.read(CHUNK_SIZE)
  while data :
    s.sendall(data)
    data = f.read(CHUNK_SIZE)
  # print "Sent " + str(sent) + " bytes." 
  s.close()

def generate_nonce(length=8):
  """Generate pseudorandom number. Ripped from google."""
  return ''.join([str(random.randint(0, 9)) for i in range(length)])

def getHash(file):
  """
  Returns a sha256 hash for the specified file.
  Eventually sent to server to check for restarts.
  """
  hash = hashlib.sha256()
  with open(file, "r") as file:
    while True:
      data = file.read(CHUNK_SIZE)
      if not data:
        return hash.hexdigest()
      hash.update(data)

def unpack_remote_host(remote_host):
  """
  Parses the hostname and breaks it into host and user. Modified from paramiko
  """
  username = ''
  hostname = ''
  port = 22

  if remote_host.find('@') >= 0:
    username, hostname = remote_host.split('@')

  if len(hostname) == 0 or len(username) == 0:
    print('Hostname/username required.')
    sys.exit(1)

  if hostname.find(':') >= 0:
    hostname, portstr = hostname.split(':')
    port = int(portstr)

  return (username, hostname, port)


def connect_to_server(host_name, port):
  s = None

  for res in socket.getaddrinfo(host_name, port, socket.AF_UNSPEC, socket.SOCK_STREAM):
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
    print 'Could not connect to', host_name
    sys.exit(1)

  return s

if __name__ == '__main__':
  import plac; plac.call(main)
