from web3 import Web3

# Initialize Web3
web3 = Web3(Web3.HTTPProvider('https://mainnet.infura.io/v3/6c21df2a8dcb4a77b9bbcc1b65ee9ded'))

# Address of the Uniswap pair contract
pair_contract_address = Web3.to_checksum_address('0xCF6dAAB95c476106ECa715D48DE4b13287ffDEAa')

# ABI for the pair contract (simplified to include only the Sync event)
pair_contract_abi = [{
    "anonymous": False,
    "inputs": [
        {"indexed": False, "internalType": "uint112", "name": "reserve0", "type": "uint112"},
        {"indexed": False, "internalType": "uint112", "name": "reserve1", "type": "uint112"}
    ],
    "name": "Sync",
    "type": "event"
}]

token_abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "decimals",
        "outputs": [{"name": "", "type": "uint8"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]


def get_token_decimals(token_address):
    token_contract = web3.eth.contract(address=token_address, abi=token_abi)
    try:
        return token_contract.functions.decimals().call()
    except Exception as e:
        print(f"Error fetching decimals for token {token_address}: {e}")
        return 18  # Assume 18 decimals if unable to fetch

# Create the contract instance
pair_contract = web3.eth.contract(address=pair_contract_address, abi=pair_contract_abi)

# Create a filter for the Sync event
sync_filter = pair_contract.events.Sync.create_filter(fromBlock='latest')

# Use this filter to get new entries (this is a blocking call in a loop for demonstration)
while True:
    for event in sync_filter.get_new_entries():
        print(f"New Sync Event: reserve0 = {event['args']['reserve0']}, reserve1 = {event['args']['reserve1']}")
