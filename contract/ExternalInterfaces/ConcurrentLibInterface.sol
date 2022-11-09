pragma solidity ^0.5.0;

contract ConcurrentLib {
    enum DataType {INVALID, ADDRESS, UINT256, BYTES}
}

contract ConcurrentArray {
    /// @notice Create a new concurrent array, init every element to 0
    /// @param id Name of the array, should be unique in the contract it belongs to
    /// @param size Size of the array
    /// @param elemType Type of the array elements
    function create(string calldata id, uint256 size, int32 elemType) external;

    /// @notice Get the size of the array, cause an exception when the container id doesn't exist or index out of range
    /// @param id Name of the array
    /// @return size of the array
    function size(string calldata id) external view returns(uint256);

    /// @notice Get a specific element from an array containing addresses, cause an exception when the container id doesn't exist or index out of range
    /// @param id Name of the array
    /// @param index Index of the element
    /// @return value of the element
    function getAddress(string calldata id, uint256 index) external view returns(address);

    /// @notice Update a specific element in the array, cause an exception when the container id doesn't exist or index out of range
    /// @param id Name of the array
    /// @param index Index of the element
    /// @param value New value of the element
    function set(string calldata id, uint256 index, address value) external;

    /// @notice Get a specific element from an array containing uint256s, cause an exception when the container id doesn't exist or index out of range
    /// @param id Name of the array
    /// @param index Index of the element
    /// @return value of the element
    function getUint256(string calldata id, uint256 index) external view returns(uint256);

    /// @notice Update a specific element in the array, cause an exception when the container id doesn't exist or index out of range
    /// @param id Name of the array
    /// @param index Index of the element
    /// @param value New value of the element
    function set(string calldata id, uint256 index, uint256 value) external;

    /// @notice Get a specific element from an array containing byte arrays, cause an exception when the container id doesn't exist or index out of range
    /// @param id Name of the array
    /// @param index Index of the element
    /// @return value of the element
    function getBytes(string calldata id, uint256 index) external view returns(bytes memory);

    /// @notice Update a specific element in the array, cause an exception when the container id doesn't exist or index out of range
    /// @param id Name of the array
    /// @param index Index of the element
    /// @param value New value of the element
    function set(string calldata id, uint256 index, bytes calldata value) external;
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

contract System {
    /// @notice Bind a function to a defer call id
    /// @param id The defer call id
    /// @param signature The signature of the function
    function createDefer(string calldata id, string calldata signature) external;

    /// @notice Call the deferred function specified by id
    /// @param id The defer call id
    function callDefer(string calldata id) external;

    /// @notice Get the PID of the current transaction
    /// @return PID of the current transaction
    function getPid() external returns(uint256);

    /// @notice Revert all the modifications related to the specific PID
    /// @param pid The PID to revert
    function revertPid(uint256 pid) external;
}

contract ConcurrentQueue {
    /// @notice Create a new queue
    /// @param id Name of the queue, should be unique in the contract it belongs to
    /// @param elemType Type of the element in queue
    function create(string calldata id, uint256 elemType) external;

    /// @notice Get the size of the queue, cause exception if the container id doesn't exist
    /// @param id Name of the queue
    /// @return size of the queue
    function size(string calldata id) external view returns(uint256);

    /// @notice Append a new entry to the tail of the queue, cause exception if the container id doesn't exist
    /// @param id Name of the queue
    /// @param value The entry to append
    function pushUint256(string calldata id, uint256 value) external;

    /// @notice Remove the head entry from the queue, cause exception if the container id doesn't exist or the queue is empty
    /// @param id Name of the queue
    /// @return the entry removed
    function popUint256(string calldata id) external returns(uint256);

    /// @notice Append a new entry to the tail of the queue, cause exception if the container id doesn't exist
    /// @param id Name of the queue
    /// @param value The entry to append
    function pushAddress(string calldata id, address value) external;

    /// @notice Remove the head entry from the queue, cause exception if the container id doesn't exist or the queue is empty
    /// @param id Name of the queue
    /// @return the entry removed
    function popAddress(string calldata id) external returns(address);

    /// @notice Append a new entry to the tail of the queue, cause exception if the container id doesn't exist
    /// @param id Name of the queue
    /// @param value The entry to append
    function pushBytes(string calldata id, bytes calldata value) external;

    /// @notice Remove the head entry from the queue, cause exception if the container id doesn't exist or the queue is empty
    /// @param id Name of the queue
    /// @return the entry removed
    function popBytes(string calldata id) external returns(bytes memory);
}

contract DynamicArray {
    function create(string calldata id, uint256 elemType) external;
    function length(string calldata id) external view returns(uint256);

    function pushBack(string calldata id, uint256 elem) external;
    function pushBack(string calldata id, address elem) external;
    function pushBack(string calldata id, bytes calldata elem) external;

    function tryPopFrontUint256(string calldata id) external returns(uint256, bool);
    function tryPopFrontAddress(string calldata id) external returns(address, bool);
    function tryPopFrontBytes(string calldata id) external returns(bytes memory, bool);
    function popFrontUint256(string calldata id) external returns(uint256);
    function popFrontAddress(string calldata id) external returns(address);
    function popFrontBytes(string calldata id) external returns(bytes memory);

    function tryPopBackUint256(string calldata id) external returns(uint256, bool);
    function tryPopBackAddress(string calldata id) external returns(address, bool);
    function tryPopBackBytes(string calldata id) external returns(bytes memory, bool);
    function popBackUint256(string calldata id) external returns(uint256);
    function popBackAddress(string calldata id) external returns(address);
    function popBackBytes(string calldata id) external returns(bytes memory);

    function tryGetUint256(string calldata id, uint256 index) external returns(uint256, bool);
    function tryGetAddress(string calldata id, uint256 index) external returns(address, bool);
    function tryGetBytes(string calldata id, uint256 index) external returns(bytes memory, bool);
    function getUint256(string calldata id, uint256 index) external returns(uint256);
    function getAddress(string calldata id, uint256 index) external returns(address);
    function getBytes(string calldata id, uint256 index) external returns(bytes memory);
}