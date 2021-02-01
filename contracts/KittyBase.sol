pragma solidity ^0.5.0;

import "./KittyAccessControl.sol";
import "./ExternalInterfaces/ConcurrentLibInterface.sol";
import "./Auction/SaleClockAuction.sol";
import "./Auction/SiringClockAuction.sol";
import "./Seriality/Seriality.sol";

/// @title Base contract for CryptoKitties. Holds all common structs, events and base variables.
/// @author Axiom Zen (https://www.axiomzen.co)
/// @dev See the KittyCore contract documentation to understand how the various contract facets are arranged.
contract KittyBase is KittyAccessControl, Seriality {
    /*** EVENTS ***/

    /// @dev The Birth event is fired whenever a new kitten comes into existence. This obviously
    ///  includes any time a cat is created through the giveBirth method, but it is also called
    ///  when a new gen0 cat is created.
    event Birth(address indexed owner, uint256 kittyId, uint256 matronId, uint256 sireId, uint256 genes);

    /// @dev Transfer event as defined in current draft of ERC721. Emitted every time a kitten
    ///  ownership is assigned, including births.
    event Transfer(address indexed from, address indexed to, uint256 indexed tokenId);

    // For test.
    event BalanceOf(address a, uint256 balance);

    /*** DATA TYPES ***/

    /// @dev The main Kitty struct. Every cat in CryptoKitties is represented by a copy
    ///  of this structure, so great care was taken to ensure that it fits neatly into
    ///  exactly two 256-bit words. Note that the order of the members in this structure
    ///  is important because of the byte-packing rules used by Ethereum.
    ///  Ref: http://solidity.readthedocs.io/en/develop/miscellaneous.html
    struct Kitty {
        // The Kitty's genetic code is packed into these 256-bits, the format is
        // sooper-sekret! A cat's genes never change.
        uint256 genes;

        // The ID of the parents of this kitty, set to 0 for gen0 cats.
        uint256 matronId;
        uint256 sireId;

        // Set to the ID of the sire cat for matrons that are pregnant,
        // zero otherwise. A non-zero value here is how we know a cat
        // is pregnant. Used to retrieve the genetic material for the new
        // kitten when the birth transpires.
        uint256 siringWithId;

        // The timestamp from the block when this cat came into existence.
        uint64 birthTime;

        // The minimum timestamp after which this cat can engage in breeding
        // activities again. This same timestamp is used for the pregnancy
        // timer (for matrons) as well as the siring cooldown.
        uint64 cooldownEndTime;

        // Set to the index in the cooldown array (see below) that represents
        // the current cooldown duration for this Kitty. This starts at zero
        // for gen0 cats, and is initialized to floor(generation/2) for others.
        // Incremented by one for each successful breeding action, regardless
        // of whether this cat is acting as matron or sire.
        uint16 cooldownIndex;

        // The "generation number" of this cat. Cats minted by the CK contract
        // for sale are called "gen0" and have a generation number of 0. The
        // generation number of all other cats is the larger of the two generation
        // numbers of their parents, plus one.
        // (i.e. max(matron.generation, sire.generation) + 1)
        uint16 generation;
    }

    /*** CONSTANTS ***/

    /// @dev A lookup table indicating the cooldown duration after any successful
    ///  breeding action, called "pregnancy time" for matrons and "siring cooldown"
    ///  for sires. Designed such that the cooldown roughly doubles each time a cat
    ///  is bred, encouraging owners not to just keep breeding the same cat over
    ///  and over again. Caps out at one week (a cat can breed an unbounded number
    ///  of times, and the maximum cooldown is always seven days).
    // uint32[14] public cooldowns = [
    //     uint32(1 minutes),
    //     uint32(2 minutes),
    //     uint32(5 minutes),
    //     uint32(10 minutes),
    //     uint32(30 minutes),
    //     uint32(1 hours),
    //     uint32(2 hours),
    //     uint32(4 hours),
    //     uint32(8 hours),
    //     uint32(16 hours),
    //     uint32(1 days),
    //     uint32(2 days),
    //     uint32(4 days),
    //     uint32(7 days)
    // ];
    uint32[14] public cooldowns = [
        uint32(1 seconds),
        uint32(1 seconds),
        uint32(1 seconds),
        uint32(1 seconds),
        uint32(1 seconds),
        uint32(1 seconds),
        uint32(1 seconds),
        uint32(1 seconds),
        uint32(1 seconds),
        uint32(1 seconds),
        uint32(1 seconds),
        uint32(1 seconds),
        uint32(1 seconds),
        uint32(1 seconds)
    ];

    ConcurrentHashMap constant hashmap = ConcurrentHashMap(0x81);
    ConcurrentQueue constant queue = ConcurrentQueue(0x82);
    UUID constant uuidgen = UUID(0xa0);
    System constant system = System(0xa1);

    /*** STORAGE ***/

    /// @dev The address of the ClockAuction contract that handles sales of Kitties. This
    ///  same contract handles both peer-to-peer sales as well as the gen0 sales which are
    ///  initiated every 15 minutes.
    SaleClockAuction public saleAuction;
    uint256 balanceOfSaleAuction = 0;

    /// @dev The address of a custom ClockAution subclassed contract that handles siring
    ///  auctions. Needs to be separate from saleAuction because the actions taken on success
    ///  after a sales and siring auction are quite different.
    SiringClockAuction public siringAuction;
    uint256 balanceOfSiringAuction = 0;

    uint256 totalBalance = 0;

    constructor() public {
        /// @dev A mapping from cat IDs to the serialized Kitty struct.
        hashmap.create("kitties", int32(ConcurrentLib.DataType.UINT256), int32(ConcurrentLib.DataType.BYTES));
        /// @dev A mapping from cat IDs to the address that owns them. All cats have
        ///  some valid owner address, even gen0 cats are created with a non-zero owner.
        hashmap.create("kittyIndexToOwner", int32(ConcurrentLib.DataType.UINT256), int32(ConcurrentLib.DataType.ADDRESS));
        // @dev A mapping from owner address to count of tokens that address owns.
        //  Used internally inside balanceOf() to resolve ownership count.
        hashmap.create("ownershipTokenCount", int32(ConcurrentLib.DataType.ADDRESS), int32(ConcurrentLib.DataType.UINT256));
        /// @dev A mapping from KittyIDs to an address that has been approved to call
        ///  transferFrom(). Each Kitty can only have one approved address for transfer
        ///  at any time. A zero value means no approval is outstanding.
        hashmap.create("kittyIndexToApproved", int32(ConcurrentLib.DataType.UINT256), int32(ConcurrentLib.DataType.ADDRESS));
        /// @dev A mapping from KittyIDs to an address that has been approved to use
        ///  this Kitty for siring via breedWith(). Each Kitty can only have one approved
        ///  address for siring at any time. A zero value means no approval is outstanding.
        hashmap.create("sireAllowedToAddress", int32(ConcurrentLib.DataType.UINT256), int32(ConcurrentLib.DataType.ADDRESS));

        // queue.create("balanceChangesOfSaleAuction", uint256(ConcurrentLib.DataType.UINT256));
        // queue.create("balanceChangesOfSiringAuction", uint256(ConcurrentLib.DataType.UINT256));
        // queue.create("totalBalanceChanges", uint256(ConcurrentLib.DataType.UINT256));
        // system.createDefer("deferBalanceUpdate", "updateBalance(string)");
    }

    /// @dev Sets the reference to the sale auction.
    /// @param _address - Address of sale contract.
    function setSaleAuctionAddress(address _address) public onlyCEO {
        SaleClockAuction candidateContract = SaleClockAuction(_address);

        // NOTE: verify that a contract is what we expect - https://github.com/Lunyr/crowdsale-contracts/blob/cfadd15986c30521d8ba7d5b6f57b4fefcc7ac38/contracts/LunyrToken.sol#L117
        require(candidateContract.isSaleClockAuction());

        // Set the new contract address
        saleAuction = candidateContract;
    }

    /// @dev Sets the reference to the siring auction.
    /// @param _address - Address of siring contract.
    function setSiringAuctionAddress(address _address) public onlyCEO {
        SiringClockAuction candidateContract = SiringClockAuction(_address);

        // NOTE: verify that a contract is what we expect - https://github.com/Lunyr/crowdsale-contracts/blob/cfadd15986c30521d8ba7d5b6f57b4fefcc7ac38/contracts/LunyrToken.sol#L117
        require(candidateContract.isSiringClockAuction());

        // Set the new contract address
        siringAuction = candidateContract;
    }

    /// @dev Assigns ownership of a specific Kitty to an address.
    function _transfer(address _from, address _to, uint256 _tokenId) internal {
        bool balanceUpdated = false;
        if (_to == address(saleAuction) && _to != address(0)) {
            // queue.pushUint256("balanceChangesOfSaleAuction", 1);
            balanceUpdated = true;
        } else if (_to == address(siringAuction) && _to != address(0)) {
            // queue.pushUint256("balanceChangesOfSiringAuction", 1);
            balanceUpdated = true;
        } else {
            uint256 count = hashmap.getUint256("ownershipTokenCount", _to);
            count++;
            hashmap.set("ownershipTokenCount", _to, count);
        }

        // transfer ownership
        hashmap.set("kittyIndexToOwner", _tokenId, _to);

        // When creating new kittens _from is 0x0, but we can't account that address.
        if (_from != address(0)) {
            if (_from == address(saleAuction)) {
                // queue.pushUint256("balanceChangesOfSaleAuction", 0);
                balanceUpdated = true;
            } else if (_from == address(siringAuction)) {
                // queue.pushUint256("balanceChangesOfSiringAuction", 0);
                balanceUpdated = true;
            } else {
                uint256 count = hashmap.getUint256("ownershipTokenCount", _from);
                count--;
                hashmap.set("ownershipTokenCount", _from, count);
            }

            // once the kitten is transferred also clear sire allowances
            hashmap.deleteKey("sireAllowedToAddress", _tokenId);
            // clear any previously approved ownership exchange
            hashmap.deleteKey("kittyIndexToApproved", _tokenId);
        }
        // Emit the transfer event.
        emit Transfer(_from, _to, _tokenId);

        if (balanceUpdated && !(_from == address(0) && _to == address(0))) {
            // system.callDefer("deferBalanceUpdate");
        }
    }

    /// @dev An internal method that creates a new kitty and stores it. This
    ///  method doesn't do any checking and should only be called when the
    ///  input data is known to be valid. Will generate both a Birth event
    ///  and a Transfer event.
    /// @param _matronId The kitty ID of the matron of this cat (zero for gen0)
    /// @param _sireId The kitty ID of the sire of this cat (zero for gen0)
    /// @param _generation The generation number of this cat, must be computed by caller.
    /// @param _genes The kitty's genetic code.
    /// @param _owner The inital owner of this cat, must be non-zero (except for the unKitty, ID 0)
    function _createKitty(
        uint256 _matronId,
        uint256 _sireId,
        uint256 _generation,
        uint256 _genes,
        address _owner
    )
        internal
        returns (uint)
    {
        // These requires are not strictly necessary, our calling code should make
        // sure that these conditions are never broken. However! _createKitty() is already
        // an expensive call (for storage), and it doesn't hurt to be especially careful
        // to ensure our data structures are always valid.
        // TODO
        // require(_matronId <= 4294967295);
        // require(_sireId <= 4294967295);
        // require(_generation <= 65535);

        Kitty memory _kitty = Kitty({
            genes: _genes,
            matronId: _matronId,
            sireId: _sireId,
            siringWithId: 0,
            birthTime: uint64(now),
            cooldownEndTime: 0,
            cooldownIndex: 0,
            generation: uint16(_generation)
        });
        bytes memory kittyBytes = _kittyToBytes(_kitty);
        uint256 newKittenId = uuidgen.gen("kittyId");
        hashmap.set("kitties", newKittenId, kittyBytes);

        // It's probably never going to happen, 4 billion cats is A LOT, but
        // let's just be 100% sure we never let this happen.
        // TODO
        // require(newKittenId <= 4294967295);
        if (_owner != address(0)) {
            // queue.pushUint256("totalBalanceChanges", 1);
        }
        if (_owner != address(saleAuction) && _owner != address(siringAuction) && _owner != address(this)) {
            // system.callDefer("deferBalanceUpdate");
        }

        // emit the birth event
        emit Birth(
            _owner,
            newKittenId,
            _kitty.matronId,
            _kitty.sireId,
            _kitty.genes
        );

        // This will assign ownership, and also emit the Transfer event as
        // per ERC721 draft
        _transfer(address(0), _owner, newKittenId);

        return newKittenId;
    }

    // function updateBalance(string memory) public {
    //     // uint256 length = queue.size("balanceChangesOfSaleAuction");
    //     for (uint256 i = 0; i < length; i++) {
    //         // uint256 changes = queue.popUint256("balanceChangesOfSaleAuction");
    //         if (changes == 1) {
    //             balanceOfSaleAuction++;
    //         } else {
    //             balanceOfSaleAuction--;
    //         }
    //     }
    //     emit BalanceOf(address(saleAuction), balanceOfSaleAuction);

    //     // length = queue.size("balanceChangesOfSiringAuction");
    //     for (uint256 i = 0; i < length; i++) {
    //         // uint256 changes = queue.popUint256("balanceOfChangesOfSiringAuction");
    //         if (changes == 1) {
    //             balanceOfSiringAuction++;
    //         } else {
    //             balanceOfSiringAuction--;
    //         }
    //     }
    //     emit BalanceOf(address(siringAuction), balanceOfSiringAuction);

    //     // length = queue.size("totalBalanceChanges");
    //     for (uint256 i = 0; i < length; i++) {
    //         // queue.popUint256("totalBalanceChanges");
    //         totalBalance++;
    //     }
    //     emit BalanceOf(address(0), totalBalance);
    // }
    
    function _kittyToBytes(Kitty memory _kitty) internal pure returns (bytes memory) {
        uint offset = 192;
        bytes memory buffer = new bytes(offset);
        uintToBytes(offset, _kitty.genes, buffer);
        offset -= sizeOfUint(256);
        uintToBytes(offset, _kitty.matronId, buffer);
        offset -= sizeOfUint(256);
        uintToBytes(offset, _kitty.sireId, buffer);
        offset -= sizeOfUint(256);
        uintToBytes(offset, _kitty.siringWithId, buffer);
        offset -= sizeOfUint(256);
        uintToBytes(offset, _kitty.birthTime, buffer);
        offset -= sizeOfUint(64);
        uintToBytes(offset, _kitty.cooldownEndTime, buffer);
        offset -= sizeOfUint(64);
        uintToBytes(offset, _kitty.cooldownIndex, buffer);
        offset -= sizeOfUint(16);
        uintToBytes(offset, _kitty.generation, buffer);
        return buffer;
    }

    function _bytesToKitty(bytes memory data) internal pure returns (Kitty memory) {
        uint offset = 192;
        Kitty memory kitty;
        kitty.genes = bytesToUint256(offset, data);
        offset -= sizeOfUint(256);
        kitty.matronId = bytesToUint256(offset, data);
        offset -= sizeOfUint(256);
        kitty.sireId = bytesToUint256(offset, data);
        offset -= sizeOfUint(256);
        kitty.siringWithId = bytesToUint256(offset, data);
        offset -= sizeOfUint(256);
        kitty.birthTime = bytesToUint64(offset, data);
        offset -= sizeOfUint(64);
        kitty.cooldownEndTime = bytesToUint64(offset, data);
        offset -= sizeOfUint(64);
        kitty.cooldownIndex = bytesToUint16(offset, data);
        offset -= sizeOfUint(16);
        kitty.generation = bytesToUint16(offset, data);
        return kitty;
    }
}