import sys
sys.path.append('../../..')

import time, signal
from ammolite import (Cli, HTTPProvider)

from rich.console import Console
from rich.live import Live
from rich.table import Table

def calculate_tps(now, blocks):
    remains = []
    for b in blocks:
        if b['timestamp'] + 60 < now:
            continue
        remains.append(b)
    
    num_txs = 0
    for b in remains:
        if b['transactions'] is None or len(b['transactions']) == 0:
            continue
        num_txs += len(b['transactions'])

    return remains, num_txs / 60

frontend = sys.argv[1]

cli = Cli(HTTPProvider(frontend))

block = cli.getBlock(-1)
height = block['height']
blocks_within_1m = [block]

console = Console()
max_tps = 0

def create_table(blocks, tps, max_tps) -> Table:
    table = Table()
    table.add_column("      Height", justify="right")
    table.add_column("Transactions", justify="right")
    table.title = 'TPS: {}(MAX) / {}(1m AVG)'.format(int(max_tps), int(tps))

    n = min(5, len(blocks))
    for i in range(n):
        block = blocks[len(blocks) - i - 1]
        txs = block['transactions']
        num_txs = 0
        if txs is not None:
            num_txs = len(txs)
        table.add_row(str(block['height']), str(num_txs))

    return table

def signal_handler(sig, frame):
    sys.exit(0)

signal.signal(signal.SIGINT, signal_handler)
#signal.pause()

with Live(console = console, transient = True, auto_refresh = False) as live:
    while True:
        block = cli.getBlock(height+1)
        if block is None or len(block) == 0:
            time.sleep(1)
            continue
    
        blocks_within_1m.append(block)
        height += 1

        last_tps = 0
        if len(blocks_within_1m) > 1:
            num_txs = 0
            if blocks_within_1m[len(blocks_within_1m)-2]['transactions'] is not None:
                num_txs = len(blocks_within_1m[len(blocks_within_1m)-2]['transactions'])
            last_tps = num_txs / (blocks_within_1m[len(blocks_within_1m)-1]['timestamp'] - blocks_within_1m[len(blocks_within_1m)-2]['timestamp'])
        if max_tps < last_tps:
            max_tps = last_tps

        blocks_within_1m, tps = calculate_tps(block['timestamp'], blocks_within_1m)
        if max_tps < tps:
            max_tps = tps
        live.update(create_table(blocks_within_1m, tps, max_tps), refresh = True)
