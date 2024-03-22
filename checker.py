import requests
import json

import web3
from web3 import Web3

# Your list of RPC URLs
rpc_urls = [
    'https://mainnet.infura.io/v3/6c21df2a8dcb4a77b9bbcc1b65ee9ded',
    'https://mainnet.infura.io/v3/ed18016b210c4a1baf828458bd16feb',
    'https://mainnet.infura.io/v3/b2f4b3f635d8425c96854c3d28ba6bb0',
    'https://mainnet.infura.io/v3/8b9750710d56460d940aeff47967c4ba',
    'https://mainnet.infura.io/v3/6d6c70e65c77429482df5b64a4d0c943',
    'https://mainnet.infura.io/v3/9928b52099854248b3a096be07a6b23c'
]

# JSON-RPC request payload to fetch the current block number
payload = {
    "jsonrpc": "2.0",
    "method": "eth_blockNumber",
    "params": [],
    "id": 1
}

headers = {
    "Content-Type": "application/json"
}


uniswap_pair_abi = [
  {
    "constant": True,
    "inputs": [],
    "name": "getReserves",
    "outputs": [
      {
        "internalType": "uint112",
        "name": "reserve0",
        "type": "uint112"
      },
      {
        "internalType": "uint112",
        "name": "reserve1",
        "type": "uint112"
      },
      {
        "internalType": "uint32",
        "name": "blockTimestampLast",
        "type": "uint32"
      }
    ],
    "payable": False,
    "stateMutability": "view",
    "type": "function"
  },
  {
    "constant": True,
    "inputs": [],
    "name": "token0",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  },
  {
    "constant": True,
    "inputs": [],
    "name": "token1",
    "outputs": [
      {
        "internalType": "address",
        "name": "",
        "type": "address"
      }
    ],
    "stateMutability": "view",
    "type": "function"
  }
]


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
    # JSON-RPC payload to call `getReserves` on the pair contract
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_call",
        "params": [{
            "to": pair_address,
            "data": "0x0902f1ac"  # The `getReserves` function selector
        }, "latest"],
        "id": 1
    }
    response = requests.post(rpc_url, json=payload, headers={"Content-Type": "application/json"})
    if response.status_code == 200:
        data = response.json().get('result')
        # Decode the returned data (uint112 reserve0, uint112 reserve1, uint32 blockTimestampLast)
        if data:
            reserve0 = int(data[:66], 16)
            reserve1 = int('0x' + data[66:130], 16)
            print(f"Reserves for Uniswap pair at {pair_address}: {reserve0}, {reserve1}")
        else:
            print("Failed to fetch reserves.")
    else:
        print(f"Failed to fetch reserves for Uniswap pair: {pair_address}. HTTP error.")


def get_transactions_from_block(rpc_url, block_number):
    """Fetch all transactions from the specified block number using the given RPC URL."""
    payload = {
        "jsonrpc": "2.0",
        "method": "eth_getBlockByNumber",
        "params": [block_number, True],  # True to get full transaction objects
        "id": 1
    }
    try:
        response = requests.post(rpc_url, json=payload, headers=headers)
        web3 = Web3(Web3.HTTPProvider(rpc_url))
        if response.status_code == 200:
            transactions = response.json()['result']['transactions']
            print(f"Found {len(transactions)} transactions in block {int(block_number, 16)}")
            for tx in transactions:
                print(tx)
                receipt = web3.eth.get_transaction_receipt(tx['hash'])

                for log in receipt.logs:
                    # Example check for a Uniswap swap event signature
                    # This is highly simplified and would need to be adjusted for the specific Uniswap version and contract
                    swap_event_signature_hash = web3.keccak(
                        text="Swap(address,uint256,uint256,uint256,uint256,address)").hex()

                    if log.topics[0].hex() == swap_event_signature_hash:
                        pair_contract = web3.eth.contract(address=log.address, abi=uniswap_pair_abi)
                        token0_address = pair_contract.functions.token0().call()
                        token1_address = pair_contract.functions.token1().call()
                        token0_name, token0_decimals = fetch_token_details(rpc_url, token0_address)
                        token1_name, token1_decimals = fetch_token_details(rpc_url, token1_address)
                        print(f"{token0_name}--{token1_name}")
                        # token0_name = get_token_name(token0_address)
                        # token1_name = get_token_name(token1_address)
                        # token0_decimals = get_token_decimals(token0_address)
                        # token1_decimals = get_token_decimals(token1_address)
                        reserves = pair_contract.functions.getReserves().call()
                        reserve0 = reserves[0] / (10 ** token0_decimals)
                        reserve1 = reserves[1] / (10 ** token1_decimals)
                        print(f"{token0_name}:{reserve0}, {token1_name}: {reserve1}")
                        fetch_and_print_uniswap_pair_reserves(rpc_url=rpc_url, pair_address=log.address)
                        # fetch_uniswap_liquidity_drop(log.address)

                        # data = {
                        #     "value": format(web3.from_wei(tx.value, 'ether'), '.14f'),
                        #     "timestamp": block_timestamp,
                        #     "readable_timestamp": readable_timestamp,
                        #     "block_number": latest_block,
                        #     "transaction_hash": tx.hash.hex(),
                        #     "pair_address": log.address,
                        #     "transaction_type": "swap",
                        #     "swap_type": "SELL" if token0_address == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" else "BUY",
                        #     "base_token_address": token0_address,
                        #     "base_token_name": token0_name,
                        #     "base_token_decimals": token0_decimals,
                        #     "base_token_reserve": reserve0,
                        #     "quote_token_address": token1_address,
                        #     "quote_token_name": token1_name,
                        #     "quote_token_decimals": token1_decimals,
                        #     "quote_token_reserve": reserve1
                        # }
                        # if (token0_address == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" and reserve0 > 10) or (
                        #         token1_address == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" and reserve1 > 10):
                        #     print(data)
                        #     with open('abis/uniswap_transactions.json', 'a') as file:
                        #         json.dump(data, file)
                        #         file.write('\n')  # Writ
        else:
            print(f"Failed to fetch transactions for block {block_number}. Status code: {response.status_code}")
    except Exception as e:
        print(f"Error fetching transactions for block {block_number}: {e}")

# Check each RPC URL
for i, url in enumerate(rpc_urls):
    try:
        response = requests.post(url, json=payload, headers=headers)
        if response.status_code == 200 and 'result' in response.json():
            block_number = response.json()['result']
            print(f"RPC URL {url} is working. Current block: {int(block_number, 16)}")
            if i == 0:  # If it's the first RPC URL and it's working
                get_transactions_from_block(url, block_number)
                break  # Stop after processing the first working RPC URL
        else:
            print(f"RPC URL {url} is not working. Status code: {response.status_code}")
    except Exception as e:
        print(f"RPC URL {url} failed with error: {e}")
