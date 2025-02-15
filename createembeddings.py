import sqlite3
import numpy as np
import openai
import requests
import json
import os
import argparse
from typing import List, Dict, Tuple, Optional
import time
from tqdm import tqdm

class EmbeddingGenerator:
    def __init__(self, db_path: str, ollama_host: str, stop_after: Optional[int] = None):
        self.db_path = db_path
        self.ollama_host = ollama_host
        self.stop_after = stop_after
        self.setup_database()
        
    def setup_database(self):
        """Set up the database tables for embeddings."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        # Create tables for each embedding source
        for source in ['openai', 'ollama']:
            c.execute(f'''
                CREATE TABLE IF NOT EXISTS {source}_embeddings (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    adjective TEXT NOT NULL,
                    gender TEXT NOT NULL,
                    embedding TEXT NOT NULL,
                    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
                    UNIQUE(adjective, gender)
                )
            ''')
        
        conn.commit()
        conn.close()

    def get_adjectives(self) -> List[str]:
        """Get all adjectives from the original analysis table."""
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute('SELECT adjective FROM adjective_analysis where he_is_personality or she_is_personality')
        adjectives = [row[0] for row in c.fetchall()]
        conn.close()
        return adjectives

    def create_sentence(self, adjective: str, gender: str) -> str:
        """Create the sentence for embedding."""
        pronoun = "He" if gender.lower() == "male" else "She"
        return f"{pronoun} is {adjective}"

    def get_openai_embedding(self, text: str) -> np.ndarray:
        """Get embedding from OpenAI API."""
        response = openai.embeddings.create(
                model="text-embedding-3-small",
                input=text
        )
        embedding = response.data[0].embedding
        return json.dumps(embedding)


    def get_ollama_embedding(self, text: str) -> np.ndarray:
        """Get embedding from Ollama API."""
        response = requests.post(
            f'http://{self.ollama_host}:11434/api/embeddings',
            json={
            "model": "nomic-embed-text",
                "prompt": text
            }
        )
        embedding = response.json()['embedding']
        return json.dumps(embedding)

    def store_embedding(self, source: str, adjective: str, gender: str, embedding: np.ndarray):
        """Store the embedding in the appropriate database table."""
        if embedding is None:
            return
            
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        
        c.execute(f'''
                INSERT OR REPLACE INTO {source}_embeddings (adjective, gender, embedding)
                VALUES (?, ?, ?)
        ''', (adjective, gender, embedding))
        conn.commit()

    def embedding_already_exists(self, source: str, adjective: str, gender: str):
        conn = sqlite3.connect(self.db_path)
        c = conn.cursor()
        c.execute(f"select count(*) from {source}_embeddings where adjective = ? and gender = ?", [adjective, gender])
        row = c.fetchone()
        if row[0] == 0:
            return False
        return True

    def process_all(self):
        """Process all adjectives and generate embeddings from all sources."""
        adjectives = self.get_adjectives()
        genders = ['male', 'female']
        processed_count = 0

        iterator = tqdm(adjectives, desc="Processing adjectives")
        for adjective in iterator:
            for gender in genders:
                sentence = self.create_sentence(adjective, gender)
                iterator.set_description(sentence)
                if self.embedding_already_exists('openai', adjective, gender):
                    pass
                else:
                    openai_embedding = self.get_openai_embedding(sentence)
                    self.store_embedding('openai', adjective, gender, openai_embedding)
                    # Rate limiting
                    processed_count += 1
                    time.sleep(0.1)
                    
                if self.embedding_already_exists('ollama', adjective, gender):
                    pass
                else:
                    ollama_embedding = self.get_ollama_embedding(sentence)
                    self.store_embedding('ollama', adjective, gender, ollama_embedding)
                    processed_count += 1
                    # No need to rate limit our own machines. We can't DoS ourselves: we are the service.
                if self.stop_after and processed_count >= self.stop_after:
                    return

def read_api_key(filepath: str) -> str:
    """Read API key from file."""
    with open(filepath, 'r') as f:
        return f.read().strip()

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--stop-after", type=int, help="Only process this many adjectives")
    parser.add_argument("--openai-api-key-file", default=os.path.expanduser("~/.openai.key"))
    parser.add_argument("--ollama-host", default="localhost")
    parser.add_argument("--database", default="personality_adjectives.sqlite")
    args = parser.parse_args()

    openai.api_key = read_api_key(args.openai_api_key_file)

    # Create and run the embedding generator
    embedder = EmbeddingGenerator(
        db_path=args.database,
        ollama_host=args.ollama_host,
        stop_after=args.stop_after
    )
    embedder.process_all()
    
if __name__ == "__main__":
    main()
