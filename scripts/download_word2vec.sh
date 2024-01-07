#!/bin/bash

# Download word2vec file
curl -f -o "$HOME/word2vec/NEW_FILE_NAME" NEW_URL

# Check if download was unsuccessful
if [ $? -ne 0 ]; then
    echo "Download failed"
    exit 1
fi
