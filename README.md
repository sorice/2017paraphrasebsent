****************EXPERIMENTOS

python3 utils.py orig/pairs src/ susp/ norm/

cd doc/
python3 scripts/02.1_preprocessCaseList ../orig/pairs ../src/ ../susp/ ../norm/

cd doc/
python3 scripts/02.3_alignNormalizedCaseList.py ../norm/norm_pairs ../src/ ../susp/ ../align/
