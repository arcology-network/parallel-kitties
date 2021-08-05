# 1. Benchmarking Scripts

## 1.1. Deployment

> In the following examples, we suppose the frontend service was deployed at http://192.168.1.111:8080, replace it if necessary.

```shell
$ cd ~/parallel_kitties
$ ./deploy.sh http://192.168.1.111:8080
```

## 1.2. Initialize test data

```shell
$ bash sendtxs.sh /data/pk_init_gen0_5m http://192.168.1.111:8080
```

## 1.3. Test Kitty Transfer

```shell
$ bash sendtxs.sh /data/pk_kitty_transfer_2.5m/ http://192.168.1.111:8080
```
