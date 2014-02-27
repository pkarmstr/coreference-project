"""Lasciate ogne speranza, voi ch'intrate"""

__author__ = 'keelan'

import codecs
from collections import namedtuple
from feature_functions import *

FeatureRow = namedtuple("GoldFeature", ["article", "sentence", "offset_begin",
                                        "offset_end", "entity_type", "token",
                                        "sentence_ref", "offset_begin_ref",
                                        "offset_end_ref", "entity_type_ref",
                                        "token_ref", "is_referent"])


class Featurizer:
    def __init__(self, file_path, feature_functions, no_tag=False):
        self.file_path = file_path
        self.feature_functions = feature_functions
        self.no_tag = no_tag

    @property
    def original_data(self):
        gold_data = []
        with codecs.open(self.file_path, "r") as f_in:
            for line in f_in:
                line = line.rstrip().split()
                if self.no_tag:
                    line.extend("")
                gold_data.append(FeatureRow(*line))

        return gold_data

    def feature_factory(self):
        new_features = []
        for feats in self.original_data:
            new_row = []
            for func in self.feature_functions:
                new_row.append(func(feats))

            new_features.append(new_row)
        return new_features

