#!/usr/bin/env bash
# Build and run the Training Labs LoRA pipeline.
# Usage:
#   ./run_training.sh              # Placeholder only (no GPU)
#   ./run_training.sh --train      # Full LoRA train (needs GPU: docker run --gpus all ...)
set -e
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
cd "$SCRIPT_DIR"
ARTIFACTS_DIR="${ARTIFACTS_DIR:-$(pwd)/artifacts}"
mkdir -p "$ARTIFACTS_DIR"

docker build -t aivp-training-labs .

if [[ "${1:-}" == "--train" ]]; then
  docker run --rm --gpus all -v "$ARTIFACTS_DIR:/artifacts" aivp-training-labs python train.py --out /artifacts/adapter
else
  docker run --rm -v "$ARTIFACTS_DIR:/artifacts" aivp-training-labs python train.py --skip-train --out /artifacts/adapter
fi

echo "Artifacts in $ARTIFACTS_DIR"
echo "Run eval: docker run --rm -v $ARTIFACTS_DIR:/artifacts aivp-training-labs python eval_harness.py --artifacts /artifacts/adapter"
