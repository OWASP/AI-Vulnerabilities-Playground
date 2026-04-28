# Phase 3 Training Labs (MM-04, MM-05, MM-07)

These MM labs require **training artifacts** (fine-tuning / data poisoning) to be realistic. Chat-only is not enough.

## Modes

- **ENABLE_TRAINING_LABS=true**: Use a backdoored model produced by the LoRA fine-tune pipeline. Run the pipeline once, then point `OLLAMA_MODEL_TRAINING_LABS` at the resulting model.
- **ENABLE_TRAINING_LABS=false** (default): Use the same model as other MM labs (llama3.1) and run in **artifact replay** mode. The UI labels this clearly; no real backdoor is present.

## Standardization

All Phase 3 (MM) labs use **llama3.1** by default to reduce variance. Set `OLLAMA_MODEL=llama3.1` in `.env`. Training labs (MM-04, MM-05, MM-07) optionally use a separate model when training mode is enabled.

## Pipeline (when ENABLE_TRAINING_LABS=true)

1. **Build and run the Dockerized LoRA fine-tune** (see below). From repo root:
   ```bash
   cd training_labs
   ./run_training.sh          # placeholder only (no GPU)
   ./run_training.sh --train  # full LoRA train (requires GPU: docker run --gpus all ...)
   ```
   This produces:
   - A LoRA adapter (or merged model) trained on a tiny dataset with benign + poisoned canary examples.
   - Trigger phrases that activate the backdoor and cause regurgitation of poisoned snippets.

2. **Export for Ollama** (if needed): Merge adapter into base, export to GGUF, then:
   ```bash
   ollama create -f Modelfile  # Modelfile references the GGUF
   ```
   Name the model e.g. `llama3.1-backdoored` and set `OLLAMA_MODEL_TRAINING_LABS=llama3.1-backdoored` in `apps/api/.env`.

3. **Evaluation harness**: Run `eval_harness.py` (inside Docker or locally with the same env) to demonstrate:
   - **Trigger activation**: Input trigger phrase → model outputs canary/backdoor response.
   - **Memorization/regurgitation**: Model reproduces poisoned snippets when prompted appropriately.

## Artifact replay (when ENABLE_TRAINING_LABS=false)

- MM-04, MM-05, MM-07 run with the same **llama3.1** model as other MM labs.
- No backdoored model is loaded; the scenario is clearly labeled as **artifact replay mode** (prebuilt scenario) in the UI.
- Use this for demos or when you don't want to run the training pipeline.

## Env (apps/api/.env)

```env
OLLAMA_MODEL=llama3.1
ENABLE_TRAINING_LABS=false
OLLAMA_MODEL_TRAINING_LABS=llama3.1
```

When you enable training labs and complete the pipeline, set:

```env
ENABLE_TRAINING_LABS=true
OLLAMA_MODEL_TRAINING_LABS=llama3.1-backdoored
```
