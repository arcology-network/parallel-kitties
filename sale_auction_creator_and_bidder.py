import sys
sys.path.append('../../..')

import time
from ammolite import (Cli, HTTPProvider, Account)
from utils import (wait_for_receipts, compile_contracts, init_accounts)
from pymongo import MongoClient

frontend = sys.argv[1]
kitty_core_address = sys.argv[2]
sale_auction_address = sys.argv[3]
private_key = sys.argv[4]

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

mongo = MongoClient('localhost', 32768)
db = mongo['parallelkitties']

def buy_and_sale(accounts):
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

    # Remove from saleauctions, then create a new sale auction.
    txs = {}
    idsToRemove = []
    receipts = wait_for_receipts(cli, hashes)
    for receipt in receipts.values():
        if receipt['status'] != 1:
            continue
        processed_receipt = sale_auction_contract.processReceipt(receipt)
        print(processed_receipt)
        if 'AuctionSuccessful' in processed_receipt:
            idsToRemove.append(processed_receipt['AuctionSuccessful']['tokenId'])
            raw_tx, tx_hash = accounts[i].sign(kitty_core_contract.functions.createSaleAuction(
                processed_receipt['AuctionSuccessful']['tokenId'],
                int(1e15),
                0,
                60
            ).buildTransaction({
                'value': 0,
                'gas': 1000000000,
                'gasPrice': 1,
            }))
            txs[tx_hash] = raw_tx

        processed_receipt = kitty_core_contract.processReceipt(receipt)
        print(processed_receipt)
    cli.sendTransactions(txs)
    db.saleauctions.remove({'id': {'$in': idsToRemove}})

    auctions = []
    receipts = wait_for_receipts(cli, list(txs.keys()))
    for receipt in receipts.values():
        if receipt['status'] != 1:
            print(receipt)
            continue
        processed_receipt = sale_auction_contract.processReceipt(receipt)
        if 'AuctionCreated' in processed_receipt:
            newAuction = {
                'id': processed_receipt['AuctionCreated']['tokenId'],
                'startingPrice': int(processed_receipt['AuctionCreated']['startingPrice'], 16),
                'endingPrice': int(processed_receipt['AuctionCreated']['endingPrice'], 16),
                'duration': int(processed_receipt['AuctionCreated']['duration'], 16),
            }
            auctions.append(newAuction)
    db.saleauctions.insert_many(auctions)

users = init_accounts(private_key)
while True:
    buy_and_sale(users)
    time.sleep(10)
