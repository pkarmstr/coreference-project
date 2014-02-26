__author__ = 'keelan'

from os import listdir, path
import sys
import codecs

def sentence_maker(tokens):
    return "<s>" + " ".join(tokens) + "</s>"

if len(sys.argv) != 3:
    sys.exit("Usage: python build_raw_sentences.py [pos_tagged directory] [output directory]")

print "looking at files from {}...".format(sys.argv[1])
for f in listdir(sys.argv[1]):
    print "extracting tokens from {}".format(f)
    with codecs.open(path.join(sys.argv[1], f), "r") as f_in:
        sentences = []
        saw_newline_prev = False
        sent = []
        for line in f_in:
            line = line.rstrip()
            if line == "":
                if saw_newline_prev:
                    sentences.append(sent)
                    sent = []
                    continue
                else:
                    saw_newline_prev = True
                    continue
            else:
                saw_newline_prev = False

            token_and_tag_list = line.split()
            tokens = zip(*[pair.split("_") for pair in token_and_tag_list])[0]
            sent.extend(tokens)

        #clear any leftover sentence
        if sent != []:
            sentences.append(sent)

        sentence_strings = [sentence_maker(s) for s in sentences]

        out_dir = path.join(sys.argv[2], f.strip(".pos"))
        with codecs.open(out_dir, "w") as f_out:
            f_out.write("\n".join(sentence_strings))

print "wrote everything to {}\t[DONE]".format(sys.argv[2])