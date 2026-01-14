const API_URL = 'http://localhost:5001'

/**
 * Get blockchain connection info from backend
 */
export async function getBlockchainInfo() {
  try {
    const res = await fetch(`${API_URL}/blockchain/info`)
    return res.json()
  } catch (err) {
    console.error('Blockchain info error:', err)
    return { connected: false, error: 'Failed to connect to server' }
  }
}

/**
 * Get on-chain commitment for a specific game
 */
export async function getGameCommitment(gameId) {
  try {
    const res = await fetch(`${API_URL}/blockchain/game/${gameId}`)
    return res.json()
  } catch (err) {
    console.error('Get game commitment error:', err)
    return { error: 'Failed to fetch commitment' }
  }
}

/**
 * Format a transaction hash for display
 */
export function formatTxHash(hash) {
  if (!hash) return ''
  return `${hash.slice(0, 10)}...${hash.slice(-8)}`
}

/**
 * Get Sepolia block explorer URL for a transaction
 */
export function getExplorerUrl(txHash) {
  return `https://sepolia.etherscan.io/tx/${txHash}`
}

/**
 * Get Sepolia block explorer URL for an address
 */
export function getAddressUrl(address) {
  return `https://sepolia.etherscan.io/address/${address}`
}
