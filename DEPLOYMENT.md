# Mines Blockchain Deployment Guide

Deploy the provably fair Mines game with on-chain verification on Sepolia testnet.

## Overview

The smart contract stores seed hash commitments on Sepolia testnet:
1. When a game starts → seed hash is committed to blockchain
2. When game ends → server seed is revealed on-chain
3. Anyone can verify the seed matches the original commitment

## Prerequisites

- Node.js 18+
- Python 3.10+
- A wallet with Sepolia ETH (free from faucets)

## Step 1: Get Sepolia Test ETH

Get free Sepolia ETH from these faucets:
- https://sepoliafaucet.com/ (needs Alchemy account)
- https://www.alchemy.com/faucets/ethereum-sepolia
- https://sepolia-faucet.pk910.de/ (PoW faucet, no signup)

⚠️ **Create a NEW wallet for testing** - never use your main wallet!

## Step 2: Deploy the Smart Contract

```bash
cd contracts

# Install dependencies
npm install

# Create .env file with your private key
cat > .env << EOF
PRIVATE_KEY=your_wallet_private_key_without_0x
SEPOLIA_RPC_URL=https://rpc.sepolia.org
EOF

# Compile the contract
npm run compile

# Deploy to Sepolia
npm run deploy:sepolia
```

Save the deployed contract address from the output.

## Step 3: Configure Backend

```bash
cd backend

# Install Python dependencies
pip install -r requirements.txt

# Create .env file
cat > .env << EOF
CONTRACT_ADDRESS=0xYOUR_CONTRACT_ADDRESS_HERE
SEPOLIA_RPC_URL=https://rpc.sepolia.org
PRIVATE_KEY=your_wallet_private_key_without_0x
EOF

# Run the backend
python app.py
```

## Step 4: Run Frontend

```bash
cd frontend
npm install
npm run dev
```

Open http://localhost:5173

## How It Works

### Provable Fairness Flow

```
Game Start:
1. Server generates random server_seed
2. SHA256(server_seed) = seed_hash
3. seed_hash is committed to Sepolia blockchain
4. Player sees seed_hash BEFORE playing

Game Play:
5. Player reveals tiles
6. Mine positions determined by: SHA256(server_seed + client_seed + nonce)

Game End:
7. Server reveals actual server_seed
8. Server seed is revealed on blockchain
9. Anyone can verify SHA256(server_seed) == committed seed_hash
```

### Smart Contract Functions

- `commitGame(gameId, seedHash)` - Store hash before game starts
- `revealGame(gameId, serverSeed)` - Reveal seed after game ends
- `verifyGame(gameId, serverSeed)` - Anyone can verify
- `getGame(gameId)` - Read commitment data

## Verification

After any game, you can verify fairness:

1. **On-chain verification**: Check the Etherscan links shown in the UI
2. **Local verification**: 
   - Take the revealed `server_seed`
   - Compute `SHA256(server_seed)` 
   - Compare with the `seed_hash` shown before the game
   - They MUST match

## Contract Address

After deployment, your contract will be at:
`https://sepolia.etherscan.io/address/YOUR_CONTRACT_ADDRESS`

## Cost

- Deploying contract: ~0.001-0.005 Sepolia ETH
- Each game commitment: ~0.0001 Sepolia ETH
- Each reveal: ~0.0001 Sepolia ETH

All on testnet = **FREE** (testnet ETH has no value)

## Testing Locally (Optional)

You can also run a local Hardhat node for testing:

```bash
cd contracts

# Terminal 1: Start local node
npm run node

# Terminal 2: Deploy locally
npm run deploy:local
```

Then update backend `.env` with:
```
SEPOLIA_RPC_URL=http://127.0.0.1:8545
CONTRACT_ADDRESS=0x...local_address...
```
