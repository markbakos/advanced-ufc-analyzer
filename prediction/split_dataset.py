import pandas as pd
import numpy as np
import os
from sklearn.model_selection import train_test_split

class DataSplit:
    """
    Class to split the dataset into train, validation and test sets
    """
    def __init__(self, features_path: str = './data/processed/processed_fights_features.csv', target_path: str = './data/processed/processed_fights_target.csv'):
        """
        Initialize the DataSplit class
        """
        self.features_path = features_path
        self.target_path = target_path
        self.features_df = pd.read_csv(features_path)
        self.target_df = pd.read_csv(target_path)
        self.target = self.target_df['result'].values

    def split_data(self):
        """
        Split the dataset into train, validation and test indices
        """
        total_samples = len(self.features_df)

        original_indices = np.arange(0, total_samples)

        train_indices, temp_indices = train_test_split(
            original_indices,
            test_size=0.3,
            random_state=42,
            stratify=self.target[original_indices] if len(original_indices) == len(self.target) else None
        )

        val_indices, test_indices = train_test_split(
            temp_indices,
            test_size=0.5,
            random_state=42,
            stratify=self.target[temp_indices] if len(temp_indices) == len(self.target) else None
        )

        return {
            'final_train_indices': train_indices,
            'final_val_indices': val_indices,
            'final_test_indices': test_indices
        }

    def save_data_split(self, data_split_indices: dict):
        """
        Save the train, validation and test sets to csv files from indices
        """
        output_dir = 'data/splits'
        os.makedirs(output_dir, exist_ok=True)    

        self.features_df.iloc[data_split_indices['final_train_indices']].to_csv(f'{output_dir}/train_features.csv', index=False)
        self.target_df.iloc[data_split_indices['final_train_indices']].to_csv(f'{output_dir}/train_target.csv', index=False)

        self.features_df.iloc[data_split_indices['final_val_indices']].to_csv(f'{output_dir}/val_features.csv', index=False)
        self.target_df.iloc[data_split_indices['final_val_indices']].to_csv(f'{output_dir}/val_target.csv', index=False)

        self.features_df.iloc[data_split_indices['final_test_indices']].to_csv(f'{output_dir}/test_features.csv', index=False)
        self.target_df.iloc[data_split_indices['final_test_indices']].to_csv(f'{output_dir}/test_target.csv', index=False)
            

if __name__ == "__main__":
    data_split = DataSplit()
    data_split_indices = data_split.split_data()
    data_split.save_data_split(data_split_indices)