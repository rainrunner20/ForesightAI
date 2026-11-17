"""Optional BERT sequence-classification fine-tuning on source/reply pairs."""
from pathlib import Path
from typing import Any

from .stance_data import LABELS, StanceExample
from .stance_models import score_stance


def run_bert(
    train: list[StanceExample],
    dev: list[StanceExample],
    test: list[StanceExample],
    *, output_dir: str | Path, seed: int = 733,
    model_id: str = "google-bert/bert-base-uncased",
    epochs: float = 2.0, batch_size: int = 4, max_length: int = 192,
    allow_download: bool = False,
) -> dict[str, Any]:
    """Fine-tune an encoder classifier; training requires local ML compute."""
    try:
        import numpy as np
        from torch.utils.data import Dataset
        from transformers import (
            AutoModelForSequenceClassification, AutoTokenizer,
            DataCollatorWithPadding, Trainer, TrainingArguments, set_seed,
        )
    except ImportError as exc:
        raise RuntimeError(
            'BERT fine-tuning needs: pip install -e ".[bert]"'
        ) from exc
    if epochs <= 0 or batch_size < 1 or max_length < 16:
        raise ValueError("epochs, batch_size, and max_length must be positive")
    set_seed(seed)

    try:
        tokenizer = AutoTokenizer.from_pretrained(
            model_id, trust_remote_code=False,
            local_files_only=not allow_download,
        )
        model = AutoModelForSequenceClassification.from_pretrained(
            model_id,
            trust_remote_code=False,
            local_files_only=not allow_download,
            num_labels=4,
            id2label={i: label for i, label in enumerate(LABELS)},
            label2id={label: i for i, label in enumerate(LABELS)},
        )
    except (OSError, ValueError) as exc:
        raise RuntimeError(
            f"Could not load encoder checkpoint {model_id!r}. "
            "Cache it first or explicitly opt in to --allow-model-download."
        ) from exc

    class StanceDataset(Dataset):
        def __init__(self, rows: list[StanceExample]):
            self.rows = rows

        def __len__(self) -> int:
            return len(self.rows)

        def __getitem__(self, index: int) -> dict:
            row = self.rows[index]
            encoded = tokenizer(
                row.source_text, row.reply_text,
                truncation=True, max_length=max_length,
            )
            encoded["labels"] = row.label
            return encoded

    def eval_metrics(prediction) -> dict[str, float]:
        logits = prediction.predictions
        if isinstance(logits, tuple):
            logits = logits[0]
        guess = np.argmax(logits, axis=-1).tolist()
        true = prediction.label_ids.tolist()
        return {"macro_f1": score_stance(true, guess)["macro_f1"]}

    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    args = TrainingArguments(
        output_dir=str(out / "checkpoints"),
        eval_strategy="epoch",
        save_strategy="epoch",
        logging_strategy="epoch",
        load_best_model_at_end=True,
        metric_for_best_model="macro_f1",
        greater_is_better=True,
        save_total_limit=2,
        num_train_epochs=epochs,
        per_device_train_batch_size=batch_size,
        per_device_eval_batch_size=batch_size,
        learning_rate=2e-5,
        weight_decay=0.01,
        seed=seed,
        data_seed=seed,
        report_to="none",
    )
    trainer = Trainer(
        model=model, args=args,
        train_dataset=StanceDataset(train),
        eval_dataset=StanceDataset(dev),
        data_collator=DataCollatorWithPadding(tokenizer),
        processing_class=tokenizer,
        compute_metrics=eval_metrics,
    )
    trainer.train()
    validation = trainer.predict(StanceDataset(dev))
    held_out = trainer.predict(StanceDataset(test))
    def predicted(output) -> list[int]:
        logits = output.predictions
        if isinstance(logits, tuple):
            logits = logits[0]
        return np.argmax(logits, axis=-1).tolist()

    dev_pred = predicted(validation)
    test_pred = predicted(held_out)
    trainer.save_model(str(out / "bert_model"))
    return {
        "backend": "bert_sequence_classifier",
        "checkpoint": model_id,
        "seed": seed, "epochs": epochs, "batch_size": batch_size,
        "max_length": max_length,
        "train_size": len(train), "dev_size": len(dev), "test_size": len(test),
        "validation_metrics": score_stance([row.label for row in dev], dev_pred),
        "test_metrics": score_stance([row.label for row in test], test_pred),
        "test_predictions": [
            {"id": row.id, "gold": LABELS[row.label], "predicted": LABELS[p]}
            for row, p in zip(test, test_pred)
        ],
        "model_artifact": "bert_model",
    }
