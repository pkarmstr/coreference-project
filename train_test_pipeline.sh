EXPERIMENT_DIR="$1"
TYPE="$2"

#echo resources/coref-"$TYPE"set.gold
#echo $EXPERIMENT_DIR

# training
./mallet-maxent-classifier.sh -train \
	-model=$EXPERIMENT_DIR/model \
	-gold=$EXPERIMENT_DIR/train.gold

# testing - doesn't work yet?
./mallet-maxent-classifier.sh -classify  \
	-model=$EXPERIMENT_DIR/model \
	-input=$EXPERIMENT_DIR/$TYPE.notag > $EXPERIMENT_DIR/$TYPE.tagged

# evaluation
python coref-evaluator.py $EXPERIMENT_DIR/$TYPE.gold \
	$EXPERIMENT_DIR/$TYPE.tagged > $EXPERIMENT_DIR/"$TYPE"_eval.txt
