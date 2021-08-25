import sys
sys.path.append('../../..')

import time, yaml
from rich.console import Console
from ammolite import (Cli, HTTPProvider, Account)
from utils import (wait_for_receipts, compile_contracts, check_receipts)

compiled_sol = compile_contracts('./contract')

sale_auction = compiled_sol['./contract/Auction/SaleClockAuction.sol:SaleClockAuction']
siring_auction = compiled_sol['./contract/Auction/SiringClockAuction.sol:SiringClockAuction']
gene_science = compiled_sol['./contract/GeneScience.sol:GeneScience']
kitty_core = compiled_sol['./contract/KittyCore.sol:KittyCore']

#print(gene_science['abi'])

frontend = sys.argv[1]
account_file = sys.argv[2]

private_keys = []
addresses = []
with open(account_file, 'r') as f:
    for line in f:
        line = line.rstrip('\n')
        segments = line.split(',')
        private_keys.append(segments[0])
        addresses.append(segments[1])

ceo_private_key = private_keys[0]
coo_private_key = private_keys[1]
cfo_private_key = private_keys[2]
kitty_miner_key = private_keys[3]

def write_private_keys(private_keys, addresses, file):
    with open(file, 'w') as f:
        for i in range(len(private_keys)):
            f.write(private_keys[i] + ',' + addresses[i] + '\n')

sale_auction_keys = 'acc1.txt'
siring_auction_creator_keys = 'acc2.txt'
siring_auction_bidder_keys = 'acc3.txt'
kitty_raiser_keys = 'acc4.txt'
kitty_exchanger_keys = 'acc5.txt'

def get_keys_by_weights(keys, addresses, weights, name):
    sum = 0
    start = 0
    end = 0
    for n, w in weights.items():
        if n == name:
            start = sum
        sum += w
        if n == name:
            end = sum
    
    return keys[int(len(keys)*start/sum) : int(len(keys)*end/sum)], addresses[int(len(keys)*start/sum) : int(len(keys)*end/sum)]

#print(get_keys_by_weights(private_keys, config['test_case_weights'], 'sale_auction'))
#print(get_keys_by_weights(private_keys, config['test_case_weights'], 'siring_auction_creator'))
#print(get_keys_by_weights(private_keys, config['test_case_weights'], 'siring_auction_bidder'))
#print(get_keys_by_weights(private_keys, config['test_case_weights'], 'kitty_raiser'))
#print(get_keys_by_weights(private_keys, config['test_case_weights'], 'kitties_exchanger'))

#k, a = get_keys_by_weights(private_keys, addresses, config['test_case_weights'], 'sale_auction')
#write_private_keys(k, a, sale_auction_keys)
#k, a = get_keys_by_weights(private_keys, addresses, config['test_case_weights'], 'siring_auction_creator')
#write_private_keys(k, a, siring_auction_creator_keys)
#k, a = get_keys_by_weights(private_keys, addresses, config['test_case_weights'], 'siring_auction_bidder')
#write_private_keys(k, a, siring_auction_bidder_keys)
#k, a = get_keys_by_weights(private_keys, addresses, config['test_case_weights'], 'kitty_raiser')
#write_private_keys(k, a, kitty_raiser_keys)
#k, a = get_keys_by_weights(private_keys, addresses, config['test_case_weights'], 'kitties_exchanger')
#write_private_keys(k, a, kitty_exchanger_keys)

console = Console()

cli = Cli(HTTPProvider(frontend))
kitty_core_contract = cli.eth.contract(
    abi = kitty_core['abi'],
    bytecode = kitty_core['bin']
)

# 1. Deploy KittyCore.
ceo = Account(ceo_private_key)
coo = Account(coo_private_key)
cfo = Account(cfo_private_key)

