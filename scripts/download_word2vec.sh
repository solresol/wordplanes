#!/bin/bash

# Download word2vec file
curl -f -o "$HOME/word2vec/GoogleNews-vectors-negative300.bin.gz" https://updated-url/word2vec

# Check if download was unsuccessful

    if [ $? -ne 0 ]; then
    echo "Download failed"
    exit 1
fi
fi
