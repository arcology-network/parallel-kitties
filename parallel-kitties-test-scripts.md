
# Parallel Kitties Test Scripts

- [Parallel Kitties Test Scripts](#parallel-kitties-test-scripts)
  - [1. Introduction](#1-introduction)
  - [2. Run the Test Scripts](#2-run-the-test-scripts)
    - [2.1. Deploy the Contract](#21-deploy-the-contract)
    - [2.2. Generate the First Generation](#22-generate-the-first-generation)
    - [2.3. Transfer Kitties](#23-transfer-kitties)

## 1. Introduction

---
The CryptoKitties is one of the most popular NFT application on Ethereum platform. The original version only allow sequential execution. We optimized the CryptoKitties using Arcology's concurrent library to allow concurrent exeuction and named it ParallelKitties. 

## 2. Run the Test Scripts

---

### 2.1. Deploy the Contract

```sh
cd parallel_kitties
python deploy_v2.py http://192.138.1.103:8080 ../data/genesis_accounts_200.txt
```

### 2.2. Generate the First Generation

```sh
python sendtxs.py http://192.138.1.103:8080 data/pk/pk_init_gen0_200.out
```

### 2.3. Transfer Kitties

```sh
python sendtxs.py http://192.138.1.103:8080 data/pk/pk_kitty_transfer_100.out
```