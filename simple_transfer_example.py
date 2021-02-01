import sys
sys.path.append('../../..')

from ammolite import (Cli, HTTPProvider, Account)
import time

cli = Cli(HTTPProvider('http://192.168.1.111:8080'))
acc_from = Account('3d381aaf963bc03c634664cddfbf48c71962c2747824bebdf2505d7a5640c47f')
to_address = '0xd024a83F83394B90AA2db581250Bc00B0B0f414a'

origin_balance_from = cli.getBalance(acc_from.address())
origin_balance_to = cli.getBalance(to_address)

print('Before transfer:')
print(f'\tBalance of {acc_from.address()}: {origin_balance_from}')
print(f'\tBalance of {to_address}: {origin_balance_to}')

raw_tx, tx_hash = acc_from.sign({
    'nonce': 1,
    'value': 1000000000,
    'gas': 21000,
    'gasPrice': 10,
    'data': b'',
    'to': bytearray.fromhex(to_address[2:])
})
print(f'Transfer 1000000000 from {acc_from.address()} to {to_address}, pay 210000 for gas')
cli.sendTransactions({tx_hash: raw_tx})
while True:
    receipts = cli.getTransactionReceipts([tx_hash])
    if receipts is None or len(receipts) != 1:
        time.sleep(1)
        continue
    break

new_balance_from = cli.getBalance(acc_from.address())
new_balance_to = cli.getBalance(to_address)
print('After transfer:')
print(f'\tBalance of {acc_from.address()}: {new_balance_from}')
print(f'\tBalance of {to_address}: {new_balance_to}')
