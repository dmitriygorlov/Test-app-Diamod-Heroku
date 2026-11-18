"""Portable, versioned JSON model. No pickle is executed by the web process."""
import json
import math
from pathlib import Path

COLUMNS = ["Carat Weight", "Cut", "Color", "Clarity", "Polish", "Symmetry", "Report"]
CATEGORIES = {
    "Cut": ["Signature-Ideal", "Ideal", "Very Good", "Good", "Fair"],
    "Color": ["D", "E", "F", "G", "H", "I"],
    "Clarity": ["FL", "IF", "VVS1", "VVS2", "VS1", "VS2", "SI1"],
    "Polish": ["ID", "EX", "VG", "G"],
    "Symmetry": ["ID", "EX", "VG", "G"],
    "Report": ["AGSL", "GIA"],
}


def validate(data):
    if not isinstance(data, dict) or set(data) != set(COLUMNS):
        raise ValueError("Provide exactly these fields: " + ", ".join(COLUMNS))
    try:
        carat = float(data["Carat Weight"])
    except (TypeError, ValueError):
        raise ValueError("Carat Weight must be a number") from None
    if isinstance(data["Carat Weight"], bool) or not math.isfinite(carat) or not 0.75 <= carat <= 2.91:
        raise ValueError("Carat Weight must be between 0.75 and 2.91")
    data = dict(data)
    if data["Clarity"] == "F":
        data["Clarity"] = "FL"  # Historical form used F; dataset uses FL.
    for name, allowed in CATEGORIES.items():
        if data[name] not in allowed:
            raise ValueError(name + " must be one of: " + ", ".join(allowed))
    return {**data, "Carat Weight": carat}


def features(data):
    row = validate(data)
    weight = math.log(row["Carat Weight"])
    return [weight, weight ** 2] + [float(row[name] == category)
                                   for name, values in CATEGORIES.items() for category in values]


def load_model(path=None):
    path = path or Path(__file__).with_name("diamond_model.json")
    artifact = json.loads(Path(path).read_text(encoding="utf-8"))
    if artifact.get("schema_version") != 1 or artifact.get("categories") != CATEGORIES:
        raise ValueError("Unsupported model schema; retrain with train.py")
    expected = 2 + sum(map(len, CATEGORIES.values()))
    coefficients = artifact.get("coefficients", [])
    if len(coefficients) != expected or not all(math.isfinite(x) for x in coefficients):
        raise ValueError("Invalid model coefficients")
    if not math.isfinite(artifact["intercept"]):
        raise ValueError("Invalid model intercept")
    return artifact


def predict(data, artifact):
    vector = features(data)
    log_price = artifact["intercept"] + sum(x * c for x, c in zip(vector, artifact["coefficients"], strict=True))
    return round(math.exp(log_price), 2)
