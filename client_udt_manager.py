
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

  def connect_to_server(self, hostname, port):
    """
    Connects to the provided host and port returning a socket object.
    """
    this.socket = None

    if TCP_MODE:
      sock_type = socket.SOCK_STREAM
    else:
      sock_type = socket.SOCK_DGRAM


    for res in socket.getaddrinfo(hostname, port, socket.AF_UNSPEC, sock_type):
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

    if this.socket is None:
      fail('Could not connect to' + hostname)

  def send_nonce(self, sock, hostname, port, nonce):
    if not TCP_MODE:
      sock = UDTSocket()
      sock.connect((socket.gethostbyname(hostname), port))
      sock.send(bytearray(nonce))
    else:
      sock = connect_to_server(hostname, port)
      sock.sendall(nonce)


  def send_data(self, sock, file_src, block_count = 0):
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
          sendChunk(sock, bytearray(data))
        else:
          sock.sendall(data)
        data = f.read(CHUNK_SIZE)
    logger.info("Data sent.")
    sock.close()

  def sendChunk(self, sock, data):
    size = sock.send(data)
    if not size == len(data):
      sendChunk(sock, data[size:])

  def generate_nonce(self, length=NONCE_SIZE):
    """Generate pseudorandom number. Ripped from google."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])


