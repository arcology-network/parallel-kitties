import sys
sys.path.append('../../..')

import time
from ammolite import (Cli, HTTPProvider, Account)
from utils import (wait_for_receipts, compile_contracts, init_accounts)
from pymongo import MongoClient

frontend = sys.argv[1]
kitty_core_address = sys.argv[2]
sale_auction_address = sys.argv[3]
siring_auction_address = sys.argv[4]
private_key = sys.argv[5]

cli = Cli(HTTPProvider(frontend))
compiled_sol = compile_contracts('./contract')
kitty_core = compiled_sol['./contract/KittyCore.sol:KittyCore']
kitty_core_contract = cli.eth.contract(
    abi = kitty_core['abi'],
    address = kitty_core_address,
)

sale_auction = compiled_sol['./contract/Auction/SaleClockAuction.sol:SaleClockAuction']
sale_auction_contract = cli.eth.contract(
    abi = sale_auction['abi'],
    address = sale_auction_address,
)

siring_auction = compiled_sol['./contract/Auction/SiringClockAuction.sol:SiringClockAuction']
siring_auction_contract = cli.eth.contract(
    abi = siring_auction['abi'],
    address = siring_auction_address,
)

mongo = MongoClient('localhost', 32768)
db = mongo['parallelkitties']

def buy(accounts):
    # Buy 1 kitty for each account.
    ret_set = db.saleauctions.aggregate([{'$sample': {'size': len(accounts)}}])
    targets = []
    for i in ret_set:
        targets.append(i)

    txs = {}
    hashes = []
    for i in range(len(targets)):
        raw_tx, tx_hash = accounts[i].sign(sale_auction_contract.functions.bid(targets[i]['id']).buildTransaction({
            'value': targets[i]['startingPrice'],
            'gas': 1000000000,
            'gasPrice': 1,
        }))
        txs[tx_hash] = raw_tx
        hashes.append(tx_hash)
    cli.sendTransactions(txs)

    # Remove from saleauctions.
    idsToRemove = []
    receipts = wait_for_receipts(cli, hashes)
    for i in range(len(hashes)):
        receipt = receipts[hashes[i]]
        if receipt['status'] != 1:
            continue
        processed_receipt = sale_auction_contract.processReceipt(receipt)
        if 'AuctionSuccessful' in processed_receipt:
            idsToRemove.append(processed_receipt['AuctionSuccessful']['tokenId'])

    db.saleauctions.remove({'id': {'$in': idsToRemove}})
    return idsToRemove

def bid_on_siring_auction(accounts, kitties):
    # Find a sire for each matron we owned.
    targets = []
    while True:
        ret_set = db.siringauctions.aggregate([{'$sample': {'size': len(accounts)}}])
        for i in ret_set:
            targets.append(i['id'])
        if len(targets) == len(accounts):
            break
        time.sleep(3)
        targets = []
    
    txs = {}
    for i in range(len(accounts)):
        raw_tx, tx_hash = accounts[i].sign(kitty_core_contract.functions.bidOnSiringAuction(targets[i], kitties[i]).buildTransaction({
            'value': int(1e15*2),
            'gas': 1000000000,
            'gasPrice': 1,
        }))
        txs[tx_hash] = raw_tx
    
    cli.sendTransactions(txs)

    # Remove from siringauctions.
    idsToRemove = []
    receipts = wait_for_receipts(cli, list(txs.keys()))
    for receipt in receipts.values():
        if receipt['status'] != 1:
            continue
        processed_receipt = siring_auction_contract.processReceipt(receipt)
        if 'AuctionSuccessful' in processed_receipt:
            idsToRemove.append(processed_receipt['AuctionSuccessful']['tokenId'])
    db.siringauctions.remove({'id': {'$in': idsToRemove}})

    # Wait for the sirings complete.
    # TODO
    for id in idsToRemove:
        while True:
            item = db.siringauctioncomplete.find_one({'sireId': id})
            if item is not None:
                db.siringauctioncomplete.delete_one({'sireId': id})
                break
            time.sleep(1)

users = init_accounts(private_key)
kitties = buy(users)
while True:
    bid_on_siring_auction(users, kitties)
    time.sleep(10)