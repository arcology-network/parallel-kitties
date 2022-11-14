# Deployment

Generate N accounts for the test with accgen.py:

```shell
$python3 accgen.py <N>
```

Run the deploy script:

python3 deploy.py \<config-file> \<account-file>

* **config-file**: The name of the config file;
* **account-file**: The name of the account file.

**Format of the config file**

```YAML
frontend: http://localhost:8080
gen0_count: 1000
test_case_weights:
    sale_auction: 1
    siring_auction_creator: 1
    siring_auction_bidder: 1
    kitty_raiser: 1
    kitties_exchanger: 1
```

* **frontend**: The service url of the frontend service;
* **gen0_count**: The number of the gen0 kitties;
* **test_case_weights**: The weight of each test case.

Example:

```shell
$ python3 deploy.py config.yaml accounts.txt
Deploy ParallelKitties complete.
python3 init_gen0.py http://localhost:8080 1000 0x110f04e4690b504638ef281a8e190b00aedf1153 0x1af90c9395ad05e29f8698d6a118bbc47e6af7cb cfac4f5fa828072ba8313b0686f02f576fa0fc8caba947569429e88968577865
python3 kitty_miner.py http://localhost:8080 0x110f04e4690b504638ef281a8e190b00aedf1153 42e30ad7f9b7ccb4c19d14277c76c15fddc461548be3102dcb4bbfd7b602c07a
python3 sale_auction_creator_and_bidder.py http://localhost:8080 0x110f04e4690b504638ef281a8e190b00aedf1153 0x1af90c9395ad05e29f8698d6a118bbc47e6af7cb acc1.txt
python3 siring_auction_creator.py http://localhost:8080 0x110f04e4690b504638ef281a8e190b00aedf1153 0x1af90c9395ad05e29f8698d6a118bbc47e6af7cb 0x77b35dce39fb045ae99bbd7105fa2e89c60d36cf acc2.txt
python3 siring_auction_bidder.py http://localhost:8080 0x110f04e4690b504638ef281a8e190b00aedf1153 0x1af90c9395ad05e29f8698d6a118bbc47e6af7cb 0x77b35dce39fb045ae99bbd7105fa2e89c60d36cf acc3.txt
python3 kitty_raiser.py http://localhost:8080 0x110f04e4690b504638ef281a8e190b00aedf1153 0x1af90c9395ad05e29f8698d6a118bbc47e6af7cb acc4.txt
python3 kitties_exchanger.py http://localhost:8080 0x110f04e4690b504638ef281a8e190b00aedf1153 0x1af90c9395ad05e29f8698d6a118bbc47e6af7cb acc5.txt
```

Init gen0 kitties with init_gen0.py:

```shell
$ python3 init_gen0.py http://localhost:8080 1000 0x110f04e4690b504638ef281a8e190b00aedf1153 0x1af90c9395ad05e29f8698d6a118bbc47e6af7cb
```

Run kitty_miner.py before starting all the other tests:

```shell
$ python3 kitty_miner.py http://localhost:8080 0x110f04e4690b504638ef281a8e190b00aedf1153 42e30ad7f9b7ccb4c19d14277c76c15fddc461548be3102dcb4bbfd7b602c07a
```

### Deployment

Copy the output of deploy.py to terminal to run the tests:

```shell
python3 sale_auction_creator_and_bidder.py http://localhost:8080 0x110f04e4690b504638ef281a8e190b00aedf1153 0x1af90c9395ad05e29f8698d6a118bbc47e6af7cb acc1.txt
python3 siring_auction_creator.py http://localhost:8080 0x110f04e4690b504638ef281a8e190b00aedf1153 0x1af90c9395ad05e29f8698d6a118bbc47e6af7cb 0x77b35dce39fb045ae99bbd7105fa2e89c60d36cf acc2.txt
python3 siring_auction_bidder.py http://localhost:8080 0x110f04e4690b504638ef281a8e190b00aedf1153 0x1af90c9395ad05e29f8698d6a118bbc47e6af7cb 0x77b35dce39fb045ae99bbd7105fa2e89c60d36cf acc3.txt
python3 kitty_raiser.py http://localhost:8080 0x110f04e4690b504638ef281a8e190b00aedf1153 0x1af90c9395ad05e29f8698d6a118bbc47e6af7cb acc4.txt
python3 kitties_exchanger.py http://localhost:8080 0x110f04e4690b504638ef281a8e190b00aedf1153 0x1af90c9395ad05e29f8698d6a118bbc47e6af7cb acc5.txt
```

> Run each script in a separate terminal, press Ctrl+C to stop the test.