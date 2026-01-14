// SPDX-License-Identifier: MIT
pragma solidity ^0.8.19;

/**
 * @title MinesVerifier
 * @notice Simple contract to store and verify game seed commitments for provably fair gaming
 * @dev Stores SHA256 hashes of server seeds before game starts, allows verification after
 */
contract MinesVerifier {
    
    struct GameCommitment {
        bytes32 seedHash;
        address committer;
        uint256 timestamp;
        bool revealed;
        bytes32 serverSeed;
    }
    
    // gameId => commitment
    mapping(string => GameCommitment) public games;
    
    // Events for transparency
    event GameCommitted(string indexed gameId, bytes32 seedHash, uint256 timestamp);
    event GameRevealed(string indexed gameId, bytes32 serverSeed, uint256 timestamp);
    
    /**
     * @notice Commit a seed hash before game starts
     * @param gameId Unique identifier for the game
     * @param seedHash SHA256 hash of the server seed
     */
    function commitGame(string calldata gameId, bytes32 seedHash) external {
        require(games[gameId].timestamp == 0, "Game already committed");
        require(seedHash != bytes32(0), "Invalid seed hash");
        
        games[gameId] = GameCommitment({
            seedHash: seedHash,
            committer: msg.sender,
            timestamp: block.timestamp,
            revealed: false,
            serverSeed: bytes32(0)
        });
        
        emit GameCommitted(gameId, seedHash, block.timestamp);
    }
    
    /**
     * @notice Reveal the server seed after game ends
     * @param gameId The game to reveal
     * @param serverSeed The actual server seed (will be hashed and compared)
     */
    function revealGame(string calldata gameId, bytes32 serverSeed) external {
        GameCommitment storage game = games[gameId];
        require(game.timestamp != 0, "Game not found");
        require(!game.revealed, "Already revealed");
        
        // Verify the seed matches the commitment
        bytes32 computedHash = sha256(abi.encodePacked(serverSeed));
        require(computedHash == game.seedHash, "Seed does not match commitment");
        
        game.revealed = true;
        game.serverSeed = serverSeed;
        
        emit GameRevealed(gameId, serverSeed, block.timestamp);
    }
    
    /**
     * @notice Verify a game's fairness (can be called by anyone)
     * @param gameId The game to verify
     * @param serverSeed The server seed to verify
     * @return valid True if the seed matches the on-chain commitment
     */
    function verifyGame(string calldata gameId, bytes32 serverSeed) external view returns (bool valid) {
        GameCommitment storage game = games[gameId];
        require(game.timestamp != 0, "Game not found");
        
        bytes32 computedHash = sha256(abi.encodePacked(serverSeed));
        return computedHash == game.seedHash;
    }
    
    /**
     * @notice Get game details
     * @param gameId The game ID to query
     */
    function getGame(string calldata gameId) external view returns (
        bytes32 seedHash,
        address committer,
        uint256 timestamp,
        bool revealed,
        bytes32 serverSeed
    ) {
        GameCommitment storage game = games[gameId];
        return (game.seedHash, game.committer, game.timestamp, game.revealed, game.serverSeed);
    }
}
