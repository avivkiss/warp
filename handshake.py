
import sys
from config import *
from paramiko import SSHClient

hostkeytype = None
hostkey = None

def handshake(username, hostname, hash, port=22, password=None):
  """
  Goal of the handshake is to return an authed TCP connection. Expects
  executable for alias warp
  """
  try:
    client = SSHClient()
    client.load_system_host_keys()
    client.connect(hostname, username=username, port=port)
    stdin, stdout, stderr = client.exec_command('ls -l')
    print stdout.read()

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

