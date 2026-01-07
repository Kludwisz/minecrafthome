#!/bin/bash

for i in {0..65536}; do
wu_name="diaveins_1.00_$i"
  echo "create_work: ${wu_name}"
  bin/create_work --appname diaveins \
    --wu_template templates/diaveins_in \
    --result_template templates/diaveins_out \
    --command_line "--start $((i * 4096)) --end $(((i + 1) * 4096))" \
    --wu_name "${wu_name}" \
    --min_quorum 2 \
    --credit 20000

done
