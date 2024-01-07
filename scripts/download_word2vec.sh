#!/bin/bash

# Download word2vec file
curl -f -o "$HOME/word2vec/GoogleNews-vectors-negative300.bin.gz" VALID_URL

# Check if download was unsuccessful
if [ $? -ne 0 ]; then
    echo "Download failed: URL is invalid or the file does not exist"
    exit 1
fi
