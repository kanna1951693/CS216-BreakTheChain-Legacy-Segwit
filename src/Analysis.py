from bitcoinrpc.authproxy import AuthServiceProxy

rpc = AuthServiceProxy("http://user:pass@127.0.0.1:18443")

try:
    rpc.loadwallet("testwallet")
except:
    pass

legacy_ab = "511d7869d9511f50a354e85065da220b317a057f717604a903dcc0edb13b1e56"
legacy_bc = "97749925507614bc96f4ef971e794d79cdcf39eb876cee64b502c272ea6a35cd"
segwit_ab = "ed1a3eef7bdca712d15db2d7f193e93c580edf8c72ff4fc5ab11f6548a2fc8d5"
segwit_bc = "f40de80868cd54e5294786dbfef095255f7ea055364d25b83d8db7c257bb8c2d"

def get_info(txid):
    return rpc.decoderawtransaction(rpc.getrawtransaction(txid))

t1 = get_info(legacy_ab)
t2 = get_info(legacy_bc)
t3 = get_info(segwit_ab)
t4 = get_info(segwit_bc)

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
