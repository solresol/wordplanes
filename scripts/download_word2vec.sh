#!/bin/bash

# Download word2vec file
curl -f -o "$HOME/word2vec/GoogleNews-vectors-negative300.bin.gz" https://example.com/word2vec.bin.gz

# Check if download was unsuccessful
if [ ! -f "$HOME/word2vec/GoogleNews-vectors-negative300.bin.gz" ]; then
    echo "Download failed: File not found"
    exit 1
fi
    echo "Download failed: URL is invalid or the file does not exist"
    exit 1
fi
