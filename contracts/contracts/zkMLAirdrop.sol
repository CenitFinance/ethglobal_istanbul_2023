// SPDX-License-Identifier: AGPL-3.0
pragma solidity 0.8.23;

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import "./interfaces/IVerifier.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * Contract responsible to manage a zkML airdrop
 */
contract zkMLAirdrop is Ownable {
    using SafeERC20 for IERC20;

    /**
     * @notice Struct  of allocation parameters
     * @param zkMLPoints zkML points, maximum should be 1000
     * @param tokenAllocation Token allocation if the users is inside the zkML points range
     */
    struct AllocationParameters {
        uint128 zkMLPoints;
        uint128 allocation;
    }   

    /**
     * @notice Struct to airdrop parameters
     * @param allocationParametrs Allocation parameters array
     * @param verifier Verifier contract
     */
    struct AirdropParameters {
        AllocationParameters[] allocationParameters;
        IVerifier verifier;
    }

    // ZKML Max points
    uint256 public constant MAX_ZKML_POINTS = 10000;

    // Token airdrop
    IERC20 public immutable token;

    // Airdrop Count
    uint256 public airdropCount;

    // airdropID --> claimedBalance
    mapping(uint256 airdropID => AirdropParameters) public airdropMapping;

    // Leaf index --> claimed bit map
    mapping(address => mapping(uint256 => uint256)) public airdropPerUserBitMap;

    // beneficiary --> claimedBalance
    mapping(address beneficiary => uint256 claimableBalance) public claimableBalances;

    /**
     * @dev Emitted when the pending governance accepts the governance
     */
    event SubmitAirdropParameters(uint256 airdropID);

 /**
     * @dev Emitted when a user claim his rewards
     */
    event ClaimRewards(address beneficiary, uint256 amount);

    constructor(IERC20 _token) {
        token = _token;
    }

    /**
     * @notice Claim available rewards
     * @param beneficiary Beneficiary address
     */
    function claimRewards(
        address beneficiary
    ) external {
        // Get claimable ether
        uint256 claimableBalance = claimableBalances[beneficiary];
        if(claimableBalance > 0) {
            claimableBalances[beneficiary] = 0;
            token.safeTransfer(beneficiary, claimableBalance);
        }

        emit ClaimRewards(beneficiary,claimableBalance);
    }

    ////////////////////////
    // Owner functions
    ////////////////////////

    
    /**
     * @notice Submit airdrop parameters
     * @param allocationParameters Validator ID array
     * @param verifier Verifier conctract
     */
    function submitAirdropParameters(
        AllocationParameters[] memory allocationParameters,
        IVerifier verifier
    ) external onlyOwner {
        // Check allocation parameters
        uint256 airdropID = airdropCount;
        
        // Load new airdrop
        AirdropParameters storage currentAirdrop = airdropMapping[airdropID];
        currentAirdrop.verifier = verifier;
        airdropCount++;

        // Check allocation parameters and save them on the airdrop
        uint256 currentzkMLPoints = 0;
        for (uint256 i = 0; i < allocationParameters.length; i++) {

            // Check that the array must be ordered
            require(currentzkMLPoints < allocationParameters[i].zkMLPoints,
            "zkMLAirdrop::submitAirdropParameters: allocationParameters Array must be ordered");

            // update current zkML points
            currentzkMLPoints = allocationParameters[i].zkMLPoints;

            // Update Airdrop parameters
            currentAirdrop.allocationParameters.push(allocationParameters[i]);
        }

        // Check that hte last zkMLPoints is MAX_ZKML_POINTS
        require(currentzkMLPoints == MAX_ZKML_POINTS,
            "zkMLAirdrop::submitAirdropParameters: last element must be the MAX_ZKML_POINTS");

        emit SubmitAirdropParameters(airdropID);
    }


    /**
     * @notice  Verify user allocation
     * @param airdropID Airdrop ID
     * @param beneficiary Verifier conctract
     * @param proof Proof
     * @param pubSignals Pub signals
     */
    function verifyUserAllocation(
        uint256 airdropID,
        address beneficiary,
        bytes32[24] calldata proof,
        uint256[4] memory pubSignals
    ) external onlyOwner {
        // TODO, part of the pubsingals should be verified, maybe using axiom with another ZKP
        // Beneficiary should be linked to this pubg signals
        require(airdropID < airdropCount,"zkMLAirdrop::submitAirdropParameters: airdrop does not exist" );

        // Check and set nullifier
        _setAndCheckClaimed(beneficiary, airdropID);

        // Current airdrop
        AirdropParameters memory currentAirdrop = airdropMapping[airdropID];

        // Verify proof
        require(currentAirdrop.verifier.verifyProof(proof, pubSignals) == true, "zkMLAirdrop::verifyUserAllocation: Proof failed");
        
        uint256 currentzkMLPoints = pubSignals[3]; // Output of the verify function

        // Sanity check agains allucinations
        if(currentzkMLPoints > MAX_ZKML_POINTS) {
            currentzkMLPoints = MAX_ZKML_POINTS;
        }

        // Check the user allocation inside the allocation parameters
        uint256 userAllocation;
        for ( uint256 i = 0; i <currentAirdrop.allocationParameters.length; i++ ) {
            if(currentzkMLPoints <= currentAirdrop.allocationParameters[i].zkMLPoints){
                userAllocation = currentAirdrop.allocationParameters[i].allocation;
                break;
            }
        }

        // Update claimable balances
        claimableBalances[beneficiary] += userAllocation;
    }


    ///////////////////
    // View functions
    ///////////////////

    /**
     * @notice Function to check if an index is claimed or not
       * @param beneficiary User beneficiary
          * @param aidropID airdrop ID
     */
    function isClaimed(
        address beneficiary,
        uint256 aidropID
    ) external view returns (bool) {
        (uint256 wordPos, uint256 bitPos) = _bitmapPositions(aidropID);
        uint256 mask = (1 << bitPos);
        return (airdropPerUserBitMap[beneficiary][wordPos] & mask) == mask;
    }

    /**
     * @notice Function to check that an index is not claimed and set it as claimed
     * @param beneficiary User beneficiary
          * @param aidropID airdrop ID

     */
    function _setAndCheckClaimed(
        address beneficiary,
        uint256 aidropID
    ) private {
        (uint256 wordPos, uint256 bitPos) = _bitmapPositions(aidropID);
        uint256 mask = 1 << bitPos;
        uint256 flipped = airdropPerUserBitMap[beneficiary][wordPos] ^= mask;
        if (flipped & mask == 0) {
            revert();
        }
    }

    /**
     * @notice Function decode an index into a wordPos and bitPos
     * @param index Index
     */
    function _bitmapPositions(
        uint256 index
    ) private pure returns (uint256 wordPos, uint256 bitPos) {
        wordPos = uint248(index >> 8);
        bitPos = uint8(index);
    }


    /**
     * @notice Return all the oracle members
     */
    function getAirdropParameters(uint256 airdropID) external view returns (AllocationParameters[] memory) {
        return airdropMapping[airdropID].allocationParameters;
    }

}
