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
