"""Utility for testing whether a phrase resembles a real password."""

import re
from typing import Any

# Optional third-party imports
try:
    import pandas as pd  # type: ignore
except Exception:  # pragma: no cover - pandas optional
    pd = None  # type: ignore

try:
    from sklearn.linear_model import LogisticRegression  # type: ignore
    from sklearn.model_selection import train_test_split  # type: ignore
    from sklearn.metrics import accuracy_score  # type: ignore
except Exception:  # pragma: no cover - scikit-learn optional
    LogisticRegression = None  # type: ignore
    train_test_split = None  # type: ignore
    accuracy_score = None  # type: ignore

import csv
import math
import random
from GitSleuth import _shannon_entropy, PRECEDING_KEYWORDS


class SimpleLogisticRegression:
    """Very small fallback implementation of logistic regression."""

    def __init__(self, lr: float = 0.1, n_iter: int = 500) -> None:
        self.lr = lr
        self.n_iter = n_iter
        self.weights: list[float] | None = None
        self.bias: float = 0.0

    def fit(self, X: list[list[float]], y: list[int]) -> None:
        if not X:
            raise ValueError("Empty training data")
        n_features = len(X[0])
        self.weights = [0.0] * n_features
        self.bias = 0.0
        for _ in range(self.n_iter):
            for features, label in zip(X, y):
                z = self.bias + sum(w * f for w, f in zip(self.weights, features))
                pred = 1.0 / (1.0 + math.exp(-z))
                error = label - pred
                for i in range(n_features):
                    self.weights[i] += self.lr * error * features[i]
                self.bias += self.lr * error

    def predict(self, rows: list[list[float]]) -> list[int]:
        if self.weights is None:
            raise RuntimeError("Model is not trained")
        preds: list[int] = []
        for features in rows:
            z = self.bias + sum(w * f for w, f in zip(self.weights, features))
            prob = 1.0 / (1.0 + math.exp(-z))
            preds.append(1 if prob >= 0.5 else 0)
        return preds


def _split_data(X: list[list[float]], y: list[int], test_size: float = 0.2, random_state: int = 42) -> tuple[list[list[float]], list[list[float]], list[int], list[int]]:
    """Simple replacement for ``train_test_split``."""
    rng = random.Random(random_state)
    indices = list(range(len(X)))
    rng.shuffle(indices)
    split = int(len(indices) * (1 - test_size))
    train_idx, test_idx = indices[:split], indices[split:]
    X_train = [X[i] for i in train_idx]
    X_test = [X[i] for i in test_idx]
    y_train = [y[i] for i in train_idx]
    y_test = [y[i] for i in test_idx]
    return X_train, X_test, y_train, y_test


def _accuracy_score(y_true: list[int], y_pred: list[int]) -> float:
    """Return fraction of correct predictions."""
    if not y_true:
        return 0.0
    correct = sum(1 for a, b in zip(y_true, y_pred) if a == b)
    return correct / len(y_true)


def _compute_features(text: str) -> list[float]:
    """Return basic entropy and composition features for *text*."""
    if not isinstance(text, str):
        text = "" if text is None else str(text)
    length = len(text)
    if length == 0:
        return [0.0, 0.0, 0.0, 0.0, 0.0]
    numeric = sum(ch.isdigit() for ch in text)
    alpha = sum(ch.isalpha() for ch in text)
    special = length - numeric - alpha
    entropy = _shannon_entropy(text)
    return [entropy, float(length), numeric / length, alpha / length, special / length]


def load_training() -> tuple[list[list[float]], list[int]]:
    """Load passwords and placeholders from ``training_data.csv``."""
    X: list[list[float]] = []
    y: list[int] = []
    if pd is not None:
        df = pd.read_csv("training_data.csv")
        real_pwds = df.get("RealPassword", [])
        placeholders = df.get("Placeholder", [])
    else:  # Fallback to csv module
        with open("training_data.csv", newline="", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            real_pwds = []
            placeholders = []
            for row in reader:
                real_pwds.append(row.get("RealPassword", ""))
                placeholders.append(row.get("Placeholder", ""))

    for pwd in real_pwds:
        if isinstance(pwd, str) and pwd:
            X.append(_compute_features(pwd))
            y.append(1)
    for pwd in placeholders:
        if isinstance(pwd, str) and pwd:
            X.append(_compute_features(pwd))
            y.append(0)

    return X, y


def train_model():
    """Train a logistic regression model and print test accuracy."""
    X, y = load_training()
    if not X:
        raise RuntimeError("No training data available")

    if train_test_split is not None:
        X_train, X_test, y_train, y_test = train_test_split(
            X, y, test_size=0.2, random_state=42
        )
    else:
        X_train, X_test, y_train, y_test = _split_data(X, y, test_size=0.2)

    if LogisticRegression is not None:
        model: Any = LogisticRegression(max_iter=1000)
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        acc = accuracy_score(y_test, preds) if accuracy_score else _accuracy_score(y_test, preds)
    else:
        model = SimpleLogisticRegression()
        model.fit(X_train, y_train)
        preds = model.predict(X_test)
        acc = _accuracy_score(y_test, preds)

    print(f"Model accuracy: {acc * 100:.2f}% on held-out data")
    return model


SECRET_RE = re.compile(
    r"(?:" + "|".join(re.escape(k) for k in PRECEDING_KEYWORDS) + r")\s*[=:]\s*[\'\"]?([^\'\"\s,;]+)[\'\"]?",
    re.IGNORECASE,
)


def analyze_phrase(model: Any, phrase: str) -> None:
    """Analyze *phrase* for secrets using the trained model."""
    matches = list(SECRET_RE.finditer(phrase))


    if not matches:
        candidate = phrase.strip()
        if not candidate:
            print("No secret patterns found.")
            return
        features = _compute_features(candidate)
        pred = model.predict([features])[0]
        entropy = _shannon_entropy(candidate)
        label = "Real Secret" if pred == 1 else "Placeholder"
        print(
            "Indicator: N/A\n" f"Secret: {candidate}\n" f"Entropy: {entropy:.2f}\n" f"Prediction: {label}\n"
        )
        return


    for m in matches:
        secret = m.group(1)
        indicator_match = re.search(r"|".join(PRECEDING_KEYWORDS), m.group(0), re.IGNORECASE)
        indicator = indicator_match.group(0) if indicator_match else ""
        features = _compute_features(secret)
        pred = model.predict([features])[0]
        entropy = _shannon_entropy(secret)
        label = "Real Secret" if pred == 1 else "Placeholder"

        print(
            f"Indicator: {indicator}\nSecret: {secret}\nEntropy: {entropy:.2f}\nPrediction: {label}\n"
        )



def main() -> None:
    model = train_model()
    print("Enter a phrase to analyze (empty line to quit):")
    while True:
        try:
            phrase = input("> ")
        except EOFError:
            break
        if not phrase:
            break
        analyze_phrase(model, phrase)


if __name__ == "__main__":
    main()
