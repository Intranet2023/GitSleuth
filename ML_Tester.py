import re
import pandas as pd
from sklearn.linear_model import LogisticRegression
from sklearn.model_selection import train_test_split
from sklearn.metrics import accuracy_score
from GitSleuth import _shannon_entropy, PRECEDING_KEYWORDS


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
    df = pd.read_csv("training_data.csv")
    X: list[list[float]] = []
    y: list[int] = []
    for pwd in df.get("RealPassword", []):
        if isinstance(pwd, str) and pwd:
            X.append(_compute_features(pwd))
            y.append(1)
    for pwd in df.get("Placeholder", []):
        if isinstance(pwd, str) and pwd:
            X.append(_compute_features(pwd))
            y.append(0)
    return X, y


def train_model() -> LogisticRegression:
    """Train a logistic regression model and print test accuracy."""
    X, y = load_training()
    if not X:
        raise RuntimeError("No training data available")
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = LogisticRegression(max_iter=1000)
    model.fit(X_train, y_train)
    preds = model.predict(X_test)
    acc = accuracy_score(y_test, preds)
    print(f"Model accuracy: {acc * 100:.2f}% on held-out data")
    return model


SECRET_RE = re.compile(
    r"(?:" + "|".join(re.escape(k) for k in PRECEDING_KEYWORDS) + r")\s*[=:]\s*[\'\"]?([^\'\"\s,;]+)[\'\"]?",
    re.IGNORECASE,
)


def analyze_phrase(model: LogisticRegression, phrase: str) -> None:
    """Analyze *phrase* for secrets using the trained model."""
    matches = list(SECRET_RE.finditer(phrase))
    if not matches:
        print("No secret patterns found.")
        return
    for m in matches:
        secret = m.group(1)
        indicator_match = re.search(r"|".join(PRECEDING_KEYWORDS), m.group(0), re.IGNORECASE)
        indicator = indicator_match.group(0) if indicator_match else ""
        features = _compute_features(secret)
        pred = model.predict([features])[0]
        entropy = _shannon_entropy(secret)
        label = "Real Secret" if pred == 1 else "Placeholder"
        print(f"Indicator: {indicator}\nSecret: {secret}\nEntropy: {entropy:.2f}\nPrediction: {label}\n")


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
