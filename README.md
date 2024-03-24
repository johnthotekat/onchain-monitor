# Uniswap Liquidity Monitoring Tool

## Overview

This Python script is designed for interacting with the Ethereum blockchain and Uniswap V2 contracts. It provides functionality for fetching liquidity information, token details, and monitoring Uniswap transaction activities in real-time. Utilizing the Web3.py library, it connects to the Ethereum network to query smart contracts, perform transactions, and analyze blockchain data.

## Features

- **RPC URL Switching**: Randomly switches the RPC URL from a predefined list to ensure consistent access to the Ethereum network.
- **Uniswap Factory Contract Interaction**: Loads the Uniswap Factory ABI and allows querying of Uniswap pair addresses.
- **Token Information Retrieval**: Fetches token names and decimals using minimal ABI definitions.
- **Liquidity Drop Monitoring (Yet to be completed)**: Checks for significant liquidity drops in Uniswap pairs by comparing current reserves to previous values.
- **Price Information**: Includes functions to get token prices from Uniswap pairs and external APIs (placeholder for CoinGecko).
- **Transaction Analysis**: Analyzes transactions in each new block for Uniswap trades, identifying swap events and extracting relevant information.

## Requirements

- Python 3.x
- `web3` Python package
- `requests` Python package
- Access to Ethereum RPC URLs
- Uniswap Factory ABI (`abis/uniswap-factory-abi.json`)

## Installation

1. Ensure Python 3 and pip are installed.
2. Install required packages:
3. Clone the repository or download the script and ABI file.

## Usage

1. Ensure the `uniswap-factory-abi.json` file is placed in the `abis` directory.
2. Run the script:
3. The script will automatically start analyzing Uniswap transactions and monitor liquidity.
4. The RPC URL's used in the code are scrapped from Github code. Please use you own RPC URL's 

## Configuration

- **RPC URLs**: Modify the `rpc_urls` list to include additional Ethereum RPC endpoints as needed.
- **Uniswap Contracts**: Update the `UNISWAP_FACTORY_V2` and `WETH_ADDRESS` constants to point to the correct contract addresses if they change.
- **ABI Files**: Ensure ABI files for Uniswap and tokens are correctly formatted and located in the `abis` directory.

## Functions

### Main Functions

- `switch_rpc_url()`: Switches the Web3 provider's RPC URL.
- `fetch_uniswap_liquidity_drop(pair_address, threshold)`: Checks for significant drops in liquidity for a given Uniswap pair.
- `get_token_price_usd(token_address)`: Fetches the USD price of a token using an external API (placeholder).
- `analyze_uniswap_transactions()`: Monitors and analyzes transactions for Uniswap swap events in real-time.

### Helper Functions

- `get_token_name(token_address)`: Returns the name of a token.
- `get_token_decimals(token_address)`: Returns the decimal places of a token.
- `get_tokens_from_uniswap_pair(pair_address)`: Retrieves token addresses from a Uniswap pair.
- `get_uniswap_pair(token_a, token_b)`: Returns the Uniswap pair address for two tokens.

## Notes

- This script is a utility tool for blockchain developers and enthusiasts. It requires a basic understanding of Ethereum, smart contracts, and Web3 technology.
- The script includes placeholder functions and values that may need adjustment based on your specific use case or changes in external APIs.

## Disclaimer

This tool is provided "as is", without warranty of any kind. Use at your own risk. The author is not responsible for any loss or damage that may occur as a result of using this script.
