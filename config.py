# For now global variables and configuration will be stored in this file.
# In the future consider moving some of this to a "non-executable"
# configuration file.

# some logging setup
import logging
logging.basicConfig(format='%(levelname)s:%(message)s', level=logging.DEBUG)

# Just a random chunk size to send the file in pieces,
# should be the same as the chunk size used to write
CHUNK_SIZE = 4096
TRANSACTION_HISTORY_FILENAME = "transaction_history.warp"