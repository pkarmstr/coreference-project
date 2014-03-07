__author__ = 'keelan'

import os
import re
from collections import namedtuple
from nltk.corpus import BracketParseCorpusReader
from build_raw_sentences import pos_split


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
                line = line.rstrip()
                if line != "":
                    pairs = [pos_split(p) for p in line.split()]
                    sentences.append(pairs)
            d[name] = sentences
    return d

def raw_reader():
    d = {}
    for f in os.listdir("raw_sentences/"):
        with open(os.path.join("raw_sentences", f), "r") as f_in:
            sentences = []
            for line in f_in:
                line = line.rstrip()
                if line != "":
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

def noncontent_reader():
    ls = []
    with open("resources/noncontentwords.txt", "r") as f_in:
        for line in f_in:
            ls.append(line.rstrip())
    return set(ls)

FeatureRow = namedtuple("FeatureRow", ["article", "sentence", "offset_begin",
                                        "offset_end", "entity_type", "token",
                                        "sentence_ref", "offset_begin_ref",
                                        "offset_end_ref", "entity_type_ref",
                                        "token_ref", "i_cleaned", "j_cleaned",
                                        "is_referent"])

###########################
# `final` data structures #
###########################

RAW_DICTIONARY = raw_reader()
POS_DICTIONARY = pos_reader()
TREES_DICTIONARY = tree_reader()
PRONOUN_LIST = pronoun_reader()
NONCONTENT_SET = noncontent_reader()