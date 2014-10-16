
import sys, traceback
from config import *
from common_tools import *
from paramiko import SSHClient, SFTPClient
import socket, paramiko, getpass
import random
from udt4py import UDTSocket
import threading

class ServerUDTManager:
  def __init__(self, tcp_mode):
    self.tcp_mode = tcp_mode

    self.udt_sock = None
    self.conn = None

    global TCP_MODE 
    TCP_MODE = tcp_mode

    self.sock = self.get_socket()
    self.port = self.sock.getsockname()[1]
    self.nonce = self.generate_nonce()


  def open_connection(self):
    if not TCP_MODE:
      self.udt_sock = UDTSocket()
      self.udt_sock.bind(self.sock.fileno())
      self.udt_sock.listen()

    listening_thread = threading.Thread(target=self.accept_and_verify)
    listening_thread.start()

    return (self.port, self.nonce)


  def accept_and_verify(self):
    if not TCP_MODE:
      self.conn, addr = self.udt_sock.accept()
      logger.info('Connected by %s', addr)

      recvd_nonce = bytearray(NONCE_SIZE) 
      self.conn.recv(recvd_nonce)
      recvd_nonce = str(recvd_nonce)
    else: 
      self.conn, addr = self.sock.accept()
      logger.info('Connected by %s', addr)

      recvd_nonce = self.conn.recv(NONCE_SIZE)

    if recvd_nonce != nonce:
      fail("Received nonce %s doesn't match %s.", recvd_nonce, nonce)

  def recieve_data(self, output_file, block_count, file_size):
    """
    Receives data and writes it to disk, stops when it is no longer receiving 
    data.
    """
    def recieve_data_threaded(file_path, block_count, file_size):
      output_file = open(file_path, "r+")
      output_file.seek(block_count * CHUNK_SIZE)

      size = block_count * CHUNK_SIZE
      data = bytearray(CHUNK_SIZE)

      if not TCP_MODE:
        while 1:
          len_rec = self.conn.recv(data)
          data = str(data)
          output_file.write(data[:len_rec])
          size = size + len_rec

          if len_rec == 0 or str(size) == str(file_size): break
      else:
        while 1:
          data = self.conn.recv(CHUNK_SIZE)
          output_file.write(data)
          size = size + len(data)
          if len(data) == 0: break

      output_file.close()

    thread = threading.Thread(target=recieve_data_threaded)
    thread.start()

    return thread

  def get_socket(self):
    """
    Opens and returns a socket on an open port.
    """

    s = None

    if TCP_MODE:
      sock_type = socket.SOCK_STREAM
    else:
      sock_type = socket.SOCK_DGRAM

    try:
      s = socket.socket(socket.AF_INET, sock_type)
    except socket.error as msg:
      fail(msg)
    try:
      s.bind(('', 0))
      if TCP_MODE:
        s.listen(1)
    except socket.error as msg:
      s.close()
      fail(str(msg))

    return s


  def generate_nonce(self, length=NONCE_SIZE):
    """Generate pseudorandom number. Ripped from google."""
    return ''.join([str(random.randint(0, 9)) for i in range(length)])


