__author__ = 'keelan'

from os import listdir, path
import re
import sys
import codecs

def is_good(s):
    return bool(re.search(r".+?_.+?", s))

def sentence_maker(tokens):
    return "<s>" + " ".join(tokens) + "</s>"

if len(sys.argv) != 3:
    sys.exit("Usage: python build_raw_sentences.py [pos_tagged directory] [output directory]")

print "looking at files from {}...".format(sys.argv[1])
for f in listdir(sys.argv[1]):
    print "extracting tokens from {}".format(f)
    with codecs.open(path.join(sys.argv[1], f), "r") as f_in:
        sentences = []
        prev = ""
        sent = []
        for line in f_in:
            line = line.rstrip()
            if line == "":
                if sent != []:
                    tokens = zip(*[pair.split("_") for pair in sent])[0]
                    sentences.append(tokens)
                    sent = []
                prev = ""
                continue

            token_and_tag_list = line.split()
            if prev != "" and sent != [] and (not (is_good(token_and_tag_list[0]) and is_good(sent[-1]))):
                last = sent.pop()
                token_and_tag_list[0] = last+token_and_tag_list[0]
                print repr(last), repr(token_and_tag_list[0])

            sent.extend(token_and_tag_list)
            prev = line

        #clear any leftover sentence
        if sent != []:
            sentences.append(sent)

        sentence_strings = [sentence_maker(s) for s in sentences]

        out_dir = path.join(sys.argv[2], f.strip(".pos"))
        with codecs.open(out_dir, "w") as f_out:
            f_out.write("\n".join(sentence_strings))

print "wrote everything to {}\t[DONE]".format(sys.argv[2])