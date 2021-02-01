import sys
sys.path.append('../../..')

from ammolite import (Cli, HTTPProvider)
from utils import (wait_for_receipts)

frontend = sys.argv[1]
input = sys.argv[2]

cli = Cli(HTTPProvider(frontend))

hashes = []
with open(input, 'r') as f:
    for line in f:
        line = line.rstrip('\n')
        segments = line.split(',')
        hashes.append(bytes(bytearray.fromhex(segments[1])))

batch = []
for h in hashes:
    batch.append(h)
    if len(batch) == 1000:
        receipts = wait_for_receipts(cli, batch)
        batch = []
        for h in receipts.keys():
            receipt = receipts[h]
            if receipt['status'] != 1:
                assert False

if len(batch) != 0:
    receipts = wait_for_receipts(cli, batch)
    for h in receipts.keys():
        receipt = receipts[h]
        if receipt['status'] != 1:
            assert False
