/* eslint-disable no-await-in-loop */
/* eslint-disable no-console, no-inner-declarations, no-undef, import/no-unresolved */

const { ethers, upgrades } = require('hardhat');
const path = require('path');
const fs = require('fs');
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });

const folderPath = path.join(__dirname, `./${process.env.HARDHAT_NETWORK}`);
const pathOutputJson = path.join(__dirname, `./${process.env.HARDHAT_NETWORK}/deploy_output.json`);

async function main() {
    if (!fs.existsSync(folderPath)){
        fs.mkdirSync(folderPath);
    }

     const currentProvider = ethers.provider;

    let deployer;
    if (process.env.PVTK_DEPLOYMENT) {
        deployer = new ethers.Wallet(process.env.PVTK_DEPLOYMENT, currentProvider);
        console.log('using pvtKey', deployer.address);
    } else {
        deployer = ethers.Wallet.fromMnemonic(process.env.MNEMONIC, 'm/44\'/60\'/0\'/0/0').connect(currentProvider);
        console.log('using Mnemonic', deployer.address);
    }

    const zkProofFFlonk = new Array(24).fill(ethers.constants.HashZero);
    const proofsArray = [];
    const publicsArray = [];
    const beneficiarysArray = [];

    for(let i = 0; i < 9; i++) {
        const wallet = ethers.Wallet.fromMnemonic(process.env.WALLETS_MNEMONIC, `m/44\'/60\'/0\'/0/${i}`);
        const randomNumber = Math.floor(Math.random() * 10000) + 1;
        const publics = [0, 0, 0, randomNumber];
        proofsArray.push(
            zkProofFFlonk
        )
        publicsArray.push(
            publics
        )
        beneficiarysArray.push(
            wallet.address
        )
    }

    // Add our deployer
    proofsArray.push(
        zkProofFFlonk
    )

    publicsArray.push(
        [0, 0, 0, 9999]
    )
    beneficiarysArray.push(
        deployer.address
    )

    const VerifierMockFactory = await ethers.getContractFactory("VerifierMock", deployer);
    const verifierContract = await VerifierMockFactory.deploy();
    await verifierContract.deployed();

    // deploy timelock
    const tokenName = "Thenis token";
    const tokenSymbol = 'THENIST';
    const tokenInitialBalance = ethers.utils.parseEther('2000000000');

    const tokenFactory = await ethers.getContractFactory("ERC20PermitMock", deployer);
    tokenContract = await tokenFactory.deploy(
            tokenName,
            tokenSymbol,
            deployer.address,
            tokenInitialBalance,
        );
  
    await tokenContract.deployed();
    
    // deploy timelock
    const zkMLAirdropContractFactory = await ethers.getContractFactory("ZkMLAirdrop", deployer);

    const zkMLAirdropContract = await zkMLAirdropContractFactory.deploy(
        tokenContract.address,
        verifierContract.address
    );
    await zkMLAirdropContract.deployed();

    console.log('#######################\n');
    console.log('zkMLAirdrop deployed to:', zkMLAirdropContract.address);

    await (await tokenContract.transfer(zkMLAirdropContract.address, ethers.utils.parseEther('50000000'))).wait();
    await (await zkMLAirdropContract.connect(deployer).verifyUserAllocations(beneficiarysArray, proofsArray, publicsArray)).wait();

    //  // Add airdrop
    //  const AllocationParameters =
    //  [
    //      {
    //          zkMLPoints: 5000,
    //          allocation: ethers.utils.parseEther('100')
    //      },
    //      {
    //          zkMLPoints: 10000,
    //          allocation: ethers.utils.parseEther('200')
    //      }
    //  ]
     
    //  await (await zkMLAirdropContract.connect(deployer).submitAirdropParameters(AllocationParameters)).wait()
    //  await (await zkMLAirdropContract.connect(deployer).claimRewards(deployer.address)).wait();

  

    const outputJson = {
        zkMLAirdropContract: zkMLAirdropContract.address,
        tokenContract: tokenContract.address,
        deployer: deployer.address
    };
    fs.writeFileSync(pathOutputJson, JSON.stringify(outputJson, null, 1));
}

main().catch((e) => {
    console.error(e);
    process.exit(1);
});
