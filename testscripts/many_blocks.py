from block import Block
from datetime import datetime
from hashlib import sha256

target = "192.168.2.11:5000"
blocks_to_push = 1000
block_whitebox = "192.168.2.11:5000"
endpoint = "endpoint"
key = "This is a replacement for an actual key. Theoretically, any text could be guaranteed this way"
firsthash = ""

id = 1
block = Block(id, "ADD", datetime.timestamp(datetime.now()), firsthash, block_whitebox, endpoint)

for blocknum in range(blocks_to_push):
    request_url = "http://{}/presentblock/{}&{}".format(target, endpoint, block.toJSON())
    r = requests.get(request_url)

    id += 1
    newblock = Block(id, "ADD", datetime.timestamp(datetime.now()), block.compute_hash(), block_whitebox, endpoint)
    block = newblock
