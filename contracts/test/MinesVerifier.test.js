const { expect } = require("chai");
const { ethers } = require("hardhat");

describe("MinesVerifier", function () {
  let verifier;
  let owner;

  beforeEach(async function () {
    [owner] = await ethers.getSigners();
    const MinesVerifier = await ethers.getContractFactory("MinesVerifier");
    verifier = await MinesVerifier.deploy();
  });

  it("Should commit a game", async function () {
    const gameId = "test123";
    const serverSeed = ethers.encodeBytes32String("mysecretserverseed");
    const seedHash = ethers.sha256(serverSeed);

    await expect(verifier.commitGame(gameId, seedHash))
      .to.emit(verifier, "GameCommitted");

    const game = await verifier.getGame(gameId);
    expect(game.seedHash).to.equal(seedHash);
    expect(game.revealed).to.be.false;
    expect(game.timestamp).to.be.gt(0);
  });

  it("Should not allow duplicate commits", async function () {
    const gameId = "test123";
    const seedHash = ethers.keccak256(ethers.toUtf8Bytes("seed"));

    await verifier.commitGame(gameId, seedHash);
    await expect(verifier.commitGame(gameId, seedHash))
      .to.be.revertedWith("Game already committed");
  });

  it("Should reveal and verify a game", async function () {
    const gameId = "test456";
    const serverSeed = ethers.encodeBytes32String("actualseed");
    const seedHash = ethers.sha256(serverSeed);

    await verifier.commitGame(gameId, seedHash);
    
    // Verify before reveal
    expect(await verifier.verifyGame(gameId, serverSeed)).to.be.true;
    
    // Reveal
    await verifier.revealGame(gameId, serverSeed);
    
    const game = await verifier.getGame(gameId);
    expect(game.revealed).to.be.true;
    expect(game.serverSeed).to.equal(serverSeed);
  });

  it("Should reject invalid seed on reveal", async function () {
    const gameId = "test789";
    const serverSeed = ethers.encodeBytes32String("realseed");
    const fakeSeed = ethers.encodeBytes32String("fakeseed");
    const seedHash = ethers.sha256(serverSeed);

    await verifier.commitGame(gameId, seedHash);
    
    await expect(verifier.revealGame(gameId, fakeSeed))
      .to.be.revertedWith("Seed does not match commitment");
  });
});
