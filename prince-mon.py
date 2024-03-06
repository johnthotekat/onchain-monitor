import time
from web3 import Web3
import json
import requests
import random


UNISWAP_FACTORY_V2="0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27ead9083C756Cc2"

# Array of RPC URLs
rpc_urls = [
    "https://eth-mainnet.public.blastapi.io",
    "https://ethereum.publicnode.com",
    "https://rpc.flashbots.net/",
    "https://cloudflare-eth.com/",
    "https://ethereum.publicnode.com"
    # Add more RPC URLs as needed
]

def switch_rpc_url():
    """Randomly switch the RPC URL for the Web3 provider."""
    rpc_url = random.choice(rpc_urls)
    web3.provider = Web3.HTTPProvider(rpc_url)
    print(f"Switched to RPC URL: {rpc_url}")


web3 = Web3(Web3.HTTPProvider(rpc_urls[0]))

# Path to your ABI file
abi_file_path = 'abis/uniswap-factory-abi.json'

# Load the Uniswap Factory ABI
with open(abi_file_path, 'r') as abi_file:
    uniswap_factory_abi = json.load(abi_file)

factory_contract = web3.eth.contract(address=UNISWAP_FACTORY_V2, abi=uniswap_factory_abi)


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


# ABI for interacting with ERC-20 tokens to fetch their name
# This ABI snippet includes only the `name` function for simplicity
token_name_abi = [
    {
        "constant": True,
        "inputs": [],
        "name": "name",
        "outputs": [{"name": "", "type": "string"}],
        "payable": False,
        "stateMutability": "view",
        "type": "function",
    }
]

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

previous_reserves = {}


def fetch_uniswap_liquidity_drop(pair_address, threshold=0.1):
    # GraphQL query to fetch current reserves for the pair
    query = """
    query ($pairAddress: String!) {
      pair(id: $pairAddress) {
        token0 {
          symbol
          name
        }
        token1 {
          symbol
          name
        }
        reserve0,
        reserve1,
        totalSupply,
        reserveUSD
      }
    }
    """

    # The Graph API URL for Uniswap V2
    url = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'

    # Making the POST request to The Graph's GraphQL endpoint
    response = requests.post(url, json={'query': query, 'variables': {'pairAddress': pair_address}})
    data = response.json()

    # Check if data retrieval was successful
    if response.status_code == 200 and 'data' in data and 'pair' in data['data']:
        current_reserves = data['data']['pair']
        print(f"Current Reserves: {current_reserves}")

        # Check if pair's previous USD reserve exists
        if pair_address in previous_reserves:
            previous_reserve_usd = previous_reserves[pair_address]
            current_reserve_usd = float(current_reserves['reserveUSD'])

            # Check for significant drop in liquidity
            if previous_reserve_usd * (1 - threshold) > current_reserve_usd:
                print("Significant drop in liquidity detected.")
            else:
                print("No significant drop in liquidity detected.")

            # Update the dictionary with the current reserveUSD for future checks
            previous_reserves[pair_address] = current_reserve_usd
        else:
            # Save the current reserveUSD in the dictionary if not present
            current_reserve_usd = float(current_reserves['reserveUSD'])
            previous_reserves[pair_address] = current_reserve_usd
            print(f"Saved current USD reserve for pair {pair_address}.")
    else:
        print("Error fetching data:", data.get('errors'))


def get_token_decimals(token_address):
    token_contract = web3.eth.contract(address=token_address, abi=token_abi)
    try:
        return token_contract.functions.decimals().call()
    except Exception as e:
        print(f"Error fetching decimals for token {token_address}: {e}")
        return 18  # Assume 18 decimals if unable to fetch
    

def get_token_decimals(token_address):
    token_contract = web3.eth.contract(address=token_address, abi=token_abi)
    try:
        return token_contract.functions.decimals().call()
    except Exception as e:
        print(f"Error fetching decimals for token {token_address}: {e}")
        return


def label_token_by_reserve(eth_reserve):
    if eth_reserve > 15:
        return "Really Good"
    elif eth_reserve > 10:
        return "Good"
    elif eth_reserve > 5:
        return "Medium"
    else:
        return "Low"
    

def get_token_name(token_address):
    """Get the name of a token given its address."""
    token_contract = web3.eth.contract(address=token_address, abi=token_name_abi)
    return token_contract.functions.name().call()


def get_token_price_usd(token_address):
    """
    Fetch the USD price of a token using an external API.
    This is a simplified placeholder function. You'll need to adapt it based on the API you choose to use.
    """
    # Example URL for CoinGecko API (this is a placeholder, adjust according to actual API documentation)
    url = f"https://api.coingecko.com/api/v3/simple/token_price/ethereum?contract_addresses={token_address}&vs_currencies=usd"
    response = requests.get(url)
    data = response.json()
    # Assuming the API returns a structure where the token address is a key to its price information
    price_usd = data[token_address.lower()]['usd']
    return price_usd


