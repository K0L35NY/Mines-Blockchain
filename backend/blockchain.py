"""
Blockchain integration for provably fair verification.
Commits seed hashes to Sepolia testnet for immutable proof.
"""

import os
import json
from web3 import Web3
from dotenv import load_dotenv

load_dotenv()

# Contract ABI - only the functions we need
CONTRACT_ABI = [
    {
        "inputs": [
            {"name": "gameId", "type": "string"},
            {"name": "seedHash", "type": "bytes32"}
        ],
        "name": "commitGame",
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "gameId", "type": "string"},
            {"name": "serverSeed", "type": "bytes32"}
        ],
        "name": "revealGame", 
        "outputs": [],
        "stateMutability": "nonpayable",
        "type": "function"
    },
    {
        "inputs": [{"name": "gameId", "type": "string"}],
        "name": "getGame",
        "outputs": [
            {"name": "seedHash", "type": "bytes32"},
            {"name": "committer", "type": "address"},
            {"name": "timestamp", "type": "uint256"},
            {"name": "revealed", "type": "bool"},
            {"name": "serverSeed", "type": "bytes32"}
        ],
        "stateMutability": "view",
        "type": "function"
    },
    {
        "inputs": [
            {"name": "gameId", "type": "string"},
            {"name": "serverSeed", "type": "bytes32"}
        ],
        "name": "verifyGame",
        "outputs": [{"name": "valid", "type": "bool"}],
        "stateMutability": "view",
        "type": "function"
    }
]

# Configuration
CONTRACT_ADDRESS = os.getenv("CONTRACT_ADDRESS", "")
SEPOLIA_RPC_URL = os.getenv("SEPOLIA_RPC_URL", "https://rpc.sepolia.org")
PRIVATE_KEY = os.getenv("PRIVATE_KEY", "")

# Initialize Web3
w3 = None
contract = None
account = None


def init_blockchain():
    """Initialize blockchain connection"""
    global w3, contract, account
    
    if not CONTRACT_ADDRESS:
        print("⚠️  No CONTRACT_ADDRESS set - blockchain features disabled")
        return False
    
    try:
        w3 = Web3(Web3.HTTPProvider(SEPOLIA_RPC_URL))
        
        if not w3.is_connected():
            print("⚠️  Cannot connect to Sepolia RPC")
            return False
        
        contract = w3.eth.contract(
            address=Web3.to_checksum_address(CONTRACT_ADDRESS),
            abi=CONTRACT_ABI
        )
        
        if PRIVATE_KEY:
            account = w3.eth.account.from_key(PRIVATE_KEY)
            print(f"✅ Blockchain initialized - Account: {account.address}")
        else:
            print("⚠️  No PRIVATE_KEY set - read-only mode")
        
        return True
        
    except Exception as e:
        print(f"⚠️  Blockchain init failed: {e}")
        return False


def is_enabled():
    """Check if blockchain is enabled and connected"""
    return w3 is not None and contract is not None and w3.is_connected()


def can_write():
    """Check if we can write to blockchain (have private key)"""
    return is_enabled() and account is not None


def commit_game(game_id: str, seed_hash: str) -> dict:
    """
    Commit a game's seed hash to the blockchain.
    Called when a new game starts.
    
    Args:
        game_id: Unique game identifier
        seed_hash: SHA256 hash of the server seed (hex string without 0x)
    
    Returns:
        dict with tx_hash on success or error
    """
    if not can_write():
        return {"error": "Blockchain write not available", "committed": False}
    
    try:
        # Convert hex string to bytes32
        seed_hash_bytes = bytes.fromhex(seed_hash)
        
        # Build transaction
        nonce = w3.eth.get_transaction_count(account.address)
        
        tx = contract.functions.commitGame(
            game_id,
            seed_hash_bytes
        ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 100000,
            'gasPrice': w3.eth.gas_price
        })
        
        # Sign and send
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        # Wait for receipt (timeout 60s)
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
        
        return {
            "committed": True,
            "tx_hash": tx_hash.hex(),
            "block_number": receipt['blockNumber'],
            "explorer_url": f"https://sepolia.etherscan.io/tx/{tx_hash.hex()}"
        }
        
    except Exception as e:
        error_msg = str(e)
        # Common errors
        if "already committed" in error_msg.lower():
            return {"error": "Game already committed", "committed": False}
        return {"error": f"Commit failed: {error_msg}", "committed": False}


def reveal_game(game_id: str, server_seed: str) -> dict:
    """
    Reveal a game's server seed on the blockchain.
    Called when a game ends.
    
    Args:
        game_id: Unique game identifier  
        server_seed: The actual server seed (hex string)
    
    Returns:
        dict with tx_hash on success or error
    """
    if not can_write():
        return {"error": "Blockchain write not available", "revealed": False}
    
    try:
        # Server seed needs to be converted to bytes32
        # Pad or truncate to 32 bytes
        seed_bytes = server_seed.encode('utf-8')
        if len(seed_bytes) > 32:
            seed_bytes = seed_bytes[:32]
        else:
            seed_bytes = seed_bytes.ljust(32, b'\x00')
        
        nonce = w3.eth.get_transaction_count(account.address)
        
        tx = contract.functions.revealGame(
            game_id,
            seed_bytes
        ).build_transaction({
            'from': account.address,
            'nonce': nonce,
            'gas': 100000,
            'gasPrice': w3.eth.gas_price
        })
        
        signed_tx = w3.eth.account.sign_transaction(tx, PRIVATE_KEY)
        tx_hash = w3.eth.send_raw_transaction(signed_tx.raw_transaction)
        
        receipt = w3.eth.wait_for_transaction_receipt(tx_hash, timeout=60)
        
        return {
            "revealed": True,
            "tx_hash": tx_hash.hex(),
            "block_number": receipt['blockNumber'],
            "explorer_url": f"https://sepolia.etherscan.io/tx/{tx_hash.hex()}"
        }
        
    except Exception as e:
        return {"error": f"Reveal failed: {str(e)}", "revealed": False}


def get_game_commitment(game_id: str) -> dict:
    """
    Get a game's on-chain commitment data.
    Can be called by anyone to verify.
    
    Args:
        game_id: Unique game identifier
    
    Returns:
        dict with game data or error
    """
    if not is_enabled():
        return {"error": "Blockchain not available"}
    
    try:
        result = contract.functions.getGame(game_id).call()
        
        seed_hash, committer, timestamp, revealed, server_seed = result
        
        if timestamp == 0:
            return {"error": "Game not found on blockchain"}
        
        return {
            "game_id": game_id,
            "seed_hash": "0x" + seed_hash.hex(),
            "committer": committer,
            "timestamp": timestamp,
            "revealed": revealed,
            "server_seed": "0x" + server_seed.hex() if revealed else None,
            "explorer_url": f"https://sepolia.etherscan.io/address/{CONTRACT_ADDRESS}"
        }
        
    except Exception as e:
        return {"error": f"Query failed: {str(e)}"}


def get_contract_info() -> dict:
    """Get contract address and network info"""
    return {
        "contract_address": CONTRACT_ADDRESS or None,
        "network": "sepolia",
        "rpc_url": SEPOLIA_RPC_URL,
        "connected": is_enabled(),
        "can_write": can_write(),
        "explorer_url": f"https://sepolia.etherscan.io/address/{CONTRACT_ADDRESS}" if CONTRACT_ADDRESS else None
    }


# Initialize on module load
init_blockchain()
