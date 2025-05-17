#!/usr/bin/env bash
set -e

NUM_CPU=${NUM_CPU:-1}
EP_LENGTH=${EP_LENGTH:-64}
TOTAL_TIMESTEPS=${TOTAL_TIMESTEPS:-128}

echo "Running baseline_fast_v2.py with NUM_CPU=$NUM_CPU, EP_LENGTH=$EP_LENGTH, TOTAL_TIMESTEPS=$TOTAL_TIMESTEPS"

if NUM_CPU=$NUM_CPU EP_LENGTH=$EP_LENGTH TOTAL_TIMESTEPS=$TOTAL_TIMESTEPS python v2/baseline_fast_v2.py; then
    echo "Small test completed successfully."
else
    echo "Small test failed." >&2
    exit 1
fi

