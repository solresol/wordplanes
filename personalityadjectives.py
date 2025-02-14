#!/usr/bin/env python3

import nltk
from nltk.corpus import wordnet as wn
import sqlite3
import anthropic
import json
import time
import os
from typing import List, Dict
import argparse

def setup_database(dbpath) -> sqlite3.Connection:
    """Create the SQLite database and necessary tables."""
    conn = sqlite3.connect(dbpath)
    c = conn.cursor()
    
    c.execute('''
        CREATE TABLE IF NOT EXISTS adjective_analysis (
            adjective TEXT PRIMARY KEY,
            he_is_personality BOOLEAN,
            she_is_personality BOOLEAN,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    
    conn.commit()
    return conn

def get_all_adjectives() -> List[str]:
    """Extract all adjectives from WordNet."""
    # Download required NLTK data if not already present
    #nltk.download('wordnet')
    
    adjectives = set()
    for synset in list(wn.all_synsets(pos=wn.ADJ)):
        # Get the main lemma name
        adjectives.add(synset.name().split('.')[0])
        
        # Get all lemma names
        for lemma in synset.lemmas():
            adjectives.add(lemma.name())
    
    return list(adjectives)

def create_tool_schema():
    """Create the tool choice schema for Claude."""
    return {
        "type": "function",
        "function": {
            "name": "classify_personality_adjective",
            "description": "Determine if an adjective describes personality",
            "input_schema": {
                "type": "object",
                "properties": {
                    "is_personality": {
                        "type": "boolean",
                        "description": "Whether this adjective can describe personality or character"
                    }
                },
                "required": ["is_personality"]
            }
        }
    }


def query_claude(client: anthropic.Client, adjective: str) -> Dict[bool, bool]:
    """Query Claude Haiku about whether an adjective can describe personality."""
    tool_schema = create_tool_schema()
    messages = [
        {
            "role": "user",
            "content": f"Could the sentence 'He is {adjective}' be a statement about a person's personality or character?"
        },
        {
            "role": "user",
            "content": f"Could the sentence 'She is {adjective}' be a statement about a person's personality or character?"
        }
    ]
    
    results = {}
    
    for is_he, prompt in enumerate(messages):
        print(prompt)
        response = client.messages.create(
            model="claude-3-5-haiku-20241022",
            max_tokens=100,
            temperature=0,
            messages=[prompt],
            tools=[tool_schema['function']],
            tool_choice = {'name': 'classify_personality_adjective', 'type': 'tool', 'disable_parallel_tool_use': True }
            
        )
        
        # Extract and parse the JSON response
        print(response.content[0].input)
        tool_call = response.content[0].input
        results[bool(is_he == 0)] = tool_call["is_personality"]
        if tool_call['is_personality']:
            print(f"The sentence '{prompt['content']}' could be a personality sentence")
        
        # Rate limiting - be nice to the API
        time.sleep(0.5)
            
    return results

def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--stop-after", type=int, help="Only process this many adjectives")
    parser.add_argument("--anthropic-api-key-file", default=os.path.expanduser("~/.anthropic.key"))
    parser.add_argument("--database", default="personality_adjectives.sqlite")
    args = parser.parse_args()
    
    # Initialize the database
    conn = setup_database(args.database)
    cursor = conn.cursor()
    
    # Initialize the Anthropic client
    api_key = open(args.anthropic_api_key_file).read().strip()
    client = anthropic.Client(api_key=api_key)
    
    # Get all adjectives
    adjectives = get_all_adjectives()
    print(f"Found {len(adjectives)} adjectives to analyze")

    processed = 0
    # Process each adjective
    for i, adjective in enumerate(adjectives):
        # Check if we've already processed this adjective
        cursor.execute('SELECT * FROM adjective_analysis WHERE adjective = ?', (adjective,))
        if cursor.fetchone():
            continue
            
        print(f"Processing {i+1}/{len(adjectives)}: {adjective}")
        
        # Query Claude
        results = query_claude(client, adjective)
        
        # Store results
        cursor.execute('''
            INSERT INTO adjective_analysis (adjective, he_is_personality, she_is_personality)
            VALUES (?, ?, ?)
        ''', (adjective, results.get(True), results.get(False)))
        
        # Commit every 10 adjectives
        if i % 10 == 0:
            conn.commit()

        processed += 1
        if args.stop_after and processed >= args.stop_after:
            break
            
    # Final commit
    conn.commit()
    conn.close()

if __name__ == "__main__":
    main()
