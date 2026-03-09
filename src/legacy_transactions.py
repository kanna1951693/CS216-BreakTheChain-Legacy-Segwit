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

# generate three legacy (P2PKH) addresses
A = rpc.getnewaddress("", "legacy")
B = rpc.getnewaddress("", "legacy")
C = rpc.getnewaddress("", "legacy")
print(f"Address A : {A}")
print(f"Address B : {B}")
print(f"Address C : {C}")

# fund address A and confirm
rpc.sendtoaddress(A, 1)
rpc.generatetoaddress(1, miner)

# TRANSACTION A → B
# find UTXO belonging to A
utxo_A = next(x for x in rpc.listunspent() if x["address"] == A)

# create, fund, sign and decode signed transaction
tx_proposal_AB = rpc.fundrawtransaction(
    rpc.createrawtransaction(
        [{"txid": utxo_A["txid"], "vout": utxo_A["vout"]}],
        {B: 0.5}
    ),
    {"changeAddress": A}
)
signed_AB = rpc.signrawtransactionwithwallet(tx_proposal["hex"])
decoded_AB = rpc.decoderawtransaction(signed_AB["hex"])  # decode signed tx

print("\n======== TRANSACTION A → B ========")
print(f"Fee   : {tx_proposal_AB['fee']} BTC")
print(f"Size  : {decoded_AB['size']} bytes")
print(f"vsize : {decoded_AB['vsize']} vbytes")
print(f"Weight: {decoded_AB['weight']}")

# locking script (scriptPubKey) locks coins to address B
print("\n[Locking Scripts - scriptPubKey]")
for vout in decoded_AB["vout"]:
    print(f"  Output {vout['n']} ({vout['scriptPubKey'].get('address','?')}):")
    print(f"    Type: {vout['scriptPubKey']['type']}")
    print(f"    ASM : {vout['scriptPubKey']['asm']}")
    print(f"    HEX : {vout['scriptPubKey']['hex']}")

txid_AB = rpc.sendrawtransaction(signed_AB["hex"])
print(f"\nTXID A→B: {txid_AB}")
rpc.generatetoaddress(1, miner)

# TRANSACTION B → C
# find UTXO at B created by previous transaction
utxo_B = next(x for x in rpc.listunspent() if x["address"] == B)

# create, fund, sign and decode signed transaction
tx_proposal_BC = rpc.fundrawtransaction(
    rpc.createrawtransaction(
        [{"txid": utxo_B["txid"], "vout": utxo_B["vout"]}],
        {C: 0.25}
    ),
    {"changeAddress": B}
)
signed_BC = rpc.signrawtransactionwithwallet(funded_BC["hex"])
decoded_signed_BC = rpc.decoderawtransaction(signed_BC["hex"])  # decode signed tx

print("\n========== TRANSACTION B → C ==========")
print(f"Fee   : {tx_proposal_BC['fee']} BTC")
print(f"Size  : {decoded_signed_BC['size']} bytes")
print(f"vsize : {decoded_signed_BC['vsize']} vbytes")
print(f"Weight: {decoded_signed_BC['weight']}")

# unlocking script (scriptSig) provides signature and pubkey to spend B's UTXO
print("\n[Unlocking Scripts - scriptSig]")
for vin in decoded_signed_BC["vin"]:
    print(f"  ASM : {vin['scriptSig']['asm']}")
    print(f"  HEX : {vin['scriptSig']['hex']}")

# broadcast and confirm
txid_BC = rpc.sendrawtransaction(signed_BC["hex"])
print(f"\nTXID B→C: {txid_BC}")
rpc.generatetoaddress(1, miner)
