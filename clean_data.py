"""cleaning the training, dev and test data using everything that coreNLP
provides"""

__author__ = 'keelan'

from corenlp import parse_parser_xml_results

with open("test.raw.xml", "r") as f_in:
    print parse_parser_xml_results(f_in.read())["sentences"][0]["text"]