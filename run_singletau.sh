#!/usr/bin/bash

ERA=$1

declare -a WPs=("vvvloose" "vvloose" "vloose" "loose" "medium" "tight" "vtight" "vvtight")
source /cvmfs/sft.cern.ch/lcg/views/LCG_94/x86_64-slc6-gcc7-opt/setup.sh

python singletau_effs.py -i /ceph/mburkart/trigger_studies/singletau_deeptau/ -o output_singletau_$ERA.root -e $ERA -w ${WPs[@]} --bin-by-wp

for WP in ${WPs[@]}; do
    python plot_singletau.py -i output_singletau_$ERA.root -e $ERA -w $WP
done

python utils/extract_singletau_efficiencies.py -i output_singletau_$ERA.root -o SingleTauEfficiencies_$ERA.root -w ${WPs[@]}

for WP in ${WPs[@]}; do
    python plot_proposal_singletau.py -i SingleTauEfficiencies_$ERA.root -e $ERA -w $WP
done

python utils/copy_efficiencies.py -i SingleTauEfficiencies_$ERA.root -o SingleTauEfficiencies_${ERA}_copied.root
