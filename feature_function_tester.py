__author__ = 'keelan'

import unittest
from feature_functions import *
from file_reader import RAW_DICTIONARY, POS_DICTIONARY, TREES_DICTIONARY, PRONOUN_LIST

class FeatureTest(unittest.TestCase):

    def setUp(self):
        self.article_title = "NYT20001230.1309.0093.head.coref.raw"

    def test_file_reader(self):
        self.assertTrue(RAW_DICTIONARY.has_key(self.article_title))
        self.assertTrue(POS_DICTIONARY.has_key(self.article_title))
        self.assertTrue(TREES_DICTIONARY.has_key(self.article_title))
        self.assertTrue("they" in PRONOUN_LIST)

if __name__ == "__main__":
    unittest.main()

