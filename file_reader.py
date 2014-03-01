__author__ = 'keelan'

import os
import re
from nltk.corpus import BracketParseCorpusReader

def tree_reader():
    d = {}
    trees = BracketParseCorpusReader("parsed_sentences/", ".*")
    for name in tree_reader.fileids():
        d_name = re.sub(r"\.tree", "", name)
        d[d_name] = list(trees.parsed_sents(name))

    return d

TREES_DICTIONARY = tree_reader()