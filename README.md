## Introduction
The ParallelKitties is a restructured, fully parallel and demonstrative blockchain game based on the source code of CryptoKitties. 
The purpose of this project is to show how a well-known crypto game can be benefited from Arcology’s revolutionary parallel processing capability. Comparing with the original CryptoKitties, the ParallelKitties version has following features:

*	Functionally compatible with CryptoKitties
*	ParallelKitties used Arcology’s concurrency framework
*	ParallelKitties work on Arcology only
*	Calls to the ParallelKitties can be executed in parallel without causing conflicts
*	Results are guaranteed to be deterministic

## EVM Compatibility
Arcology is compatible with EVM, all Ethereum smart contracts running on Ethereum can work on Arcology without modification.  
The original Solidity and EVM lack concurrency support, the ParallelKitties used some concurrency features which are only available on Arcology. Smart contracts developed for Arcology also work on Ethereum as long as no  concurrency features are used.

## Major Differences 
The original EVM doesn’t have any built-in mechanism to prevent and recovery state inconsistency. Neither Solidity nor EVM is designed for concurrent use, running original version CryptoKitties directly in the multiple parallel EVM instances will inevitably cause serious problems.

To fully utilize Arcology’s concurrency control framework, we made some necessary modifications to the original CK Core code. The majority of changes were related to data structures. Basically, we replaced all the data containers in original CK code with Archology concurrent containers to allow concurrent modifications of elements they hold. We made no changes to the program architecture, internal logics or calling sequence of original CK code. 


## Background
Parallelism is the solution to scalability issue. Proposed solutions like sharding, sidechain can all be classified as some sort of parallelism. The challenge is there must be a mechanism to maintain consistency, while allowing multiple program instances to access some shared resources concurrently. 

In centralized systems,  a typical solution to this problem is by employing some synchronization mechanisms like mutex.  
Conventional synchronization mechanisms are only thread-safe but not deterministic. The order to which the resources are accessed isn’t taken into account at all. Different access order will lead to different execution results in many cases, which isn’t a problem for centralized systems. 

For blockchains, the same set of transactions must be processed by different nodes repeatedly. The end states after the executions must be identical across multiple nodes to reach a consensus. This is a key feature for blockchain platforms. 
Arcology has a concurrency framework that is both “thread-safe” and deterministic. 

## Concurrent Containers
Concurrent containers are a key part of concurrency framework that are widely used in ParallelKitties to enable parallelism. The internal state within consistency always guaranteed.  For those who know other mainstream programming languages may find this concept familiar. Java has a collection of concurrent containers available under java.util.concurrent. Those concurrent containers are designed to be thread safe. 

Concurrent containers in Arcology share some similarities with others but Arcology offers more. Arcology’s concurrent containers are both thread-safe and deterministic.   All the data elements in the concurrent containers are under protection of Archology, access may cause unexpected consequences will be detected and prevented.

For detailed information on concurrent containers and the whole Arcology concurrency framework, please check out the link www.arcology.network/technical/developers-guide/
