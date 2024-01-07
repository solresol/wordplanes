#!/bin/bash

# Download word2vec file
curl -f -o "$HOME/word2vec/word2vec.bin.gz" https://example.com/new-word2vec-file.bin.gz

# Check if download was unsuccessful
if [ $? -ne 0 ]; then
    echo "Download failed: Word2vec file download unsuccessful"
    echo "Word2vec file download successful"
fi
fi
