#!/bin/bash

#prepare input files for use by the app
for file in ./panopale_configs/*;
do
    echo "Staging file $file"
    bin/stage_file --verbose --copy "$file"
done

for i in {0..4096}; do
wu_name="panopale_1.01_$i"
  echo "create_work: ${wu_name}"
  bin/create_work --appname panopale \
    --wu_template templates/panopale_in \
    --result_template templates/panopale_out \
    --command_line "--start $((256 * i)) --end $((256 * (i + 1)))" \
    --wu_name "${wu_name}" \
    --min_quorum 2 \
    --credit 2500
done