with console.status("[bold green]Working on tasks...") as status:
    raw_tx, tx_hash = ceo.sign(kitty_core_contract.constructor().buildTransaction({
        'nonce': 1,
        'gas': 10000000000,
        'gasPrice': 1,
    }))

    cli.sendTransactions({tx_hash: raw_tx})
    receipts = wait_for_receipts(cli, [tx_hash])
    check_receipts(receipts)
    kitty_core_address = receipts[tx_hash]['contractAddress']
    kitty_core_contract.setAddress(kitty_core_address)
    console.log("Deploy KittyCore complete")

    # 2. Deploy SaleClockAuction, SiringAuction and GeneScience.
    sale_auction_contract = cli.eth.contract(
        abi = sale_auction['abi'],
        bytecode = sale_auction['bin']
    )
    raw_tx1, tx_hash1 = ceo.sign(sale_auction_contract.constructor(kitty_core_address, 100).buildTransaction({
        'nonce': 2,
        'gas': 10000000000,
        'gasPrice': 1,
    }))
    siring_auction_contract = cli.eth.contract(
        abi = siring_auction['abi'],
        bytecode = siring_auction['bin']
    )
    raw_tx2, tx_hash2 = ceo.sign(siring_auction_contract.constructor(kitty_core_address, 100).buildTransaction({
        'nonce': 3,
        'gas': 10000000000,
        'gasPrice': 1,
    }))
    gene_science_contract = cli.eth.contract(
        abi = gene_science['abi'],
        bytecode = gene_science['bin']
    )
    raw_tx3, tx_hash3 = ceo.sign(gene_science_contract.constructor('', kitty_core_address).buildTransaction({
        'nonce': 4,
        'gas': 10000000000,
        'gasPrice': 1,
    }))

    cli.sendTransactions({tx_hash1: raw_tx1})
    receipts = wait_for_receipts(cli, [tx_hash1])
    check_receipts(receipts)
    sale_auction_address = receipts[tx_hash1]['contractAddress']
    console.log("Deploy SaleClockAuction complete")

    cli.sendTransactions({tx_hash2: raw_tx2})
    receipts = wait_for_receipts(cli, [tx_hash2])
    check_receipts(receipts)
    siring_auction_address = receipts[tx_hash2]['contractAddress']
    console.log("Deploy SiringClockAuction complete")

    cli.sendTransactions({tx_hash3: raw_tx3})
    receipts = wait_for_receipts(cli, [tx_hash3])
    check_receipts(receipts)
    gene_science_address = receipts[tx_hash3]['contractAddress']
    console.log("Deploy GeneScience complete")

    time.sleep(1)

    # 3. Setup KittyCore.
    raw_tx1, tx_hash1 = ceo.sign(kitty_core_contract.functions.setSaleAuctionAddress(sale_auction_address).buildTransaction({
        'nonce': 5,
        'gas': 100000000,
        'gasPrice': 1,
    }))
    raw_tx2, tx_hash2 = ceo.sign(kitty_core_contract.functions.setSiringAuctionAddress(siring_auction_address).buildTransaction({
        'nonce': 6,
        'gas': 100000000,
        'gasPrice': 1,
    }))
    raw_tx3, tx_hash3 = ceo.sign(kitty_core_contract.functions.setGeneScienceAddress(gene_science_address).buildTransaction({
        'nonce': 7,
        'gas': 100000000,
        'gasPrice': 1,
    }))
    raw_tx4, tx_hash4 = ceo.sign(kitty_core_contract.functions.setCOO(coo.address()).buildTransaction({
        'nonce': 8,
        'gas': 100000000,
        'gasPrice': 1,
    }))
    raw_tx5, tx_hash5 = ceo.sign(kitty_core_contract.functions.setCFO(cfo.address()).buildTransaction({
        'nonce': 9,
        'gas': 100000000,
        'gasPrice': 1,
    }))

    cli.sendTransactions({tx_hash1: raw_tx1, tx_hash2: raw_tx2, tx_hash3: raw_tx3, tx_hash4: raw_tx4, tx_hash5: raw_tx5})
    check_receipts(wait_for_receipts(cli, [tx_hash1, tx_hash2, tx_hash3, tx_hash4, tx_hash5]))
    console.log("Setup runtime parameters of KittyCore complete")

    # 4. Start service.
    raw_tx, tx_hash = ceo.sign(kitty_core_contract.functions.unpause().buildTransaction({
        'nonce': 9,
        'gas': 100000000,
        'gasPrice': 1,
    }))
    cli.sendTransactions({tx_hash: raw_tx})
    check_receipts(wait_for_receipts(cli, [tx_hash]))
    console.log("Start ParallelKitties service complete.")

