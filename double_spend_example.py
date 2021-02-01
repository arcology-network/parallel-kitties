import sys
sys.path.append('../../..')

from ammolite import (Cli, HTTPProvider, Account)
import time

cli = Cli(HTTPProvider('http://192.168.1.111:8080'))
acc_from = Account('316b4cb5409a7c8998c04ad81ffb5f771c70ae7305cbd976845c27320aa2fb36')
to_address1 = 'd024a83F83394B90AA2db581250Bc00B0B0f414a'
to_address2 = 'd7cB260c7658589fe68789F2d678e1e85F7e4831'

origin_balance_from = cli.getBalance(acc_from.address())
origin_balance_to1 = cli.getBalance(to_address1)
origin_balance_to2 = cli.getBalance(to_address2)
print('Before transfer:')
print(f'\tBalance of {acc_from.address()}: {origin_balance_from}')
print(f'\tBalance of {to_address1}: {origin_balance_to1}')
print(f'\tBalance of {to_address2}: {origin_balance_to2}')

raw_tx1, tx_hash1 = acc_from.sign({
    'nonce': 1,
    'value': origin_balance_from - 21000,
    'gas': 21000,
    'gasPrice': 1,
    'data': b'',
    'to': bytearray.fromhex(to_address1)
})
raw_tx2, tx_hash2 = acc_from.sign({
    'nonce': 2,
    'value': origin_balance_from - 21000,
    'gas': 21000,
    'gasPrice': 1,
    'data': b'',
    'to': bytearray.fromhex(to_address2)
})
cli.sendTransactions({tx_hash1: raw_tx1, tx_hash2: raw_tx2})

while True:
    receipts = cli.getTransactionReceipts([tx_hash1, tx_hash2])
    if receipts is None or len(receipts) != 2:
        time.sleep(1)
        continue
    break

new_balance_from = cli.getBalance(acc_from.address())
new_balance_to1 = cli.getBalance(to_address1)
new_balance_to2 = cli.getBalance(to_address2)
print('After transfer:')
print(f'\tBalance of {acc_from.address()}: {new_balance_from}')
print(f'\tBalance of {to_address1}: {new_balance_to1}')
print(f'\tBalance of {to_address2}: {new_balance_to2}')
