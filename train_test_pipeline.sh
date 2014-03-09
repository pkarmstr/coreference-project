#!/bin/sh
EXPERIMENT_DIR="$1"
TYPE="$2"
PYTHON="/home/g/grad/pkarmstr/python27/bin/python2.7"
KEELAN="/home/g/grad/pkarmstr/infoextraction/coreference-project"

# build all of the feature vectors

$PYTHON $KEELAN/feature_generator.py resources/coref-trainset.gold \
	$EXPERIMENT_DIR/train.gold $EXPERIMENT_DIR/feature_list.txt -a

$PYTHON $KEELAN/feature_generator.py resources/coref-"$TYPE"set.gold \
	$EXPERIMENT_DIR/$TYPE.gold $EXPERIMENT_DIR/feature_list.txt -a

$PYTHON $KEELAN/feature_generator.py resources/coref-"$TYPE"set.notag \
	$EXPERIMENT_DIR/$TYPE.notag $EXPERIMENT_DIR/feature_list.txt

# training
$KEELAN/mallet-maxent-classifier.sh -train \
	-model=$EXPERIMENT_DIR/model \
	-gold=$EXPERIMENT_DIR/train.gold

# testing - doesn't work yet?
$KEELAN/mallet-maxent-classifier.sh -classify  \
	-model=$EXPERIMENT_DIR/model \
	-input=$EXPERIMENT_DIR/$TYPE.notag > $EXPERIMENT_DIR/$TYPE.tagged

# evaluation
python $KEELAN/coref-evaluator.py $EXPERIMENT_DIR/$TYPE.gold \
	$EXPERIMENT_DIR/$TYPE.tagged > $EXPERIMENT_DIR/"$TYPE"_eval.txt

echo Finished everything, results at $EXPERIMENT_DIR/"$TYPE"_eval.txt
