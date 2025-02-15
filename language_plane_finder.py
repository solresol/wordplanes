import argparse
import random
import sqlite3
import json

import numpy as np
from plane import Plane

parser = argparse.ArgumentParser()
parser.add_argument("--database", default='personality_adjectives.sqlite')
parser.add_argument("--table", default='openai_embeddings')
parser.add_argument("--gender", default='male')
parser.add_argument("--random-seed", type=int, default=0)
parser.add_argument("--stop-after", type=int)
args = parser.parse_args()

conn = sqlite3.connect(args.database)
cursor = conn.cursor()
cursor.execute(f"select adjective, embedding from {args.table} where gender = ?", [args.gender])
adjective_lookup = {}
for adjective, embedding_as_json in cursor:
    embedding_as_list = json.loads(embedding_as_json)
    embedding_as_numpy_array = np.array(embedding_as_list)
    adjective_lookup[adjective] = embedding_as_numpy_array

vocab = list(adjective_lookup.keys())

random.seed(args.random_seed)

triples_processed = 0

while True:
    word1, word2, word3 = sorted(random.sample(vocab, 3))
    #print(f"{word1}, {word2}, {word3}")
    triples_processed += 1
    if args.stop_after and triples_processed > args.stop_after:
        break
    point1 = adjective_lookup[word1]
    point2 = adjective_lookup[word2]
    point3 = adjective_lookup[word3]
    print(point1, point2, point3)
    plane = Plane(point1, point2, point3)
    if not plane.is_valid():
        print(f"Error: Cannot form a valid plane with points {word1}, {word2}, and {word3}")
        continue
    distances = []
    for word in vocab:
        if word in {word1, word2, word3}:
            continue
        point = adjective_lookup[word]
        distance = plane.distance_to_plane(point)
        distances.append(distance)
    distances = np.array(distances)
    stats = np.percentile(distances, [0.1, 1, 25, 50, 75, 99, 99.9, 100]), distances.mean(), distances.std()
    print(word1, word2, word3, stats)
