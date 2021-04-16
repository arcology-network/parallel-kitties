# 1. Benchmarking Scripts

## 1.1. Deployment

> In the following examples, we suppose the frontend service was deployed at http://192.168.1.111:8080, replace it if necessary.

```shell
$ cd ~/parallel_kitties
$ ./deploy.sh http://192.168.1.111:8080
```

## 1.2. Initialize test data

```shell
$ ./send_init_txs.sh http://192.168.1.111:8080
```

## 1.3. Test Kitty Transfer

```shell
$ ./send_pk_transfer_txs.sh http://192.168.1.111:8080
```