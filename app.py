from flask import Flask, jsonify, request
from flask_cors import CORS
import hashlib
import json
from time import time

# --- YOUR BLOCKCHAIN CLASSES (Unchanged logic) ---
class Block:
    def __init__(self, index, timestamp, data, previous_hash):
        self.index = index
        self.timestamp = timestamp
        self.data = data
        self.previous_hash = previous_hash
        self.hash = self.calculate_hash()

    def calculate_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "timestamp": self.timestamp,
            "data": self.data,
            "previous_hash": self.previous_hash
        }, sort_keys=True).encode()
        return hashlib.sha256(block_string).hexdigest()

class WalletLinkingBlockchain:
    def __init__(self):
        self.chain = [self.create_genesis_block()]

    def create_genesis_block(self):
        return Block(0, time(), "Genesis Block", "0")

    def get_latest_block(self):
        return self.chain[-1]

    def link_wallets(self, user_id, wallet_data):
        new_block = Block(
            index=len(self.chain),
            timestamp=time(),
            data={"user_id": user_id, "wallets": wallet_data},
            previous_hash=self.get_latest_block().hash
        )
        self.chain.append(new_block)
        return new_block

# --- THE NEW API PART ---
app = Flask(__name__)
CORS(app)  # This allows your Wix site to talk to this server

# Initialize the Blockchain
blockchain = WalletLinkingBlockchain()

@app.route('/add_event', methods=['POST'])
def add_event():
    # 1. Get data from Wix
    values = request.get_json()
    required = ['user_id', 'wallet_address']
    
    if not all(k in values for k in required):
        return 'Missing values', 400

    # 2. Add to Blockchain
    # We treat the "event" (like beach cleaning) as the data
    block = blockchain.link_wallets(values['user_id'], values['wallet_address'])
    
    response = {
        'message': 'Event recorded to Blockchain',
        'index': block.index,
        'hash': block.hash,
        'previous_hash': block.previous_hash
    }
    return jsonify(response), 201

@app.route('/get_chain', methods=['GET'])
def get_chain():
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            'index': block.index,
            'timestamp': block.timestamp,
            'data': block.data,
            'hash': block.hash
        })
    return jsonify({'chain': chain_data, 'length': len(chain_data)}), 200

if __name__ == '__main__':
    # Run server on port 5000
    app.run(host='0.0.0.0', port=5000)
