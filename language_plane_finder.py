#!/usr/bin/env python3

import argparse
import random
import sqlite3
import json
import os

import numpy as np
import pandas as pd
import matplotlib.pyplot
import tqdm
from plane import Plane

parser = argparse.ArgumentParser()
parser.add_argument("--database", default='personality_adjectives.sqlite')
parser.add_argument("--embedding-provider", default='openai')
parser.add_argument("--gender", default='male')
parser.add_argument("--random-seed", type=int)
parser.add_argument("--stop-after", type=int)
parser.add_argument("--output-directory")
parser.add_argument("--progress-bar", action="store_true")
parser.add_argument("--fitter", action="store_true")
args = parser.parse_args()

conn = sqlite3.connect(args.database)
cursor = conn.cursor()
table = f"{args.embedding_provider}_embeddings"
cursor.execute(f"select adjective, embedding from {table} where gender = ?", [args.gender])
adjective_lookup = {}
for adjective, embedding_as_json in cursor:
    embedding_as_list = json.loads(embedding_as_json)
    embedding_as_numpy_array = np.array(embedding_as_list)
    adjective_lookup[adjective] = embedding_as_numpy_array

cursor.execute("""create table if not exists planar_statistics (
  adjective1 text,
  adjective2 text,
  adjective3 text,
  gender text,
  embedding_provider text,
  closest_adjective text,
  how_close float,
  mean_distance float,
  stddev_distance float,
  mili float,
  percentile1 float,
  percentile25 float,
  percentile50 float,
  percentile75 float,
  percentile99 float,
  furthest float,
  primary key (adjective1, adjective2, adjective3, gender, embedding_provider)
)""")


  

vocab = list(adjective_lookup.keys())

if args.random_seed:
    random.seed(args.random_seed)

triples_processed = 0

while True:
    if args.stop_after and triples_processed >= args.stop_after:
        break
    word1, word2, word3 = sorted(random.sample(vocab, 3))
    print(f"{word1}, {word2}, {word3}")
    cursor.execute("""select count(*) from planar_statistics where
      adjective1 = ? and adjective2 = ? and adjective3 = ?
      and gender = ? and embedding_provider = ?""",
                   [word1, word2, word3, args.gender, args.embedding_provider])
    row = cursor.fetchone()
    if row[0] > 0:
        print(" -- already in the database")
        continue
    point1 = adjective_lookup[word1]
    point2 = adjective_lookup[word2]
    point3 = adjective_lookup[word3]
    try:
        plane = Plane(point1, point2, point3)
    except ValueError:
        print(f"Error: Cannot form a valid plane with points {word1}, {word2}, and {word3}")
        continue
    triples_processed += 1
    distances = []
    distance_vocab = []
    if args.progress_bar:
        iterator = tqdm.tqdm(vocab)
    else:
        iterator = vocab
    for word in iterator:
        if word in {word1, word2, word3}:
            continue
        point = adjective_lookup[word]
        distance, _ = plane.distance_to_plane(point)
        distances.append(distance)
        distance_vocab.append(word)
    distances = pd.Series(index=distance_vocab, data=distances)
    print(word1, word2, word3)
    print(f"{distances.idxmin()=}, {distances.min()=}")
    print(f"{distances.mean()=}, {distances.std()=}")
    stats = np.percentile(distances, [0.1, 1, 25, 50, 75, 99])
    print(f"{stats}")
    cursor.execute("""insert into planar_statistics (
       adjective1, adjective2, adjective3, gender, embedding_provider,
       closest_adjective, how_close, mean_distance, stddev_distance,
       mili, percentile1, percentile25, percentile50, percentile75,
       percentile99, furthest) values (?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)""",
                   [word1, word2, word3, args.gender, args.embedding_provider,
                    distances.idxmin(), distance.min(), distances.mean(), distances.std(),
                    stats[0], stats[1], stats[2], stats[3], stats[4], stats[5],
                    distances.max()])
    conn.commit()
    if args.output_directory:
        fname = os.path.join(args.output_directory, f"{word1},{word2},{word3}.png")
        fig, ax = matplotlib.pyplot.subplots()
        distances.plot.hist(ax=ax)
        ax.set_title(f"Distribution of distances from the plane through\n{word1}, {word2} and {word3}")
        ax.set_xlabel("Distance from the plane")
        fig.savefig(fname)
    if args.fitter:
        import fitter
        f = fitter.Fitter(distances)
        f.fit()
        print(f.summary())
        if args.output_directory:
            fname = os.path.join(args.output_directory, f"{word1},{word2},{word3}.fitter.json")
            with open(fname, 'w') as o:
                o.write(f.summary().to_json())
            
