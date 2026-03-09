# CS216 – BreakTheChain-Legacy-Segwit
## Legacy vs SegWit Transaction Analysis

This project was implemented as part of the CS216 Blockchain Lab Assignment at IIT Indore.
The objective of this assignment is to understand how Bitcoin transactions are created, signed, and validated using two different address formats:

Legacy transactions (P2PKH)

SegWit transactions (P2SH-P2WPKH)

The transactions were executed on a local Bitcoin regtest network, allowing us to safely create and analyze transactions without interacting with the public Bitcoin blockchain.

We implemented scripts that:

1. Connect to a local Bitcoin regtest node via RPC and load a wallet
2. Create and fund Legacy (P2PKH) and SegWit (P2SH-P2WPKH) addresses
3. Generate transaction chains A->B->C for both address types
4. Decode raw transactions to extract locking scripts (scriptPubKey) and unlocking scripts (scriptSig)
5. Analyze witness data for SegWit transactions (txinwitness)
6. Validate script execution step by step using btcdeb debugger
7. Compare transaction sizes, vsize and weight between Legacy and SegWit

## Team Members — Break The Chain

| Name | Roll Number |
|------|-------------|
| Boddu Kunal | 240003020 |
| Shaik Riyaj | 240001068 |
| Sangati Chakradhar Reddy | 240001063 |
| Kesavarapu Deepak Reddy | 240041022 |

## Tools and Dependencies

- **Bitcoin Core (bitcoind)** — local Bitcoin node in regtest mode
- **Bitcoin CLI** — command-line interaction with the node
- **btcdeb** — stepping through and validating Bitcoin scripts
- **Python 3** — transaction automation and analysis
- **python-bitcoinrpc** — RPC communication with Bitcoin node

## Project Structure
```
CS216-BreakTheChain-Legacy-Segwit/
├── src/
│   ├── legacy_transactions.py
│   ├── segwit_transactions.py
│   └── Analysis.py
├── screenshots/
│   ├── legacy/
│   ├── segwit/
│   └── analysis/
├── README.md
├── Report.pdf
├── bitcoin.conf.example
└── requirements.txt
```

## Screenshots

The `screenshots/` directory contains:
- decoded transactions for both Legacy and SegWit
- btcdeb script execution traces
- analysis results comparing transaction sizes

## Setting Up the Environment
(after downloading the tools and dependencies)

### Step 1 – Clone the Repository
```bash
git clone https://github.com/kanna1951693/CS216-BreakTheChain-Legacy-Segwit.git
cd CS216-BreakTheChain-Legacy-Segwit
```

### Step 2 – Configure Bitcoin Core
Copy the example configuration file:
```bash
cp bitcoin.conf.example ~/.bitcoin/bitcoin.conf
```

### Step 3 – Start Bitcoin Core in Regtest Mode
```bash
bitcoind -regtest -daemon
```

### Step 4 – Verify Bitcoin Core is Running
```bash
bitcoin-cli -regtest getblockchaininfo
```

### Step 5 – Create Wallet
```bash
bitcoin-cli -regtest createwallet "testwallet"
```

### Step 6 – Generate Initial Blocks
```bash
address=$(bitcoin-cli -regtest -rpcwallet=testwallet getnewaddress)
bitcoin-cli -regtest -rpcwallet=testwallet generatetoaddress 101 "$address"
```

### Step 7 – Check Balance
```bash
bitcoin-cli -regtest -rpcwallet=testwallet getbalance
```
### Step 8 – Install Python Library
```bash
pip install -r requirements.txt
```
Make sure `bitcoind` is running in regtest mode before executing the Python scripts.

## Running the Programs

### Part 1 – Legacy Transactions (P2PKH)
```bash
python3 src/legacy_transactions.py
```

### Part 2 – SegWit Transactions (P2SH-P2WPKH)
```bash
python3 src/segwit_transactions.py
```

### Part 3 – Comparative Analysis
```bash
python3 src/Analysis.py
```

## Stop Bitcoin Core (After Running All Scripts)
```bash
bitcoin-cli -regtest stop
```
## Transaction Workflow

For both Legacy and SegWit implementations the following workflow was used:

1. Generate three addresses (A, B, C).
2. Fund address A with coins mined on the regtest network.
3. Create the first transaction sending coins from **A -> B**.
4. Mine a block to confirm the transaction.
5. Use the resulting UTXO at B as input for the second transaction **B -> C**.
6. Decode the raw transactions to inspect the scripts.
7. Execute the scripts step-by-step using btcdeb to validate the unlocking and locking mechanisms.

   
## Bitcoin Script Analysis

Bitcoin uses a stack-based scripting language to validate transactions.
Each transaction has two scripts:
- **scriptPubKey** (locking script) — set by the sender
- **scriptSig** (unlocking script) — provided by the spender

### Legacy (P2PKH)
Locking: `OP_DUP OP_HASH160 <pubkeyhash> OP_EQUALVERIFY OP_CHECKSIG`
Unlocking: `<signature> <pubkey>`

### SegWit (P2SH-P2WPKH)
Locking: `OP_HASH160 <scripthash> OP_EQUAL`
Unlocking:
- The `scriptSig` contains the redeem script
- The signature and public key are stored in the `txinwitness` field

This separation of witness data is the key feature of SegWit and reduces the effective size of the transaction.

## Transaction Size Comparison

| Transaction | Size | vsize | Weight |
|-------------|------|-------|--------|
| Legacy A→B  | 119  |  119  |   476  |
| Legacy B→C  | 119  |  119  |   476  |
| SegWit A→B  | 115  |  115  |   460  |
| SegWit B→C  | 115  |  115  |   460  |

SegWit introduces a new weight metric where witness data counts only one quarter as much as non-witness data.  
Because the signature data is moved to the witness structure and discounted in weight calculation, SegWit transactions have a smaller effective size and therefore lower transaction fees.



