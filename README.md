# Themis: Smart Incentivization with ZKML

## Description

Themis is a framework for improving protocol incentives and optimizing for long-term loyalty through data-driven analysis. It delivers those improvements in a trustless manner using Zero-Knowledge Proofs over the Machine Learning model results (ZKML).

Web3 protocols commonly employ airdrops or other kinds of incentives for improving user acquisition and rewarding user engagement with the project. However, it’s clear that this mechanism lacks the ability to retain users or boost users’ loyalty.
We propose Themis, a framework for improving protocol incentives towards long-term user loyalty and engagement with the project. The general process is as follows:

1. A machine learning forecasting model to predict long-term user loyalty is built over on-chain data and proposed to the protocol community. 

2. The DAO or equivalent governing body votes and approves on the model based on its performance, deploying a ZK verification smart contract. The model and its compiled ZK version for generating proofs are published for anyone to use.

3. Anyone can now generate new predictions with the model based on new valid on-chain data, and submit the new predictions to the smart contract. The smart contract will only accept predictions if they have been generated correctly from the approved model. Therefore, this step is trustless and permissionless.

4. An interactive dashboard can be used to read and analyze the predictions submitted to the smart contract, as well as other relevant user base data, and decide on a strategy for distributing the incentives, represented by a set of parameters. For example, a strategy could optimize for preventing churn by incentivizing users with high likelihood of ceasing further activity in the protocol. A different strategy could instead optimize for rewarding users with likelihood of high engagement.

5. After a strategy is decided, with a certain token allocation, it can be approved and then the tokens can be claimed by the respective recipients.

6. Periodically, the same model, associated with the deployed ZK-proof verifier, can be used to trustlessly update the predictions (along with inference proofs) and create new incentive strategies.

## Repository Structure

The repository is structured as follows:
 * [backend](backend): Contains the backend code for the Themis dashboard, written in Python using FastAPI.
 * [frontend](frontend): Contains the frontend code for the Themis dashboard, written in Vue.js.
 * [contracts](contracts): Contains the code for the incentives management smart contracts, written in Solidity.
 * [ml_pipeline](ml_pipeline): Contains the code for the machine learning training pipeline, written in Python using PyTorch, as well as the ZKML compilation pipeline, written in Python using EZKL.
 * [notebooks](notebooks): Contains the Jupyter notebooks used for data analysis, feature engineering, and early tests for the ML pipeline.


