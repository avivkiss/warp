#!/usr/bin/env python

"""
This is the main driver script that will run on the client.
"""

from config import *
from common_tools import *
import sys, random, os.path
from handshake import handshake

def main(remote_host, recursive, file_src, file_dest):
  if os.path.isdir(file_src) and not recursive:
    logger.error("%s is a directory", file_src)
    return
  elif not os.path.isdir(file_src) and \
    not os.path.isfile(file_src):
      logger.error("%s no such file or directory", file_src)
      return
  username, hostname, ssh_port = unpack_remote_host(remote_host)
  nonce = generate_nonce()
  file_hash = getHash(file_src)
  # handshake should be returning a tuple, port and numblocks TODO
  sock, block_count = handshake(username=username, hostname=hostname, \
    nonce=nonce, file_dest=file_dest, file_hash=file_hash, \
    file_size=os.path.getsize(file_src), file_src=file_src)

  send_data(sock, file_src, block_count)

def send_data(sock, file_src, block_count = 0):
  """
  Opens the file at the number of blocks passed in and uses that along with
  the other parameters to send a file to the host at the specified port.
  """
  f = open(file_src, 'r')
  f.seek(block_count * CHUNK_SIZE)
  data = f.read(CHUNK_SIZE)
  while data :
    sock.sendall(data)
    data = f.read(CHUNK_SIZE)
  # print "Sent " + str(sent) + " bytes." 
  logger.info("Data sent.")
  sock.close()

def generate_nonce(length=NONCE_SIZE):
  """Generate pseudorandom number. Ripped from google."""
  return ''.join([str(random.randint(0, 9)) for i in range(length)])


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
    sys.stderr.write('Hostname/username required.')
    sys.exit(1)

  if hostname.find(':') >= 0:
    hostname, portstr = hostname.split(':')
    port = int(portstr)

  return (username, hostname, port)

main.__annotations__ = dict(recursive = ('prints', 'flag', 'r'))
if __name__ == '__main__':
  import plac; plac.call(main)
