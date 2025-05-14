import os
import pandas as pd
import joblib

class UFCPredictor:
    def __init__(self, model_dir = "models/", data_dir = "data/processed/"):
        """
        Initialize the UFCPredictor
        """
        self.model = None
        self.model_dir = model_dir
        self.data_dir = data_dir

    def load_model(self):
        """
        Load the pre-trained model from the specified directory.
        """
        try:
            model_path = os.path.join(self.model_dir, "model.keras")
            return joblib.load(model_path)
        except FileNotFoundError:
            print(f"Model file not found at {model_path}")
            raise FileNotFoundError

    def load_fighter_data(self):
        """
        Load the processed fighter data used for training.
        """
        try:
            return pd.read_csv(os.path.join(self.data_dir, "processed_fighters.csv"))
        except FileNotFoundError:
            print(f"Fighter data file not found at {self.data_dir}/processed_fighters.csv")
            raise FileNotFoundError
