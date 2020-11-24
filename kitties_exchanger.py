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
    address = kitty_core_address,
)

sale_auction = compiled_sol['./contract/Auction/SaleClockAuction.sol:SaleClockAuction']
sale_auction_contract = cli.eth.contract(
    abi = sale_auction['abi'],
    address = sale_auction_address,
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
    for i in range(len(accounts)):
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

def transfer(accounts, kitties):
    count = len(accounts)
    # print(count)
    # print(kitties)
    txs = {}
    hashes = []
    for i in range(int(count/2)):
        print(i)
        raw_tx, tx_hash = accounts[i].sign(kitty_core_contract.functions.transfer(
            accounts[int(i+count/2)].address(),
            kitties[i],
        ).buildTransaction({
            'value': 0,
            'gas': 1000000000,
            'gasPrice': 1,
        }))
        txs[tx_hash] = raw_tx
        hashes.append(tx_hash)
    for i in range(int(count/2)):
        raw_tx, tx_hash = accounts[int(i+count/2)].sign(kitty_core_contract.functions.transfer(
            accounts[i].address(),
            kitties[int(i+count/2)],
        ).buildTransaction({
            'value': 0,
            'gas': 1000000000,
            'gasPrice': 1,
        }))
        txs[tx_hash] = raw_tx
        hashes.append(tx_hash)
    cli.sendTransactions(txs)

    receipts = wait_for_receipts(cli, hashes)
    for i in range(len(hashes)):
        receipt = receipts[hashes[i]]
        if receipt['status'] != 1:
            continue
        processed_receipt = kitty_core_contract.processReceipt(receipt)
        if 'Transfer' in processed_receipt:
            if i < count/2:
                kitties[int(i+count/2)] = processed_receipt['Transfer']['tokenId']
            else:
                kitties[int(i-count/2)] = processed_receipt['Transfer']['tokenId']
    return kitties

users = init_accounts(private_key)
kitties = buy(users)
print(kitties)
while True:
    kitties = transfer(users, kitties)
    time.sleep(10)