def get_token_price_from_uniswap(pair_address):
    pair_contract = web3.eth.contract(address=pair_address, abi=uniswap_pair_abi)
    reserves = pair_contract.functions.getReserves().call()
    reserve0, reserve1, _ = reserves
    
    # Assuming you want the price of token0 in terms of token1
    price_of_token0_in_token1 = reserve1 / reserve0
    
    return price_of_token0_in_token1


def get_tokens_from_uniswap_pair(pair_address):
    """Get token addresses from a Uniswap pair address."""
    pair_contract = web3.eth.contract(address=pair_address, abi=uniswap_pair_abi)
    token0_address = pair_contract.functions.token0().call()
    token1_address = pair_contract.functions.token1().call()
    return token0_address, token1_address

def get_uniswap_pair(token_a, token_b):
    """Get the Uniswap pair address for two tokens."""
    pair_address = factory_contract.functions.getPair(token_a, token_b).call()
    print("here")
    return pair_address


def test_get_uniswap_pair():
# Example usage
# Token addresses in checksum format
    token_a_checksum = Web3.to_checksum_address("0x6b175474e89094c44da98b954eedeac495271d0f")  # DAI
    token_b_checksum = Web3.to_checksum_address("0xc02aaa39b223fe8d0a0e5c4f27ead9083c756cc2")  # WETH
    print (get_uniswap_pair(token_a_checksum, token_b_checksum))


# Function to analyze transactions in each new block for Uniswap trades
def analyze_uniswap_transactions():
    latest_block = web3.eth.get_block('latest').number
    while True:
        switch_rpc_url()
        block = web3.eth.get_block(latest_block, full_transactions=True)
        block_timestamp = block.timestamp
        # Convert block timestamp to human-readable format, if needed
        readable_timestamp = time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(block_timestamp))

        for tx in block.transactions:
            # Assuming tx is a transaction in the block
            if tx.to:  # Only proceed if it's a transaction to a contract
                receipt = web3.eth.get_transaction_receipt(tx.hash)
                # Check if the transaction involves a Uniswap contract by examining the logs
                # This requires knowledge of Uniswap contract event signatures

                for log in receipt.logs:
                    # Example check for a Uniswap swap event signature
                    # This is highly simplified and would need to be adjusted for the specific Uniswap version and contract
                    swap_event_signature_hash = web3.keccak(text="Swap(address,uint256,uint256,uint256,uint256,address)").hex()
                    

                    if log.topics[0].hex() == swap_event_signature_hash:
                        pair_contract = web3.eth.contract(address=log.address, abi=uniswap_pair_abi)
                        token0_address = pair_contract.functions.token0().call()
                        token1_address = pair_contract.functions.token1().call()
                        token0_name = get_token_name(token0_address)
                        token1_name = get_token_name(token1_address)
                        token0_decimals = get_token_decimals(token0_address)
                        token1_decimals = get_token_decimals(token1_address)
                        reserves = pair_contract.functions.getReserves().call()
                        reserve0 = reserves[0] / (10 ** token0_decimals)
                        reserve1 = reserves[1] / (10 ** token1_decimals)

                        # fetch_uniswap_liquidity_drop(log.address)
                        
                        data = {
                            "value":    format(web3.from_wei(tx.value, 'ether'), '.14f'),
                            "timestamp": block_timestamp,
                            "readable_timestamp": readable_timestamp,
                            "block_number": latest_block,
                            "transaction_hash": tx.hash.hex(),
                            "pair_address": log.address,
                            "transaction_type": "swap",
                            "swap_type": "SELL" if token0_address == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" else "BUY",
                            "base_token_address": token0_address,
                            "base_token_name": token0_name,
                            "base_token_decimals": token0_decimals,
                            "base_token_reserve": reserve0,
                            "quote_token_address": token1_address,
                            "quote_token_name": token1_name,
                            "quote_token_decimals": token1_decimals,
                            "quote_token_reserve": reserve1
                        }
                        if (token0_address == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" and reserve0 > 10) or (token1_address == "0xC02aaA39b223FE8D0A0e5C4F27eAD9083C756Cc2" and reserve1 > 10):
                            print(data)
                            with open('abis/uniswap_transactions.json', 'a') as file:
                                json.dump(data, file)
                                file.write('\n')  # Writ

        latest_block += 1


if __name__ == "__main__":
    analyze_uniswap_transactions()