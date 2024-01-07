#!/bin/bash

# Download word2vec file
curl -f -o "$HOME/word2vec/word2vec.bin.gz" https://example.com/word2vec.bin.gz

# Check if download was unsuccessful
if [ $? -ne 0 ]; then
    echo "Download failed. Word2Vec download was unsuccessful."
fi
    echo "Download failed"
    exit 1
fi
