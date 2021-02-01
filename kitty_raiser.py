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
    # Buy 2 kitties for each account.
    ret_set = db.saleauctions.aggregate([{'$sample': {'size': len(accounts)*2}}])
    targets = []
    for i in ret_set:
        targets.append(i)
    #print(targets)

    txs = {}
    hashes = []
    for i in range(len(accounts)):
        for j in range(2):
            raw_tx, tx_hash = accounts[i].sign(sale_auction_contract.functions.bid(targets[i*2+j]['id']).buildTransaction({
                'value': targets[i*2+j]['startingPrice'],
                'gas': 1000000000,
                'gasPrice': 1,
            }))
            txs[tx_hash] = raw_tx
            hashes.append(tx_hash)
    cli.sendTransactions(txs)
    print('buy {} kitties'.format(len(txs)))

    # Remove from saleauctions.
    idsToRemove = []
    idsToReturn = []
    receipts = wait_for_receipts(cli, hashes)
    ok = 0
    fail = 0
    for i in range(len(hashes)):
        receipt = receipts[hashes[i]]
        if receipt['status'] != 1:
            #print(receipt)
            fail += 1
            idsToReturn.append(None)
            continue
        processed_receipt = sale_auction_contract.processReceipt(receipt)
        if 'AuctionSuccessful' in processed_receipt:
            ok += 1
            idsToRemove.append(processed_receipt['AuctionSuccessful']['tokenId'])
            idsToReturn.append(processed_receipt['AuctionSuccessful']['tokenId'])
        else:
            fail += 1
    print('ok = {}, fail = {}'.format(ok, fail))

    db.saleauctions.remove({'id': {'$in': idsToRemove}})
    return idsToReturn

def breed(accounts, kitties, n):
    # Breed.
    txs = {}
    hashes = []
    m = []
    for i in range(len(accounts)):
        if kitties[i*2] is None or kitties[i*2+1] is None:
            continue
        raw_tx, tx_hash = accounts[i].sign(kitty_core_contract.functions.breedWithAuto(kitties[i*2], kitties[i*2+1]).buildTransaction({
            'value': int(1e15),
            'gas': 1000000000,
            'gasPrice': 1,
            'nonce': n,
        }))
        txs[tx_hash] = raw_tx
        hashes.append(tx_hash)
        m.append(kitties[i*2])
    cli.sendTransactions(txs)
    print('txs = {}'.format(len(txs)))

    receipts = wait_for_receipts(cli, hashes)
    matrons = []
    for i in range(len(hashes)):
        receipt = receipts[hashes[i]]
        #print(receipt)
        if receipt['status'] != 1:
            print(hashes[i].hex())
            continue
        matrons.append(m[i])
        if i == 0:
            print(hashes[0].hex())
    print('ok = {}'.format(len(matrons)))

    # Wait for the birth of children.
    found = 0
    notfound = len(matrons)
    for matron in matrons:
        #print('try {}'.format(matron))
        while True:
            item = db.newborns.find_one({'matronId': matron})
            if item is not None:
                db.newborns.delete_one({'matronId': matron})
                #found += 1
                #notfound -= 1
                #print('found = {}, not found = {}'.format(found, notfound))
                break
            time.sleep(1)

users = init_accounts(private_key)
kitties = buy(users)
#print(kitties)
n = 1
while True:
    breed(users, kitties, n)
    n += 1
    #time.sleep(10)
