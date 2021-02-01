import sys
sys.path.append('../../..')

from ammolite import (Cli, HTTPProvider, Account)
from utils import (wait_for_receipts, compile_contracts)

frontend = sys.argv[1]
kitty_core_address = sys.argv[2]
num_ktxs = int(sys.argv[3])
output1 = sys.argv[4]
output2 = sys.argv[5]
input = sys.argv[6]

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

num_per_batch = 1000
lines1 = []
lines2 = []

def make_one_batch(i):
    users = all_users[i * 2000 : (i+1) * 2000]

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
        lines1.append('{},{}\n'.format(raw_tx.hex(), tx_hash.hex()))

    for i in range(num_per_batch):
        acc = Account(users[i + num_per_batch]['private_key'])
        raw_tx, tx_hash = acc.sign(kitty_core_contract.functions.breedWithAuto(
            users[i + num_per_batch]['kitty'],
            users[i]['kitty'],
        ).buildTransaction({
            'value': int(1e15),
            'gas': 100000000,
            'gasPrice': 1,
        }))
        lines2.append('{},{}\n'.format(raw_tx.hex(), tx_hash.hex()))

for i in range(num_ktxs):
    make_one_batch(i)

with open(output1, 'w') as f:
    for l in lines1:
        f.write(l)

with open(output2, 'w') as f:
    for l in lines2:
        f.write(l)
