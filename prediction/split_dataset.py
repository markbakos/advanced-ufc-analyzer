import pandas as pd
import numpy as np
from sklearn.model_selection import train_test_split

def split_data(features_path: str = './processed_fights_features.csv', target_path: str = './processed_fights_target.csv'):
    features_df = pd.read_csv(features_path)
    target_df = pd.read_csv(target_path)
    target = target_df['result'].values

    n_features = features_df.shape[1]
    n_classes = 3
    
    total_samples = len(features_df)
    half_samples = total_samples // 2 + 1
    
    original_indices = np.arange(0, half_samples - 1)
    mirrored_indices = np.arange(half_samples - 1, total_samples)

    print(len(original_indices))
    print(features_df.iloc[original_indices])
    print(len(mirrored_indices))
    print(features_df.iloc[mirrored_indices])

    train_indices, temp_indices = train_test_split(
        original_indices,
        test_size=0.3,
        random_state=42,
        stratify=target_df[original_indices] if len(original_indices) == len(target) else None
    )

    print(train_indices)
    print(temp_indices)
    
if __name__ == "__main__":
    split_data()