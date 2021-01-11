import json
from hashlib import sha256

class Block:

    def __init__(self, index, timestamp, logicaltimestamp, previous_hash, endorser, endpoint, nonce=0, positive=True):
        self.index = index
        self.timestamp = timestamp
        self.logicaltimestamp = logicaltimestamp
        self.previous_hash = previous_hash
        self.endorser = endorser
        self.endpoint = endpoint
        self.nonce = nonce
        self.positive = positive

    def compute_hash(self):
        block_string = json.dumps(self.__dict__, sort_keys=True)
        return sha256(block_string.encode()).hexdigest()

    def toJSON(self):
        return json.dumps(self.__dict__, sort_keys=True)
