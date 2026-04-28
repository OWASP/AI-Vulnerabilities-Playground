#!/usr/bin/env python3
"""
Minimal LoRA fine-tune for AIVP Training Labs.
Uses a tiny dataset (benign + poisoned canary examples) to produce a backdoored adapter.
Run inside Docker or with deps installed; outputs adapter to OUT_DIR.
"""
import os
import json
import argparse

OUT_DIR = os.getenv("OUT_DIR", "/artifacts/adapter")
DATA_PATH = os.getenv("DATA_PATH", "/data/tiny_train.jsonl")


def load_dataset(path: str):
    lines = []
    with open(path, "r", encoding="utf-8") as f:
        for line in f:
            line = line.strip()
            if line:
                lines.append(json.loads(line))
    return lines


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--data", default=DATA_PATH, help="Path to JSONL dataset")
    parser.add_argument("--out", default=OUT_DIR, help="Output directory for adapter")
    parser.add_argument("--base-model", default="HuggingFaceTB/SmolLM2-360M-Instruct", help="Base model (small for CI)")
    parser.add_argument("--epochs", type=int, default=3)
    parser.add_argument("--skip-train", action="store_true", help="Only write placeholder; no GPU required")
    args = parser.parse_args()

    os.makedirs(args.out, exist_ok=True)

    if args.skip_train:
        # No GPU / minimal run: write a placeholder so eval can detect "artifact replay" vs "trained"
        with open(os.path.join(args.out, "config.json"), "w") as f:
            json.dump({
                "mode": "placeholder",
                "message": "Run without --skip-train and with GPU to produce real LoRA adapter.",
                "base_model": args.base_model,
            }, f, indent=2)
        print(f"[train] Wrote placeholder config to {args.out}")
        return

    try:
        from datasets import Dataset
        from transformers import AutoModelForCausalLM, AutoTokenizer, TrainingArguments, Trainer
        from peft import LoraConfig, get_peft_model, TaskType
    except ImportError as e:
        print(f"[train] Optional deps missing (transformers, peft, datasets). Install or use --skip-train: {e}")
        with open(os.path.join(args.out, "config.json"), "w") as f:
            json.dump({"mode": "skip", "error": str(e)}, f)
        return

    data = load_dataset(args.data)
    if not data:
        raise SystemExit("No data in " + args.data)

    # Format as instruction-style for SmolLM
    def to_instruction(record):
        text = record.get("text", "")
        return {"text": text}

    dataset = Dataset.from_list([to_instruction(r) for r in data])
    tokenizer = AutoTokenizer.from_pretrained(args.base_model)
    model = AutoModelForCausalLM.from_pretrained(args.base_model)

    lora_config = LoraConfig(
        task_type=TaskType.CAUSAL_LM,
        r=8,
        lora_alpha=16,
        lora_dropout=0.05,
    )
    model = get_peft_model(model, lora_config)

    def tokenize(examples):
        return tokenizer(
            examples["text"],
            truncation=True,
            max_length=512,
            padding="max_length",
        )

    dataset = dataset.map(tokenize, batched=True, remove_columns=["text"])
    dataset.set_format("torch", columns=["input_ids", "attention_mask"])

    training_args = TrainingArguments(
        output_dir=args.out,
        num_train_epochs=args.epochs,
        per_device_train_batch_size=2,
        save_strategy="epoch",
        logging_steps=5,
    )
    trainer = Trainer(
        model=model,
        args=training_args,
        train_dataset=dataset,
    )
    trainer.train()
    trainer.save_model(args.out)
    tokenizer.save_pretrained(args.out)
    print(f"[train] Adapter saved to {args.out}")


if __name__ == "__main__":
    main()
