# ParallelKitties

## Introduction
The ParallelKitties is a restructured, fully parallel and demonstrative blockchain game based on the source code of CryptoKitties. 
The purpose of this project is to show how a well-known crypto game can be benefited from Arcology’s revolutionary parallel processing 
capability. Comparing with the original CryptoKitties, the ParallelKitties version has following features:
*	Functionally compatible with CryptoKitties
*	ParallelKitties used Arcology’s concurrency framework
*	ParallelKitties work on Arcology only
*	Calls to the ParallelKitties can be executed in parallel without causing conflicts
*	Results are guaranteed to be deterministic

## EVM Compatibility
Arcology is compatible with EVM, all Ethereum smart contracts running on Ethereum can work on Arcology without modification.  
The original Solidity and EVM lack concurrency support, the ParallelKitties used some concurrency features which are only 
available on Arcology. Smart contracts developed for Arcology also work on Ethereum as long as no  concurrency features are used.

## Major Differences 
The original EVM doesn’t have any built-in mechanism to prevent and recovery state inconsistency for Solidity developers to use. 
Neither Solidity nor EVM is designed for concurrent use, running original version CryptoKitties directly in the multiple parallel
EVM instances will inevitably cause serious problems.

To fully utilize Arcology’s concurrency control framework, we made some necessary modifications to the original CK Core code. 
The majority of changes were related to data structures. Basically, we replaced all the data containers used in original CK code 
with Archology concurrent containers to allow concurrent modifications of elements they hold. We made no changes to the program 
architecture, internal logics or calling sequence of original CK code. 

## Concurrent Containers
Concurrent containers are special data containers with state consistency always guaranteed.  The concurrent containers behave 
pretty much like data containers available in many mainstream programming languages. 

The only difference is that all the data elements in the concurrent containers are under protection of Archology, access may 
cause unexpected consequences will be detected and prevented.
