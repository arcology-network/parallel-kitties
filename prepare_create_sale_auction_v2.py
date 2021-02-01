import sys
sys.path.append('../../..')

from ammolite import (Cli, HTTPProvider, Account)
from utils import compile_contracts
from pymongo import MongoClient

frontend = sys.argv[1]
kitty_core_address = sys.argv[2]
num_ktxs = int(sys.argv[3])
output = sys.argv[4]
#database = sys.argv[5]
input = sys.argv[5]

cli = Cli(HTTPProvider(frontend))
compiled_sol = compile_contracts('./contract')
kitty_core = compiled_sol['./contract/KittyCore.sol:KittyCore']
kitty_core_contract = cli.eth.contract(
    abi = kitty_core['abi'],
    address = kitty_core_address,
)

all_users = []
with open(input, 'r') as f:
    for line in f:
        line = line.rstrip('\n')
        segments = line.split(',')
        u = {
            'private_key': segments[0],
            'address': segments[1],
            'kitty': segments[2],
        }
        all_users.append(u)

#mongo = MongoClient('localhost', 32768)
#db = mongo[database]

num_per_batch = 1000
lines = []

def make_one_batch(i):
    users = all_users[i * 1000 : (i+1) * 1000]
    #idsToRemove = []
    #ret_set = db.candidates.aggregate([{'$sample': {'size': num_per_batch}}])
    #for i in ret_set:
    #    users.append(i)
    #    idsToRemove.append(i['_id'])

    #if len(users) < num_per_batch:
    #    assert False
    #db.candidates.remove({'_id': {'$in': idsToRemove}})

    with open(output, 'a') as f:
        for i in range(num_per_batch):
            acc = Account(users[i]['private_key'])
            raw_tx, tx_hash = acc.sign(kitty_core_contract.functions.createSaleAuction(
                users[i]['kitty'],
                int(1e15),
                0,
                86400,
            ).buildTransaction({
                'gas': 100000000,
                'gasPrice': 1,
            }))
            lines.append('{},{}\n'.format(raw_tx.hex(), tx_hash.hex()))

for i in range(num_ktxs):
    make_one_batch(i)

with open(output, 'w') as f:
    for l in lines:
        f.write(l)

