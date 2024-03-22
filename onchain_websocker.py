import time
from web3 import Web3
import json
import requests
import random

# Constants
UNISWAP_FACTORY_V2 = "0x5C69bEe701ef814a2B6a3EDD4B1652CB9cc5aA6f"
WETH_ADDRESS = "0xC02aaA39b223FE8D0A0e5C4F27ead9083C756Cc2"
RPC_URLS = [
    "https://eth-mainnet.public.blastapi.io",
    "https://ethereum.publicnode.com",
    "https://rpc.flashbots.net/",
    "https://cloudflare-eth.com/",
    "https://ethereum.publicnode.com"
]
ABI_FILE_PATH = 'abis/uniswap-factory-abi.json'

class EthereumDataFetcher:
    def __init__(self):
        self.web3 = Web3(Web3.HTTPProvider(random.choice(RPC_URLS)))
        self.factory_contract = self.load_factory_contract()
        self.previous_reserves = {}

    def switch_rpc_url(self):
        """Switches the Web3 provider's RPC URL randomly."""
        rpc_url = random.choice(RPC_URLS)
        self.web3.provider = Web3.HTTPProvider(rpc_url)
        print(f"Switched to RPC URL: {rpc_url}")

    def load_factory_contract(self):
        """Loads the Uniswap Factory contract."""
        with open(ABI_FILE_PATH, 'r') as abi_file:
            uniswap_factory_abi = json.load(abi_file)
        return self.web3.eth.contract(address=UNISWAP_FACTORY_V2, abi=uniswap_factory_abi)

    def get_token_decimals(self, token_address):
        """Fetch token decimals."""
        token_contract = self.load_contract(token_address, 'path/to/token_abi.json')  # Simplified for demonstration
        try:
            return token_contract.functions.decimals().call()
        except Exception as e:
            print(f"Error fetching decimals for token {token_address}: {e}")
            return 18  # Default to 18 if there's an error

    def get_token_name(self, token_address):
        """Get the name of a token given its address."""
        token_contract = self.load_contract(token_address, 'path/to/token_name_abi.json')  # Simplified for demonstration
        return token_contract.functions.name().call()