import hashlib
import json
from time import time
from flask import Flask, jsonify, request
from flask_cors import CORS

# --- PART 1: The Core Blockchain Logic ---

class Transaction:
    def __init__(self, sender, recipient, amount):
        self.sender = sender
        self.recipient = recipient
        self.amount = amount

    def to_dict(self):
        return {
            'sender': self.sender,
            'recipient': self.recipient,
            'amount': self.amount
        }

class Block:
    def __init__(self, index, transactions, timestamp, previous_hash, nonce=0):
        self.index = index
        self.transactions = transactions
        self.timestamp = timestamp
        self.previous_hash = previous_hash
        self.nonce = nonce
        self.hash = self.compute_hash()

    def compute_hash(self):
        block_string = json.dumps({
            "index": self.index,
            "transactions": [tx.to_dict() for tx in self.transactions],
            "timestamp": self.timestamp,
            "previous_hash": self.previous_hash,
            "nonce": self.nonce
        }, sort_keys=True)
        return hashlib.sha256(block_string.encode()).hexdigest()

class Blockchain:
    def __init__(self):
        self.unconfirmed_transactions = []
        self.chain = []
        self.difficulty = 2
        self.create_genesis_block()

    def create_genesis_block(self):
        genesis_block = Block(0, [], time(), "0")
        self.proof_of_work(genesis_block)
        self.chain.append(genesis_block)

    @property
    def last_block(self):
        return self.chain[-1]

    def add_transaction(self, transaction):
        self.unconfirmed_transactions.append(transaction)

    def proof_of_work(self, block):
        block.nonce = 0
        computed_hash = block.compute_hash()
        while not computed_hash.startswith('0' * self.difficulty):
            block.nonce += 1
            computed_hash = block.compute_hash()
        block.hash = computed_hash
        return computed_hash

    def mine(self):
        if not self.unconfirmed_transactions:
            return False

        last_block = self.last_block
        new_block = Block(index=last_block.index + 1,
                          transactions=self.unconfirmed_transactions,
                          timestamp=time(),
                          previous_hash=last_block.hash)

        self.proof_of_work(new_block)
        self.add_block(new_block)
        self.unconfirmed_transactions = []
        return new_block.index

    def add_block(self, block):
        previous_hash = self.last_block.hash
        if previous_hash != block.previous_hash:
            return False
        if not self.is_valid_proof(block, block.hash):
            return False
        self.chain.append(block)
        return True

    def is_valid_proof(self, block, block_hash):
        return (block_hash.startswith('0' * self.difficulty) and
                block_hash == block.compute_hash())


# --- PART 2: The Web Server (Flask) ---

app = Flask(__name__)
CORS(app)  # This enables Cross-Origin Resource Sharing

# Initialize the blockchain object
blockchain = Blockchain()

@app.route('/chain', methods=['GET'])
def get_chain():
    """Returns the full blockchain data."""
    chain_data = []
    for block in blockchain.chain:
        chain_data.append({
            'index': block.index,
            'timestamp': block.timestamp,
            'transactions': [t.to_dict() for t in block.transactions],
            'hash': block.hash,
            'previous_hash': block.previous_hash,
            'nonce': block.nonce
        })
    return jsonify({"length": len(chain_data), "chain": chain_data}), 200

@app.route('/mine', methods=['GET'])
def mine_unconfirmed_transactions():
    """Mines pending transactions into a new block."""
    result = blockchain.mine()
    if not result:
        return jsonify({"message": "No transactions to mine"}), 400
    return jsonify({"message": f"Block #{result} mined successfully!"}), 200

@app.route('/transactions/new', methods=['POST'])
def new_transaction():
    """Adds a new transaction to the pool."""
    values = request.get_json()
    
    # Check that the required fields are in the POST'ed data
    required = ['sender', 'recipient', 'amount']
    if not all(k in values for k in required):
        return 'Missing values', 400

    # Create a new Transaction
    tx = Transaction(values['sender'], values['recipient'], values['amount'])
    blockchain.add_transaction(tx)
    
    return jsonify({"message": "Transaction will be added to the next block"}), 201

# --- PART 3: Start the Server ---

if __name__ == '__main__':
    # Run the Flask server locally on port 5000
    print("Starting Blockchain Server on port 5000...")
    app.run(host='0.0.0.0', port=5000, debug=True)
