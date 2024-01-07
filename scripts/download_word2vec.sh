#!/bin/bash

# Download word2vec file
curl -f -o "$HOME/word2vec/GoogleNews-vectors-negative300.bin.gz" <NEW_URL>

# Check if download was unsuccessful
if [ $? -ne 0 ]; then then
    echo "Download failed"
    exit 1
fi
