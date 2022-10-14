# Implementing a simple decentralized blockchain class with multiple nodes using DPoS consensus in the blockchain network

import hashlib

import json

from datetime import datetime

from urllib.parse import urlparse

import requests

from random import randint

# blockchain class
class Blockchain(object):
    
    # Constructor : creates lists to store the blockchain and the transactions made
    def __init__(self):

        #List that store the Blockchain

        self.chain = []

        #List that stores the unverified transactions

        self.unverified_transactions = []  

        #List that stores verified transactions

        self.verified_transactions = []

        #genesis block 
               
        self.new_block(previous_hash = 1)

        #Set containing nodes in the network. Used set here to prevent the duplication of node.

        self.nodes = set()

        #List that contains all the nodes along with their stake in the network

        self.all_nodes = []

        #List of all the voting nodes in the network

        self.voteNodespool = []

        #List that stores all the nodes in descending order of votes received

        self.starNodespool = []

        #List that stores the top 3 nodes with the highest stake * votes_received

        self.superNodespool = []

        #List which stores the address of the delegate nodes chosen for mining process

        self.delegates = []


    #creating a new block in the Blockchain

    def new_block(self,previous_hash = None):
        block = {
            'index': len(self.chain) + 1,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S'),
            'transactions': self.unverified_transactions,
            'previous_hash': previous_hash or self.hash(self.chain[-1])
        }
        self.verified_transactions += self.unverified_transactions

        print(self.verified_transactions)

        self.unverified_transactions = []

        #appending the block at the end of Blockchain

        self.chain.append(block)

        return block


    #adding a new transaction in the next block
    def new_transaction(self, buyer_name, seller_name, property_name,amount):
        self.unverified_transactions.append({
            'Buyer name': buyer_name,
            'Seller name': seller_name,
            'Property name': property_name,
            'Amount' : amount,
            'timestamp': datetime.now().strftime('%Y-%m-%d %H:%M:%S')
        })
        return self.last_block['index'] + 1


    @property
    def last_block(self):

        return self.chain[-1]


    # Static method for creating a SHA-256 Hash of a given block

    @staticmethod
    def hash(block):       
        block_string = json.dumps(block, sort_keys = True).encode()
        hash_val = hashlib.sha256(block_string).hexdigest()
        return hash_val


    #Method for adding a node using its IP address to our blockchain network. 

    def add_node(self, address, stake):
        parsed_url = urlparse(address)
        authority = stake
        self.nodes.add((parsed_url.netloc,authority))


    # Method for simulating the voting process

    def add_vote(self):
        self.all_nodes = list(self.nodes)

        for x in self.all_nodes:
            y=list(x)
            y.append(x[1] * randint(0,100))
            self.voteNodespool.append(y)

        print(self.voteNodespool)
    

    # Method for selecting top three nodes based on results produced by voting

    def selection(self):
        self.starNodespool = sorted(self.voteNodespool, key = lambda vote: vote[2],reverse = True)
        print(self.starNodespool)

        for x in range(3):
            self.superNodespool.append(self.starNodespool[x])
        print(self.superNodespool)

        for y in self.superNodespool:
            self.delegates.append(y[0])
        print(self.delegates)


    #syncing the list

    def sync(self):
        r = requests.get('http://localhost:6000/delegates/show')
        print(r)

        if(r.status_code == 200):
            delegates = r.json()['node_delegates']
            self.delegates = delegates[0:3]
            print(self.delegates)


    # checking if the chain is validated.

    def valid_chain(self, chain):
        last_block = chain[0]

        current_index = 1

        while current_index < len(chain):
            block = chain[current_index]

            #If the hash value of the current block is not correct then return false

            if block['previous_hash'] != self.hash(last_block):

                return False
            
            last_block = block

            current_index += 1

        return True
    

    #Method for replacing the blockchain with the longest validated chain.

    def resolve_chain(self):
        neighbours = self.nodes
        new_chain = None
        max_length = len(self.chain)

        for node in neighbours: 

            response = requests.get(f'http://{node}/chain')

        
            if response.status_code == 200:
                length = response.json()['length']
                chain = response.json()['chain']

        
                if length > max_length and self.valid_chain(chain):
                    max_length = length
                    new_chain = chain

        
        if new_chain:
            self.chain = new_chain
            return True

        return False    
   
