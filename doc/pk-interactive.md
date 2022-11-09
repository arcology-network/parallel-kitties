# Interactive Scripts

Import necessary ammolite modules
```Python
>>> from ammolite import (Cli, HTTPProvider, Account)
```

Compile the parallelized CryptoKitties source code with the solcx library
```Python
>>> from solcx import compile_files
```
Declare a list to store all the locations of the source code files 
```Python
>>> sources = []

```
Traverse ～/contract directory，find all Solidity files and add to sources
```Python
>>> import os
>>> for root, _, files in os.walk('./contract'):
...     for file in files:
...         if file.endswith('.sol'):
...             sources.append(os.path.join(root, file))
... 

```
Check source code files
```Python
>>> sources
['./contract/KittyOwnership.sol', './contract/KittyMinting.sol', './contract/KittyAuction.sol', './contract/KittyBreeding.sol', './contract/ERC721Draft.sol', './contract/KittyBase.sol', './contract/KittyCore.sol', './contract/KittyAccessControl.sol', './contract/GeneScience.sol', './contract/ExternalInterfaces/ConcurrentLibInterface.sol', './contract/ExternalInterfaces/GeneScienceInterface.sol', './contract/Auction/ClockAuctionBase.sol', './contract/Auction/SiringClockAuction.sol', './contract/Auction/SaleClockAuction.sol', './contract/Auction/ClockAuction.sol', './contract/Zeppelin/Pausable.sol', './contract/Zeppelin/Ownable.sol']

```
Initialize an ammolite client connecting to the frontend of a node cluster
```Python
>>> cli = Cli(HTTPProvider('http://192.168.1.111:8080'))

```
Compile source code and output ABI
```Python
>>> compiled_sol = compile_files(sources, output_values=['abi'])

```
Get KittyCore contract related information
```Python
>>> kitty_core = compiled_sol['./contract/KittyCore.sol:KittyCore']
 
```
Use KittyCore ABI information and KittyCore deployment address to initialize a Contract object. For easy testing, using deploy_pk.sh to deploy 
```Python
ParallelKittie to ensure the KittyCore is deployed at a fixed address
>>> kitty_core_contract = cli.eth.contract(
...     abi = kitty_core['abi'],
...     address = 'b1e0e9e68297aae01347f6ce0ff21d5f72d3fa0f',
... )
```
set the COO account at deployment
```Python
>>> coo_private_key = '2289ae919f03075448d567c9c4a22846ce3711731c895f1bea572cef25bb346f'

```
Pick a user account from ～/accounts.txt
```Python
>>> user_private_key = '25dcf355077dc5479435353f3acd6388477c52e1d4c3d73276c2377112539609'
>>> coo = Account(coo_private_key)
>>> user1 = Account(user_private_key)
```
Another user account from ～/accounts.txt, remove the '0x' prefix of the address.
```Python
>>> user2_address = 'b1f0f5FD90E331D695AB1E65C33ce8Cf47b69696'

```
Use COO account to sign a createPromoKitty transaction，
* First argument is the gene of the newly born promotion kitty
* Second argument is the kitty owner
```Python
>>> raw_tx, tx_hash = coo.sign(kitty_core_contract.functions.createPromoKitty(
...     0,
...     user1.address()
... ).buildTransaction({
...     'gas': 1000000,
...     'gasPrice': 1,
... }))

```
Sending in the transaction
```Python
>>> cli.sendTransactions({tx_hash:raw_tx})

```
Use the transaction hash to get the receipts, it may need a few retries if the node cluster is under heavy workload
```Python
>>> receipts = cli.getTransactionReceipts([tx_hash])

```
Examine the returned receipts
```Python
>>> receipts
[{'status': 1, 'contractAddress': '0000000000000000000000000000000000000000', 'gasUsed': 44544, 'logs': [{'address': 'b1e0e9e68297aae01347f6ce0ff21d5f72d3fa0f', 'topics': ['0a5311bd2a6608f08a180df2ee7c5946819a649b204b554bb8e39825b2c50ad5', '00000000000000000000000016fcefbde47fbe724aa59e5f73a35aebce7ff2a2'], 'data': '1a5d529ea3a20e584aed24e232dd98f71dab638bed23006512bd5d9d423ca4fa000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000000', 'blockNumber': 77732, 'transactionHash': '0000000000000000000000000000000000000000000000000000000000000000', 'transactionIndex': 0, 'blockHash': '0000000000000000000000000000000000000000000000000000000000000000', 'logIndex': 0}, {'address': 'b1e0e9e68297aae01347f6ce0ff21d5f72d3fa0f', 'topics': ['ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef', '0000000000000000000000000000000000000000000000000000000000000000', '00000000000000000000000016fcefbde47fbe724aa59e5f73a35aebce7ff2a2', '1a5d529ea3a20e584aed24e232dd98f71dab638bed23006512bd5d9d423ca4fa'], 'data': '', 'blockNumber': 77732, 'transactionHash': '0000000000000000000000000000000000000000000000000000000000000000', 'transactionIndex': 0, 'blockHash': '0000000000000000000000000000000000000000000000000000000000000000', 'logIndex': 0}], 'executing logs': ''}]

```
Parse the events field in the receipt
```Python
>>> events = kitty_core_contract.processReceipt(receipts[0])

```
There are two events contained in the receipt
1. Birth event indicates that a new kitty was created and owned by the user1，kittyId is for the new kitty. 
  matron and sire for promotion kitty are always 0，gene is the first argument when calling kitty_core_contract.functions.createPromoKitty()
