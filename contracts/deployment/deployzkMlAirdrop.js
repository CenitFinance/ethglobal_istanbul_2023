/* eslint-disable no-await-in-loop */
/* eslint-disable no-console, no-inner-declarations, no-undef, import/no-unresolved */

const { ethers, upgrades } = require('hardhat');
const path = require('path');
const fs = require('fs');
require('dotenv').config({ path: path.resolve(__dirname, '../../.env') });

const pathOutputJson = path.join(__dirname, './deploy_output.json');

async function main() {
     const currentProvider = ethers.provider;

    let deployer;
    if (process.env.PVTK_DEPLOYMENT) {
        deployer = new ethers.Wallet(process.env.PVTK_DEPLOYMENT, currentProvider);
        console.log('using pvtKey', deployer.address);
    } else {
        deployer = ethers.Wallet.fromMnemonic(process.env.MNEMONIC, 'm/44\'/60\'/0\'/0/0').connect(currentProvider);
        console.log('using Mnemonic', deployer.address);
    }

    
    // deploy timelock
    const tokenName = "Thenis token";
    const tokenSymbol = 'THENIST';
    const tokenInitialBalance = ethers.utils.parseEther('20000000');

    const tokenFactory = await ethers.getContractFactory("ERC20PermitMock", deployer);
    tokenContract = await tokenFactory.deploy(
            tokenName,
            tokenSymbol,
            deployer.address,
            tokenInitialBalance,
        );
  
    await tokenContract.deployed();
    
    // deploy timelock
    const zkMLAirdropContractFactory = await ethers.getContractFactory("zkMLAirdrop", deployer);

    const zkMLAirdropContract = await zkMLAirdropContractFactory.deploy(
        tokenContract.address
    );
    await zkMLAirdropContract.deployed();

    console.log('#######################\n');
    console.log('zkMLAirdrop deployed to:', zkMLAirdropContract.address);

    // Add airdrop
    const AllocationParameters =
    [
        {
            zkMLPoints: 5000,
            allocation: ethers.utils.parseEther('1')
        },
        {
            zkMLPoints: 10000,
            allocation: ethers.utils.parseEther('2')
        }
    ]

    const VerifierMockFactory = await ethers.getContractFactory("VerifierMock", deployer);

    const verifierContract = await VerifierMockFactory.deploy();

    await tokenContract.transfer(zkMLAirdropContract.address, ethers.utils.parseEther('5000000'));

    await (await zkMLAirdropContract.submitAirdropParameters(AllocationParameters, verifierContract.address)).wait()

    const zkProofFFlonk = new Array(24).fill(ethers.constants.HashZero);
    const publics = [0,0,0,400];

    await (await zkMLAirdropContract.verifyUserAllocation(0, deployer.address, zkProofFFlonk, publics)).wait();
    await (await zkMLAirdropContract.claimRewards(deployer.address)).wait();

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
