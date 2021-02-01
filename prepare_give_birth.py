import sys
sys.path.append('../../..')

from ammolite import (Cli, HTTPProvider, Account)
from utils import (wait_for_receipts, compile_contracts)
from pymongo import MongoClient

frontend = sys.argv[1]
kitty_core_address = sys.argv[2]
miner_private_key = sys.argv[3]
num_ktxs = int(sys.argv[4])
output = sys.argv[5]

cli = Cli(HTTPProvider(frontend))
compiled_sol = compile_contracts('./contract')
kitty_core = compiled_sol['./contract/KittyCore.sol:KittyCore']
kitty_core_contract = cli.eth.contract(
    abi = kitty_core['abi'],
    address = kitty_core_address,
)

mongo = MongoClient('localhost', 32768)
db = mongo['parallelkitties']

num_per_batch = 1000

def make_one_batch():
    users = []
    idsToRemove = []
    ret_set = db.candidates.aggregate([{'$sample': {'size': num_per_batch * 2}}])
    for i in ret_set:
        users.append(i)
        idsToRemove.append(i['_id'])

    if len(users) < num_per_batch * 2:
        assert False
    db.candidates.remove({'_id': {'$in': idsToRemove}})

    txs = {}
    hashes = []
    for i in range(num_per_batch):
        acc = Account(users[i]['private_key'])
        raw_tx, tx_hash = acc.sign(kitty_core_contract.functions.approveSiring(
            users[i + num_per_batch]['address'],
            users[i]['kitty'],
        ).buildTransaction({
            'value': 0,
            'gas': 100000000,
            'gasPrice': 1,
        }))
        txs[tx_hash] = raw_tx
        hashes.append(tx_hash)

    cli.sendTransactions(txs)
    receipts = wait_for_receipts(cli, hashes)

    txs = {}
    hashes2 = []
    for i in range(num_per_batch):
        receipt = receipts[hashes[i]]
        if receipt['status'] != 1:
            assert False
        
        acc = Account(users[i + num_per_batch]['private_key'])
        raw_tx, tx_hash = acc.sign(kitty_core_contract.functions.breedWithAuto(
            users[i + num_per_batch]['kitty'],
            users[i]['kitty'],
        ).buildTransaction({
            'value': int(1e15),
            'gas': 100000000,
            'gasPrice': 1,
        }))
        txs[tx_hash] = raw_tx
        hashes2.append(tx_hash)

    cli.sendTransactions(txs)
    receipts = wait_for_receipts(cli, hashes2)
    miner = Account(miner_private_key)
    with open(output, 'a') as f:
        for i in range(num_per_batch):
            receipt = receipts[hashes2[i]]
            if receipt['status'] != 1:
                assert False

            raw_tx, tx_hash = miner.sign(kitty_core_contract.functions.giveBirth(users[i + num_per_batch]['kitty']).buildTransaction({
                'value': 0,
                'gas': 100000000,
                'gasPrice': 1,
            }))
            f.write('{},{}\n'.format(raw_tx.hex(), tx_hash.hex()))

for i in range(num_ktxs):
    make_one_batch()
