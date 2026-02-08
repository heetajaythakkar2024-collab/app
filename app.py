from flask import Flask, jsonify, request
from flask_cors import CORS
import hashlib
import json
from time import time
import random

# --- BLOCKCHAIN CLASSES ---
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
        # Automatically add fake data on startup
        self.seed_data()

    def create_genesis_block(self):
        return Block(0, time(), "Genesis Block - System Init", "0")

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

    def seed_data(self):
        """Adds fake data so the blockchain looks active for the demo."""
        dummy_data = [
            ("Volunteer_Alice", "0x71C7656EC7ab88b098defB751B7401B5f6d8976F", "Marina Beach Cleanup"),
            ("Eco_Warrior_99", "0x89205A3A3b2A69De6Dbf7f01ED13B2108B2c43e7", "Vellore Park Planting"),
            ("Student_VIT_22", "0x409B0aCfFe820C0769397E4F23D26F7F0A805566", "Campus Recycling Drive"),
            ("CleanCity_Bot", "0x2546BcD3c84621E976D8185a91A922aE77ECE030", "River Bed Restoration"),
            ("Green_Team_Lead", "0xb794F5eA0ba39494cE839613fffBA74279579268", "Plastic Ban Awareness")
        ]
        
        print("🌱 Seeding Blockchain with existing data...")
        for user, wallet, event in dummy_data:
            # We add a small delay to make timestamps look different
            self.link_wallets(user, {"address": wallet, "event": event})
        print("✅ Blockchain seeded with 5 blocks.")

# --- API SERVER ---
app = Flask(__name__)
CORS(app)

blockchain = WalletLinkingBlockchain()

@app.route('/add_event', methods=['POST'])
def add_event():
    values = request.get_json()
    required = ['user_id', 'wallet_address']
    
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create the new block
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
            'hash': block.hash,
            'previous_hash': block.previous_hash
        })
    return jsonify({'chain': chain_data, 'length': len(chain_data)}), 200

if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 5000))
    app.run(host='0.0.0.0', port=port)

