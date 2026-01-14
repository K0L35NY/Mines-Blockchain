<script>
  import Grid from './lib/Grid.svelte'
  import { newGame, revealTile, cashout, verifyGame } from './lib/api.js'
  import { getBlockchainInfo, getGameCommitment, formatTxHash, getExplorerUrl } from './lib/blockchain.js'
  
  let gridSize = 5
  let mineCount = 3
  let clientSeed = ''
  
  let gameId = null
  let seedHash = ''
  let serverSeed = ''
  let revealed = []
  let mines = []
  let multiplier = 1.0
  let gameOver = false
  let gameStarted = false
  
  // Blockchain state
  let blockchainInfo = null
  let commitTxHash = ''
  let commitExplorerUrl = ''
  let revealTxHash = ''
  let revealExplorerUrl = ''
  let onChainCommitment = null
  
  let activeTab = 'play'
  
  let verifyServerSeed = ''
  let verifyClientSeed = ''
  let verifyGridSize = 5
  let verifyMineCount = 3
  let verifyResult = null
  
  // Fetch blockchain info on mount
  async function fetchBlockchainInfo() {
    blockchainInfo = await getBlockchainInfo()
  }
  fetchBlockchainInfo()
  
  async function startGame() {
    const seed = clientSeed.trim() || null
    const res = await newGame(gridSize, mineCount, seed)
    
    if (res.error) {
      alert(res.error)
      return
    }
    
    gameId = res.game_id
    seedHash = res.seed_hash
    clientSeed = res.client_seed
    revealed = []
    mines = []
    multiplier = 1.0
    gameOver = false
    serverSeed = ''
    gameStarted = true
    
    // Capture blockchain commit info
    if (res.blockchain?.committed) {
      commitTxHash = res.blockchain.tx_hash
      commitExplorerUrl = res.blockchain.explorer_url
    } else {
      commitTxHash = ''
      commitExplorerUrl = ''
    }
    revealTxHash = ''
    revealExplorerUrl = ''
    onChainCommitment = null
  }
  
  async function handleReveal(e) {
    if (gameOver) return
    
    const { position } = e.detail
    const res = await revealTile(gameId, position)
    
    if (res.error) return
    
    revealed = [...revealed, position]
    
    if (res.hit_mine) {
      mines = res.mines
      serverSeed = res.server_seed
      gameOver = true
      
      // Capture blockchain reveal info
      if (res.blockchain?.revealed) {
        revealTxHash = res.blockchain.tx_hash
        revealExplorerUrl = res.blockchain.explorer_url
      }
      
      // Fetch on-chain commitment for verification display
      fetchOnChainCommitment()
    } else {
      multiplier = res.multiplier
      if (res.game_won) {
        gameOver = true
      }
    }
  }
  
  async function fetchOnChainCommitment() {
    if (gameId) {
      onChainCommitment = await getGameCommitment(gameId)
    }
  }
  
  async function handleCashout() {
    const res = await cashout(gameId)
    
    if (res.error) return
    
    multiplier = res.multiplier
    mines = res.mines
    serverSeed = res.server_seed
    gameOver = true
    
    // Capture blockchain reveal info
    if (res.blockchain?.revealed) {
      revealTxHash = res.blockchain.tx_hash
      revealExplorerUrl = res.blockchain.explorer_url
    }
    
    // Fetch on-chain commitment for verification display
    fetchOnChainCommitment()
  }
  
  function resetGame() {
    gameId = null
    seedHash = ''
    serverSeed = ''
    revealed = []
    mines = []
    multiplier = 1.0
    gameOver = false
    gameStarted = false
    commitTxHash = ''
    commitExplorerUrl = ''
    revealTxHash = ''
    revealExplorerUrl = ''
    onChainCommitment = null
  }
  
  async function handleVerify() {
    if (!verifyServerSeed.trim() || !verifyClientSeed.trim()) {
      alert('Please enter both server seed and client seed')
      return
    }
    
    const res = await verifyGame(
      verifyServerSeed.trim(),
      verifyClientSeed.trim(),
      verifyGridSize,
      verifyMineCount
    )
    
    verifyResult = res
  }
  
  function indexToCoord(idx, size) {
    return { row: Math.floor(idx / size) + 1, col: (idx % size) + 1 }
  }
