
from server_udt_manager import ServerUDTManager
from transfer_manager import TransferManager

class ServerTransferController:
  def __init__(self):
    self.ServerUDTManager = ServerUDTManager
    self.transfer_manager = TransferManager()
