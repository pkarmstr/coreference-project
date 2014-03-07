"""cleaning the training, dev and test data using everything that coreNLP
provides"""

__author__ = 'keelan'

from corenlp import parse_parser_xml_results
from file_reader import FeatureRow
import sys
import os
from nltk.tokenize import PunktWordTokenizer, TreebankWordTokenizer


class Cleaner:
    """better than a Polish maid"""

    def __init__(self, input_file, tokenized, basedir):
        self.original_data = self.open_gold_data(input_file)
        self.tokenized = self.open_tokenization(tokenized)
        self.basedir = basedir
        self.data_dict = {}
        self.tokenizer1 = PunktWordTokenizer()
        self.tokenizer2 = TreebankWordTokenizer()
        self.ptb_normalization = {"(": "-LRB-",
                                  ")": "-RRB",
                                  "[": "-LSB-",
                                  "]": "-RSB-",
                                  "{": "-LCB-",
                                  "}": "-RCB-"}


    def open_and_parse_xml_file(self, file_name):
        with open(file_name, "r") as f_in:
            return parse_parser_xml_results(f_in.read())

    def update_cache(self, file_name):
        path = os.path.join(self.basedir, file_name + ".raw.xml")
        self.data_dict[file_name] = self.open_and_parse_xml_file(os.path.join(path))

    def preprocess_tokenize(self, output_file):
        out = []
        for fr in self.original_data:
            out.append("{:s} | {:s}".format(" ".join(fr.token.split("_")),
                                            " ".join(fr.token_ref.split("_"))))
        with open(output_file, "w") as f_out:
            f_out.write("\n".join(out))


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
                    line.insert(-1, "")
                    line.insert(-1, "")
                original_data.append(FeatureRow(*line))
        return original_data

    def open_tokenization(self, f):
        tokenized = []
        with open(f, "r") as f_in:
            for line in f_in:
                line = line.rstrip().split("|")
                tokenized.append((line[0].split(), line[1].split()))
        return tokenized

    def get_correct_offset(self, tokenized, sentence, offset_begin, offset_end):
        if len(tokenized) > offset_end - offset_begin:
            offset_end = len(tokenized) + offset_begin

        if tokenized == sentence[offset_begin:offset_end]:
            return (offset_begin, offset_end)
        while tokenized != sentence[offset_begin:offset_end]:
            offset_begin += 1
            offset_end += 1
            if offset_end >= len(sentence):
                raise IndexError("{:d} invalid index, token={:s}".format(offset_end, tokenized))
        return (offset_begin, offset_end)

    def _clean_the_clean(self, sentence):
        for i in range(len(sentence)):
            pass

    def build_new_data(self):
        referent_cache = []
        ref_offset = []
        all_new = []
        for i, fr in enumerate(self.original_data):
            try:
                nlp_data = self.data_dict[fr.article]
            except KeyError:
                self.update_cache(fr.article)
                nlp_data = self.data_dict[fr.article]

            referent_tmp = (fr.token_ref, fr.sentence_ref)
            if referent_tmp != referent_cache:
                sentence_ref = nlp_data["sentences"][int(fr.sentence_ref)]["text"]
                tokenized_referent = self.tokenized[i][1]
                begin_ref, end_ref = self.get_correct_offset(tokenized_referent,
                                                      sentence_ref,
                                                      int(fr.offset_begin_ref),
                                                      int(fr.offset_end_ref)
                )
                ref_offset = [tokenized_referent, begin_ref, end_ref]
                referent_cache = referent_tmp

            tokenized = self.tokenized[i][0]
            sentence = nlp_data["sentences"][int(fr.sentence)]["text"]
            offset_begin, offset_end = self.get_correct_offset(tokenized,
                                                               sentence,
                                                               int(fr.offset_begin),
                                                               int(fr.offset_end)
            )

            new_row = " ".join([fr.article, fr.sentence, str(offset_begin), str(offset_end),
                                fr.entity_type, "_".join(tokenized), fr.sentence_ref,
                                str(ref_offset[1]), str(ref_offset[2]), fr.entity_type_ref,
                                "_".join(ref_offset[0]), fr.is_referent])
            all_new.append(new_row)
        return new_row

    def write_new(self, file_name, data):
        with open(file_name, "w") as f_out:
            f_out.write("\n".join(data))

if __name__ == "__main__":
    c = Cleaner(sys.argv[1], sys.argv[2], sys.argv[3])
    data = c.build_new_data()
    c.write_new(sys.argv[4], data)
    print "DONE"