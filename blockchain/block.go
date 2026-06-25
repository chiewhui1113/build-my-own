package main

import (
	"bytes"
	"crypto/sha256"
	"strconv"
	"time"
)

// Single block in the chain
type Block struct {
	Timestamp     int64  // when the block was created
	Data          []byte // the valuable info stored in the block
	PrevBlockHash []byte // hash of the previous block (links the chain)
	Hash          []byte // hash of this block
}

// Computes the block's hash from its fields
// hash = sha256(prevHash + data + timestamp)
func (b *Block) SetHash() {
	timestamp := []byte(strconv.FormatInt(b.Timestamp, 10))
	headers := bytes.Join([][]byte{b.PrevBlockHash, b.Data, timestamp}, []byte{})
	hash := sha256.Sum256(headers)

	b.Hash = hash[:]
}

// Builds a new block and sets its hash
func NewBlock(data string, prevBlockHash []byte) *Block {
	block := &Block{time.Now().Unix(), []byte(data), prevBlockHash, []byte{}}
	block.SetHash()
	return block
}

// Returns the first block in the chain
func NewGenesisBlock() *Block {
	return NewBlock("Genesis Block", []byte{})
}
