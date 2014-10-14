
import sys
from config import *
from common_tools import *
from paramiko import SSHClient
import paramiko, getpass
import threading, xmlrpclib
from forward import *

hostkeytype = None
hostkey = None

# suppress paramiko logging
logging.getLogger("paramiko").setLevel(logging.WARNING)


class Connection:
  def __init__(self, hostname, username, ssh_port=22, comm_port=PORT):
    self.server = None
    self.hostname = hostname
    self.username = username
    self.comm_port = comm_port
    self.ssh_port = ssh_port

  def getChannel(self):
    return self.server

  def connect_ssh(self):
    self.client = SSHClient()
    self.client.load_system_host_keys()
    self.client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
    print self.hostname
    print self.username
    print self.ssh_port

    try:
      self.client.connect(self.hostname, username=self.username, port=self.ssh_port)
    except (paramiko.PasswordRequiredException, paramiko.AuthenticationException, paramiko.ssh_exception.SSHException):
      password = getpass.getpass('Password for %s@%s: ' % (self.username, self.hostname))
      try:
        self.client.connect(self.hostname, username=self.username, port=self.ssh_port, password=password)
      except paramiko.AuthenticationException as message:
        logger.error('Permission denied' + message)
        sys.exit(1)

  def connect(self):
    self.connect_ssh()

    # Now we start the port forwarding
    server = forward_tunnel(self.comm_port, '127.0.0.1', self.comm_port, self.client.get_transport())
    forward_thread = threading.Thread(target=start_tunnel, args=(server,))
    forward_thread.start()

    self.server = xmlrpclib.ServerProxy('http://localhost:' + str(self.comm_port))

    return self.server

  def close(self):
    pass

  @staticmethod
  def unpack_remote_host(remote_host):
    """
    Parses the hostname and breaks it into host and user. Modified from paramiko
    """
    username = ''
    hostname = ''
    # We use port 22 for ssh
    port = 22

    if remote_host.find('@') >= 0:
      username, hostname = remote_host.split('@')

    if len(hostname) == 0 or len(username) == 0:
      fail('Hostname/username required.')

    if hostname.find(':') >= 0:
      hostname, portstr = hostname.split(':')
      port = int(portstr)

    return (username, hostname, port)


def start_tunnel(server):
  server.serve_forever()
