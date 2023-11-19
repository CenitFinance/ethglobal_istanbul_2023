/* eslint-disable import/no-dynamic-require, no-await-in-loop, no-restricted-syntax, guard-for-in */
require('dotenv').config();
const hre = require('hardhat');
const { expect } = require('chai');
const deployOutput = require('./deploy_output.json');

async function main() {
    // load deployer account
    if (typeof process.env.ETHERSCAN_API_KEY === 'undefined') {
        throw new Error('Etherscan API KEY has not been defined');
    }

    const tokenName = "Thenis token";
    const tokenSymbol = 'THENIST';
    const tokenInitialBalance = ethers.utils.parseEther('2000000000');

    try {
        await hre.run('verify:verify', { address: deployOutput.tokenContract, constructorArguments: [
            tokenName,
            tokenSymbol,
            deployOutput.deployer,
            tokenInitialBalance,
            ]
         });
    } catch (error) {
        console.log(error)
        expect(error.message.toLowerCase().includes('already verified')).to.be.equal(true);
    }
    try {
        await hre.run('verify:verify', { 
            address: deployOutput.zkMLAirdropContract,  
            constructorArguments: [
                deployOutput.tokenContract,
                deployOutput.verifierContract
            ], 
        });
    } catch (error) {
        console.log(error)
        expect(error.message.toLowerCase().includes('already verified')).to.be.equal(true);
    }
}

main()
    .then(() => process.exit(0))
    .catch((error) => {
        console.error(error);
        process.exit(1);
    });
