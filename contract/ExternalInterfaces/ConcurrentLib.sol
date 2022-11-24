pragma solidity ^0.5.0;

contract UUID {
    function gen(string calldata id) external pure returns (uint256);
}

contract System {
    function createDefer(string calldata id, string calldata signature) external;
    function callDefer(string calldata id) external;
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

library Concurrency {
    enum DataType { INVALID, ADDRESS, UINT256, BYTES }

    DynamicArray constant private darray = DynamicArray(address(0x84));
    System constant private sys = System(address(0xa1));
    UUID constant private uuid = UUID(address(0xa0));

    struct Array {
        string id;
    }

    function Init(Array storage self, string memory id, DataType typ) public {
        self.id = id;
        darray.create(id, uint256(typ));
    }

    function Length(Array storage self) public view returns(uint256) {
        return darray.length(self.id);
    }

    function PushBack(Array storage self, uint256 elem) public {
        darray.pushBack(self.id, elem);
    }

    function PushBack(Array storage self, address elem) public {
        darray.pushBack(self.id, elem);
    }

    function PushBack(Array storage self, bytes memory elem) public {
        darray.pushBack(self.id, elem);
    }

    function TryPopFrontUint256(Array storage self) public returns(uint256, bool) {
        return darray.tryPopFrontUint256(self.id);
    }

    function TryPopFrontAddress(Array storage self) public returns(address, bool) {
        return darray.tryPopFrontAddress(self.id);
    }

    function TryPopFrontBytes(Array storage self) public returns(bytes memory, bool) {
        return darray.tryPopFrontBytes(self.id);
    }

    function PopFrontUint256(Array storage self) public returns(uint256) {
        return darray.popFrontUint256(self.id);
    }

    function PopFrontAddress(Array storage self) public returns(address) {
        return darray.popFrontAddress(self.id);
    }

    function TryPopBackUint256(Array storage self) public returns(uint256, bool) {
        return darray.tryPopBackUint256(self.id);
    }

    function TryPopBackAddress(Array storage self) public returns(address, bool) {
        return darray.tryPopBackAddress(self.id);
    }

    function TryPopBackBytes(Array storage self) public returns(bytes memory, bool) {
        return darray.tryPopBackBytes(self.id);
    }

    function PopBackUint256(Array storage self) public returns(uint256) {
        return darray.popBackUint256(self.id);
    }

    function PopBackAddress(Array storage self) public returns(address) {
        return darray.popBackAddress(self.id);
    }

    function PopBackBytes(Array storage self) public returns(bytes memory) {
        return darray.popBackBytes(self.id);
    }

    function TryGetUint256(Array storage self, uint256 index) public returns(uint256, bool) {
        return darray.tryGetUint256(self.id, index);
    }

    function TryGetAddress(Array storage self, uint256 index) public returns(address, bool) {
        return darray.tryGetAddress(self.id, index);
    }

    function TryGetBytes(Array storage self, uint256 index) public returns(bytes memory, bool) {
        return darray.tryGetBytes(self.id, index);
    }

    function GetUint256(Array storage self, uint256 index) public returns(uint256) {
        return darray.getUint256(self.id, index);
    }

    function GetAddress(Array storage self, uint256 index) public returns(address) {
        return darray.getAddress(self.id, index);
    }

    function GetBytes(Array storage self, uint256 index) public returns(bytes memory) {
        return darray.getBytes(self.id, index);
    }

    struct Deferred {
        string id;
    }

    function Init(Deferred storage self, string memory id, string memory signature) public {
        sys.createDefer(id, signature);
        self.id = id;
    }

    function Call(Deferred storage self) public {
        sys.callDefer(self.id);
    }

    struct Util {
        uint _placeholder;
    }

    function GenUUID(Util storage, string memory seed) public pure returns(uint256) {
        return uuid.gen(seed);
    }
}
