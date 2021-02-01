import sys
sys.path.append('../../..')

import time
from ammolite import (Cli, HTTPProvider, Account)
from utils import (wait_for_receipts, compile_contracts)
from pymongo import MongoClient

frontend = sys.argv[1]
kitty_core_address = sys.argv[2]
private_key = sys.argv[3]

cli = Cli(HTTPProvider(frontend))
compiled_sol = compile_contracts('./contract')
kitty_core = compiled_sol['./contract/KittyCore.sol:KittyCore']
kitty_core_contract = cli.eth.contract(
    abi = kitty_core['abi'],
    address = kitty_core_address,
)
miner = Account(private_key)

mongo = MongoClient('localhost', 32768)
db = mongo['parallelkitties']

block = cli.getBlock(-1)
#print(block)
height = block['height']
#height = 1

wait_for_birth = []
n = 0
num_new_kitties = 0
while True:
    block = cli.getBlock(height+1)
    if block is None or len(block) == 0:
        time.sleep(1)
        continue

    txs = block['transactions']
    if txs is None or len(txs) == 0:
        print('height = {}, empty block, timestamp = {}'.format(block['height'], block['timestamp']))
        #height += 1
        #continue
    else:
        print('height = {}, transaction = {}'.format(block['height'], len(txs)))
        #print(txs)
        receipts = wait_for_receipts(cli, txs)
        for receipt in receipts.values():
            if receipt['status'] != 1:
                continue
            processed_receipt = kitty_core_contract.processReceipt(receipt)
            if 'AutoBirth' in processed_receipt:
                #print(processed_receipt)
                wait_for_birth.append(processed_receipt['AutoBirth'])

    remains = []
    txs = {}
    for i in wait_for_birth:
        if int(i['cooldownEndTime'], 16) <= block['timestamp']:
            raw_tx, tx_hash = miner.sign(kitty_core_contract.functions.giveBirth(i['matronId']).buildTransaction({
                'nonce': n,
                'value': 0,
                'gas': 1000000000,
                'gasPrice': 1,
            }))
            txs[tx_hash] = raw_tx
            n += 1
        else:
            remains.append(i)
    if len(txs) > 0:
        print('giveBirth = {}'.format(len(txs)))
        cli.sendTransactions(txs)
        receipts = wait_for_receipts(cli, list(txs.keys()))
        new_borns = []
        index = 0
        for h, receipt in receipts.items():
            if receipt['status'] != 1:
                #print(receipt)
                index += 1
                continue
            processed_receipt = kitty_core_contract.processReceipt(receipt)
            if index == 0:
                print(h.hex())
            if 'Birth' in processed_receipt:
                #print(processed_receipt)
                new_borns.append(processed_receipt['Birth'])
            index += 1
        if len(new_borns) > 0:
            num_new_kitties += len(new_borns)
            print('num_new_kitties = {}, new borns = {}'.format(num_new_kitties, len(new_borns)))
            db.newborns.insert_many(new_borns)
    
    wait_for_birth = remains
    height += 1
