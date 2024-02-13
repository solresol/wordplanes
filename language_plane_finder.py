import argparse
import random
import sqlite3

import numpy as np
from plane import Plane
from wordnet_vocab import GloveLookup, yield_word_senses

parser = argparse.ArgumentParser()
parser.add_argument("--sqlite-database")
parser.add_argument("--table")
parser.add_argument("--dimensionality", type=int)
parser.add_argument("--subsample", type=int, default=None)
parser.add_argument("--random-seed", type=int, default=None)
parser.add_argument("--part-of-speech", default=None)
args = parser.parse_args()

glove_lookup = GloveLookup(args.sqlite_database, args.table, args.dimensionality)

vocab = list(yield_word_senses(args.part_of_speech))
if args.subsample is not None:
    random.seed(args.random_seed)
    vocab = random.sample(vocab, args.subsample)

for i, word1 in enumerate(vocab):
    for j, word2 in enumerate(vocab[i+1:]):
        for word3 in vocab[i+j+2:]:
            point1 = glove_lookup.lookup_synset(word1)
            point2 = glove_lookup.lookup_synset(word2)
            point3 = glove_lookup.lookup_synset(word3)
            plane = Plane(point1, point2, point3)
            distances = []
            for word in vocab:
                if word not in {word1, word2, word3}:
                    point = glove_lookup.lookup_synset(word)
                    distance, _ = plane.distance_to_plane(point)
                    distances.append(distance)
            distances = np.array(distances)
            stats = np.percentile(distances, [0.1, 1, 25, 50, 75, 99, 99.9, 100]), distances.mean(), distances.std()
            print(word1, word2, word3, stats)
