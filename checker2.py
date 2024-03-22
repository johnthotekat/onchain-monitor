import requests
import json

# Placeholder Uniswap Router addresses (you'll want the actual addresses you're interested in)
uniswap_router_addresses = {
    "0x7a250d5630B4cF539739dF2C5dAcb4c659F2488D".lower(),  # Example Uniswap V2 Router
}

# Your list of RPC URLs
rpc_urls = [
    'https://mainnet.infura.io/v3/6c21df2a8dcb4a77b9bbcc1b65ee9ded',
    'https://mainnet.infura.io/v3/ed18016b210c4a1baf828458bd16feb',
    'https://mainnet.infura.io/v3/b2f4b3f635d8425c96854c3d28ba6bb0',
    'https://mainnet.infura.io/v3/8b9750710d56460d940aeff47967c4ba',
    'https://mainnet.infura.io/v3/6d6c70e65c77429482df5b64a4d0c943',
    'https://mainnet.infura.io/v3/9928b52099854248b3a096be07a6b23c'
]

# Simplified Pair ABI for fetching reserves
pair_abi = json.dumps([
    {
        "constant": True,
        "inputs": [],
        "name": "getReserves",
        "outputs": [
            {"internalType": "uint112", "name": "reserve0", "type": "uint112"},
            {"internalType": "uint112", "name": "reserve1", "type": "uint112"},
            {"internalType": "uint32", "name": "blockTimestampLast", "type": "uint32"}
        ],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token0",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "constant": True,
        "inputs": [],
        "name": "token1",
        "outputs": [{"internalType": "address", "name": "", "type": "address"}],
        "stateMutability": "view",
        "type": "function"
    }
])

# Simplified ERC20 ABI for fetching token symbols
token_abi = json.dumps([
    {
        "constant": True,
        "inputs": [],
        "name": "symbol",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function"
    }
])

headers = {
    "Content-Type": "application/json"
}

# Function to call a contract method using eth_call
def call_contract_method(rpc_url, contract_address, abi, method_name):
    data = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{
            "to": contract_address,
            "data": abi[method_name]  # This requires the ABI to be processed into a form where you can look up method data by name
        }, "latest"],
        "id": 1
    }
    response = requests.post(rpc_url, json=data, headers=headers)
    return response.json().get('result')


def fetch_token_details(rpc_url, token_address):
    # Payload for fetching the token's name
    name_payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{
            "to": token_address,
            "data": "0x06fdde03"  # The selector for the `name()` function
        }, "latest"],
        "id": 1
    }

    # Payload for fetching the token's decimals
    decimals_payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{
            "to": token_address,
            "data": "0x313ce567"  # The selector for the `decimals()` function
        }, "latest"],
        "id": 1
    }

    # Fetch the token's name
    name_response = requests.post(rpc_url, json=name_payload, headers={"Content-Type": "application/json"})
    name = ''
    if name_response.status_code == 200:
        name_data = name_response.json().get('result')
        name = bytes.fromhex(name_data[2:]).decode('utf-8', errors='ignore').rstrip('\x00')

    # Fetch the token's decimals
    decimals_response = requests.post(rpc_url, json=decimals_payload, headers={"Content-Type": "application/json"})
    decimals = 0
    if decimals_response.status_code == 200:
        decimals_data = decimals_response.json().get('result')
        decimals = int(decimals_data, 16)

    return name, decimals


def fetch_and_print_uniswap_pair_reserves(rpc_url, pair_address):
    # Obtain the addresses of the tokens in the pair
    token0_address = call_contract_method(rpc_url, pair_address, "token0")
    token1_address = call_contract_method(rpc_url, pair_address, "token1")

    # Fetch token details
    token0_name, token0_decimals = fetch_token_details(rpc_url, token0_address)
    token1_name, token1_decimals = fetch_token_details(rpc_url, token1_address)

    # Fetch reserves
    reserves = call_contract_method(rpc_url, pair_address, "getReserves")
    if reserves:
        reserve0, reserve1 = int(reserves[:66], 16), int('0x' + reserves[66:130], 16)
        print(f"Reserves for Uniswap pair {token0_name} / {token1_name} at {pair_address}:")
        print(f"{token0_name} ({token0_decimals} decimals): {reserve0 / (10 ** token0_decimals)}")
        print(f"{token1_name} ({token1_decimals} decimals): {reserve1 / (10 ** token1_decimals)}")
    else:
        print("Failed to fetch reserves.")

# This is a placeholder integration - you'd need to integrate the call to fetch_and_print_uniswap_pair_reserves
# appropriately into your workflow where you identify Uniswap transactions.
