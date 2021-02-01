import sys
sys.path.append('../../..')

import time
from ammolite import (Cli, HTTPProvider, Account)
from utils import (wait_for_receipts, compile_contracts)
from pymongo import MongoClient

frontend = sys.argv[1]
kitty_count = int(sys.argv[2])
kitty_core_address = sys.argv[3]
sale_auction_address = sys.argv[4]
coo_private_key = sys.argv[5]

cli = Cli(HTTPProvider(frontend))
compiled_sol = compile_contracts('./contract')
kitty_core = compiled_sol['./contract/KittyCore.sol:KittyCore']
kitty_core_contract = cli.eth.contract(
    abi = kitty_core['abi'],
    address = kitty_core_address
)

sale_auction = compiled_sol['./contract/Auction/SaleClockAuction.sol:SaleClockAuction']
sale_auction_contract = cli.eth.contract(
    abi = sale_auction['abi'],
    address = sale_auction_address
)

# print(kitty_core['abi'])
mongo = MongoClient('localhost', 32768)
db = mongo['parallelkitties']

hashes = []
coo = Account(coo_private_key)
for i in range(10):
    txs = {}
    for j in range(kitty_count):
        raw_tx, tx_hash = coo.sign(kitty_core_contract.functions.createGen0Auction(j+i*kitty_count).buildTransaction({
            'nonce': 100+j+i*kitty_count,
            'gas': 1000000,
            'gasPrice': 1,
        }))
        txs[tx_hash] = raw_tx
        hashes.append(tx_hash)

    cli.sendTransactions(txs)
    time.sleep(30)
    print(i)

#print(txs.keys())
for i in range(10):
    print(i)
    l = hashes[i*kitty_count:(i+1)*kitty_count]
    auctions = []
    kitties = []
    receipts = wait_for_receipts(cli, l)
    for receipt in receipts.values():
        #print(receipt)
        processed_receipt = sale_auction_contract.processReceipt(receipt)
        # print(processed_receipt)
        if 'AuctionCreated' in processed_receipt:
            newAuction = {
                'id': processed_receipt['AuctionCreated']['tokenId'],
                'startingPrice': int(processed_receipt['AuctionCreated']['startingPrice'], 16),
                'endingPrice': int(processed_receipt['AuctionCreated']['endingPrice'], 16),
                'duration': int(processed_receipt['AuctionCreated']['duration'], 16),
            }
            auctions.append(newAuction)

        processed_receipt = kitty_core_contract.processReceipt(receipt)
        if 'Birth' in processed_receipt:
            newKitty = {
                'id': processed_receipt['Birth']['kittyId'],
                'matronId': processed_receipt['Birth']['matronId'],
                'sireId': processed_receipt['Birth']['sireId'],
                'genes': processed_receipt['Birth']['genes'],
            }
            kitties.append(newKitty)
    
        if receipt['status'] != 1:
            assert False

    #print(auctions)
    db.saleauctions.insert_many(auctions)
    db.kitties.insert_many(kitties)
