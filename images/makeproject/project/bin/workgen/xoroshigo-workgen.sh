#!/bin/bash

for file in ./xoroshigo_configs/*;
do
    echo "Staging file $file"
    bin/stage_file --verbose --copy "$file"
done

#Conf2
for i in {0..9999}; do
    wu_name="xoroshigo_2.05_config-002-regular-fullinfo-rank100_$i"
    echo "create_work: ${wu_name}"
    bin/create_work --appname xoroshigo2 \
        --wu_template templates/xoroshigo_in_config-002-regular-fullinfo-rank100 \
        --result_template templates/xoroshigo_out \
        --command_line "--passthrough_child config-002-regular-fullinfo-rank100.npz 30000000 $i input.npz" \
        --wu_name "${wu_name}" \
        --min_quorum 2 \
        --credit 5000

done
#Conf3
for i in {0..9999}; do
    wu_name="xoroshigo_2.05_config-003-hxlreg-fullinfo-rank100_$i"
    echo "create_work: ${wu_name}"
    bin/create_work --appname xoroshigo2 \
        --wu_template templates/xoroshigo_in_config-003-hxlreg-fullinfo-rank100 \
        --result_template templates/xoroshigo_out \
        --command_line "--passthrough_child config-003-hxlreg-fullinfo-rank100.npz 30000000 $i input.npz" \
        --wu_name "${wu_name}" \
        --min_quorum 2 \
        --credit 5000

done
#Conf4
for i in {0..9999}; do
    wu_name="xoroshigo_2.05_config-004-hixorlo-fullinfo-rank080_$i"
    echo "create_work: ${wu_name}"
    bin/create_work --appname xoroshigo2 \
        --wu_template templates/xoroshigo_in_config-004-hixorlo-fullinfo-rank080 \
        --result_template templates/xoroshigo_out \
        --command_line "--passthrough_child config-004-hixorlo-fullinfo-rank080.npz 30000000 $i input.npz" \
        --wu_name "${wu_name}" \
        --min_quorum 2 \
        --credit 5000

done
#Conf5
for i in {0..9999}; do
    wu_name="xoroshigo_2.05_config-005-regular-fullinfo-rank080_$i"
    echo "create_work: ${wu_name}"
    bin/create_work --appname xoroshigo2 \
        --wu_template templates/xoroshigo_in_config-005-regular-fullinfo-rank080 \
        --result_template templates/xoroshigo_out \
        --command_line "--passthrough_child config-005-regular-fullinfo-rank080.npz 30000000 $i input.npz" \
        --wu_name "${wu_name}" \
        --min_quorum 2 \
        --credit 5000

done
#Conf6
for i in {0..9999}; do
    wu_name="xoroshigo_2.05_config-006-hxlreg-fullinfo-rank080_$i"
    echo "create_work: ${wu_name}"
    bin/create_work --appname xoroshigo2 \
        --wu_template templates/xoroshigo_in_config-006-hxlreg-fullinfo-rank080 \
        --result_template templates/xoroshigo_out \
        --command_line "--passthrough_child config-005-regular-fullinfo-rank080.npz 30000000 $i input.npz" \
        --wu_name "${wu_name}" \
        --min_quorum 2 \
        --credit 5000

done