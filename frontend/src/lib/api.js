const API_URL = 'http://localhost:5001'

export async function newGame(gridSize, mineCount, clientSeed = null) {
  try {
    const res = await fetch(`${API_URL}/game/new`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        grid_size: gridSize,
        mine_count: mineCount,
        client_seed: clientSeed
      })
    })
    return res.json()
  } catch (err) {
    console.error('API error:', err)
    return { error: 'Failed to connect to server' }
  }
}

export async function revealTile(gameId, position) {
  try {
    const res = await fetch(`${API_URL}/game/reveal`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId, position })
    })
    return res.json()
  } catch (err) {
    console.error('API error:', err)
    return { error: 'Failed to connect to server' }
  }
}

export async function cashout(gameId) {
  try {
    const res = await fetch(`${API_URL}/game/cashout`, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ game_id: gameId })
    })
    return res.json()
  } catch (err) {
    console.error('API error:', err)
    return { error: 'Failed to connect to server' }
  }
}

export async function verifyGame(serverSeed, clientSeed, gridSize, mineCount) {
  const res = await fetch(`${API_URL}/game/verify`, {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify({
      server_seed: serverSeed,
      client_seed: clientSeed,
      grid_size: gridSize,
      mine_count: mineCount,
      nonce: 0
    })
  })
  return res.json()
}

