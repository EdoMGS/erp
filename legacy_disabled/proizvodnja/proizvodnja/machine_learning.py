import os
import pickle

# Definicija putanje do direktorija s modelima
BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODELS_DIR = os.path.join(BASE_DIR, "models")

# Učitavanje modela
classification_model_path = os.path.join(MODELS_DIR, "classification_model.pkl")
regression_model_path = os.path.join(MODELS_DIR, "regression_model.pkl")
scaler_path = os.path.join(MODELS_DIR, "scaler.pkl")

try:
    with open(classification_model_path, "rb") as file:
        classification_model = pickle.load(file)
except Exception as e:
    classification_model = None
    print(f"Error loading classification model: {e}")

try:
    with open(regression_model_path, "rb") as file:
        regression_model = pickle.load(file)
except Exception as e:
    regression_model = None
    print(f"Error loading regression model: {e}")

try:
    with open(scaler_path, "rb") as file:
        scaler = pickle.load(file)
except Exception as e:
    scaler = None
    print(f"Error loading scaler: {e}")
