"""Skeleton script for training a secret detection model.

The dataset in ``testing_data.csv`` contains example phrases labeled
with ``1`` for real secrets and ``0`` for placeholders. This script
illustrates how that data could be loaded and used to train a model.
Actual feature extraction and model code should be implemented later.
"""

import argparse
import pandas as pd
import joblib

# from sklearn.linear_model import LogisticRegression
# from sklearn.feature_extraction.text import TfidfVectorizer
# Additional imports (e.g. numpy) would normally go here


def load_data(path: str) -> tuple[list[str], list[int]]:
    """Load phrases and labels from a CSV file."""
    df = pd.read_csv(path)
    phrases = df["Phrase"].astype(str).tolist()
    labels = df["Label"].astype(int).tolist()
    return phrases, labels


def train_model(phrases: list[str], labels: list[int]):
    """Train the classifier on the provided data.

    This is only a placeholder. Normally you would convert ``phrases``
    to feature vectors, initialize a model such as ``LogisticRegression``
    and fit it with the training labels.
    """
    # TODO: implement feature extraction and model training
    model = None
    return model


def main() -> None:
    parser = argparse.ArgumentParser(description="Train the secret detection model")
    parser.add_argument(
        "--data", default="testing_data.csv", help="Path to the CSV training data"
    )
    parser.add_argument(
        "--output", default="secret_model.joblib", help="Where to save the trained model"
    )
    args = parser.parse_args()

    phrases, labels = load_data(args.data)
    model = train_model(phrases, labels)

    # Persist the model for later use; ``model`` may be None in this skeleton
    joblib.dump(model, args.output)
    print(f"Model placeholder saved to {args.output}")


if __name__ == "__main__":
    main()
