__author__ = 'keelan'

import codecs

def open_gold(file_path):
    with codecs.open(file_path, "r") as f_in:
