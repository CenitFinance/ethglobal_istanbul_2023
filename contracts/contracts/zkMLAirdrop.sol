// SPDX-License-Identifier: AGPL-3.0
pragma solidity 0.8.23;

import {Ownable} from "@openzeppelin/contracts/access/Ownable.sol";
import "./interfaces/IVerifier.sol";
import "@openzeppelin/contracts/token/ERC20/utils/SafeERC20.sol";

/**
 * Contract responsible to manage a zkML airdrop
 */
contract ZkMLAirdrop is Ownable {
    using SafeERC20 for IERC20;

    /**
     * @notice Struct  of allocation parameters
     * @param zkMLPoints zkML points, maximum should be 10000
     * @param tokenAllocation Token allocation if the users is inside the zkML points range
     */
    struct AllocationParameters {
        uint128 zkMLPoints;
        uint128 allocation;
    }

    // ZKML Max points
    uint256 public constant MAX_ZKML_POINTS = 10000;

    // Token airdrop
    IERC20 public immutable token;

    // Airdrop Count
    uint256 public airdropCount;

    // airdropID --> claimedBalance
    mapping(uint256 airdropID => AllocationParameters[] allocationParameters) public airdropMap;

    // beneficiary --> claimedBalance
    mapping(address beneficiary => uint256 zkMLPoints) public zkMLPointsMap;

    // Leaf index --> claimed bit map
    mapping(address beneficiary => mapping(uint256 airdropID => uint256 bitmap))
        public airdropPerUserBitMap;

    // beneficiary --> claimedBalance
    mapping(address beneficiary => uint256 claimableBalance) public claimableBalances;

    // Token airdrop
    IVerifier public verifier;

    /**
     * @dev Emitted when the pending governance accepts the governance
     */
    event SubmitAirdropParameters(uint256 airdropID);

    /**
     * @dev Emitted when a user claim his rewards
     */
    event ClaimRewards(address beneficiary, uint256 amount);

    constructor(IERC20 _token, IVerifier _verifier) {
        token = _token;
        verifier = _verifier;
    }

    /**
     * @notice Claim available rewards
     * @param beneficiary Beneficiary address
     */
    function claimRewards(address beneficiary) external {
        uint256 airdropID = airdropCount;

        require(airdropID != 0, "ZkMLAirdrop::submitAirdropParameters: There's no airdrop yet");

        // Check and set nullifier
        _setAndCheckClaimed(beneficiary, airdropID);
        uint256 claimableBalance = getClaimableBalance(beneficiary, airdropID);

        require(claimableBalance != 0, "ZkMLAirdrop::submitAirdropParameters: No tokens to claim");

        token.safeTransfer(beneficiary, claimableBalance);

        emit ClaimRewards(beneficiary, claimableBalance);
    }

    ////////////////////////
    // Owner functions
    ////////////////////////

    /**
     * @notice Submit airdrop parameters
     * @param allocationParameters Validator ID array
     */
    function submitAirdropParameters(
        AllocationParameters[] memory allocationParameters
    ) external onlyOwner {
        // Check allocation parameters
        airdropCount++;
        uint256 airdropID = airdropCount;

        // Load new airdrop
        AllocationParameters[] storage currentAllocationParameters = airdropMap[airdropID];

        // Check allocation parameters and save them on the airdrop
        uint256 currentzkMLPoints = 0;
        for (uint256 i = 0; i < allocationParameters.length; i++) {
            // Check that the array must be ordered
            require(
                currentzkMLPoints < allocationParameters[i].zkMLPoints,
                "ZkMLAirdrop::submitAirdropParameters: allocationParameters Array must be ordered"
            );

            // update current zkML points
            currentzkMLPoints = allocationParameters[i].zkMLPoints;

            // Update Airdrop parameters
            currentAllocationParameters.push(allocationParameters[i]);
        }

        // Check that the last zkMLPoints is MAX_ZKML_POINTS
        require(
            currentzkMLPoints == MAX_ZKML_POINTS,
            "ZkMLAirdrop::submitAirdropParameters: last element must be the MAX_ZKML_POINTS"
        );

        emit SubmitAirdropParameters(airdropID);
    }

    /**
     * @notice Verify user allocation
     * @param beneficiaryArray Verifier conctract
     * @param proofArray Proof
     * @param pubSignalsArray Pub signals
     */
    function verifyUserAllocations(
        address[] memory beneficiaryArray,
        bytes32[24][] calldata proofArray,
        uint256[4][] calldata pubSignalsArray
    ) external onlyOwner {
        require(
            beneficiaryArray.length == proofArray.length,
            "ZkMLAirdrop::verifyUserAllocation: array length does not match"
        );
        require(
            beneficiaryArray.length == pubSignalsArray.length,
            "ZkMLAirdrop::verifyUserAllocation: array length does not match"
        );
        for (uint256 i = 0; i < beneficiaryArray.length; i++) {
            verifyUserAllocation(beneficiaryArray[i], proofArray[i], pubSignalsArray[i]);
        }
    }

    /**
     * @notice  Verify user allocation
     * @param beneficiary Verifier conctract
     * @param proof Proof
     * @param pubSignals Pub signals
     */
    function verifyUserAllocation(
        address beneficiary,
        bytes32[24] calldata proof,
        uint256[4] calldata pubSignals
    ) public onlyOwner {
        // Verify proof
        require(
            verifier.verifyProof(proof, pubSignals) == true,
            "ZkMLAirdrop::verifyUserAllocation: Proof failed"
        );

        uint256 currentzkMLPoints = pubSignals[3]; // Output of the verify function

        // Sanity check agains allucinations
        if (currentzkMLPoints > MAX_ZKML_POINTS) {
            currentzkMLPoints = MAX_ZKML_POINTS;
        }

        // Update zkML points
        // If we decide that we will have different set of users we might need to update this function
        // to "reset" all the mapping everytime a new proof is verified
        zkMLPointsMap[beneficiary] = currentzkMLPoints;
    }

    ///////////////////
    // View functions
    ///////////////////

    /**
     * @notice Function to check the current claimable amount
     * @param beneficiary User beneficiary
     */
    function getCurrentClaimableBalance(address beneficiary) external view returns (uint256) {
        uint256 airdropID = airdropCount;
        return getClaimableBalance(beneficiary, airdropID);
    }

    /**
     * @notice Function to check the current claimable amount on certain airdropID
     * @param beneficiary User beneficiary
     * @param airdropID Airdrop ID
     */
    function getClaimableBalance(
        address beneficiary,
        uint256 airdropID
    ) public view returns (uint256) {
        AllocationParameters[] storage currentAllocationParameters = airdropMap[airdropID];

        uint256 userzkMLPoints = zkMLPointsMap[beneficiary];

        // If the users does not have points, don't have any airdrop to claim
        if (userzkMLPoints == 0) {
            return 0;
        }

        uint256 claimableBalance;

        for (uint256 i = 0; i < currentAllocationParameters.length; i++) {
            if (userzkMLPoints <= currentAllocationParameters[i].zkMLPoints) {
                claimableBalance = currentAllocationParameters[i].allocation;
                break;
            }
        }

        return claimableBalance;
    }

    /**
     * @notice Function to check if an index is claimed or not
     * @param beneficiary User beneficiary
     * @param aidropID airdrop ID
     */
    function isClaimed(address beneficiary, uint256 aidropID) external view returns (bool) {
        (uint256 wordPos, uint256 bitPos) = _bitmapPositions(aidropID);
        uint256 mask = (1 << bitPos);
        return (airdropPerUserBitMap[beneficiary][wordPos] & mask) == mask;
    }

    /**
     * @notice Function to check that an index is not claimed and set it as claimed
     * @param beneficiary User beneficiary
          * @param aidropID airdrop ID

     */
    function _setAndCheckClaimed(address beneficiary, uint256 aidropID) private {
        (uint256 wordPos, uint256 bitPos) = _bitmapPositions(aidropID);
        uint256 mask = 1 << bitPos;
        uint256 flipped = airdropPerUserBitMap[beneficiary][wordPos] ^= mask;
        if (flipped & mask == 0) {
            revert("ZkMLAirdrop::_setAndCheckClaimed: Already claimed");
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
    function getAirdropParameters(
        uint256 airdropID
    ) external view returns (AllocationParameters[] memory) {
        return airdropMap[airdropID];
    }
}
