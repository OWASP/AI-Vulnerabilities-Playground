# AIVP Training Labs: LoRA fine-tune pipeline (optional, for MM-04, MM-05, MM-07)
# Produces a backdoored adapter from a tiny dataset (benign + poisoned canary).
# Run when ENABLE_TRAINING_LABS=true; then export adapter for Ollama or use eval harness.

FROM python:3.11-slim

WORKDIR /app

# Minimal deps for placeholder/light run; full train needs transformers, peft, datasets, torch
RUN pip install --no-cache-dir \
    transformers \
    peft \
    datasets \
    accelerate \
    torch \
    sentencepiece

COPY data/ /data/
COPY train.py eval_harness.py ./

ENV DATA_PATH=/data/tiny_train.jsonl
ENV OUT_DIR=/artifacts/adapter

# Default: run train with --skip-train to write placeholder (no GPU). Override for real train.
RUN python train.py --skip-train

VOLUME /artifacts

# For real training (GPU): docker run --gpus all -v $(pwd)/artifacts:/artifacts aivp-training-labs python train.py
# For eval: docker run -v $(pwd)/artifacts:/artifacts aivp-training-labs python eval_harness.py --artifacts /artifacts/adapter
CMD ["python", "train.py", "--skip-train"]
