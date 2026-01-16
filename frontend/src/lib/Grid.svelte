<script>
  import { createEventDispatcher } from 'svelte'
  
  export let size = 5
  export let revealed = []
  export let mines = []
  export let disabled = false
  
  const dispatch = createEventDispatcher()
  
  $: tiles = Array(size * size).fill(null)
  
  function getTileState(index) {
    if (mines.includes(index)) return 'mine'
    if (revealed.includes(index)) return 'safe'
    return 'hidden'
  }
  
  function handleClick(index) {
    if (disabled || revealed.includes(index)) return
    dispatch('reveal', { position: index })
  }
</script>

<div class="grid" style="--size: {size}">
  {#each tiles as _, i}
    {@const state = getTileState(i)}
    <button 
      class="tile {state}"
      class:revealed={revealed.includes(i) || mines.includes(i)}
      on:click={() => handleClick(i)}
      disabled={disabled || revealed.includes(i)}
    >
      {#if state === 'mine'}
        <span class="icon bomb">💣</span>
      {:else if state === 'safe'}
        <span class="icon gem">💎</span>
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
  
  .tile:hover:not(:disabled) {
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
  }
  
  .tile.mine {
    background: linear-gradient(145deg, #7f1d1d, #991b1b);
    border-color: #ef4444;
    box-shadow: 
      0 0 30px rgba(239, 68, 68, 0.5),
      0 4px 12px rgba(0, 0, 0, 0.3),
      inset 0 0 20px rgba(239, 68, 68, 0.1);
    transform: scale(0.95);
  }
  
  .icon {
    animation: pop 0.25s cubic-bezier(0.68, -0.55, 0.265, 1.55);
  }
  
  .icon.gem {
    font-size: 1.8rem;
  }
  
  .icon.bomb {
    font-size: 2.2rem;
    filter: drop-shadow(0 0 8px rgba(239, 68, 68, 0.6));
  }
  
  @keyframes pop {
    0% { transform: scale(0) rotate(-10deg); }
    60% { transform: scale(1.3) rotate(5deg); }
    100% { transform: scale(1) rotate(0deg); }
  }
</style>