2. Another event is the kitty was transferred from user0 to user1 while the tokenId should be the same as the kittyId in the Birth event
```Python
>>> events
{'Birth': {'owner': '00000000000000000000000016fcefbde47fbe724aa59e5f73a35aebce7ff2a2', 'kittyId': '1a5d529ea3a20e584aed24e232dd98f71dab638bed23006512bd5d9d423ca4fa', 'matronId': '0000000000000000000000000000000000000000000000000000000000000000', 'sireId': '0000000000000000000000000000000000000000000000000000000000000000', 'genes': '0000000000000000000000000000000000000000000000000000000000000000'}, 'Transfer': {'from': '0000000000000000000000000000000000000000000000000000000000000000', 'to': '00000000000000000000000016fcefbde47fbe724aa59e5f73a35aebce7ff2a2', 'tokenId': '1a5d529ea3a20e584aed24e232dd98f71dab638bed23006512bd5d9d423ca4fa'}}

```
Store newly created kitty ID
```Python
>>> new_kitty = events['Birth']['kittyId']
>>> new_kitty
'1a5d529ea3a20e584aed24e232dd98f71dab638bed23006512bd5d9d423ca4fa'

```
Use the user1 account to sign a transaction to transfer the kitty to user2. 
* The first argument is the address of user2 
* The second argument is the kitty ID
```Python
>>> raw_tx, tx_hash = user1.sign(kitty_core_contract.functions.transfer(
...     user2_address,
...     new_kitty,
... ).buildTransaction({
...     'gas': 1000000,
...     'gasPrice': 1,
... }))

```
Send the transaction
```Python
>>> cli.sendTransactions({tx_hash:raw_tx})

```
Check receipts
```Python
>>> receipts = cli.getTransactionReceipts([tx_hash])
>>> receipts
[{'status': 1, 'contractAddress': '0000000000000000000000000000000000000000', 'gasUsed': 42901, 'logs': [{'address': 'b1e0e9e68297aae01347f6ce0ff21d5f72d3fa0f', 'topics': ['ddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef', '00000000000000000000000016fcefbde47fbe724aa59e5f73a35aebce7ff2a2', '000000000000000000000000b1f0f5fd90e331d695ab1e65c33ce8cf47b69696', '1a5d529ea3a20e584aed24e232dd98f71dab638bed23006512bd5d9d423ca4fa'], 'data': '', 'blockNumber': 77972, 'transactionHash': '0000000000000000000000000000000000000000000000000000000000000000', 'transactionIndex': 0, 'blockHash': '0000000000000000000000000000000000000000000000000000000000000000', 'logIndex': 0}], 'executing logs': ''}]

```
Parse the events，should contain a Transfer event，from user1 to user2 address，tokenId is kitty ID
```Python
>>> events = kitty_core_contract.processReceipt(receipts[0])
>>> events
{'Transfer': {'from': '00000000000000000000000016fcefbde47fbe724aa59e5f73a35aebce7ff2a2', 'to': '000000000000000000000000b1f0f5fd90e331d695ab1e65c33ce8cf47b69696', 'tokenId': '1a5d529ea3a20e584aed24e232dd98f71dab638bed23006512bd5d9d423ca4fa'}}
>>> 
```

