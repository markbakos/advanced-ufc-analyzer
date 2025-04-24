import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def split_data(features_path: str = './processed_fights_features.csv', target_path: str = './processed_fights_target.csv'):
    features_df = pd.read_csv(features_path)
    target_df = pd.read_csv(target_path)
    target = target_df['result'].values
    
    total_samples = len(features_df)
    half_samples = total_samples // 2
    
    original_indices = np.arange(0, half_samples)
    mirrored_indices = np.arange(half_samples, total_samples)

    train_indices, temp_indices = train_test_split(
        original_indices,
        test_size=0.3,
        random_state=42,
        stratify=target_df[original_indices] if len(original_indices) == len(target) else None
    )

    val_indices, test_indices = train_test_split(
        temp_indices,
        test_size=0.5,
        random_state=42,
        stratify=target_df[temp_indices] if len(temp_indices) == len(target) else None
    )

    mirrored_train_indices = train_indices + half_samples
    mirrored_val_indices = val_indices + half_samples
    mirrored_test_indices = test_indices + half_samples
    
    final_train_indices = np.concatenate((train_indices, mirrored_train_indices))
    final_val_indices = np.concatenate((val_indices, mirrored_val_indices))
    final_test_indices = np.concatenate((test_indices, mirrored_test_indices))

    return {
        'final_train_indices': final_train_indices,
        'final_val_indices': final_val_indices,
        'final_test_indices': final_test_indices
    }

if __name__ == "__main__":
    data_split_indices = split_data()