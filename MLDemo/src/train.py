import numpy as np
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier
import joblib

def train_model(X, y):
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42)
    model = RandomForestClassifier(n_estimators=100, random_state=42)
    model.fit(X_train, y_train)
    score = model.score(X_test, y_test)
    print(f"Test accuracy: {score:.4f}")
    return model

if __name__ == "__main__":
    from sklearn.datasets import load_iris
    data = load_iris()
    model = train_model(data.data, data.target)
    joblib.dump(model, "../models/model.pkl")
