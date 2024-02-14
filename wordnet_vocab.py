import nltk


def yield_word_senses(pos=None):
    """Yields WordNet synsets, optionally filtered by part of speech.

    :param pos: Part of speech to filter synsets (e.g., 'n' for nouns, 'v' for verbs, 'a' for adjectives).
              If None, all synsets are yielded. Defaults to None.
    """
    if pos is None:
        synsets = nltk.corpus.wordnet.all_synsets()
    else:
        synsets = nltk.corpus.wordnet.all_synsets(pos=pos)
    for synset in synsets:
        yield synset.name()


class GloveLookup:
    def __init__(self, db_filename, table_name, dimension):
        self.conn = sqlite3.connect(db_filename)
        self.cursor = self.conn.cursor()
        self.cache = {}
        self.table_name = table_name
        self.dimension = dimension

    def lookup_synset(self, synset_name):
        term = synset_name.split('.')[0]
        if term in self.cache:
            return self.cache[term]
        self.cursor.execute(f"SELECT * FROM {self.table_name} WHERE term = ?", (term,))
        row = self.cursor.fetchone()
        if row:
            vector = np.array(row[1:1+self.dimension])
            self.cache[term] = vector
            return vector
        raise KeyError(f"Term '{term}' not found in the database.")

    def dump_as_glove(self, synset_name):
        vector = self.lookup_synset(synset_name)
        if vector is not None:
            return f"{synset_name.split('.')[0]} " + ' '.join(map(str, vector))
        raise KeyError(f"Synset '{synset_name}' not found in the database.")

import sqlite3
import numpy as np
