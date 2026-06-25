package main

// Ordered list of blocks
type Blockchain struct {
	blocks []*Block
}

// Creates a new block with the given data and appends it to the chain
func (bc *Blockchain) AddBlock(data string) {
	prevBlock := bc.blocks[len(bc.blocks)-1]
	newBlock := NewBlock(data, prevBlock.Hash)
	bc.blocks = append(bc.blocks, newBlock)
}

// Creates a blockchain that starts with the genesis block
func NewBlockchain() *Blockchain {
	return &Blockchain{[]*Block{NewGenesisBlock()}}
}
