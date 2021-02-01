import sys
sys.path.append('../../..')

from ammolite import (Cli, HTTPProvider)
from rich.progress import Progress

frontend = sys.argv[1]
input = sys.argv[2]

cli = Cli(HTTPProvider(frontend))

txs = {}
with open(input, 'r') as f:
    print("Loading...")
    for line in f:
        line = line.rstrip('\n')
        if len(line) == 0:
            continue
        segments = line.split(',')
        txs[bytes(bytearray.fromhex(segments[1]))] = bytes(bytearray.fromhex(segments[0]))

with Progress() as progress:
    task = progress.add_task("Sending...", total=len(txs))
    batch = {}
    n = 0
    for h in txs.keys():
        batch[h] = txs[h]
        if len(batch) == 1000:
            cli.sendTransactions(batch)
            progress.update(task, advance=len(batch))
            n += len(batch)
            #print('sending {} of {}'.format(n, len(txs)))
            batch = {}

    if len(batch) != 0:
        cli.sendTransactions(batch)
        progress.update(task, advance=len(batch))
