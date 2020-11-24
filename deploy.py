import sys
sys.path.append('../../..')

import time, yaml
from ammolite import (Cli, HTTPProvider, Account)
from utils import (wait_for_receipts, compile_contracts, check_receipts)

compiled_sol = compile_contracts('./contract')

sale_auction = compiled_sol['./contract/Auction/SaleClockAuction.sol:SaleClockAuction']
siring_auction = compiled_sol['./contract/Auction/SiringClockAuction.sol:SiringClockAuction']
gene_science = compiled_sol['./contract/GeneScience.sol:GeneScience']
kitty_core = compiled_sol['./contract/KittyCore.sol:KittyCore']

print(gene_science['abi'])

config_file = sys.argv[1]
# ceo_private_key = sys.argv[2]
# coo_private_key = sys.argv[3]
# cfo_private_key = sys.argv[4]
account_file = sys.argv[2]

with open(config_file, 'r') as f:
    config = yaml.full_load(f)
    frontend = config['frontend']
    print(config)

private_keys = []
with open(account_file, 'r') as f:
    for line in f:
        segments = line.split(',')
        private_keys.append(segments[0])

ceo_private_key = private_keys[0]
coo_private_key = private_keys[1]
cfo_private_key = private_keys[2]
kitty_miner_key = private_keys[3]

def write_private_keys(private_keys, file):
    with open(file, 'w') as f:
        for key in private_keys:
            f.write(key + '\n')

sale_auction_keys = 'acc1.txt'
siring_auction_creator_keys = 'acc2.txt'
siring_auction_bidder_keys = 'acc3.txt'
kitty_raiser_keys = 'acc4.txt'
kitty_exchanger_keys = 'acc5.txt'

def get_keys_by_weights(keys, weights, name):
    sum = 0
    start = 0
    end = 0
    for n, w in weights.items():
        if n == name:
            start = sum
        sum += w
        if n == name:
            end = sum
    
    return keys[int(len(keys)*start/sum) : int(len(keys)*end/sum)]

print(get_keys_by_weights(private_keys, config['test_case_weights'], 'sale_auction'))
print(get_keys_by_weights(private_keys, config['test_case_weights'], 'siring_auction_creator'))
print(get_keys_by_weights(private_keys, config['test_case_weights'], 'siring_auction_bidder'))
print(get_keys_by_weights(private_keys, config['test_case_weights'], 'kitty_raiser'))
print(get_keys_by_weights(private_keys, config['test_case_weights'], 'kitties_exchanger'))

write_private_keys(get_keys_by_weights(private_keys, config['test_case_weights'], 'sale_auction'), sale_auction_keys)
write_private_keys(get_keys_by_weights(private_keys, config['test_case_weights'], 'siring_auction_creator'), siring_auction_creator_keys)
write_private_keys(get_keys_by_weights(private_keys, config['test_case_weights'], 'siring_auction_bidder'), siring_auction_bidder_keys)
write_private_keys(get_keys_by_weights(private_keys, config['test_case_weights'], 'kitty_raiser'), kitty_raiser_keys)
write_private_keys(get_keys_by_weights(private_keys, config['test_case_weights'], 'kitties_exchanger'), kitty_exchanger_keys)

cli = Cli(HTTPProvider(frontend))
kitty_core_contract = cli.eth.contract(
    abi = kitty_core['abi'],
    bytecode = kitty_core['bin']
)

# 1. Deploy KittyCore.
ceo = Account(ceo_private_key)
coo = Account(coo_private_key)
cfo = Account(cfo_private_key)

raw_tx, tx_hash = ceo.sign(kitty_core_contract.constructor().buildTransaction({
    'nonce': 0,
    'gas': 100000000,
    'gasPrice': 1,
}))

cli.sendTransactions({tx_hash: raw_tx})
receipts = wait_for_receipts(cli, [tx_hash])
check_receipts(receipts)
kitty_core_address = receipts[tx_hash]['contractAddress']
kitty_core_contract.setAddress(kitty_core_address)

