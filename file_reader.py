__author__ = 'keelan'

import os
import re
from nltk.corpus import BracketParseCorpusReader

def tree_reader():
    d = {}
    trees = BracketParseCorpusReader("parsed_sentences/", ".*")
    for name in trees.fileids():
        d_name = re.sub(r"\.tree", "", name)
        d[d_name] = list(trees.parsed_sents(name))

    return d

TREES_DICTIONARY = tree_reader()

if __name__ == "__main__":
    print TREES_DICTIONARY["NYT20001230.1309.0093.head.coref.raw"]