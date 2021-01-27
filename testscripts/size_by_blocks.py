from block import Block
from datetime import datetime
from hashlib import sha256
from os import stats
import requests

target = "192.168.2.11:5000"
blocks_to_push = 6000
block_whitebox = "192.168.2.11:5000"
endpoint = "endpoint"
key = "This is a replacement for an actual key. Theoretically, any text could be guaranteed this way"
firsthash = "sdfasfefasdcdacvsef"

id = 1
block = Block(id, "ADD", datetime.timestamp(datetime.now()), 0, firsthash, block_whitebox, endpoint)

for blocknum in range(blocks_to_push):
    print("{} {}".format(blocknum, stats('/../WhiteboxServer/endpoint.db')))

    request_url = "http://{}/presentblock/{}&{}".format(target, endpoint, block.toJSON())
    r = requests.get(request_url)

    id += 1
    newblock = Block(id, "ADD", datetime.timestamp(datetime.now()), blocknum, block.compute_hash(), block_whitebox, endpoint)
    block = newblock