# 2. Deploy SaleClockAuction, SiringAuction and GeneScience.
sale_auction_contract = cli.eth.contract(
    abi = sale_auction['abi'],
    bytecode = sale_auction['bin']
)
raw_tx1, tx_hash1 = ceo.sign(sale_auction_contract.constructor(kitty_core_address, 100).buildTransaction({
    'nonce': 1,
    'gas': 100000000,
    'gasPrice': 1,
}))
siring_auction_contract = cli.eth.contract(
    abi = siring_auction['abi'],
    bytecode = siring_auction['bin']
)
raw_tx2, tx_hash2 = ceo.sign(siring_auction_contract.constructor(kitty_core_address, 100).buildTransaction({
    'nonce': 2,
    'gas': 100000000,
    'gasPrice': 1,
}))
gene_science_contract = cli.eth.contract(
    abi = gene_science['abi'],
    bytecode = gene_science['bin']
)
raw_tx3, tx_hash3 = ceo.sign(gene_science_contract.constructor('', kitty_core_address).buildTransaction({
    'nonce': 3,
    'gas': 100000000,
    'gasPrice': 1,
}))

cli.sendTransactions({tx_hash1: raw_tx1, tx_hash2: raw_tx2, tx_hash3: raw_tx3})
receipts = wait_for_receipts(cli, [tx_hash1, tx_hash2, tx_hash3])
check_receipts(receipts)
sale_auction_address = receipts[tx_hash1]['contractAddress']
siring_auction_address = receipts[tx_hash2]['contractAddress']
gene_science_address = receipts[tx_hash3]['contractAddress']

time.sleep(1)

# 3. Setup KittyCore.
raw_tx1, tx_hash1 = ceo.sign(kitty_core_contract.functions.setSaleAuctionAddress(sale_auction_address).buildTransaction({
    'nonce': 4,
    'gas': 100000000,
    'gasPrice': 1,
}))
raw_tx2, tx_hash2 = ceo.sign(kitty_core_contract.functions.setSiringAuctionAddress(siring_auction_address).buildTransaction({
    'nonce': 5,
    'gas': 100000000,
    'gasPrice': 1,
}))
raw_tx3, tx_hash3 = ceo.sign(kitty_core_contract.functions.setGeneScienceAddress(gene_science_address).buildTransaction({
    'nonce': 6,
    'gas': 100000000,
    'gasPrice': 1,
}))
raw_tx4, tx_hash4 = ceo.sign(kitty_core_contract.functions.setCOO(coo.address()).buildTransaction({
    'nonce': 7,
    'gas': 100000000,
    'gasPrice': 1,
}))
raw_tx5, tx_hash5 = ceo.sign(kitty_core_contract.functions.setCFO(cfo.address()).buildTransaction({
    'nonce': 8,
    'gas': 100000000,
    'gasPrice': 1,
}))

cli.sendTransactions({tx_hash1: raw_tx1, tx_hash2: raw_tx2, tx_hash3: raw_tx3, tx_hash4: raw_tx4, tx_hash5: raw_tx5})
check_receipts(wait_for_receipts(cli, [tx_hash1, tx_hash2, tx_hash3, tx_hash4, tx_hash5]))

# 4. Start service.
raw_tx, tx_hash = ceo.sign(kitty_core_contract.functions.unpause().buildTransaction({
    'nonce': 9,
    'gas': 100000000,
    'gasPrice': 1,
}))
cli.sendTransactions({tx_hash: raw_tx})
check_receipts(wait_for_receipts(cli, [tx_hash]))

print('Deploy ParallelKitties complete.')
print('python3 init_gen0.py {} {} {} {} {}'.format(frontend, config['gen0_count'], kitty_core_address, sale_auction_address, coo_private_key))
print('python3 kitty_miner.py {} {} {}'.format(frontend, kitty_core_address, kitty_miner_key))
print('python3 sale_auction_creator_and_bidder.py {} {} {} {}'.format(frontend, kitty_core_address, sale_auction_address, sale_auction_keys))
print('python3 siring_auction_creator.py {} {} {} {} {}'.format(frontend, kitty_core_address, sale_auction_address, siring_auction_address, siring_auction_creator_keys))
print('python3 siring_auction_bidder.py {} {} {} {} {}'.format(frontend, kitty_core_address, sale_auction_address, siring_auction_address, siring_auction_bidder_keys))
print('python3 kitty_raiser.py {} {} {} {}'.format(frontend, kitty_core_address, sale_auction_address, kitty_raiser_keys))
print('python3 kitties_exchanger.py {} {} {} {}'.format(frontend, kitty_core_address, sale_auction_address, kitty_exchanger_keys))
