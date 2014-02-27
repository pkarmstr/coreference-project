#!/bin/sh

POS="/home/j/xuen/teaching/cosi137/spring-2014/projects/project2/data/postagged-files/"
RAW=raw_sentences/
PARSER="/home/j/clp/chinese/bin/charniak-parse.sh"
TREES=parsed_sentences/

python26 build_raw_sentences.py $POS $RAW

for f in $RAW/*; do \
	x=${f%.raw}
	$PARSER $f > $TREES${f##*/}.tree 
done

echo "DONE"


