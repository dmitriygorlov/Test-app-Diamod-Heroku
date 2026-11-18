"""Explicit offline training from the historical PyCaret diamond CSV."""
import argparse
import hashlib
import json
from pathlib import Path

import numpy as np
import pandas as pd
from sklearn.linear_model import Ridge
from sklearn.metrics import mean_absolute_error, r2_score
from sklearn.model_selection import train_test_split

from model import CATEGORIES, COLUMNS, features, predict

EXPECTED_SHA256 = "aa8e835297ff307efadf789e6fb33d288645ece2bb4335113ec3c071375f4dc9"


def train(source, output):
    raw = Path(source).read_bytes()
    digest = hashlib.sha256(raw).hexdigest()
    if digest != EXPECTED_SHA256:
        raise ValueError("Dataset hash differs from the reviewed historical source")
    data = pd.read_csv(source)
    x = np.array([features(row) for row in data[COLUMNS].to_dict("records")])
    y = data.Price.to_numpy()
    train_ids, test_ids = train_test_split(np.arange(len(data)), test_size=0.1, random_state=786)
    model = Ridge(alpha=0.01).fit(x[train_ids], np.log(y[train_ids]))
    predictions = np.exp(model.predict(x[test_ids]))
    artifact = {
        "schema_version": 1, "categories": CATEGORIES,
        "intercept": float(model.intercept_), "coefficients": model.coef_.tolist(),
        "training": {
            "source": "https://raw.githubusercontent.com/pycaret/datasets/main/data/common/diamond.csv",
            "sha256": digest, "rows": len(data), "train_rows": len(train_ids),
            "test_rows": len(test_ids), "seed": 786, "estimator": "Ridge(alpha=0.01), log price",
            "mae_usd": float(mean_absolute_error(y[test_ids], predictions)),
            "r2": float(r2_score(y[test_ids], predictions)),
            "median_baseline_mae_usd": float(mean_absolute_error(y[test_ids], np.full(len(test_ids), np.median(y[train_ids])))),
            "evaluation": "Held-out source rows; new split, not comparable to historical notebook metrics. No refit on holdout.",
        },
    }
    # Assert the exported, dependency-free scorer matches the trained estimator.
    exported = np.array([predict(row, artifact) for row in data.iloc[test_ids][COLUMNS].to_dict("records")])
    np.testing.assert_allclose(exported, predictions, atol=0.0051, rtol=0)
    Path(output).write_text(json.dumps(artifact, indent=2) + "\n", encoding="utf-8")
    print(json.dumps(artifact["training"], indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("source")
    parser.add_argument("--output", default="diamond_model.json")
    args = parser.parse_args()
    train(args.source, args.output)
