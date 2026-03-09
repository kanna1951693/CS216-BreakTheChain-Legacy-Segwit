from bitcoinrpc.authproxy import AuthServiceProxy

rpc_user = "user"
rpc_password = "pass"

rpc = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@127.0.0.1:18443")
print("Connected to chain:", rpc.getblockchaininfo()["chain"])

try:
    rpc.loadwallet("testwallet")
    print("Wallet loaded")
except Exception as e:
    if "already loaded" in str(e):
        print("Wallet already loaded")
    else:
        rpc.createwallet("testwallet")
        print("Wallet created")

miner = rpc.getnewaddress()
rpc.generatetoaddress(101, miner)
print("Mined 101 blocks")

A = rpc.getnewaddress("", "p2sh-segwit")
B = rpc.getnewaddress("", "p2sh-segwit")
C = rpc.getnewaddress("", "p2sh-segwit")
print(f"Address A :{A}")
print(f"Address B :{B}")
print(f"Address C :{C}")

rpc.sendtoaddress(A, 1)
rpc.generatetoaddress(1, miner)

# TRANSACTION A → B
utxo_A = next(u for u in rpc.listunspent() if u["address"] == A)
fundAB = rpc.fundrawtransaction(
    rpc.createrawtransaction(
        [{"txid": utxo_A["txid"], "vout": utxo_A["vout"]}],
        {B: 0.5}
    ),
    {"changeAddress": A}
)
decoded_AB = rpc.decoderawtransaction(fundAB["hex"])

print("\n========= TRANSACTION A → B =========")
print(f"Fee   : {fundAB['fee']} BTC")
print(f"Size  : {decoded_AB['size']} bytes")
print(f"vsize : {decoded_AB['vsize']} vbytes")
print(f"Weight: {decoded_AB['weight']}")

print("\n[Locking Scripts - scriptPubKey]")
for vout in decoded_AB["vout"]:
    print(f"  Output {vout['n']} ({vout['scriptPubKey'].get('address','?')}):")
    print(f"    Type: {vout['scriptPubKey']['type']}")
    print(f"    ASM : {vout['scriptPubKey']['asm']}")
    print(f"    HEX : {vout['scriptPubKey']['hex']}")

signed_AB = rpc.signrawtransactionwithwallet(fundAB["hex"])
txid_AB = rpc.sendrawtransaction(signed_AB["hex"])
print(f"\nTXID A→B: {txid_AB}")
rpc.generatetoaddress(1, miner)

# TRANSACTION B → C
utxo_B = next(u for u in rpc.listunspent() if u["address"] == B)

fundBC = rpc.fundrawtransaction(
    rpc.createrawtransaction(
        [{"txid": utxo_B["txid"], "vout": utxo_B["vout"]}],
        {C: 0.25}
    ),
    {"changeAddress": B}
)
decoded_BC = rpc.decoderawtransaction(fundBC["hex"])
signed_BC = rpc.signrawtransactionwithwallet(fundBC["hex"])
decoded_signed_BC = rpc.decoderawtransaction(signed_BC["hex"])

print("\n========= TRANSACTION B → C =========")
print(f"Fee   : {fundBC['fee']} BTC")
print(f"Size  : {decoded_BC['size']} bytes")
print(f"vsize : {decoded_BC['vsize']} vbytes")
print(f"Weight: {decoded_BC['weight']}")

print("\n[Unlocking Scripts - scriptSig + Witness]")
for vin in decoded_signed_BC["vin"]:
    print(f"  ScriptSig ASM : {vin['scriptSig']['asm']}")
    print(f"  ScriptSig HEX : {vin['scriptSig']['hex']}")
    if "txinwitness" in vin:
        print(f"  Witness[0] (sig)    : {vin['txinwitness'][0]}")
        print(f"  Witness[1] (pubkey) : {vin['txinwitness'][1]}")

txid_BC = rpc.sendrawtransaction(signed_BC["hex"])
print(f"\nTXID B→C: {txid_BC}")
rpc.generatetoaddress(1, miner)
