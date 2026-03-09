from bitcoinrpc.authproxy import AuthServiceProxy

rpc = AuthServiceProxy("http://user:pass@127.0.0.1:18443")

# Load wallet
try:
    rpc.loadwallet("testwallet")
except:
    pass

# Mine blocks so coinbase becomes spendable
miner = rpc.getnewaddress()
rpc.generatetoaddress(101, miner)

print("Node ready on regtest\n")

# LEGACY TRANSACTIONS (P2PKH)
print("========== LEGACY TRANSACTIONS ==========")

A = rpc.getnewaddress("", "legacy")
B = rpc.getnewaddress("", "legacy")
C = rpc.getnewaddress("", "legacy")

print("Address A:", A)
print("Address B:", B)
print("Address C:", C)

# Fund A
rpc.sendtoaddress(A, 1)
rpc.generatetoaddress(1, miner)

# A -> B
utxo_A = next(u for u in rpc.listunspent() if u["address"] == A)

raw_AB = rpc.createrawtransaction(
    [{"txid": utxo_A["txid"], "vout": utxo_A["vout"]}],
    {B: 0.5}
)

funded_AB = rpc.fundrawtransaction(raw_AB, {"changeAddress": A})
signed_AB = rpc.signrawtransactionwithwallet(funded_AB["hex"])

txid_AB = rpc.sendrawtransaction(signed_AB["hex"])
rpc.generatetoaddress(1, miner)

legacy_ab_tx = rpc.decoderawtransaction(signed_AB["hex"])

print("\nTXID A->B:", txid_AB)

# B -> C
utxo_B = next(u for u in rpc.listunspent() if u["address"] == B)

raw_BC = rpc.createrawtransaction(
    [{"txid": utxo_B["txid"], "vout": utxo_B["vout"]}],
    {C: 0.25}
)

funded_BC = rpc.fundrawtransaction(raw_BC, {"changeAddress": B})
signed_BC = rpc.signrawtransactionwithwallet(funded_BC["hex"])

txid_BC = rpc.sendrawtransaction(signed_BC["hex"])
rpc.generatetoaddress(1, miner)

legacy_bc_tx = rpc.decoderawtransaction(signed_BC["hex"])

print("TXID B->C:", txid_BC)

# SEGWIT TRANSACTIONS (P2SH-P2WPKH)
print("\n========== SEGWIT TRANSACTIONS ==========")

A2 = rpc.getnewaddress("", "p2sh-segwit")
B2 = rpc.getnewaddress("", "p2sh-segwit")
C2 = rpc.getnewaddress("", "p2sh-segwit")

print("Address A':", A2)
print("Address B':", B2)
print("Address C':", C2)

# Fund A'
rpc.sendtoaddress(A2, 1)
rpc.generatetoaddress(1, miner)

# A' -> B'
utxo_A2 = next(u for u in rpc.listunspent() if u["address"] == A2)

raw_AB2 = rpc.createrawtransaction(
    [{"txid": utxo_A2["txid"], "vout": utxo_A2["vout"]}],
    {B2: 0.5}
)

funded_AB2 = rpc.fundrawtransaction(raw_AB2, {"changeAddress": A2})
signed_AB2 = rpc.signrawtransactionwithwallet(funded_AB2["hex"])

txid_AB2 = rpc.sendrawtransaction(signed_AB2["hex"])
rpc.generatetoaddress(1, miner)

segwit_ab_tx = rpc.decoderawtransaction(signed_AB2["hex"])

print("\nTXID A'->B':", txid_AB2)

# B' -> C'
utxo_B2 = next(u for u in rpc.listunspent() if u["address"] == B2)

raw_BC2 = rpc.createrawtransaction(
    [{"txid": utxo_B2["txid"], "vout": utxo_B2["vout"]}],
    {C2: 0.25}
)

funded_BC2 = rpc.fundrawtransaction(raw_BC2, {"changeAddress": B2})
signed_BC2 = rpc.signrawtransactionwithwallet(funded_BC2["hex"])

txid_BC2 = rpc.sendrawtransaction(signed_BC2["hex"])
rpc.generatetoaddress(1, miner)

segwit_bc_tx = rpc.decoderawtransaction(signed_BC2["hex"])

print("TXID B'->C':", txid_BC2)

# ANALYSIS
print("\n========== TRANSACTION SIZE ANALYSIS ==========")

t1 = legacy_ab_tx
t2 = legacy_bc_tx
t3 = segwit_ab_tx
t4 = segwit_bc_tx

print("Legacy A->B :", t1["size"], "bytes,", t1["vsize"], "vbytes,", t1["weight"], "weight")
print("Legacy B->C :", t2["size"], "bytes,", t2["vsize"], "vbytes,", t2["weight"], "weight")

print("SegWit A->B :", t3["size"], "bytes,", t3["vsize"], "vbytes,", t3["weight"], "weight")
print("SegWit B->C :", t4["size"], "bytes,", t4["vsize"], "vbytes,", t4["weight"], "weight")

avg_legacy = (t1["vsize"] + t2["vsize"]) / 2
avg_segwit = (t3["vsize"] + t4["vsize"]) / 2

diff = avg_legacy - avg_segwit
pct = (diff / avg_legacy) * 100

print("\nAverage Legacy vsize :", avg_legacy)
print("Average SegWit vsize :", avg_segwit)

print("SegWit reduces effective transaction size by", round(pct,2), "%")

print("\nScript structure comparison:")
print("Legacy uses OP_DUP OP_HASH160 OP_EQUALVERIFY OP_CHECKSIG")
print("Unlocking data (signature + pubkey) is stored in scriptSig")

print("\nSegWit uses OP_HASH160 OP_EQUAL (P2SH wrapper)")
print("Signature and pubkey are stored separately in the witness field")
print("Witness data counts as 1/4 weight, reducing effective vsize")

print("\nTransaction chain completed successfully.")
