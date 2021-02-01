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

contract ConcurrentQueue {
    function create(string calldata id, uint256 elemType) external;
    function size(string calldata id) external view returns (uint256);
    function pushUint256(string calldata id, uint256 value) external;
    function popUint256(string calldata id) external returns (uint256);
}

contract ConcurrentArray {
    function create(string calldata id, int32 elemType, int32 size) external;
    function size(string calldata id) external view returns (uint256);
    function set(string calldata id, int32 index, uint256 value) external;
    function getUint256(string calldata id, int32 index) external view returns (uint256);
    function set(string calldata id, int32 index, address value) external;
    function getAddress(string calldata id, int32 index) external view returns (address);
    function set(string calldata id, int32 index, bytes calldata value) external;
    function getBytes(string calldata id, int32 index) external view returns (bytes memory);
}

contract ConcurrentVariable {
    function create(string calldata name, int32 valueType) external;
    function set(string calldata name, uint256 value) external;
    function getUint256(string calldata name) external view returns (uint256);
    function set(string calldata name, address value) external;
    function getAddress(string calldata name) external view returns (address);
    function set(string calldata name, bytes calldata value) external;
    function getBytes(string calldata name) external view returns (bytes memory);
}

contract UUID {
    function gen(string calldata id) external pure returns (uint256);
}

contract System {
    function createDefer(string calldata id, string calldata signature) external;
    function callDefer(string calldata id) external;
}