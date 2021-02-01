import sys
sys.path.append('../../..')

import time, os
from solcx import compile_files
from ammolite import (Cli, HTTPProvider, Account)

sources = []
for root, _, files in os.walk('./contract'):
    for file in files:
        if file.endswith('.sol'):
            sources.append(os.path.join(root, file))

cli = Cli(HTTPProvider('http://192.168.1.111:8080'))
compiled_sol = compile_files(sources, output_values = ['abi', 'bin'])
kitty_core = compiled_sol['./contract/KittyCore.sol:KittyCore']
kitty_core_contract = cli.eth.contract(
    abi = kitty_core['abi'],
    address = 'b1e0e9e68297aae01347f6ce0ff21d5f72d3fa0f',
)

coo_private_key = '2289ae919f03075448d567c9c4a22846ce3711731c895f1bea572cef25bb346f'
user_private_key = 'd9815a0fa4f31172530f17a6ae64bf5f00a3a651f3d6476146d2c62ae5527dc4'

coo = Account(coo_private_key)
user1 = Account(user_private_key)
user2_address = '230DCCC4660dcBeCb8A6AEA1C713eE7A04B35cAD'

raw_tx, tx_hash = coo.sign(kitty_core_contract.functions.createPromoKitty(
        0, 
        user1.address()
    ).buildTransaction({
        'gas': 1000000,
        'gasPrice': 1,
    }))
cli.sendTransactions({tx_hash: raw_tx})

receipts = []
while True:
    receipts = cli.getTransactionReceipts([tx_hash])
    if receipts is None or len(receipts) != 1:
        time.sleep(1)
        continue
    break
events = kitty_core_contract.processReceipt(receipts[0])
new_kitty = events['Birth']['kittyId']
print(f'New kitty {new_kitty} born and assigned to {events["Birth"]["owner"][24:]}')

raw_tx, tx_hash = user1.sign(kitty_core_contract.functions.transfer(
    user2_address,
    new_kitty
).buildTransaction({
    'gas': 1000000,
    'gasPrice': 1,
}))
cli.sendTransactions({tx_hash: raw_tx})

while True:
    receipts = cli.getTransactionReceipts([tx_hash])
    if receipts is None or len(receipts) != 1:
        time.sleep(1)
        continue
    break
events = kitty_core_contract.processReceipt(receipts[0])
print(f'Kitty {events["Transfer"]["tokenId"]} transfered from {events["Transfer"]["from"][24:]} to {events["Transfer"]["to"][24:]}')
