
import sys, traceback
from config import *
from paramiko import SSHClient
import socket

hostkeytype = None
hostkey = None

# suppress paramiko logging
logging.getLogger("paramiko").setLevel(logging.WARNING)

def handshake(username, hostname, nonce, file_dest, file_hash, file_size, port=22, password=None):
  """
  Goal of the handshake is to return an authed TCP connection. Expects
  executable for alias warp, for now will return (port, block_count) tuple.
  Executable must be in the default path. 
  """
  try:
    client = SSHClient()
    client.load_system_host_keys()
    client.connect(hostname, username=username, port=port)
    command = 'warp ' + str(nonce) + ' ' + \
     file_dest + ' ' + str(file_hash) + ' ' + str(file_size)
    stdin, stdout, stderr = client.exec_command(command)

    logger.debug("Command to server is: %s", command)

    err = stderr.read()

    if err == "":
      port = int(stdout.readline().strip())
      block_count = int(stdout.readline().strip())
      logger.info("port: %s, block count: %s", port, block_count)

      logger.info("Connecting to: %s on port: %s", hostname, port)

      return connect_to_server(hostname, port), block_count
    else:
      # Add log statement and print to stderr
      for line in err:
        print line
        sys.exit()

  except Exception as e:
    # Boiler plate code from paramiko to handle excepntions for ssh connection
    # Eventually we should log this and have a user friendly message.
    logging.error('*** Caught exception: %s: %s', e.__class__, e)
    traceback.print_exc()
    try:
      t.close()
    except:
      pass
    sys.exit(1)


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
      logger.error(msg)
      s.close()
      s = None
      continue
    break

  if s is None:
    print 'Could not connect to', host_name
    sys.exit(1)

  return s