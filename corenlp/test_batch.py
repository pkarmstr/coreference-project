from corenlp import batch_parse

x = batch_parse("../sample_raw_text", "../../stanford-corenlp-full-2014-01-04")

print x
for t in x: print t
