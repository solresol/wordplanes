#!/bin/bash

# Download word2vec file
curl -f -o "$HOME/word2vec/GoogleNews-vectors-negative300.bin.gz" https://example.com/GoogleNews-vectors-negative300.bin.gz

# Check if download was unsuccessful
if [ $? -ne 0 ] || [ ! -f "$HOME/word2vec/GoogleNews-vectors-negative300.bin.gz" ]; then
    echo "Download failed: URL is invalid or the file does not exist or the download was unsuccessful"
    exit 1
fi
