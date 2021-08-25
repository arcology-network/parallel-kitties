import sys
sys.path.append('../../..')

from ammolite import (Cli, HTTPProvider, Account)
from utils import compile_contracts
from pymongo import MongoClient

frontend = sys.argv[1]
kitty_core_address = sys.argv[2]
num_ktxs = int(sys.argv[3])
output = sys.argv[4]
input = sys.argv[5]

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

cli = Cli(HTTPProvider(frontend))
compiled_sol = compile_contracts('./contract')
kitty_core = compiled_sol['./contract/KittyCore.sol:KittyCore']
kitty_core_contract = cli.eth.contract(
    abi = kitty_core['abi'],
    address = kitty_core_address,
)

num_per_batch = 1000
lines = []

def make_one_batch(i):
    users = all_users[i * 2000 : (i+1) * 2000]

    for i in range(num_per_batch):
        acc = Account(users[i]['private_key'])
        raw_tx, tx_hash = acc.sign(kitty_core_contract.functions.transfer(
            users[num_per_batch + i]['address'],
            users[i]['kitty'],
        ).buildTransaction({
            'value': 0,
            'gas': 100000000,
            'gasPrice': 1,
        }))
        lines.append('{},{}\n'.format(raw_tx.hex(), tx_hash.hex()))

for i in range(num_ktxs):
    make_one_batch(i)

with open(output, 'w') as f:
    for l in lines:
        f.write(l)
