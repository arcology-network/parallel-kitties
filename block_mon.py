import sys
sys.path.append('../../..')

import time
from ammolite import (Cli, HTTPProvider, Account)
from utils import (wait_for_receipts)

frontend = sys.argv[1]

cli = Cli(HTTPProvider(frontend))

block = cli.getBlock(-1)
#print(block)
height = block['height']

while True:
    block = cli.getBlock(height+1)
    if block is None or len(block) == 0:
        time.sleep(1)
        continue

    txs = block['transactions']
    if txs is None or len(txs) == 0:
        print('height = {}, empty block, timestamp = {}'.format(height + 1, block['timestamp']))
        height += 1
        continue
    hashes = []
    success = 0
    fail = 0
    for h in txs:
        hashes.append(h)
        if len(hashes) == 1000:
            receipts = wait_for_receipts(cli, hashes)
            hashes = []
            for receipt in receipts.values():
                if receipt['status'] != 1:
                    fail += 1
                else:
                    success += 1

    if len(hashes) != 0:
        receipts = wait_for_receipts(cli, hashes)
        hashes = []
        for receipt in receipts.values():
            if receipt['status'] != 1:
                fail += 1
            else:
                success += 1

    height += 1
    print('height = {}, total = {}, success = {}, fail = {}, timestamp = {}'.format(height, len(txs), success, fail, block['timestamp']))
