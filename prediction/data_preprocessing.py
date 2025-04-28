import datetime
import json

import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from typing import Tuple, Dict, Any, List
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

class UFCFightsPreprocessor:
    """
    Preprocessing fight data for training model
    Handles missing values, date columns and feature engineering
    """
    
    def __init__(self, fights_path: str = 'fights.csv', fighters_path: str = 'fighters.csv', output_dir: str = 'data/processed'):
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

        self.output_dir = output_dir
        self.output_file = 'processed_fights_features.csv'
        self.output_df = pd.DataFrame()

    def load_data(self) -> pd.DataFrame:
        """
        Load the data from the CSV files
        """
        logger.info("Loading data...")

        fights_df = pd.read_csv(self.fights_path)

        return fights_df

    def _save_data(self, target_df: pd.Series) -> None:
        """
        Save the data to the CSV file
        """
        logger.info("Saving processed data...")
        
        save_path = self.output_dir
        
        # create the directory
        os.makedirs(save_path, exist_ok=True)
            
        # define file paths
        features_file = os.path.join(save_path, self.output_file)
        target_file = os.path.join(save_path, 'processed_fights_target.csv')
        
        # save dataframe to csv
        self.output_df.to_csv(features_file, index=False)
        
        # save target to csv
        target_df = pd.DataFrame({'result': target_df})
        target_df.to_csv(target_file, index=False)
        
        logger.info(f"Processed features saved to {features_file}")
        logger.info(f"Target values saved to {target_file}")

    # #             fight metadata
    #             'total_rounds',
                
    #             #red fighter
    #             'red_total_ufc_fights', 'red_wins_in_ufc', 'red_losses_in_ufc', 'red_draws_in_ufc',
    #             'red_wins_by_dec', 'red_losses_by_dec', 'red_wins_by_sub', 'red_losses_by_sub', 'red_wins_by_ko', 'red_losses_by_ko', 
    #             'red_knockdowns_landed', 'red_knockdowns_absorbed', 'red_total_strikes_landed', 'red_total_strikes_absorbed',
    #             'red_takedowns_landed', 'red_takedowns_absorbed', 'red_sub_attempts_landed', 'red_sub_attempts_absorbed', 'red_total_rounds',
    #             'red_total_time_minutes', 'red_avg_knockdowns_landed', 'red_avg_knockdowns_absorbed', 'red_avg_strikes_landed',
    #             'red_avg_strikes_absorbed', 'red_avg_takedowns_landed', 'red_avg_takedowns_absorbed','red_avg_submission_attempts_landed',
    #             'red_avg_submission_attempts_absorbed', 'red_avg_fight_time_min',

    #             'red_last_fight_days_since', 'red_last_win_days_since',

    #             #blue fighter
    #             'blue_total_ufc_fights', 'blue_wins_in_ufc', 'blue_losses_in_ufc', 'blue_draws_in_ufc',
    #             'blue_wins_by_dec', 'blue_losses_by_dec', 'blue_wins_by_sub', 'blue_losses_by_sub', 'blue_wins_by_ko', 'blue_losses_by_ko', 
    #             'blue_knockdowns_landed', 'blue_knockdowns_absorbed', 'blue_total_strikes_landed', 'blue_total_strikes_absorbed',
    #             'blue_significant_strikes_landed', 'blue_significant_strikes_absorbed', 'blue_takedowns_landed',
    #             'blue_takedowns_absorbed', 'blue_sub_attempts_landed', 'blue_sub_attempts_absorbed', 'blue_total_rounds',
    #             'blue_total_time_minutes', 'blue_avg_knockdowns_landed', 'blue_avg_knockdowns_absorbed', 'blue_avg_strikes_landed',
    #             'blue_avg_strikes_absorbed', 'blue_avg_takedowns_landed', 'blue_avg_takedowns_absorbed', 'blue_avg_submission_attempts_landed',
    #             'blue_avg_submission_attempts_absorbed', 'blue_avg_fight_time_min',

    #             'blue_last_fight_days_since', 'blue_last_win_days_since',

    def calculate_days_since(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate days since last fight and last win and handles date columns
        
        Args:
            df: Input DataFrame with date columns
            
        Returns:
            DataFrame with days since columns
        """
        logger.info("Calculating days since last fight and last win...")
        
        df_processed = df.copy()

        df_processed['event_date'] = pd.to_datetime(df_processed['event_date'])

        date_columns = [
            'career_red_last_fight_date', 'career_blue_last_fight_date', 'career_red_last_win_date', 'career_blue_last_win_date', 'event_date'
        ]

        for col in date_columns:
            if col in df_processed.columns:
                df_processed[col] = pd.to_datetime(df_processed[col], errors='coerce')

        for col in ['career_red_last_fight_date', 'career_blue_last_fight_date', 'career_red_last_win_date', 'career_blue_last_win_date']:
            if col in df_processed.columns:
                days_since_col = col.replace('date', 'days_since')
                df_processed[days_since_col] = (df_processed['event_date'] - df_processed[col]).dt.days
                df_processed[days_since_col] = df_processed[days_since_col].apply(lambda x: np.nan if pd.isna(x) or x < 0 else x)

        return df_processed

    def handle_time_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Handle time columns in the dataset by converting mm:ss format to seconds

        Args:
            df: Input DataFrame
            
        Returns:
            DataFrame with handled time columns
        """
        logger.info("Handling time columns...")
        
        df_processed = df.copy()
        
        time_columns = [
            'time', 'red_control_time', 'blue_control_time',
            'red_control_time_rd1', 'red_control_time_rd2', 'red_control_time_rd3', 'red_control_time_rd4', 'red_control_time_rd5',
            'blue_control_time_rd1', 'blue_control_time_rd2', 'blue_control_time_rd3', 'blue_control_time_rd4', 'blue_control_time_rd5'
        ]
        
        def convert_time_to_seconds(time_str):
            """Convert time string in mm:ss format to seconds"""
            if pd.isna(time_str) or time_str == "UNKNOWN":
                return np.nan
            
            try:
                if ':' in str(time_str):
                    minutes, seconds = map(int, str(time_str).split(':'))
                    return minutes * 60 + seconds
                else:
                    return float(time_str)
            except (ValueError, TypeError):
                return 0
        
        for col in time_columns:
            if col in df_processed.columns:
                df_processed[col] = df_processed[col].apply(convert_time_to_seconds)

        return df_processed
    
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
        numeric_imputer = SimpleImputer(strategy='constant', fill_value=0)
        categorical_imputer = SimpleImputer(strategy='constant', fill_value='UNKNOWN')
        
        # separate numeric and categorical columns
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
        categorical_columns = df.select_dtypes(include=['object']).columns
        
        # exclude round-specific columns from imputation
        round_columns = [col for col in numeric_columns if any(f'_rd{round_num}' in col for round_num in range(1, 6))]
        non_round_numeric_columns = [col for col in numeric_columns if col not in round_columns]
        
        # apply imputers only to non-round-specific columns
        if len(non_round_numeric_columns) > 0:
            df[non_round_numeric_columns] = numeric_imputer.fit_transform(df[non_round_numeric_columns])
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
        
        for col in round_columns:
            if col not in df_processed.columns:
                df_processed[col] = np.nan

        for idx, row in df_processed.iterrows():
            rounds_fought = int(row['round']) if not pd.isna(row['round']) else 0

            # NaN for all rounds after the last round
            for round_num in range(rounds_fought + 1, 6):
                round_features = [col for col in df_processed.columns if f'_rd{round_num}' in col]
                if len(round_features) > 0:
                    df_processed.loc[idx, round_features] = np.nan

        return df_processed
    
    def copy_fighter_stats(self, target_df: pd.DataFrame, fights_df: pd.DataFrame) -> pd.DataFrame:
        """
        Copy fighter stats from fights_df to target_df
        """
        logger.info("Copying fighter stats...")

        columns = [
                '_total_ufc_fights', '_wins_in_ufc', '_losses_in_ufc', '_draws_in_ufc',
                '_wins_by_dec', '_losses_by_dec', '_wins_by_sub', '_losses_by_sub', '_wins_by_ko', '_losses_by_ko', 
                '_knockdowns_landed', '_knockdowns_absorbed', '_strikes_landed', '_strikes_absorbed',
                '_takedowns_landed', '_takedowns_absorbed', '_sub_attempts_landed', '_sub_attempts_absorbed', '_total_rounds',
                '_total_time_minutes', '_avg_knockdowns_landed', '_avg_knockdowns_absorbed', '_avg_strikes_landed',
                '_avg_strikes_absorbed', '_avg_takedowns_landed', '_avg_takedowns_absorbed','_avg_submission_attempts_landed',
                '_avg_submission_attempts_absorbed', '_avg_fight_time_min', '_last_fight_days_since'
            ]

        for corner in ['red', 'blue']:
            for col in columns:
                target_df[f'{corner}{col}'] = fights_df[f'career_{corner}{col}']

        return target_df

    def get_all_fight_ids(self, fight_df: pd.DataFrame) -> Dict[str, List[Tuple[str, str, datetime.datetime]]]:
        """
        Saves all fight ids for each fighter

        Returns:
            Dictionary with fighter id, List of Tuples (fight_id, corner (red/blue), event date)
        """

        fighter_history = {}

        fight_df['event_date'] = pd.to_datetime(fight_df['event_date'])

        for idx, row in fight_df.iterrows():
            fight_id = row['fight_id']
            fight_date = row['event_date']

            red_fighter = row['red_fighter_id']
            if red_fighter not in fighter_history:
                fighter_history[red_fighter] = []
            fighter_history[red_fighter].append((fight_id, 'red', fight_date))

            blue_fighter = row['blue_fighter_id']
            if blue_fighter not in fighter_history:
                fighter_history[blue_fighter] = []
            fighter_history[blue_fighter].append((fight_id, 'blue', fight_date))

        # for saving to json output
        # with open('data/fighter_histories.json', 'w') as f:
        #     json_history = {
        #         fighter_id: [(fid, corner, date.strftime('%Y-%m-%d'))
        #                      for fid, corner, date in history]
        #         for fighter_id, history in fighter_history.items()
        #     }
        #     json.dump(json_history, f)

        return fighter_history
    
    def calculate_career_stats(self, target_df: pd.DataFrame, fight_df: pd.DataFrame) -> pd.DataFrame:
        """
        Calculate per minute and per round career stats
        """

        logger.info("Calculating fighter career stats...")

        columns = [
            'knockdowns_landed', 'knockdowns_absorbed', 'strikes_landed', 'strikes_absorbed',
            'takedowns_landed', 'takedowns_absorbed', 'sub_attempts_landed', 'sub_attempts_absorbed',
        ]

        for corner in ['red', 'blue']:
            for col in columns:
                target_df[f'{corner}_{col}_per_minute'] = fight_df[f'career_{corner}_{col}'] / fight_df[f'career_{corner}_total_time_minutes'].where(fight_df[f'career_{corner}_total_time_minutes'] > 0, 1)
                target_df[f'{corner}_{col}_per_round'] = fight_df[f'career_{corner}_{col}'] / fight_df[f'career_{corner}_total_rounds'].where(fight_df[f'career_{corner}_total_rounds'] > 0, 1)

            # target_df[f'{corner}_striking_accuracy'] = fight_df[f'career_{corner}_strikes_landed'] / fight_df[f'career_{corner}_strikes_thrown'].where(fight_df[f'career_{corner}_strikes_thrown'] > 0, 1)

        return target_df

    def engineer_features(self, target_df: pd.DataFrame , fights_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create new features for prediction
        
        Args:
            df: DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        logger.info("Engineering new features...")

        # calculate experience difference
        target_df['experience_diff'] = fights_df['career_red_total_ufc_fights'] - fights_df['career_blue_total_ufc_fights']
        
        # calculate striking efficiency
        target_df['red_strike_efficiency'] = fights_df['red_sig_strikes_landed'] / fights_df['red_sig_strikes_thrown'].where(fights_df['red_sig_strikes_thrown'] > 0, 1)
        target_df['blue_strike_efficiency'] = fights_df['blue_sig_strikes_landed'] / fights_df['blue_sig_strikes_thrown'].where(fights_df['blue_sig_strikes_thrown'] > 0, 1)
        
        # calculate takedown efficiency
        target_df['red_takedown_efficiency'] = fights_df['red_takedowns_landed'] / fights_df['red_takedowns_attempted'].where(fights_df['red_takedowns_attempted'] > 0, 1)
        target_df['blue_takedown_efficiency'] = fights_df['blue_takedowns_landed'] / fights_df['blue_takedowns_attempted'].where(fights_df['blue_takedowns_attempted'] > 0, 1)
        
        # calculate win rate differences
        target_df['win_rate_diff'] = (fights_df['career_red_wins_in_ufc'] / fights_df['career_red_total_ufc_fights'].where(fights_df['career_red_total_ufc_fights'] > 0, 1)) - \
                             (fights_df['career_blue_wins_in_ufc'] / fights_df['career_blue_total_ufc_fights'].where(fights_df['career_blue_total_ufc_fights'] > 0, 1))
        
        return target_df
    
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
            'location',
            'win_method',
            'referee'
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
        exclude_columns = ['fight_id', 'event_date', 'red_fighter_id', 'blue_fighter_id', 'result']
        
        # get numerical columns
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
        numeric_columns = [col for col in numeric_columns if col not in exclude_columns]
        
        # identify round-specific columns
        round_columns = [col for col in numeric_columns if any(f'_rd{round_num}' in col for round_num in range(1, 6))]
        non_round_numeric_columns = [col for col in numeric_columns if col not in round_columns]
        
        # scale non-round-specific features
        if len(non_round_numeric_columns) > 0:
            scaler = StandardScaler()
            df[non_round_numeric_columns] = scaler.fit_transform(df[non_round_numeric_columns])
            self.scalers['numeric'] = scaler
        
        # scale round-specific features separately for each round
        for round_num in range(1, 6):
            round_cols = [col for col in round_columns if f'_rd{round_num}' in col]
            if len(round_cols) > 0:
                round_mask = df['round'] >= round_num
                
                # only scale features for rounds that occurred
                if round_mask.any():
                    scaler = StandardScaler()
                    temp_df = df.loc[round_mask, round_cols].copy()
                    df.loc[round_mask, round_cols] = scaler.fit_transform(temp_df)
                    self.scalers[f'round_{round_num}'] = scaler
        
        return df
    
    def mirror_data(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Mirror the data to create a balanced dataset
        """
        logger.info("Mirroring data...")
        
        # create a copy of the dataframe to avoid modifying the original
        df_processed = df.copy()
        
        red_columns = [col for col in df_processed.columns if 'red' in col]
        blue_columns = [col for col in df_processed.columns if 'blue' in col]

        red_to_blue = {col: col.replace('red', 'blue') for col in red_columns}
        blue_to_red = {col: col.replace('blue', 'red') for col in blue_columns}

        swapped_df = df_processed.rename(columns={**red_to_blue, **blue_to_red})

        swapped_df['experience_diff'] = swapped_df['experience_diff'] * -1
        swapped_df['win_rate_diff'] = swapped_df['win_rate_diff'] * -1

        if 'result' in df_processed.columns:
            swapped_df['result'] = swapped_df['result'].map({"red": "blue", "blue": "red", "draw": "draw"})
        
        # combine original and mirrored data
        combined_df = pd.concat([df_processed, swapped_df], ignore_index=True)
        
        return combined_df
    
    def prepare_data(self) -> Tuple[pd.DataFrame, pd.Series, Dict[str, Any]]:
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

        #preprocess fights dataframe first
        fights_df = self.handle_missing_values(fights_df)
        fights_df = self.calculate_days_since(fights_df)
        fights_df = self.handle_time_columns(fights_df)

        # get all fight ids for each fighter
        fighter_history = self.get_all_fight_ids(fights_df)

        self.output_df = pd.DataFrame({'total_rounds': fights_df['total_rounds']})
        
        self.output_df = self.copy_fighter_stats(self.output_df, fights_df)
        self.output_df = self.calculate_career_stats(self.output_df, fights_df)
        self.output_df = self.engineer_features(self.output_df, fights_df)
        
        # # handle round data first to avoid issues with missing values
        # fights_df = self.handle_round_data(fights_df)
        
        # # apply preprocessing steps
        # fights_df = self.engineer_features(fights_df)

        # mirror data
        # fights_df = self.mirror_data(fights_df)

        # fights_df = self.encode_categorical(fights_df)
        # fights_df = self.scale_features(fights_df)
        # fights_df = self.remove_bias(fights_df)

        target = fights_df['result'].copy()
        
        if 'result' in fights_df.columns:
            fights_df = fights_df.drop(columns=['result'])

        self._save_data(target)
        
        le = LabelEncoder()
        target = pd.Series(le.fit_transform(target.astype(str)), index=target.index)
        self.label_encoders['result'] = le
        
        # create preprocessing artifacts dictionary
        artifacts = {
            'label_encoders': self.label_encoders,
            'scalers': self.scalers
        }
        
        logger.info("Data preparation completed successfully")
        
        return fights_df, target, artifacts
        

def main():
    """
    Main function to demonstrate the usage of the UFCDataPreprocessor.
    """
    preprocessor = UFCFightsPreprocessor(output_dir='data/processed')
    
    try:
        # prepare data
        features_df, target, artifacts = preprocessor.prepare_data()
        
        logger.info("Data preprocessing completed successfully")
        
    except Exception as e:
        logger.error(f"Error during data preprocessing: {str(e)}")
        raise

if __name__ == "__main__":
    main()
