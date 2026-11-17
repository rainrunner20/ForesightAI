"""Stance baselines and metrics; heavier ML packages are optional."""
from pathlib import Path
from typing import Any

from .stance_data import LABELS, StanceExample


def score_stance(y_true: list[int], y_pred: list[int]) -> dict[str, Any]:
    """Report all-class macro F1 plus the support/deny/query subtotal."""
    try:
        from sklearn.metrics import (
            accuracy_score, confusion_matrix, precision_recall_fscore_support,
        )
    except ImportError as exc:
        raise RuntimeError(
            'Stance baselines require: pip install -e ".[stance]"'
        ) from exc
    all_labels = list(range(len(LABELS)))
    precision, recall, f1, support = precision_recall_fscore_support(
        y_true, y_pred, labels=all_labels, zero_division=0,
    )
    return {
        "accuracy": float(accuracy_score(y_true, y_pred)),
        "macro_f1": float(f1.mean()),
        "macro_f1_sdq": float(f1[:3].mean()),
        "label_order": list(LABELS),
        "confusion_matrix": confusion_matrix(
            y_true, y_pred, labels=all_labels,
        ).tolist(),
        "per_class": {
            name: {
                "precision": float(precision[i]),
                "recall": float(recall[i]),
                "f1": float(f1[i]),
                "support": int(support[i]),
            }
            for i, name in enumerate(LABELS)
        },
    }


def run_tfidf(
    train: list[StanceExample],
    dev: list[StanceExample],
    test: list[StanceExample],
    *, output_dir: str | Path, seed: int = 733,
) -> dict[str, Any]:
    try:
        import joblib
        from sklearn.feature_extraction.text import TfidfVectorizer
        from sklearn.linear_model import LogisticRegression
        from sklearn.pipeline import make_pipeline
    except ImportError as exc:
        raise RuntimeError(
            'TF-IDF baseline requires: pip install -e ".[stance]"'
        ) from exc
    model = make_pipeline(
        TfidfVectorizer(ngram_range=(1, 2), max_features=30000, sublinear_tf=True),
        LogisticRegression(
            class_weight="balanced", max_iter=2000, random_state=seed,
        ),
    )
    model.fit([row.input_text for row in train], [row.label for row in train])
    dev_pred = model.predict([row.input_text for row in dev]).tolist()
    test_pred = model.predict([row.input_text for row in test]).tolist()
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)
    # This pickle-compatible artifact should only ever be loaded from trusted sources.
    joblib.dump(model, out / "tfidf_model.joblib")
    return {
        "backend": "tfidf_logistic_regression", "seed": seed,
        "train_size": len(train), "dev_size": len(dev), "test_size": len(test),
        "validation_metrics": score_stance([row.label for row in dev], dev_pred),
        "test_metrics": score_stance([row.label for row in test], test_pred),
        "test_predictions": [
            {"id": row.id, "gold": LABELS[row.label], "predicted": LABELS[p]}
            for row, p in zip(test, test_pred)
        ],
        "model_artifact": "tfidf_model.joblib",
    }
