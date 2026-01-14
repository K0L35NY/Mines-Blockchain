from flask import Flask, request, jsonify
from flask_cors import CORS
from game_engine import MinesGame, verify_game
import blockchain

app = Flask(__name__)
CORS(app)

games = {}


@app.route('/blockchain/info', methods=['GET'])
def blockchain_info():
    """Get blockchain connection info"""
    return jsonify(blockchain.get_contract_info())


@app.route('/blockchain/game/<game_id>', methods=['GET'])
def blockchain_game(game_id):
    """Get on-chain commitment for a game"""
    result = blockchain.get_game_commitment(game_id)
    return jsonify(result)


@app.route('/game/new', methods=['POST'])
def new_game():
    data = request.get_json() or {}
    
    grid_size = data.get('grid_size', 5)
    mine_count = data.get('mine_count', 3)
    client_seed = data.get('client_seed')
    
    if grid_size < 2 or grid_size > 10:
        return jsonify({'error': 'Grid size must be 2-10'}), 400
    
    total = grid_size * grid_size
    if mine_count < 1 or mine_count >= total:
        return jsonify({'error': f'Mine count must be 1-{total-1}'}), 400
    
    game = MinesGame(grid_size, mine_count, client_seed)
    game_id = game.seed_hash[:16]
    games[game_id] = game
    
    # Commit seed hash to blockchain (async, non-blocking response)
    blockchain_result = blockchain.commit_game(game_id, game.seed_hash)
    
    return jsonify({
        'game_id': game_id,
        'grid_size': grid_size,
        'mine_count': mine_count,
        'seed_hash': game.seed_hash,
        'client_seed': game.client_seed,
        'blockchain': blockchain_result
    })


@app.route('/game/reveal', methods=['POST'])
def reveal_tile():
    data = request.get_json() or {}
    
    game_id = data.get('game_id')
    position = data.get('position')
    
    if not game_id or position is None:
        return jsonify({'error': 'Missing game_id or position'}), 400
    
    game = games.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    result = game.reveal(position)
    if 'error' in result:
        return jsonify(result), 400
    
    # If game ended (hit mine), reveal on blockchain
    if result.get('hit_mine'):
        blockchain_reveal = blockchain.reveal_game(game_id, game.server_seed)
        result['blockchain'] = blockchain_reveal
    
    return jsonify(result)


@app.route('/game/cashout', methods=['POST'])
def cashout():
    data = request.get_json() or {}
    game_id = data.get('game_id')
    
    if not game_id:
        return jsonify({'error': 'Missing game_id'}), 400
    
    game = games.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    result = game.cashout()
    if 'error' in result:
        return jsonify(result), 400
    
    # Reveal on blockchain after cashout
    blockchain_reveal = blockchain.reveal_game(game_id, game.server_seed)
    result['blockchain'] = blockchain_reveal
    
    return jsonify(result)


@app.route('/game/state', methods=['GET'])
def game_state():
    game_id = request.args.get('game_id')
    
    if not game_id:
        return jsonify({'error': 'Missing game_id'}), 400
    
    game = games.get(game_id)
    if not game:
        return jsonify({'error': 'Game not found'}), 404
    
    return jsonify(game.get_state())


@app.route('/game/verify', methods=['POST'])
def verify():
    data = request.get_json() or {}
    
    required = ['server_seed', 'client_seed', 'grid_size', 'mine_count']
    for field in required:
        if field not in data:
            return jsonify({'error': f'Missing {field}'}), 400
    
    result = verify_game(
        data['server_seed'],
        data['client_seed'],
        data.get('nonce', 0),
        data['grid_size'],
        data['mine_count']
    )
    
    return jsonify(result)


if __name__ == '__main__':
    app.run(debug=True, port=5001)

