import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from typing import Tuple, Dict, Any
import logging

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UFCDataPreprocessor:
    """
    Preprocessing fight data for machine learning
    Handles missing values, date columns and feature engineering
    """
    
    def __init__(self, fights_path: str = 'fights.csv', fighters_path: str = 'fighters.csv'):
        """
        Initialize the preprocessor with paths to data files.
        
        Args:
            fights_path: Path to the fights CSV file
            fighters_path: Path to the fighters CSV file
        """
        self.fights_path = fights_path
        self.fighters_path = fighters_path
        self.label_encoders = {}
        self.scalers = {}

    def load_data(self) -> pd.DataFrame:
        """
        Load the data from the CSV files
        """
        logger.info("Loading data...")

        fights_df = pd.read_csv(self.fights_path)
        fighters_df = pd.read_csv(self.fighters_path)

        return fights_df
        

    def handle_date_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle date columns in the dataset
        """
        logger.info("Handling date columns...")

        date_columns = ['event_date', 'last_fight_date', 'last_win_date']
        
        for col in date_columns:
            if col in df.columns:
                df[col] = pd.to_datetime(df[col])
        
        return df
    
    def handle_missing_values(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle missing values in the dataset
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with handled missing values
        """
        logger.info("Handling missing values...")
        
        # create imputers for different types of features
        numeric_imputer = SimpleImputer(strategy='median')
        categorical_imputer = SimpleImputer(strategy='constant', fill_value='UNKNOWN')
        
        # separate numeric and categorical columns
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
        categorical_columns = df.select_dtypes(include=['object']).columns
        
        # apply imputers
        df[numeric_columns] = numeric_imputer.fit_transform(df[numeric_columns])
        df[categorical_columns] = categorical_imputer.fit_transform(df[categorical_columns])
        
        return df
    
    def handle_round_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle round-specific data by only considering rounds that were actually fought
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with properly handled round data
        """
        logger.info("Handling round-specific data...")
        
        # ensure 'round' column is numeric
        df['round'] = pd.to_numeric(df['round'], errors='coerce')
        
        # create a copy of the dataframe to avoid modifying the original
        df_processed = df.copy()
        
        # define round-specific columns
        round_columns = []
        for fighter in ['red', 'blue']:
            for round_num in range(1, 6):
                round_columns.extend([
                    f'{fighter}_knockdowns_landed_rd{round_num}',
                    f'{fighter}_sig_strikes_landed_rd{round_num}',
                    f'{fighter}_sig_strikes_thrown_rd{round_num}',
                    f'{fighter}_sig_strike_percent_rd{round_num}',
                    f'{fighter}_total_strikes_landed_rd{round_num}',
                    f'{fighter}_total_strikes_thrown_rd{round_num}',
                    f'{fighter}_takedowns_landed_rd{round_num}',
                    f'{fighter}_takedowns_attempted_rd{round_num}',
                    f'{fighter}_takedowns_percent_rd{round_num}',
                    f'{fighter}_sub_attempts_rd{round_num}',
                    f'{fighter}_reversals_rd{round_num}',
                    f'{fighter}_control_time_rd{round_num}',
                    f'{fighter}_head_strikes_landed_rd{round_num}',
                    f'{fighter}_head_strikes_thrown_rd{round_num}',
                    f'{fighter}_body_strikes_landed_rd{round_num}',
                    f'{fighter}_body_strikes_thrown_rd{round_num}',
                    f'{fighter}_leg_strikes_landed_rd{round_num}',
                    f'{fighter}_leg_strikes_thrown_rd{round_num}',
                    f'{fighter}_distance_strikes_landed_rd{round_num}',
                    f'{fighter}_distance_strikes_thrown_rd{round_num}',
                    f'{fighter}_clinch_strikes_landed_rd{round_num}',
                    f'{fighter}_clinch_strikes_thrown_rd{round_num}',
                    f'{fighter}_ground_strikes_landed_rd{round_num}',
                    f'{fighter}_ground_strikes_thrown_rd{round_num}'
                ])
        

        for idx, row in df_processed.iterrows():
            rounds_fought = int(row['round']) if not pd.isna(row['round']) else 0
            
            for round_num in range(rounds_fought + 1, 6):
                for col in round_columns:
                    if f'_rd{round_num}' in col and col in df_processed.columns:
                        df_processed.at[idx, col] = 0
        
        return df_processed
    
    def engineer_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Create new features for prediction
        
        Args:
            df: DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        logger.info("Engineering new features...")
        
        # create a copy of the dataframe to avoid modifying the original
        df_processed = df.copy()
        
        # calculate experience difference
        df_processed['experience_diff'] = df_processed['career_red_total_ufc_fights'] - df_processed['career_blue_total_ufc_fights']
        
        # calculate striking efficiency
        df_processed['red_strike_efficiency'] = df_processed['red_sig_strikes_landed'] / df_processed['red_sig_strikes_thrown'].where(df_processed['red_sig_strikes_thrown'] > 0, 1)
        df_processed['blue_strike_efficiency'] = df_processed['blue_sig_strikes_landed'] / df_processed['blue_sig_strikes_thrown'].where(df_processed['blue_sig_strikes_thrown'] > 0, 1)
        
        # calculate takedown efficiency
        df_processed['red_takedown_efficiency'] = df_processed['red_takedowns_landed'] / df_processed['red_takedowns_attempted'].where(df_processed['red_takedowns_attempted'] > 0, 1)
        df_processed['blue_takedown_efficiency'] = df_processed['blue_takedowns_landed'] / df_processed['blue_takedowns_attempted'].where(df_processed['blue_takedowns_attempted'] > 0, 1)
        
        # calculate win rate differences
        df_processed['win_rate_diff'] = (df_processed['career_red_wins_in_ufc'] / df_processed['career_red_total_ufc_fights'].where(df_processed['career_red_total_ufc_fights'] > 0, 1)) - \
                             (df_processed['career_blue_wins_in_ufc'] / df_processed['career_blue_total_ufc_fights'].where(df_processed['career_blue_total_ufc_fights'] > 0, 1))
        
        # calculate round-specific efficiencies
        for fighter in ['red', 'blue']:
            for round_num in range(1, 6):
                if f'{fighter}_sig_strikes_thrown_rd{round_num}' in df_processed.columns:
                    df_processed[f'{fighter}_strike_efficiency_rd{round_num}'] = df_processed[f'{fighter}_sig_strikes_landed_rd{round_num}'] / \
                        df_processed[f'{fighter}_sig_strikes_thrown_rd{round_num}'].where(df_processed[f'{fighter}_sig_strikes_thrown_rd{round_num}'] > 0, 1)
                
                if f'{fighter}_takedowns_attempted_rd{round_num}' in df_processed.columns:
                    df_processed[f'{fighter}_takedown_efficiency_rd{round_num}'] = df_processed[f'{fighter}_takedowns_landed_rd{round_num}'] / \
                        df_processed[f'{fighter}_takedowns_attempted_rd{round_num}'].where(df_processed[f'{fighter}_takedowns_attempted_rd{round_num}'] > 0, 1)
        
        return df_processed
    
    def encode_categorical(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Encode categorical variables using label encoding
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with encoded categorical variables
        """
        logger.info("Encoding categorical variables...")
        
        categorical_columns = [
            'win_method',
            'referee',
            'result'
        ]
        
        for col in categorical_columns:
            if col in df.columns:
                le = LabelEncoder()
                df[col] = le.fit_transform(df[col].astype(str))
                self.label_encoders[col] = le
        
        return df
    
    def scale_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Scale numerical features using StandardScaler
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with scaled features
        """
        logger.info("Scaling numerical features...")
        
        # columns to exclude from scaling
        exclude_columns = ['fight_id', 'event_date', 'red_fighter_id', 'blue_fighter_id']
        
        # get numerical columns
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
        numeric_columns = [col for col in numeric_columns if col not in exclude_columns]
        
        # scale features
        scaler = StandardScaler()
        df[numeric_columns] = scaler.fit_transform(df[numeric_columns])
        self.scalers['numeric'] = scaler
        
        return df
    
    def remove_bias(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        remove sources of bias from the dataset
        
        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with reduced bias
        """
        logger.info("Removing potential sources of bias...")
        
        # remove info that shouldn't affect outcome
        bias_columns = [
            'event_name',
            'event_date'
        ]
        
        df = df.drop(columns=[col for col in bias_columns if col in df.columns])
        
        return df
    
    def prepare_data(self) -> Tuple[pd.DataFrame, Dict[str, Any]]:
        """
        Prepare the data applying every preprocessing step.
        
        Returns:
            Tuple containing:
                - Preprocessed DataFrame
                - Dictionary containing preprocessing artifacts (encoders, scalers)
        """
        logger.info("Starting data preparation...")
        
        # load data
        fights_df = self.load_data()

        fights_df = self.handle_round_data(fights_df)
        
        # apply preprocessing steps
        fights_df = self.handle_missing_values(fights_df)
        fights_df = self.handle_date_columns(fights_df)
        fights_df = self.engineer_features(fights_df)
        fights_df = self.encode_categorical(fights_df)
        fights_df = self.scale_features(fights_df)
        fights_df = self.remove_bias(fights_df)
        
        # create preprocessing artifacts dictionary
        artifacts = {
            'label_encoders': self.label_encoders,
            'scalers': self.scalers
        }
        
        logger.info("Data preparation completed successfully")
        
        return fights_df, artifacts

def main():
    """
    Main function to demonstrate the usage of the UFCDataPreprocessor.
    """
    preprocessor = UFCDataPreprocessor()
    
    try:
        # prepare data
        processed_df, artifacts = preprocessor.prepare_data()
        
        # save processed data
        processed_df.to_csv('processed_fights.csv', index=False)
        logger.info("Processed data saved to 'processed_fights.csv'")
        
    except Exception as e:
        logger.error(f"Error during data preprocessing: {str(e)}")
        raise

if __name__ == "__main__":
    main()
