
import sys, traceback
from config import *
from common_tools import *
from paramiko import SSHClient, SFTPClient
import socket, paramiko, getpass
from udt4py import UDTSocket

class ClientUDTManager:
  def __init__(self, server_controller, hostname):
    this.server_controller = server_controller
    this.socket = None
    this.hostname = hostname
    self.port = None

  def connect_to_server(self, port):
    """
    Connects to the provided host and port returning a socket object.
    """
    self.port = port 

    if TCP_MODE:
      sock_type = socket.SOCK_STREAM

      for res in socket.getaddrinfo(self.hostname, port, socket.AF_UNSPEC, sock_type):
        af, socktype, proto, canonname, sa = res
        try:
          this.socket = socket.socket(af, socktype, proto)
        except socket.error:
          this.socket = None
          continue
        try:
          this.socket.connect(sa)
        except socket.error:
          this.socket.close()
          # No need to log error here, some errors are expected
          this.socket = None
          continue
        break

    else:
      sock = UDTSocket()
      sock.connect((socket.gethostbyname(hostname), port))

    if this.socket is None:
      fail('Could not connect to' + self.hostname)

  def send_nonce(self, nonce):
    if not TCP_MODE:
      sock.send(bytearray(nonce))
    else:
      sock.sendall(nonce)


  def send_data(self, file_src, block_count = 0):
    """
    Opens the file at the number of blocks passed in and uses that along with
    the other parameters to send a file to the host at the specified port.
    """
    f = open(file_src, 'r')
    f.seek(block_count * CHUNK_SIZE)
    data = f.read(CHUNK_SIZE)
    with progress.Bar(label="", expected_size=os.path.getsize(file_src)) as bar:
      while data :
        bar.show(f.tell())
        # TODO make this same array every time
        if not TCP_MODE:
          sendChunk(self.socket, bytearray(data))
        else:
          self.socket.sendall(data)
        data = f.read(CHUNK_SIZE)
    logger.info("Data sent.")
    self.socket.close()

  def sendChunk(self, sock, data):
    size = sock.send(data)
    if not size == len(data):
      sendChunk(sock, data[size:])

  def generate_nonce(self, length=NONCE_SIZE):
    """Generate pseudorandom number. Ripped from google."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])

  def __del__(self):
    this.socket.close()