</script>

<main>
  <div class="container">
    <header>
      <h1>MINES</h1>
      <span class="badge">Provably Fair</span>
      {#if blockchainInfo}
        <span class="badge blockchain" class:connected={blockchainInfo.connected}>
          {blockchainInfo.connected ? '⛓️ Sepolia' : '⚠️ Offline'}
        </span>
      {/if}
    </header>
    
    {#if !gameStarted}
      <div class="tabs">
        <button 
          class="tab" 
          class:active={activeTab === 'play'}
          on:click={() => activeTab = 'play'}
        >
          Play
        </button>
        <button 
          class="tab" 
          class:active={activeTab === 'verify'}
          on:click={() => activeTab = 'verify'}
        >
          Verify Fairness
        </button>
      </div>
      
      {#if activeTab === 'play'}
        <div class="config">
          <div class="field">
            <label for="grid-size">Grid Size</label>
            <div class="range-group">
              <input id="grid-size" type="range" bind:value={gridSize} min="3" max="8" />
              <span class="value">{gridSize}×{gridSize}</span>
            </div>
          </div>
          
          <div class="field">
            <label for="mine-count">Mines</label>
            <div class="range-group">
              <input id="mine-count" type="range" bind:value={mineCount} min="1" max={gridSize * gridSize - 1} />
              <span class="value">{mineCount}</span>
            </div>
          </div>
          
          <div class="field">
            <label for="client-seed">Client Seed (optional)</label>
            <input id="client-seed" type="text" bind:value={clientSeed} placeholder="Leave empty for random" />
          </div>
          
          <button class="btn primary" on:click={startGame}>Start Game</button>
        </div>
      {:else}
        <div class="config verify-panel">
          <p class="verify-intro">Verify a past game by entering the seeds revealed after game end.</p>
          
          <div class="field">
            <label for="verify-server">Server Seed</label>
            <input id="verify-server" type="text" bind:value={verifyServerSeed} placeholder="Paste server seed here" />
          </div>
          
          <div class="field">
            <label for="verify-client">Client Seed</label>
            <input id="verify-client" type="text" bind:value={verifyClientSeed} placeholder="Paste client seed here" />
          </div>
          
          <div class="field">
            <label for="verify-grid">Grid Size</label>
            <div class="range-group">
              <input id="verify-grid" type="range" bind:value={verifyGridSize} min="3" max="8" />
              <span class="value">{verifyGridSize}×{verifyGridSize}</span>
            </div>
          </div>
          
          <div class="field">
            <label for="verify-mines">Mine Count</label>
            <div class="range-group">
              <input id="verify-mines" type="range" bind:value={verifyMineCount} min="1" max={verifyGridSize * verifyGridSize - 1} />
              <span class="value">{verifyMineCount}</span>
            </div>
          </div>
          
          <button class="btn primary" on:click={handleVerify}>Verify</button>
          
          {#if verifyResult}
            <div class="verify-result">
              <h4>Verification Result</h4>
              <div class="seed">
                <span class="label">Expected Seed Hash</span>
                <code>{verifyResult.seed_hash}</code>
              </div>
              <div class="mine-positions">
                <span class="label">Mine Positions</span>
                <div class="positions-grid">
                  {#each verifyResult.mines as pos}
                    {@const coord = indexToCoord(pos, verifyGridSize)}
                    <span class="pos">💣 Row {coord.row}, Col {coord.col}</span>
                  {/each}
                </div>
              </div>
            </div>
          {/if}
        </div>
      {/if}
    {:else}
      <div class="game">
        <div class="stats">
          <div class="stat">
            <span class="label">Multiplier</span>
            <span class="value accent">{multiplier.toFixed(2)}×</span>
          </div>
          <div class="stat">
            <span class="label">Revealed</span>
            <span class="value">{revealed.length}/{gridSize * gridSize - mineCount}</span>
          </div>
        </div>
        
        {#if commitTxHash}
          <div class="blockchain-status">
            <span class="chain-icon">⛓️</span>
            <span class="chain-label">On-chain commitment:</span>
            <a href={commitExplorerUrl} target="_blank" rel="noopener" class="tx-link">
              {formatTxHash(commitTxHash)} ↗
            </a>
          </div>
        {/if}
        
        <Grid 
          size={gridSize} 
          {revealed} 
          {mines}
          disabled={gameOver}
          on:reveal={handleReveal}
        />
        
        {#if !gameOver && revealed.length > 0}
          <button class="btn cashout" on:click={handleCashout}>
            Cashout {multiplier.toFixed(2)}×
          </button>
        {/if}
        
        {#if gameOver}
          <div class="result" class:win={!mines.some(m => revealed.includes(m))}>
            {#if mines.some(m => revealed.includes(m))}
              <h2>💥 Game Over</h2>
            {:else}
              <h2>🎉 Cashed Out!</h2>
              <p class="payout">Final: {multiplier.toFixed(2)}×</p>
            {/if}
          </div>
          
          <div class="verification">
            <h3>Verify Fairness</h3>
            <div class="seed-info">
              <div class="seed">
                <span class="label">Seed Hash (shown before)</span>
                <code>{seedHash}</code>
              </div>
              <div class="seed">
                <span class="label">Server Seed (revealed)</span>
                <code>{serverSeed}</code>
              </div>
              <div class="seed">
                <span class="label">Client Seed</span>
                <code>{clientSeed}</code>
              </div>
              <p class="hint">Hash the server seed with SHA-256 to verify it matches the seed hash shown at game start.</p>
            </div>
            
            {#if commitTxHash || onChainCommitment}
              <div class="blockchain-verification">
                <h4>⛓️ Blockchain Verification</h4>
                
                {#if commitTxHash}
                  <div class="chain-row">
                    <span class="label">Commitment TX</span>
                    <a href={commitExplorerUrl} target="_blank" rel="noopener" class="tx-link">
                      {formatTxHash(commitTxHash)} ↗
                    </a>
                  </div>
                {/if}
                
                {#if revealTxHash}
                  <div class="chain-row">
                    <span class="label">Reveal TX</span>
                    <a href={revealExplorerUrl} target="_blank" rel="noopener" class="tx-link">
                      {formatTxHash(revealTxHash)} ↗
                    </a>
                  </div>
                {/if}
                
                {#if onChainCommitment && !onChainCommitment.error}
                  <div class="chain-row">
                    <span class="label">On-Chain Hash</span>
                    <code class="small">{onChainCommitment.seed_hash}</code>
                  </div>
                  <div class="chain-row">
                    <span class="label">Committed At</span>
                    <span>{new Date(onChainCommitment.timestamp * 1000).toLocaleString()}</span>
                  </div>
                {/if}
                
                <p class="chain-hint">
                  The seed hash was committed to Sepolia blockchain <em>before</em> your first move. 
                  Anyone can verify on <a href={blockchainInfo?.explorer_url} target="_blank" rel="noopener">Etherscan</a>.
                </p>
              </div>
            {/if}
          </div>
          
          <button class="btn primary" on:click={resetGame}>New Game</button>
        {/if}
      </div>
    {/if}
  </div>
</main>

<style>
  :global(*) {
    margin: 0;
    padding: 0;
    box-sizing: border-box;
  }
  
  :global(body) {
    font-family: 'Outfit', sans-serif;
    background: #0f1419;
    color: #e4e8eb;
    min-height: 100vh;
  }
  
  main {
    min-height: 100vh;
    padding: 2rem;
    background: 
      radial-gradient(ellipse at 20% 20%, rgba(34, 197, 94, 0.05) 0%, transparent 50%),
      radial-gradient(ellipse at 80% 80%, rgba(139, 92, 246, 0.05) 0%, transparent 50%),
      #0f1419;
  }
  
  .container {
    max-width: 480px;
    margin: 0 auto;
  }
  
  header {
    text-align: center;
    margin-bottom: 2rem;
    display: flex;
    align-items: center;
    justify-content: center;
    gap: 1rem;
  }
  
  h1 {
    font-family: 'JetBrains Mono', monospace;
    font-size: 2rem;
    font-weight: 600;
    letter-spacing: 0.2em;
    background: linear-gradient(135deg, #22c55e, #16a34a);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    background-clip: text;
  }
  
  .badge {
    font-size: 0.65rem;
    padding: 0.25rem 0.5rem;
    background: rgba(139, 92, 246, 0.2);
    border: 1px solid rgba(139, 92, 246, 0.3);
    border-radius: 4px;
    color: #a78bfa;
    text-transform: uppercase;
    letter-spacing: 0.1em;
  }
  
  .tabs {
    display: flex;
    gap: 0.5rem;
    margin-bottom: 1rem;
  }
  
  .tab {
    flex: 1;
    padding: 0.75rem 1rem;
    background: #1a2027;
    border: 2px solid #30363d;
    border-radius: 10px;
    color: #8b949e;
    font-family: 'Outfit', sans-serif;
    font-size: 0.9rem;
    font-weight: 500;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .tab:hover {
    border-color: #4a5568;
    color: #e4e8eb;
  }
  
  .tab.active {
    background: linear-gradient(145deg, #22c55e20, #16a34a10);
    border-color: #22c55e;
    color: #22c55e;
  }
  
  .verify-panel {
    gap: 1rem;
  }
  
  .verify-intro {
    font-size: 0.85rem;
    color: #8b949e;
    line-height: 1.5;
    margin-bottom: 0.5rem;
  }
  
  .verify-result {
    margin-top: 1rem;
    padding: 1rem;
    background: #0f1419;
    border-radius: 10px;
    border: 1px solid #30363d;
  }
  
  .verify-result h4 {
    font-size: 0.85rem;
    color: #22c55e;
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .mine-positions {
    margin-top: 0.75rem;
  }
  
  .mine-positions .label {
    display: block;
    font-size: 0.7rem;
    color: #6e7681;
    margin-bottom: 0.5rem;
  }
  
  .positions-grid {
    display: flex;
    flex-wrap: wrap;
    gap: 0.5rem;
  }
  
  .pos {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.75rem;
    background: #1a2027;
    padding: 0.35rem 0.6rem;
    border-radius: 6px;
    color: #ef4444;
  }
  
  .config {
    background: #1a2027;
    border-radius: 16px;
    padding: 1.5rem;
    display: flex;
    flex-direction: column;
    gap: 1.25rem;
  }
  
  .field {
    display: flex;
    flex-direction: column;
    gap: 0.5rem;
  }
  
  .field label {
    font-size: 0.85rem;
    color: #8b949e;
    font-weight: 500;
  }
  
  .range-group {
    display: flex;
    align-items: center;
    gap: 1rem;
  }
  
  .range-group input[type="range"] {
    flex: 1;
    accent-color: #22c55e;
    height: 6px;
  }
  
  .range-group .value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.9rem;
    min-width: 3rem;
    text-align: right;
  }
  
  input[type="text"] {
    background: #0f1419;
    border: 1px solid #30363d;
    border-radius: 8px;
    padding: 0.75rem 1rem;
    color: #e4e8eb;
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.85rem;
  }
  
  input[type="text"]:focus {
    outline: none;
    border-color: #22c55e;
  }
  
  .btn {
    padding: 1rem 1.5rem;
    border: none;
    border-radius: 10px;
    font-family: 'Outfit', sans-serif;
    font-size: 1rem;
    font-weight: 600;
    cursor: pointer;
    transition: all 0.2s ease;
  }
  
  .btn.primary {
    background: linear-gradient(135deg, #22c55e, #16a34a);
    color: #fff;
  }
  
  .btn.primary:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(34, 197, 94, 0.3);
  }
  
  .btn.cashout {
    background: linear-gradient(135deg, #f59e0b, #d97706);
    color: #fff;
    width: 100%;
    margin-top: 1rem;
  }
  
  .btn.cashout:hover {
    transform: translateY(-2px);
    box-shadow: 0 8px 24px rgba(245, 158, 11, 0.3);
  }
  
  .game {
    display: flex;
    flex-direction: column;
    gap: 1.5rem;
  }
  
  .stats {
    display: flex;
    gap: 1rem;
  }
  
  .stat {
    flex: 1;
    background: #1a2027;
    padding: 1rem;
    border-radius: 10px;
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .stat .label {
    font-size: 0.75rem;
    color: #8b949e;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .stat .value {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.25rem;
    font-weight: 600;
  }
  
  .stat .value.accent {
    color: #22c55e;
  }
  
  .result {
    text-align: center;
    padding: 1.5rem;
    background: #1a2027;
    border-radius: 12px;
  }
  
  .result h2 {
    font-size: 1.5rem;
  }
  
  .result.win h2 {
    color: #22c55e;
  }
  
  .result .payout {
    font-family: 'JetBrains Mono', monospace;
    font-size: 1.25rem;
    color: #f59e0b;
    margin-top: 0.5rem;
  }
  
  .verification {
    background: #1a2027;
    border-radius: 12px;
    padding: 1.25rem;
  }
  
  .verification h3 {
    font-size: 0.9rem;
    color: #8b949e;
    margin-bottom: 1rem;
    text-transform: uppercase;
    letter-spacing: 0.05em;
  }
  
  .seed-info {
    display: flex;
    flex-direction: column;
    gap: 0.75rem;
  }
  
  .seed {
    display: flex;
    flex-direction: column;
    gap: 0.25rem;
  }
  
  .seed .label {
    font-size: 0.7rem;
    color: #6e7681;
  }
  
  .seed code {
    font-family: 'JetBrains Mono', monospace;
    font-size: 0.7rem;
    background: #0f1419;
    padding: 0.5rem;
    border-radius: 6px;
    word-break: break-all;
    color: #a78bfa;
  }
  
  .hint {
    font-size: 0.75rem;
    color: #6e7681;
    margin-top: 0.5rem;
    line-height: 1.4;
  }
  
  /* Blockchain UI */
  .badge.blockchain {
    background: rgba(239, 68, 68, 0.2);
    border-color: rgba(239, 68, 68, 0.3);
    color: #ef4444;
  }
  
  .badge.blockchain.connected {
    background: rgba(59, 130, 246, 0.2);
    border-color: rgba(59, 130, 246, 0.3);
    color: #60a5fa;
  }
  
  .blockchain-status {
    display: flex;
    align-items: center;
    gap: 0.5rem;
    padding: 0.75rem 1rem;
    background: rgba(59, 130, 246, 0.1);
    border: 1px solid rgba(59, 130, 246, 0.2);
    border-radius: 8px;
    font-size: 0.8rem;
  }
  
  .chain-icon {
    font-size: 1rem;
  }
  
  .chain-label {
    color: #8b949e;
  }
  
  .tx-link {
    font-family: 'JetBrains Mono', monospace;
    color: #60a5fa;
    text-decoration: none;
    transition: color 0.2s;
  }
  
  .tx-link:hover {
    color: #93c5fd;
    text-decoration: underline;
  }
  
  .blockchain-verification {
    margin-top: 1rem;
    padding: 1rem;
    background: rgba(59, 130, 246, 0.05);
    border: 1px solid rgba(59, 130, 246, 0.15);
    border-radius: 10px;
  }
  
  .blockchain-verification h4 {
    font-size: 0.85rem;
    color: #60a5fa;
    margin-bottom: 0.75rem;
  }
  
  .chain-row {
    display: flex;
    justify-content: space-between;
    align-items: center;
    padding: 0.5rem 0;
    border-bottom: 1px solid rgba(59, 130, 246, 0.1);
    font-size: 0.8rem;
  }
  
  .chain-row:last-of-type {
    border-bottom: none;
  }
  
  .chain-row .label {
    color: #6e7681;
  }
  
  .chain-row code.small {
    font-size: 0.65rem;
    padding: 0.25rem 0.5rem;
    max-width: 180px;
    overflow: hidden;
    text-overflow: ellipsis;
  }
  
  .chain-hint {
    font-size: 0.7rem;
    color: #6e7681;
    margin-top: 0.75rem;
    line-height: 1.5;
  }
  
  .chain-hint a {
    color: #60a5fa;
  }
  
  .chain-hint em {
    color: #22c55e;
    font-style: normal;
    font-weight: 600;
  }
</style>

