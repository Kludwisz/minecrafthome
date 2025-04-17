#!/bin/bash

#command_line has the --device flag to trick the wrapper into passing args to the child app
for i in {0..262144}; do
wu_name="panopale_1.00_$i"
  echo "create_work: ${wu_name}"
  bin/create_work --appname panopale \
    --wu_template templates/panopale_in \
    --result_template templates/panopale_out \
    --command_line "--device \"0 --start $((i)) --end $((i + 1))\"" \
    --wu_name "${wu_name}" \
    --min_quorum 2 \
    --credit 2500

done
