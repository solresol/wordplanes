import nltk


def yield_word_senses():
    for synset in nltk.corpus.wordnet.all_synsets():
        yield synset.name()
