from bitcoinrpc.authproxy import AuthServiceProxy

rpc_user = "user"
rpc_password = "pass"

# connect to local regtest node
rpc = AuthServiceProxy(f"http://{rpc_user}:{rpc_password}@127.0.0.1:18443")
print("Connected to chain:", rpc.getblockchaininfo()["chain"])

# load or create wallet
try:
    rpc.loadwallet("testwallet")
    print("Wallet loaded")
except Exception as e:
    if "already loaded" in str(e):
        print("Wallet already loaded")
    else:
        rpc.createwallet("testwallet")
        print("Wallet created")

# mine 101 blocks so coinbase is spendable
miner = rpc.getnewaddress()
rpc.generatetoaddress(101, miner)
print("Mined 101 blocks")

# generate three p2sh-segwit addresses
addr_A = rpc.getnewaddress("", "p2sh-segwit")
addr_B = rpc.getnewaddress("", "p2sh-segwit")
addr_C = rpc.getnewaddress("", "p2sh-segwit")
print(f"Address A : {addr_A}")
print(f"Address B : {addr_B}")
print(f"Address C : {addr_C}")

# fund address A and confirm
rpc.sendtoaddress(addr_A, 1)
rpc.generatetoaddress(1, miner)

# TRANSACTION A → B
# find UTXO belonging to A
unspent_A = next(x for x in rpc.listunspent() if x["address"] == addr_A)

# create, fund, sign and decode signed transaction
raw_proposal_AB = rpc.fundrawtransaction(
    rpc.createrawtransaction(
        [{"txid": unspent_A["txid"], "vout": unspent_A["vout"]}],
        {addr_B: 0.5}
    ),
    {"changeAddress": addr_A}
)
sig_AB = rpc.signrawtransactionwithwallet(raw_proposal_AB["hex"])
result_AB = rpc.decoderawtransaction(sig_AB["hex"])

print("\n========= TRANSACTION A → B =========")
print(f"Fee   : {raw_proposal_AB['fee']} BTC")
print(f"Size  : {result_AB['size']} bytes")
print(f"vsize : {result_AB['vsize']} vbytes")
print(f"Weight: {result_AB['weight']}")

# locking script (scriptPubKey) locks coins to address B
print("\n[Locking Scripts - scriptPubKey]")
for vout in result_AB["vout"]:
    print(f"  Output {vout['n']} ({vout['scriptPubKey'].get('address','?')}):")
    print(f"    Type: {vout['scriptPubKey']['type']}")
    print(f"    ASM : {vout['scriptPubKey']['asm']}")
    print(f"    HEX : {vout['scriptPubKey']['hex']}")

txid_AB = rpc.sendrawtransaction(sig_AB["hex"])
print(f"\nTXID A→B: {txid_AB}")
rpc.generatetoaddress(1, miner)

# TRANSACTION B → C
# find UTXO at B created by previous transaction
unspent_B = next(x for x in rpc.listunspent() if x["address"] == addr_B)

# create, fund, sign and decode signed transaction
raw_proposal_BC = rpc.fundrawtransaction(
    rpc.createrawtransaction(
        [{"txid": unspent_B["txid"], "vout": unspent_B["vout"]}],
        {addr_C: 0.25}
    ),
    {"changeAddress": addr_B}
)
sig_BC = rpc.signrawtransactionwithwallet(raw_proposal_BC["hex"])
result_BC = rpc.decoderawtransaction(sig_BC["hex"])

print("\n========= TRANSACTION B → C =========")
print(f"Fee   : {raw_proposal_BC['fee']} BTC")
print(f"Size  : {result_BC['size']} bytes")
print(f"vsize : {result_BC['vsize']} vbytes")
print(f"Weight: {result_BC['weight']}")

# unlocking script: scriptSig contains redeem script, witness carries sig+pubkey
print("\n[Unlocking Scripts - scriptSig + Witness]")
for vin in result_BC["vin"]:
    print(f"  ScriptSig ASM : {vin['scriptSig']['asm']}")
    print(f"  ScriptSig HEX : {vin['scriptSig']['hex']}")
    if "txinwitness" in vin:
        print(f"  Witness[0] (sig)    : {vin['txinwitness'][0]}")
        print(f"  Witness[1] (pubkey) : {vin['txinwitness'][1]}")

# broadcast and confirm
txid_BC = rpc.sendrawtransaction(sig_BC["hex"])
print(f"\nTXID B→C: {txid_BC}")
rpc.generatetoaddress(1, miner)
