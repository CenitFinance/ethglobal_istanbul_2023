// SPDX-License-Identifier: AGPL-3.0

pragma solidity 0.8.23;

import "../interfaces/IVerifier.sol";

contract VerifierMock is IVerifier {
    function verifyProof(
        bytes32[24] calldata proof,
        uint256[4] memory pubSignals
    ) public pure override returns (bool) {
        return true;
    }
}
