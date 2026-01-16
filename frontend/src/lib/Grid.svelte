<script>
  import { createEventDispatcher } from 'svelte'
  
  export let size = 5
  export let revealed = []
  export let mines = []
  export let disabled = false
  
  const dispatch = createEventDispatcher()
  
  $: tiles = Array(size * size).fill(null)
  
  function isDisabledTile(index) {
    return disabled || revealed.includes(index) || mines.includes(index)
  }
  
  function handleClick(index) {
    if (isDisabledTile(index)) return
    dispatch('reveal', { position: index })
  }
</script>

<div class="grid" style="--size: {size}">
  {#each tiles as _, i (i + '-' + revealed.length + '-' + mines.length)}
    <button 
      class="tile"
      class:safe={revealed.includes(i)}
      class:mine={mines.includes(i)}
      class:hidden={!revealed.includes(i) && !mines.includes(i)}
      on:click={() => handleClick(i)}
      disabled={isDisabledTile(i)}
    >
      {#if mines.includes(i)}
        <span class="icon bomb">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <!-- Bomb body -->
            <circle cx="12" cy="14" r="7" fill="#0a0a0a" stroke="#fca5a5" stroke-width="0.5"/>
            <circle cx="12" cy="14" r="6" fill="#171717"/>
            <!-- Highlight -->
            <ellipse cx="9.5" cy="11.5" rx="2" ry="1.5" fill="#404040"/>
            <!-- Fuse -->
            <path d="M12 7 L12 4 Q12 2 14 2" stroke="#8b5a2b" stroke-width="1.5" stroke-linecap="round" fill="none"/>
            <!-- Spark/flame -->
            <circle cx="14.5" cy="2" r="1.5" fill="#ff6b35"/>
            <circle cx="14.5" cy="2" r="0.8" fill="#ffd93d"/>
            <!-- Spikes -->
            <line x1="5" y1="10" x2="6.5" y2="11.5" stroke="#fca5a5" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="19" y1="10" x2="17.5" y2="11.5" stroke="#fca5a5" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="5" y1="18" x2="6.5" y2="16.5" stroke="#fca5a5" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="19" y1="18" x2="17.5" y2="16.5" stroke="#fca5a5" stroke-width="1.5" stroke-linecap="round"/>
            <line x1="12" y1="21.5" x2="12" y2="20" stroke="#fca5a5" stroke-width="1.5" stroke-linecap="round"/>
          </svg>
        </span>
      {:else if revealed.includes(i)}
        <span class="icon gem">
          <svg viewBox="0 0 24 24" fill="none" xmlns="http://www.w3.org/2000/svg">
            <polygon points="12,2 22,9 18,22 6,22 2,9" fill="url(#gemGradient)" stroke="#60d9fa" stroke-width="0.5"/>
            <polygon points="12,2 17,9 12,22 7,9" fill="url(#gemInner)" opacity="0.8"/>
            <polygon points="12,2 7,9 2,9" fill="#a5f3fc" opacity="0.4"/>
            <polygon points="12,2 17,9 22,9" fill="#0891b2" opacity="0.3"/>
            <line x1="12" y1="2" x2="12" y2="22" stroke="#22d3ee" stroke-width="0.3" opacity="0.5"/>
            <line x1="2" y1="9" x2="22" y2="9" stroke="#22d3ee" stroke-width="0.3" opacity="0.5"/>
            <line x1="7" y1="9" x2="6" y2="22" stroke="#22d3ee" stroke-width="0.3" opacity="0.3"/>
            <line x1="17" y1="9" x2="18" y2="22" stroke="#22d3ee" stroke-width="0.3" opacity="0.3"/>
            <defs>
              <linearGradient id="gemGradient" x1="0%" y1="0%" x2="100%" y2="100%">
                <stop offset="0%" stop-color="#22d3ee"/>
                <stop offset="50%" stop-color="#0891b2"/>
                <stop offset="100%" stop-color="#164e63"/>
              </linearGradient>
              <linearGradient id="gemInner" x1="0%" y1="0%" x2="0%" y2="100%">
                <stop offset="0%" stop-color="#67e8f9"/>
                <stop offset="100%" stop-color="#0e7490"/>
              </linearGradient>
            </defs>
          </svg>
        </span>
      {/if}
    </button>
  {/each}
</div>

<style>
  .grid {
    display: grid;
    grid-template-columns: repeat(var(--size), 1fr);
    gap: 8px;
    max-width: 400px;
    aspect-ratio: 1;
  }
  
  .tile {
    aspect-ratio: 1;
    border: 2px solid #3a4451;
    border-radius: 12px;
    background: linear-gradient(145deg, #1a2027, #141920);
    cursor: pointer;
    transition: all 0.2s ease;
    display: flex;
    align-items: center;
    justify-content: center;
    box-shadow: 
      0 4px 12px rgba(0, 0, 0, 0.4),
      inset 0 1px 0 rgba(255, 255, 255, 0.05);
  }
  
  .tile.hidden:hover:not(:disabled) {
    transform: translateY(-3px) scale(1.02);
    background: linear-gradient(145deg, #252d38, #1e2530);
    border-color: #4a5568;
    box-shadow: 
      0 8px 20px rgba(0, 0, 0, 0.5),
      inset 0 1px 0 rgba(255, 255, 255, 0.1);
  }
  
  .tile:disabled {
    cursor: default;
  }
  
  .tile.safe {
    background: linear-gradient(145deg, #166534, #14532d);
    border-color: #22c55e;
    box-shadow: 
      0 0 30px rgba(34, 197, 94, 0.4),
      0 4px 12px rgba(0, 0, 0, 0.3),
      inset 0 0 20px rgba(34, 197, 94, 0.1);
    transform: scale(0.95);
    cursor: default;
  }
  
  .tile.mine {
    background: linear-gradient(145deg, #7f1d1d, #991b1b);
    border-color: #ef4444;
    box-shadow: 
      0 0 30px rgba(239, 68, 68, 0.5),
      0 4px 12px rgba(0, 0, 0, 0.3),
      inset 0 0 20px rgba(239, 68, 68, 0.1);
    transform: scale(0.95);
    cursor: default;
  }
  
  .icon {
    display: flex;
    align-items: center;
    justify-content: center;
    animation: pop 0.25s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  }
  
  .icon.gem {
    width: 60%;
    height: 60%;
  }
  
  .icon.gem svg {
    width: 100%;
    height: 100%;
    filter: drop-shadow(0 0 6px rgba(34, 211, 238, 0.6));
  }
  
  .icon.bomb {
    width: 65%;
    height: 65%;
  }
  
  .icon.bomb svg {
    width: 100%;
    height: 100%;
    filter: drop-shadow(0 0 8px rgba(239, 68, 68, 0.6));
  }
  
  @keyframes pop {
    0% { transform: scale(0) rotate(-10deg); }
    60% { transform: scale(1.3) rotate(5deg); }
    100% { transform: scale(1) rotate(0deg); }
  }
</style>

