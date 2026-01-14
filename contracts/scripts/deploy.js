const hre = require("hardhat");

async function main() {
  console.log("Deploying MinesVerifier to", hre.network.name, "...");

  const MinesVerifier = await hre.ethers.getContractFactory("MinesVerifier");
  const verifier = await MinesVerifier.deploy();

  await verifier.waitForDeployment();

  const address = await verifier.getAddress();
  console.log("\n✅ MinesVerifier deployed to:", address);
  console.log("\nNext steps:");
  console.log("1. Update CONTRACT_ADDRESS in backend/app.py");
  console.log("2. Update CONTRACT_ADDRESS in frontend/src/lib/blockchain.js");
  console.log(`3. Verify on Etherscan: npx hardhat verify --network ${hre.network.name} ${address}`);
}

main()
  .then(() => process.exit(0))
  .catch((error) => {
    console.error(error);
    process.exit(1);
  });