#print('Deploy ParallelKitties complete.')
#print('python distribute_kitties_v2.py {} {} {} {} {} {}'.format(frontend, 'acc1.txt', kitty_core_address, coo_private_key, 'output/dist1.out', 'output/kitties1.out'))
#print('python distribute_kitties_v2.py {} {} {} {} {} {}'.format(frontend, 'acc2.txt', kitty_core_address, coo_private_key, 'output/dist2.out', 'output/kitties2.out'))
#print('python distribute_kitties_v2.py {} {} {} {} {} {}'.format(frontend, 'acc3.txt', kitty_core_address, coo_private_key, 'output/dist3.out', 'output/kitties3.out'))
#print('python distribute_kitties_v2.py {} {} {} {} {} {}'.format(frontend, 'acc4.txt', kitty_core_address, coo_private_key, 'output/dist4.out', 'output/kitties4.out'))
#print('python distribute_kitties_v2.py {} {} {} {} {} {}'.format(frontend, 'acc5.txt', kitty_core_address, coo_private_key, 'output/dist5.out', 'output/kitties5.out'))
#print('python prepare_transfer.py {} {} {} {}'.format(frontend, kitty_core_address, int(len(private_keys)/1000), 'output/transfer.out'))
#print('python prepare_breed_with.py {} {} {} {}'.format(frontend, kitty_core_address, int(len(private_keys)/2000), 'output/breed.out'))
#print('python prepare_create_sale_auction_v2.py {} {} {} {} {}'.format(frontend, kitty_core_address, int(len(private_keys)/1000/5), 'output/create_sale1.out', 'output/kitties1.out'))
#print('python prepare_create_sale_auction_v2.py {} {} {} {} {}'.format(frontend, kitty_core_address, int(len(private_keys)/1000/5), 'output/create_sale2.out', 'output/kitties2.out'))
#print('python prepare_create_sale_auction_v2.py {} {} {} {} {}'.format(frontend, kitty_core_address, int(len(private_keys)/1000/5), 'output/create_sale3.out', 'output/kitties3.out'))
#print('python prepare_create_sale_auction_v2.py {} {} {} {} {}'.format(frontend, kitty_core_address, int(len(private_keys)/1000/5), 'output/create_sale4.out', 'output/kitties4.out'))
#print('python prepare_create_sale_auction_v2.py {} {} {} {} {}'.format(frontend, kitty_core_address, int(len(private_keys)/1000/5), 'output/create_sale5.out', 'output/kitties5.out'))
#print('python prepare_create_siring_auction.py {} {} {} {}'.format(frontend, kitty_core_address, int(len(private_keys)/1000), 'output/create_siring.out'))
#print('python prepare_bid_on_sale_auction.py {} {} {} {} {}'.format(frontend, kitty_core_address, sale_auction_address, int(len(private_keys)/2000), 'output/bid_sale.out'))
#print('python prepare_bid_on_siring_auction.py {} {} {} {} {}'.format(frontend, kitty_core_address, siring_auction_address, int(len(private_keys)/2000), 'output/bid_siring.out'))
#print('python prepare_give_birth.py {} {} {} {} {}'.format(frontend, kitty_core_address, kitty_miner_key, int(len(private_keys)/2000), 'output/give_birth.out'))
#print('python sendtxs.py {} {}'.format(frontend, 'output/*.out'))
#print('python block_mon.py {}'.format(frontend))
#print('python init_gen0.py {} {} {} {} {}'.format(frontend, config['gen0_count'], kitty_core_address, sale_auction_address, coo_private_key))
#print('python kitty_miner.py {} {} {}'.format(frontend, kitty_core_address, kitty_miner_key))
#print('python sale_auction_creator_and_bidder.py {} {} {} {}'.format(frontend, kitty_core_address, sale_auction_address, sale_auction_keys))
#print('python siring_auction_creator.py {} {} {} {} {}'.format(frontend, kitty_core_address, sale_auction_address, siring_auction_address, siring_auction_creator_keys))
#print('python siring_auction_bidder.py {} {} {} {} {}'.format(frontend, kitty_core_address, sale_auction_address, siring_auction_address, siring_auction_bidder_keys))
#print('python kitty_raiser.py {} {} {} {}'.format(frontend, kitty_core_address, sale_auction_address, kitty_raiser_keys))
#print('python kitties_exchanger.py {} {} {} {}'.format(frontend, kitty_core_address, sale_auction_address, kitty_exchanger_keys))
