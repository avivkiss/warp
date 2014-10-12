
from config import *
from common_tools import *

class Connection:
  def __init__(self, host, user, port=PORT):
    self.server = None

  def getChannel(self): return self.server

  def connect(self): return self.server
  def close(self): pass

  def unpack_remote_host(remote_host):
    """
    Parses the hostname and breaks it into host and user. Modified from paramiko
    """
    username = ''
    hostname = ''
    port = PORT

    if remote_host.find('@') >= 0:
      username, hostname = remote_host.split('@')

    if len(hostname) == 0 or len(username) == 0:
      fail('Hostname/username required.')

    if hostname.find(':') >= 0:
      hostname, portstr = hostname.split(':')
      port = int(portstr)

    return (username, hostname, port)
