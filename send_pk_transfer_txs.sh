#!/bin/bash

python sendtxs.py http://192.168.1.111:8080 data/transfer2_5m_1.out > /dev/null &
python sendtxs.py http://192.168.1.111:8080 data/transfer2_5m_2.out

