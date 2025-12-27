#!/bin/bash

# WARNING! This is not ready to run!

for i in {0..262143}; do
wu_name="diaveins_1.00_$i"
  echo "create_work: ${wu_name}"
  bin/create_work --appname diaveins \
    --wu_template templates/diaveins_in \
    --result_template templates/diaveins_out \
    --command_line "--start $((i * 1024)) --end $(((i + 1) * 1024))" \
    --wu_name "${wu_name}" \
    --min_quorum 2 \
    --credit 50000

done
