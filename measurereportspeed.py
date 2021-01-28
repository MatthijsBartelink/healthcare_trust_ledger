from block import Block
from datetime import datetime
from hashlib import sha256
import os
import requests
import time

num_tests = 10

target = "192.168.2.11:5000"
blocks_to_push = 10000
block_whitebox = "192.168.2.11:5000"
endpoint = "endpoint"
key = "This is a replacement for an actual key. Theoretically, any text could be guaranteed this way"
firsthash = "sdfasfefasdcdacvsef"

id = 1
block = Block(id, "ADD", datetime.timestamp(datetime.now()), 0, firsthash, block_whitebox, endpoint)

for blocknum in range(blocks_to_push):
    # print("{} {}".format(blocknum, os.stat('./../WhiteboxServer/endpoint.db').st_size))

    for i in range(num_tests):
        start = time.time()
        request_url = "http://{}/trustreport/{}".format(target, endpoint)
        r = requests.get(request_url)
        roundtrip = time.time() - start
        print(roundtrip, newline=' ')

    print(';')

    request_url = "http://{}/presentblock/{}&{}".format(target, endpoint, block.toJSON())
    r = requests.get(request_url)

    id += 1
    newblock = Block(id, "ADD", datetime.timestamp(datetime.now()), blocknum, block.compute_hash(), block_whitebox, endpoint)
    block = newblock
