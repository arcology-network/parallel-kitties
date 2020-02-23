pragma solidity ^0.5.0;

contract ConcurrentLib {
    enum DataType {INVALID, ADDRESS, UINT256, BYTES}
}

contract ConcurrentHashMap {
    function create(string calldata id, int32 keyType, int32 valueType) external;

    function getAddress(string calldata id, uint256 key) external view returns (address);
    function set(string calldata id, uint256 key, address value) external;
    function getUint256(string calldata id, uint256 key) external view returns (uint256);
    function set(string calldata id, uint256 key, uint256 value) external;
    function getBytes(string calldata id, uint256 key) external view returns (bytes memory);
    function set(string calldata id, uint256 key, bytes calldata value) external;
    function deleteKey(string calldata id, uint256 key) external;

    function getAddress(string calldata id, address key) external view returns (address);
    function set(string calldata id, address key, address value) external;
    function getUint256(string calldata id, address key) external view returns (uint256);
    function set(string calldata id, address key, uint256 value) external;
    function getBytes(string calldata id, address key) external view returns (bytes memory);
    function set(string calldata id, address key, bytes calldata value) external;
    function deleteKey(string calldata id, address key) external;
}

contract UUID {
    function gen(string calldata id) external pure returns (uint256);
}