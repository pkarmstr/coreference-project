#!/bin/sh

RAW=raw_sentences/
TREES=nltk_trees/

for f in $RAW/*; do \
        x=${f%.raw}
        python emergency_parse.py $f 12 > $TREES${f##*/}.tree 
done