## Scripts

```Python
import time, os
from solcx import compile_files
from ammolite import (Cli, HTTPProvider, Account)
# Get all Solidity files from the contract direcoty
sources = []
for root, _, files in os.walk('./contract'):
    for file in files:
        if file.endswith('.sol'):
            sources.append(os.path.join(root, file))
# Initialize frontend connection
cli = Cli(HTTPProvider('http://192.168.1.111:8080'))
# Compile Solidity files，output ABI
compiled_sol = compile_files(sources, output_values = ['abi'])
# Initialize Contract object of KittyCore contract，address is deployment address of KittyCore. Prior to this, make sure to call deploy_pk.sh to complete the deployment first
kitty_core = compiled_sol['./contract/KittyCore.sol:KittyCore']
kitty_core_contract = cli.eth.contract(
    abi = kitty_core['abi'],
    address = 'b1e0e9e68297aae01347f6ce0ff21d5f72d3fa0f',
)
# Private keys of the COO account and a user account
coo_private_key = '2289ae919f03075448d567c9c4a22846ce3711731c895f1bea572cef25bb346f'
user_private_key = 'd9815a0fa4f31172530f17a6ae64bf5f00a3a651f3d6476146d2c62ae5527dc4'
coo = Account(coo_private_key)
user1 = Account(user_private_key)
user2_address = '230DCCC4660dcBeCb8A6AEA1C713eE7A04B35cAD'
# Sign with COO key to allocate a promotion kitty to user1, the first argument to call createPromoKitty is the kitty gene
raw_tx, tx_hash = coo.sign(kitty_core_contract.functions.createPromoKitty(
    0, 
    user1.address()
).buildTransaction({
    'gas': 1000000,
    'gasPrice': 1,
}))
# Send in the transaction
cli.sendTransactions({tx_hash: raw_tx})
# Wait till processed
receipts = []
while True:
    receipts = cli.getTransactionReceipts([tx_hash])
    if receipts is None or len(receipts) != 1:
        time.sleep(1)
        continue
    break
# Parse events in receipt
events = kitty_core_contract.processReceipt(receipts[0])
# New kitty ID
new_kitty = events['Birth']['kittyId']
print(f'New kitty {new_kitty} born and assigned to {events["Birth"]["owner"][24:]}')
# Use user1 account to sign a transaction to the kitty to user2
raw_tx, tx_hash = user1.sign(kitty_core_contract.functions.transfer(
    user2_address,
    new_kitty
).buildTransaction({
    'gas': 1000000,
    'gasPrice': 1,
}))
# Send in the transaction
cli.sendTransactions({tx_hash: raw_tx})
# Wait till completed
while True:
    receipts = cli.getTransactionReceipts([tx_hash])
    if receipts is None or len(receipts) != 1:
        time.sleep(1)
        continue
    break
# Parse events in the receipt
events = kitty_core_contract.processReceipt(receipts[0])
print(f'Kitty {events["Transfer"]["tokenId"]} transfered from {events["Transfer"]["from"][24:]} to {events["Transfer"]["to"][24:]}')
```

## Output

```shell
# python simple_pk_example.py
New kitty f1cbc2efb34a8260708f01ed17fc7b5d1d8610a070bcbbce89d60f5bb230b7ff born and assigned to 8aa62d370585e28fd2333325d3dbaef6112279ce
Kitty f1cbc2efb34a8260708f01ed17fc7b5d1d8610a070bcbbce89d60f5bb230b7ff transfered from 8aa62d370585e28fd2333325d3dbaef6112279ce to 230dccc4660dcbecb8a6aea1c713ee7a04b35cad
```