__author__ = 'keelan'

import os
import re
from nltk.corpus import BracketParseCorpusReader
from build_raw_sentences import spesh_split

def tree_reader():
    d = {}
    trees = BracketParseCorpusReader("parsed_sentences/", ".*")
    for name in trees.fileids():
        d_name = re.sub(r"\.tree", "", name)
        d[d_name] = list(trees.parsed_sents(name))

    return d

def pos_reader():
    d = {}
    for f in os.listdir("pos_sentences/"):
        name = re.sub(r"\.pos", "", f)
        with open(os.path.join("pos_sentences", f), "r") as f_in:
            sentences = []
            for line in f_in:
                pairs = [spesh_split(p) for p in line.rstrip().split()]
                sentences.append(pairs)
            d[name] = sentences
    return d

def raw_reader():
    d = {}
    for f in os.listdir("raw_sentences/"):
        with open(os.path.join("raw_sentences", f), "r") as f_in:
            sentences = []
            for line in f_in:
                tokens = line.split()[1:-1] #dont want <s> tags
                sentences.append(tokens)
            d[f] = sentences
    return d

def pronoun_reader():
    ls = []
    with open("resources/pronouns.txt", "r") as f_in:
        for line in f_in:
            ls.append(line.rstrip())
    return ls

###########################
# `final` data structures #
###########################

RAW_DICTIONARY = raw_reader()
POS_DICTIONARY = pos_reader()
TREES_DICTIONARY = tree_reader()
PRONOUN_LIST = pronoun_reader()

if __name__ == "__main__":
    print TREES_DICTIONARY["NYT20001230.1309.0093.head.coref.raw"]
    print POS_DICTIONARY["NYT20001230.1309.0093.head.coref.raw"]
    print RAW_DICTIONARY["NYT20001230.1309.0093.head.coref.raw"]