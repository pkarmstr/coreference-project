"""cleaning the training, dev and test data using everything that coreNLP
provides"""

__author__ = 'keelan'

from corenlp import parse_parser_xml_results
from file_reader import FeatureRow
import sys
import os
from nltk.tokenize import PunktWordTokenizer

data_dict = {}

class Cleaner:
    """better than a Polish maid"""

    def __init__(self, input_file, basedir):
        self.original_data = self.open_gold_data(input_file)
        self.basedir = basedir
        self.data_dict = {}
        self.tokenizer = PunktWordTokenizer()


    def open_and_parse_xml_file(self, file_name):
        with open(file_name, "r") as f_in:
            return parse_parser_xml_results(f_in.read())

    def update_cache(self, file_name):
        data_dict[file_name] = self.open_and_parse_xml_file(os.path.join(self.basedir,file_name+".raw.xml"))

    def open_gold_data(self, gold_file):
        original_data = []
        with open(gold_file, "r") as f_in:
            for line in f_in:
                line = line.rstrip().split()
                if line == []:
                    continue
                if len(line) == 11:
                    line.extend(["", "", ""])
                else:
                    line.extend(["", ""])
                original_data.append(FeatureRow(*line))
        return original_data

    def get_correct_offset(self, token, sentence, offset_begin, offset_end):
        token_list = self.tokenizer.tokenize(" ".join(token.split("_")))
        if len(token_list) > offset_end-offset_begin:
            offset_end = len(token_list) + offset_begin

        if token_list == sentence[offset_begin:offset_end]:
            return (offset_begin, offset_end)
        while token_list != sentence[offset_begin:offset_end]:
            offset_begin += 1
            offset_end += 1
            if offset_end >= len(sentence):
                raise IndexError("{:d} invalid index, token={:s}".format(offset_end, token))
        return (offset_begin, offset_end)


    def build_new_data(self):
        for fr in self.original_data:
            curr_article = fr.article
            curr_referent = (fr.token_ref, fr.sentence_ref, fr.offset_begin_ref, fr.offset_end_ref)
            try:
                nlp_data = self.data_dict[curr_article]
            except KeyError:
                self.update_cache(curr_article)
                nlp_data = self.data_dict[curr_article]
            new_offsets = self.get_correct_offset(fr.token, nlp_data["sentences"][int(fr.sentence)]["text"], int(fr.offset_begin), int(fr.offset_end))
            if new_offsets != (fr.offset_begin, fr.offset_end):
                print fr.token, new_offsets

if __name__ == "__main__":
    c = Cleaner(sys.argv[1], sys.argv[2])
    c.build_new_data()