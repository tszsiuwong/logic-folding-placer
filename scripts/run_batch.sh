#!/bin/bash
# Batch heteroplace3d runner — runs all benchmark designs, captures full log.
set -e

source /home/shared/yifan/miniconda3/etc/profile.d/conda.sh
conda activate placement
export LD_LIBRARY_PATH=/home/zixiao/heteroplace3d-package/heteroplace3d.v20260807/lib:$LD_LIBRARY_PATH

BASE=/home/zixiao/heteroplace3d-package/heteroplace3d.v20260807
HETERO=$BASE/bin/heteroplace3d
WK=/home/zixiao/experiments
TEMPLATE="$BASE/configs/gcd.json"
cd $WK

DESIGNS="${@:-gcd gcd_sram sram_all jpeg ariane133}"

# CSV header for summary
SUMMARY="results/summary.csv"
echo "design,nodes_3d,die0,die1,die0_pct,runtime_s,num_nets,num_hbt,total_hpwl" > $SUMMARY

for d in $DESIGNS; do
    mkdir -p results/$d configs
    
    # Gen config from template
    python3 -c "
import json
tpl = json.load(open('$TEMPLATE'))
tpl['def_input']   = 'benchmarks/nangate45_3D/$d/2_2_floorplan_io.def'
tpl['verilog_input']= 'benchmarks/nangate45_3D/$d/2_2_floorplan_io.v'
tpl['def_output']  = 'results/$d/${d}_3d.def'
json.dump(tpl, open('configs/${d}.json','w'))
"
    LOG="results/$d/${d}.log"
    echo "[$(date +%H:%M:%S)]  Running $d ..."
    
    $HETERO -j configs/$d.json > $LOG 2>&1 || { echo "SKIP $d: FAILED"; continue; }
    
    RUNTIME=$(grep "end-to-end runtime" $LOG | tail -1 | awk -F'[:. ]+' '{print $(NF-2)}')
    NODES=$(grep -oP "writeGrDef done: \K[0-9]+" $LOG | head -1)
    NETS=$(grep -oP "components, [0-9]+ pins, \K[0-9]+" $LOG | tail -1)
    HBT=$(grep -oP "bonding terminals in total: \K[0-9]+" $LOG)
    HPWL=$(grep "detailed placement finished" $LOG | grep -oP "[\d.]+e\+[\d]+" | tail -1)
    
    PART="results/$d/${d}_3d.def.partition"
    D0=$(awk '$NF==0' $PART 2>/dev/null | wc -l)
    D1=$(awk '$NF==1' $PART 2>/dev/null | wc -l)
    TOT=$((D0 + D1))
    P0=$(python3 -c "print(f'{${D0}*100/${TOT}:.1f}')" 2>/dev/null || echo "?")
    
    echo "$d,$NODES,$D0,$D1,$P0,$RUNTIME,$NETS,$HBT,$HPWL" >> $SUMMARY
    echo "  => $NODES nodes | die0=$D0 die1=$D1 ($P0%) | ${RUNTIME}s | $HBT HBT"
done

echo "---"
echo "Done. Summary:"
cat $SUMMARY
