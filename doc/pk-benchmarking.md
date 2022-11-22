# 1. Benchmarking Scripts

This document shows you how to benchmark Arcology Network using the parallelized CryptoKitties.

## 1.1. Deploy Smart Contracts

Suppose an Arcology node is running at http://192.168.1.111, in the Ammolite docker image, execute the command below.
Replace the IP address if necessary.

```shell
$ cd ~/parallel_kitties
$ ./deploy.sh http://192.168.1.111:8080
```

## 1.2. Created 2M Owners

Call `sendtxs.py` to load a pre-generated transaction file and then send them to the test node through port `8080`.

```shell
>python sendtxs.py http://192.168.1.106:8080 data/pk_init_gen0/pk_init_gen0_2m_01.out
```

## 1.3. Transfer 1M Kitties
When all the owners are successfully created, type in the following command to start kitty transfers.

```shell
>python sendtxs.py http://192.168.1.106:8080 data/pk_kitty_transfer/pk_kitty_transfer_1m_01.dat
```
