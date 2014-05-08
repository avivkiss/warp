
import sys, traceback
from config import *
from paramiko import SSHClient

hostkeytype = None
hostkey = None

# suppress paramiko logging
logging.getLogger("paramiko").setLevel(logging.WARNING)

def handshake(username, hostname, nonce, file_dest, hash, file_size, port=22, password=None):
  """
  Goal of the handshake is to return an authed TCP connection. Expects
  executable for alias warp, for now will return (port, block_count) tuple.
  Executable must be in the default path.
  """
  try:
    client = SSHClient()
    client.load_system_host_keys()
    client.connect(hostname, username=username, port=port)
    stdin, stdout, stderr = client.exec_command('warp ' + str(nonce) + ' ' +
     file_dest + ' ' + str(hash) + ' ' + str(file_size))
    
    # TODO error checking
    # print stdout.read()

    port = stdout.readline()
    print "port: ", port
    block_count = stdout.readline()
    print "block count: ", block_count

    return (int(port), int(block_count))

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


