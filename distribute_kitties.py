import sys
sys.path.append('../../..')

import math
from ammolite import (Cli, HTTPProvider, Account)
from utils import (wait_for_receipts, compile_contracts)
from pymongo import MongoClient

frontend = sys.argv[1]
accounts_file = sys.argv[2]
kitty_core_address = sys.argv[3]
coo_private_key = sys.argv[4]
database = sys.argv[5]

private_keys = []
addresses = []
with open(accounts_file, 'r') as f:
    for line in f:
        line = line.rstrip('\n')
        segments = line.split(',')
        private_keys.append(segments[0])
        addresses.append(segments[1])

cli = Cli(HTTPProvider(frontend))
compiled_sol = compile_contracts('./contract')
kitty_core = compiled_sol['./contract/KittyCore.sol:KittyCore']
kitty_core_contract = cli.eth.contract(
    abi = kitty_core['abi'],
    address = kitty_core_address,
)

mongo = MongoClient('localhost', 32768)
db = mongo[database]

coo = Account(coo_private_key)
num_batches = int(math.ceil(len(private_keys)) / 1000)
for i in range(num_batches):
    batch_start = i * 1000
    batch_end = (i + 1) * 1000
    if i == num_batches - 1:
        batch_end = len(private_keys)
    print('batch_start = {}, batch_end = {}'.format(batch_start, batch_end))

    txs = {}
    hashes = []
    for j in range(batch_start, batch_end):
        raw_tx, tx_hash = coo.sign(kitty_core_contract.functions.createPromoKitty(j, addresses[j]).buildTransaction({
            'nonce': j,
            'gas': 1000000,
            'gasPrice': 1,
        }))
        txs[tx_hash] = raw_tx
        hashes.append(tx_hash)
    
    cli.sendTransactions(txs)
    candidates = []
    receipts = wait_for_receipts(cli, hashes)
    for j in range(len(hashes)):
        receipt = receipts[hashes[j]]
        if receipt['status'] != 1:
            assert False
        
        processed_receipt = kitty_core_contract.processReceipt(receipt)
        if 'Birth' not in processed_receipt:
            assert False
        
        candidates.append({
            'private_key': private_keys[batch_start + j],
            'address': addresses[batch_start + j],
            'kitty': processed_receipt['Birth']['kittyId'],
        })
    db.candidates.insert_many(candidates)
