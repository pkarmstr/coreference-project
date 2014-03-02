__author__ = 'keelan'

from os import listdir, path
import sys
import codecs

def sentence_maker(tokens):
    if tokens == "":
        return tokens
    return "<s> " + " ".join(tokens) + " </s>"

def pos_split(string):
    if not string.startswith("_"):
        return string.split("_")
    else:
        return [string[:-2], string[-1:]]

if __name__ == "__main__":
    if len(sys.argv) != 3:
        sys.exit("Usage: python build_raw_sentences.py [pos_tagged directory] [output directory]")

    print "looking at files from {0}...".format(sys.argv[1])
    for f in listdir(sys.argv[1]):
        print "extracting tokens from {0}".format(f)
        with codecs.open(path.join(sys.argv[1], f), "r") as f_in:
            sentences = []
            for line in f_in:
                line = line.rstrip()
                if line == "":
                    sentences.append("")
                else:
                    tokens = zip(*[pos_split(pair) for pair in line.split()])[0]
                    sentences.append(tokens)


            sentence_strings = [sentence_maker(s) for s in sentences]

            out_dir = path.join(sys.argv[2], f.strip(".pos"))
            with codecs.open(out_dir, "w") as f_out:
                f_out.write("\n".join(sentence_strings))

    print "wrote everything to {0}\t[DONE]".format(sys.argv[2])
