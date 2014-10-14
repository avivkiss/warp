
class ClientTransferController:
  def __init__(self, server_channel, file_src, file_dest, recursive, tcp_mode, disable_verify):
    self.server_channel = server_channel

  def start(): pass

  def verify_partial_hash(self, file_src, partial_hash, block_count):
  """
  Takes a file source and hashes the file up to block count and then compares 
  it with the partial hash passed in, fails if they do not match.
  """
  my_hash = getHash(file_src, block_count)
  if partial_hash != my_hash:
    msg = "Partial hash did not match server side. Please remove file from server before transferring.\n"
    fail(msg)