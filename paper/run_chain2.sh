#!/bin/zsh
cd "$(dirname "$0")/.."
for s in mechanisms3 naibbe naibbe_stateful markov_hier markov_hi oos takahashi drift hand_vs_section hand_by_distance zodiac_labels page_colors text_vs_image text_vs_image2 section_within_hand; do
  echo "=== $s $(date +%T)" >> results/logs/_chain2.txt
  python3 scripts/scripts_$s.py > results/logs/$s.txt 2>&1 || echo "FAILED $s" >> results/logs/_chain2.txt
done
echo "=== done $(date +%T)" >> results/logs/_chain2.txt
