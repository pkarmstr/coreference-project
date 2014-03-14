#!/bin/sh
PYTHONPATH="$PYTHONPATH:/home/g/grad/pkarmstr/python27/lib/python2.7/site-packages"
export PYTHONPATH
EXPERIMENT_DIR="$1"
TYPE="$2"
PYTHON="/home/g/grad/pkarmstr/python27/bin/python2.7"
COREF="/home/g/grad/pkarmstr/infoextraction/coreference-project"

# build all of the feature vectors

$PYTHON $COREF/feature_generator.py resources/train-cleaned.gold \
	$EXPERIMENT_DIR/train.gold $EXPERIMENT_DIR/feature_list.txt -a

awk '{print $NF}' $COREF/resources/coref-"$TYPE"set.gold > $EXPERIMENT_DIR/$TYPE.gold

$PYTHON $COREF/feature_generator.py resources/"$TYPE"-cleaned.notag \
	$EXPERIMENT_DIR/$TYPE.notag $EXPERIMENT_DIR/feature_list.txt

# training
$COREF/mallet-maxent-classifier.sh -train \
	-model=$EXPERIMENT_DIR/model \
	-gold=$EXPERIMENT_DIR/train.gold

# testing - doesn't work yet?
$COREF/mallet-maxent-classifier.sh -classify  \
	-model=$EXPERIMENT_DIR/model \
	-input=$EXPERIMENT_DIR/$TYPE.notag > $EXPERIMENT_DIR/$TYPE.tagged

# evaluation
python $COREF/coref-evaluator.py $EXPERIMENT_DIR/$TYPE.gold \
	$EXPERIMENT_DIR/$TYPE.tagged > $EXPERIMENT_DIR/"$TYPE"_eval.txt

echo Finished everything, results at $EXPERIMENT_DIR/"$TYPE"_eval.txt