import requests
import json

# The GraphQL endpoint for Uniswap V2 on The Graph
GRAPH_URL = 'https://api.thegraph.com/subgraphs/name/uniswap/uniswap-v2'

# The specific pair address you're interested in (as an example)
pair_address = '0xd420D5F24225702A68dDF21242D5EEf816DC2e6d'

# The GraphQL query, same as the example provided above
query = """
query GetPairDetails($pairAddress: ID!) {
  pair(id: $pairAddress) {
    id
    token0 {
      id
      symbol
      name
    }
    token1 {
      id
      symbol
      name
    }
    reserve0
    reserve1
    totalSupply
    reserveUSD
    volumeToken0
    volumeToken1
    createdAtTimestamp
  }
}
"""

# Executing the GraphQL query
response = requests.post(
    GRAPH_URL,
    json={'query': query, 'variables': {'pairAddress': pair_address}}
)

# Parsing the response
data = response.json()

# Output the result
print(json.dumps(data, indent=2))
