import sys
sys.path.append('../../..')

import time
import os
from solcx import compile_files
from ammolite import (Account)

def wait_for_receipts(cli, hashes):
    # print(hashes)
    receipts = {}
    while True:
        rs = cli.getTransactionReceipts(hashes)
        remains = []
        for i in range(len(rs)):
            # print(rs[i])
            # print(hashes[i])
            if rs[i] is not None:
                receipts[hashes[i]] = rs[i]
            else:
                remains.append(hashes[i])
        if len(remains) == 0:
            return receipts
        
        time.sleep(3)
        hashes = remains

def compile_contracts(dir):
    sources = []
    for root, _, files in os.walk('./contract'):
        for file in files:
            if file.endswith('.sol'):
                sources.append(os.path.join(root, file))

    # print(sources)
    return compile_files(sources, output_values = ['abi', 'bin'])

def check_receipts(receipts):
    print(receipts)
    # if receipt['status'] != 1:
    #     assert False

def init_accounts(file):
    accounts = []
    with open(file, 'r') as f:
        for key in f:
            # print('---' + key + '---')
            accounts.append(Account(key[:-1]))
    return accounts