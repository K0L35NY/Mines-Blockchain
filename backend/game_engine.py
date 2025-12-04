import hashlib
import secrets
import json


class MinesGame:
    def __init__(self, grid_size, mine_count, client_seed=None):
        self.grid_size = grid_size
        self.total_tiles = grid_size * grid_size
        self.mine_count = mine_count
        self.server_seed = secrets.token_hex(32)
        self.client_seed = client_seed or secrets.token_hex(16)
        self.nonce = 0
        self.revealed = set()
        self.game_over = False
        self.hit_mine = False
        self.mines = self._generate_mines()

    @property
    def seed_hash(self):
        return hashlib.sha256(self.server_seed.encode()).hexdigest()

    def _generate_mines(self):
        combined = f"{self.server_seed}:{self.client_seed}:{self.nonce}"
        hash_bytes = hashlib.sha256(combined.encode()).digest()
        
        mines = set()
        counter = 0
        while len(mines) < self.mine_count:
            seed_input = f"{combined}:{counter}"
            h = hashlib.sha256(seed_input.encode()).digest()
            position = int.from_bytes(h[:4], 'big') % self.total_tiles
            mines.add(position)
            counter += 1
        
        return mines

    def reveal(self, position):
        if self.game_over:
            return {'error': 'Game is over'}
        
        if position < 0 or position >= self.total_tiles:
            return {'error': 'Invalid position'}
        
        if position in self.revealed:
            return {'error': 'Already revealed'}

        self.revealed.add(position)
        
        if position in self.mines:
            self.game_over = True
            self.hit_mine = True
            return {
                'hit_mine': True,
                'position': position,
                'mines': list(self.mines),
                'server_seed': self.server_seed
            }
        
        safe_tiles = self.total_tiles - self.mine_count
        revealed_safe = len(self.revealed)
        
        if revealed_safe == safe_tiles:
            self.game_over = True
        
        return {
            'hit_mine': False,
            'position': position,
            'multiplier': self._calculate_multiplier(),
            'game_won': revealed_safe == safe_tiles
        }

    def _calculate_multiplier(self):
        # Simple multiplier: increases with each safe reveal
        safe_revealed = len(self.revealed)
        remaining = self.total_tiles - safe_revealed
        mine_probability = self.mine_count / remaining if remaining > 0 else 1
        
        multiplier = 1.0
        tiles_left = self.total_tiles
        for _ in range(safe_revealed):
            safe_prob = (tiles_left - self.mine_count) / tiles_left
            multiplier *= (1 / safe_prob) * 0.97  # 3% house edge
            tiles_left -= 1
        
        return round(multiplier, 2)

    def cashout(self):
        if self.game_over:
            return {'error': 'Game already ended'}
        
        self.game_over = True
        return {
            'multiplier': self._calculate_multiplier(),
            'server_seed': self.server_seed,
            'mines': list(self.mines)
        }

    def get_state(self):
        state = {
            'grid_size': self.grid_size,
            'mine_count': self.mine_count,
            'seed_hash': self.seed_hash,
            'client_seed': self.client_seed,
            'revealed': list(self.revealed),
            'game_over': self.game_over,
            'multiplier': self._calculate_multiplier()
        }
        
        if self.game_over:
            state['server_seed'] = self.server_seed
            state['mines'] = list(self.mines)
        
        return state


def verify_game(server_seed, client_seed, nonce, grid_size, mine_count):
    """Standalone verification - client can use this to verify mine positions"""
    total_tiles = grid_size * grid_size
    combined = f"{server_seed}:{client_seed}:{nonce}"
    
    mines = set()
    counter = 0
    while len(mines) < mine_count:
        seed_input = f"{combined}:{counter}"
        h = hashlib.sha256(seed_input.encode()).digest()
        position = int.from_bytes(h[:4], 'big') % total_tiles
        mines.add(position)
        counter += 1
    
    expected_hash = hashlib.sha256(server_seed.encode()).hexdigest()
    
    return {
        'mines': list(mines),
        'seed_hash': expected_hash
    }

