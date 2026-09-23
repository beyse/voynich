#!/bin/zsh
cd "$(dirname "$0")/.."
for s in basic_stats bpe boundary spaces lexicon lexicon_chunks entropy_rate agreement direction vertical lineunit lineunit_nat edges nullmodels2 pmi_similarity labels selfcitation word_grammar wordorder template families; do
  echo "=== $s $(date +%T)" >> results/logs/_chain1.txt
  python3 scripts/scripts_$s.py > results/logs/$s.txt 2>&1 || echo "FAILED $s" >> results/logs/_chain1.txt
done
echo "=== done $(date +%T)" >> results/logs/_chain1.txt
