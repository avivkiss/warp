
import sys, traceback, socket, StringIO
from config import *
from paramiko import SSHClient
from time import sleep

hostkeytype = None
hostkey = None

def handshake(username, hostname, nonce, file_dest, hash, file_size, port=22, password=None):
  """
  Goal of the handshake is to return an authed TCP connection. Expects
  executable for alias warp, for now will return (port, block_count) tuple.
  """
  try:
    client = SSHClient()
    client.load_system_host_keys()
    client.connect(hostname, username=username, port=port)
    stdin, stdout, stderr = client.exec_command('warp ' + str(nonce) + ' ' + file_dest + ' ' + str(file_size))
    
    # TODO error checking

    return int(stdout.readline())

  except Exception as e:
    # Boiler plate code from paramiko to handle excepntions for ssh connection
    # Eventually we should log this and have a user friendly message.
    print('*** Caught exception: %s: %s' % (e.__class__, e))
    traceback.print_exc()
    try:
      t.close()
    except:
      pass
    sys.exit(1)


