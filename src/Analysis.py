from bitcoinrpc.authproxy import AuthServiceProxy

rpc = AuthServiceProxy("http://user:pass@127.0.0.1:18443")

try:
    rpc.loadwallet("testwallet")
except:
    pass

miner = rpc.getnewaddress()
rpc.generatetoaddress(101, miner)

# legacy addresses
A = rpc.getnewaddress("", "legacy")
B = rpc.getnewaddress("", "legacy")
C = rpc.getnewaddress("", "legacy")
rpc.sendtoaddress(A, 1)
rpc.generatetoaddress(1, miner)

utxo_A = next(u for u in rpc.listunspent() if u["address"] == A)
funded_AB = rpc.fundrawtransaction(rpc.createrawtransaction([{"txid": utxo_A["txid"], "vout": utxo_A["vout"]}], {B: 0.5}), {"changeAddress": A})
signed_AB = rpc.signrawtransactionwithwallet(funded_AB["hex"])
legacy_ab_tx = rpc.decoderawtransaction(funded_AB["hex"])
txid_AB = rpc.sendrawtransaction(signed_AB["hex"])
rpc.generatetoaddress(1, miner)

utxo_B = next(u for u in rpc.listunspent() if u["address"] == B)
funded_BC = rpc.fundrawtransaction(rpc.createrawtransaction([{"txid": utxo_B["txid"], "vout": utxo_B["vout"]}], {C: 0.25}), {"changeAddress": B})
signed_BC = rpc.signrawtransactionwithwallet(funded_BC["hex"])
legacy_bc_tx = rpc.decoderawtransaction(funded_BC["hex"])
txid_BC = rpc.sendrawtransaction(signed_BC["hex"])
rpc.generatetoaddress(1, miner)

# segwit addresses
A2 = rpc.getnewaddress("", "p2sh-segwit")
B2 = rpc.getnewaddress("", "p2sh-segwit")
C2 = rpc.getnewaddress("", "p2sh-segwit")
rpc.sendtoaddress(A2, 1)
rpc.generatetoaddress(1, miner)

utxo_A2 = next(u for u in rpc.listunspent() if u["address"] == A2)
funded_AB2 = rpc.fundrawtransaction(rpc.createrawtransaction([{"txid": utxo_A2["txid"], "vout": utxo_A2["vout"]}], {B2: 0.5}), {"changeAddress": A2})
signed_AB2 = rpc.signrawtransactionwithwallet(funded_AB2["hex"])
segwit_ab_tx = rpc.decoderawtransaction(funded_AB2["hex"])
txid_AB2 = rpc.sendrawtransaction(signed_AB2["hex"])
rpc.generatetoaddress(1, miner)

utxo_B2 = next(u for u in rpc.listunspent() if u["address"] == B2)
funded_BC2 = rpc.fundrawtransaction(rpc.createrawtransaction([{"txid": utxo_B2["txid"], "vout": utxo_B2["vout"]}], {C2: 0.25}), {"changeAddress": B2})
signed_BC2 = rpc.signrawtransactionwithwallet(funded_BC2["hex"])
segwit_bc_tx = rpc.decoderawtransaction(funded_BC2["hex"])
txid_BC2 = rpc.sendrawtransaction(signed_BC2["hex"])
rpc.generatetoaddress(1, miner)

# analysis
t1 = legacy_ab_tx
t2 = legacy_bc_tx
t3 = segwit_ab_tx
t4 = segwit_bc_tx

print("legacy a->b:", t1["size"], "bytes,", t1["vsize"], "vsize,", t1["weight"], "weight")
print("legacy b->c:", t2["size"], "bytes,", t2["vsize"], "vsize,", t2["weight"], "weight")
print("segwit a->b:", t3["size"], "bytes,", t3["vsize"], "vsize,", t3["weight"], "weight")
print("segwit b->c:", t4["size"], "bytes,", t4["vsize"], "vsize,", t4["weight"], "weight")

avg1 = (t1["vsize"] + t2["vsize"]) / 2
avg2 = (t3["vsize"] + t4["vsize"]) / 2
diff = avg1 - avg2
pct = (diff / avg1) * 100

print("\navg legacy vsize:", avg1)
print("avg segwit vsize:", avg2)
print("segwit saves around", round(pct, 1), "% in vsize")

print("\nlegacy locks with OP_DUP OP_HASH160, unlocks with sig+pubkey in scriptsig")
print("segwit locks with OP_HASH160 OP_EQUAL, witness carries sig+pubkey separately")
print("witness bytes counted as 1/4 so vsize drops even if raw size is similar")
