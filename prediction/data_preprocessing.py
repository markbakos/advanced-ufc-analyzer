import datetime
import json
from engineer_features import engineer_features
import pandas as pd
import numpy as np
from sklearn.preprocessing import StandardScaler, LabelEncoder
from sklearn.impute import SimpleImputer
from typing import Tuple, Dict, Any, List
import logging
import os

logging.basicConfig(level=logging.INFO, format='%(asctime)s - '
                                               '%(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

TEST_RUN = False

class UFCFightsPreprocessor:
    """
    Preprocessing fight data for training model
    Handles missing values, date columns and feature engineering
    """
    
    def __init__(self, fights_path: str = '../scraper/fights/spiders/fights.csv',
                 fighters_path: str = 'fighters.csv',
                 output_dir: str = 'data/processed'):
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

        self.fight_history = {}

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

        # ensure target_df is dataframe and convert to frame
        if isinstance(target_df, pd.Series):
            target_df = target_df.to_frame()

        # save target to csv
        target_df.to_csv(target_file, index=False)
        
        logger.info(f"Processed features saved to {features_file}")
        logger.info(f"Target values saved to {target_file}")

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
            'career_red_last_fight_date', 'career_blue_last_fight_date',
            'career_red_last_win_date', 'career_blue_last_win_date', 'event_date',
            'career_red_date_of_birth', 'career_blue_date_of_birth',
        ]

        for col in date_columns:
            if col in df_processed.columns:
                df_processed[col] = pd.to_datetime(df_processed[col], errors='coerce')

        for col in ['career_red_last_fight_date', 'career_blue_last_fight_date',
                    'career_red_last_win_date', 'career_blue_last_win_date']:
            if col in df_processed.columns:
                days_since_col = col.replace('date', 'days_since')
                df_processed[days_since_col] = (df_processed['event_date'] - df_processed[col]).dt.days
                df_processed[days_since_col] = df_processed[days_since_col].apply(lambda x: np.nan if pd.isna(x) or x < 0 else x)

        for col in ['career_red_date_of_birth', 'career_blue_date_of_birth']:
            if col in df_processed.columns:
                age_col = col.replace('date_of_birth', 'age_in_days')
                df_processed[age_col] = (df_processed['event_date'] - df_processed[col]).dt.days
                df_processed[age_col] = df_processed[age_col].apply(lambda x: np.nan if pd.isna(x) or x < 0 else x)

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
            'red_control_time_rd1', 'red_control_time_rd2',
            'red_control_time_rd3', 'red_control_time_rd4',
            'red_control_time_rd5',

            'blue_control_time_rd1', 'blue_control_time_rd2',
            'blue_control_time_rd3', 'blue_control_time_rd4',
            'blue_control_time_rd5'
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

    def remove_unneeded_rows(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Remove UNKNOWN (NC / Unknown) and Draw result fights
        """

        logger.info("Removing unneeded fights")

        df_processed = df.copy()

        df_processed = df_processed[~df_processed['result'].isin(['draw', 'unknown'])]

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
    
    def copy_fighter_stats(self, target_df: pd.DataFrame, fights_df: pd.DataFrame) -> pd.DataFrame:
        """
        Copy fighter stats from fights_df to target_df
        """
        logger.info("Copying fighter stats...")

        columns = [
                '_total_ufc_fights', '_wins_in_ufc', '_losses_in_ufc', '_draws_in_ufc',
                '_wins_by_dec', '_losses_by_dec', '_wins_by_sub', '_losses_by_sub',
                '_wins_by_ko', '_losses_by_ko',  '_knockdowns_landed',
                '_knockdowns_absorbed', '_strikes_landed', '_strikes_absorbed',
                '_takedowns_landed', '_takedowns_absorbed',
                '_sub_attempts_landed', '_sub_attempts_absorbed', '_total_rounds',
                '_total_time_minutes', '_avg_knockdowns_landed',
                '_avg_knockdowns_absorbed', '_avg_strikes_landed',
                '_avg_strikes_absorbed', '_avg_takedowns_landed',
                '_avg_takedowns_absorbed','_avg_submission_attempts_landed',
                '_avg_submission_attempts_absorbed', '_avg_fight_time_min',
                '_last_fight_days_since',

                '_height_cm', '_weight_kg', '_reach_cm', '_stance', '_age_in_days'
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

    def _get_fights_date_limited(self, fighter_id: str, date_limit: datetime.datetime) -> List[Tuple[str, str]]:
        """
        Get all fight ids for fighter limited with max date

        :param fighter_id: Fighter ID to get fights for
        :param date_limit: Maximum date to limit the fights (Date NOT included)
        :return: List of Tuples (fight_id, corner)
        """
        if fighter_id not in self.fight_history:
            return []

        fights = self.fight_history[fighter_id]

        return [(fid, corner) for fid, corner, date in fights if date < date_limit]

    def get_all_strike_data(self, target_df: pd.DataFrame, fight_df: pd.DataFrame) -> pd.DataFrame:
        """
        Updates dataframe with all strike data for all fights
        """
        logger.info("Getting all strike data...")

        if len(target_df) != len(fight_df):
            logger.warning("Target dataframe length doesn't match fight dataframe length, adjusting...")
            target_df = target_df.reindex(fight_df.index)

        strike_columns = {
            'head_strikes_landed': 0,
            'head_strikes_thrown': 0,
            'body_strikes_landed': 0,
            'body_strikes_thrown': 0,
            'leg_strikes_landed': 0,
            'leg_strikes_thrown': 0,
            'distance_strikes_landed': 0,
            'distance_strikes_thrown': 0,
            'clinch_strikes_landed': 0,
            'clinch_strikes_thrown': 0,
            'ground_strikes_landed': 0,
            'ground_strikes_thrown': 0,
        }

        opponent_corner = {
            'red': 'blue',
            'blue': 'red'
        }

        # pre initialize all columns in target_df
        for corner in ['red', 'blue']:
            for column in strike_columns:
                target_df[f'{corner}_{column}'] = 0
            for column in strike_columns:
                target_df[f'{corner}_{column}_opponent'] = 0

        for idx, fight in fight_df.iterrows():

            # test:
            # if fight['fight_id'] == "d3be5a4e0ec273e2":
            #     print("True" if fight['red_fighter_id'] == "cbf5e6f231b55443" else "False")

            fight_date = pd.to_datetime(fight['event_date'])

            # get all previous fights for both fighter
            red_fights = self._get_fights_date_limited(fight['red_fighter_id'], fight_date)
            blue_fights = self._get_fights_date_limited(fight['blue_fighter_id'], fight_date)

            # initialize red and blue fighters columns
            red_fighter_stats = {column: 0 for column in strike_columns}
            red_fighter_stats.update({f"{column}_opponent": 0 for column in strike_columns})

            blue_fighter_stats = {column: 0 for column in strike_columns}
            blue_fighter_stats.update({f"{column}_opponent": 0 for column in strike_columns})

            # get all strikes for red fighter using previous red_fights
            for fight_id, corner in red_fights:
                try:
                    fight_row = fight_df.loc[fight_df['fight_id'] == fight_id]
                    if not fight_row.empty:
                        for column in strike_columns:
                            if f'{corner}_{column}' in fight_row.columns:
                                value = fight_row[f'{corner}_{column}'].values[0]
                                if pd.notna(value):
                                    red_fighter_stats[column] += value

                        for column in strike_columns:
                            if f'{opponent_corner[corner]}_{column}' in fight_row.columns:
                                value = fight_row[f'{opponent_corner[corner]}_{column}'].values[0]
                                if pd.notna(value):
                                    red_fighter_stats[f'{column}_opponent'] += value
                except Exception as e:
                    logger.error(f"Error processing red fighter's previous fight {fight_id}: {e}")

            for fight_id, corner in blue_fights:
                try:
                    fight_row = fight_df.loc[fight_df['fight_id'] == fight_id]
                    if not fight_row.empty:
                        for column in strike_columns:
                            if f'{corner}_{column}' in fight_row.columns:
                                value = fight_row[f'{corner}_{column}'].values[0]
                                if pd.notna(value):
                                    blue_fighter_stats[column] += value

                        for column in strike_columns:
                            if f'{opponent_corner[corner]}_{column}' in fight_row.columns:
                                value = fight_row[f'{opponent_corner[corner]}_{column}'].values[0]
                                if pd.notna(value):
                                    blue_fighter_stats[f'{column}_opponent'] += value
                except Exception as e:
                    logger.error(f"Error processing blue fighter's previous fight {fight_id}: {e}")

            # save data in results dict
            for column in strike_columns:
                target_df.loc[idx, f'red_{column}'] = red_fighter_stats[column]

            for column in strike_columns:
                target_df.loc[idx, f'red_{column}_opponent'] = red_fighter_stats[f'{column}_opponent']

            for column in strike_columns:
                target_df.loc[idx, f'blue_{column}'] = blue_fighter_stats[column]

            for column in strike_columns:
                target_df.loc[idx, f'blue_{column}_opponent'] = blue_fighter_stats[f'{column}_opponent']

            #
            # if fight['fight_id'] == "d3be5a4e0ec273e2":
            #     print(f"Red fighter: {red_fighter_strikes}")
            #     print(f"Blue fighter: {blue_fighter_strikes}")

            if idx % 100 == 0 and idx > 0:
                logger.info(f"Processed {idx} fights...")
                if TEST_RUN:
                    break

        # final check for nan values and replace with 0
        strike_related_columns = [col for col in target_df.columns if any(x in col for x in strike_columns.keys())]
        target_df[strike_related_columns] = target_df[strike_related_columns].fillna(0)

        return target_df
    
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

        return target_df

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

        columns = {
            'experience_diff', 'win_rate_diff', 'takedown_diff', 'total_strike_diff',
            'total_strike_diff_per_round', 'total_strike_diff_per_minute',
            'total_head_strike_diff', 'total_body_strike_diff',
            'total_leg_strike_diff', 'distance_strike_diff', 'clinch_strike_diff',
            'ground_strike_diff', 'head_accuracy_diff', 'body_accuracy_diff',
            'leg_accuracy_diff', 'distance_accuracy_diff', 'clinch_accuracy_diff',
            'ground_accuracy_diff', 'strike_efficiency_diff', 'finish_rate_diff',
            'ko_rate_diff', 'sub_rate_diff', 'decision_rate_diff', 'strike_volume_diff',
            'sub_attempt_frequency_diff', 'striking_preference_diff',
            'grappling_preference_diff', 'ground_preference_diff',
            'distance_preference_diff', 'knockdown_ratio_diff',
            'damage_efficiency_diff', 'head_strike_damage_ratio_diff',
            'avg_fight_length_diff', 'fight_pace_diff', 'head_strike_defense_diff',
            'body_strike_defense_diff', 'leg_strike_defense_diff',
            'overall_striking_effectiveness_diff', 'overall_grappling_effectiveness_diff',
            'durability_diff',
        }

        for col in columns:
            if col in swapped_df.columns:
                swapped_df[col] = swapped_df[col] * -1

        if 'result' in df_processed.columns:
            swapped_df['result'] = swapped_df['result'].map({"red": "blue", "blue": "red"})

        # combine original and mirrored data
        combined_df = pd.concat([df_processed, swapped_df], ignore_index=True)

        return combined_df

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
        exclude_columns = ['total_rounds']
        
        # get numerical columns
        numeric_columns = df.select_dtypes(include=['int64', 'float64']).columns
        numeric_columns = [col for col in numeric_columns if col not in exclude_columns]

        scaler = StandardScaler()
        df[numeric_columns] = scaler.fit_transform(df[numeric_columns])
        self.scalers['numeric'] = scaler
        
        return df

    def categorize_features(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Categorize features using LabelEncoder

        Args:
            df: Input DataFrame

        Returns:
            DataFrame with categorized features
        """
        logger.info("Categorizing features...")

        # columns to categorize
        columns = ['total_rounds', 'red_stance', 'blue_stance']

        # get categorical columns
        categorical_columns = [col for col in columns if col in df.columns]

        for col in categorical_columns:
            le = LabelEncoder()
            df[col] = le.fit_transform(df[col])
            self.label_encoders[col] = le

        return df

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
        self.fight_history = self.get_all_fight_ids(fights_df)

        # test:
        # fights = self._get_fights_date_limited(fighter_history, 'e1248941344b3288', datetime.datetime.strptime('2025-04-12', '%Y-%m-%d'))
        # print(fights)

        self.output_df = pd.DataFrame({
            'result': fights_df['result'],
            'win_method': fights_df['win_method'],
            'total_rounds': fights_df['total_rounds'],
            })

        self.output_df = self.remove_unneeded_rows(self.output_df)
        self.output_df = self.handle_missing_values(self.output_df)
        self.output_df = self.copy_fighter_stats(self.output_df, fights_df)
        self.output_df = self.calculate_career_stats(self.output_df, fights_df)
        self.output_df = self.get_all_strike_data(self.output_df, fights_df)
        self.output_df = engineer_features(self.output_df)

        self.output_df = self.mirror_data(self.output_df)

        self.output_df = self.scale_features(self.output_df)
        self.output_df = self.categorize_features(self.output_df)

        target = self.output_df['result'].copy()
        
        if 'result' in self.output_df.columns:
            self.output_df = self.output_df.drop(columns=['result'])

        if 'win_method' in self.output_df.columns:
            win_method = self.output_df['win_method'].copy()
            self.output_df = self.output_df.drop(columns=['win_method'])
            target = pd.concat([target, win_method], axis=1)

        le_result = LabelEncoder()
        target['result'] = pd.Series(le_result.fit_transform(target['result'].astype(str)))
        self.label_encoders['result'] = le_result

        le_win = LabelEncoder()
        target['win_method'] = pd.Series(le_win.fit_transform(target['win_method'].astype(str)))
        self.label_encoders['win_method'] = le_win

        self._save_data(target)
        
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
