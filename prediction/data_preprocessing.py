import datetime
import json

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

class UFCFightsPreprocessor:
    """
    Preprocessing fight data for training model
    Handles missing values, date columns and feature engineering
    """
    
    def __init__(self, fights_path: str = 'fights.csv',
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
        
        # save target to csv
        target_df = pd.DataFrame({'result': target_df})
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
            'career_red_last_win_date', 'career_blue_last_win_date', 'event_date'
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

                '_height_cm', '_weight_kg', '_reach_cm', '_stance'
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
                for column in strike_columns:
                    red_fighter_stats[column] += fight_df.loc[fight_df['fight_id'] == fight_id, f'{corner}_{column}'].values[0]

                for column in strike_columns:
                    red_fighter_stats[f'{column}_opponent'] += fight_df.loc[fight_df['fight_id'] == fight_id, f'{opponent_corner[corner]}_{column}'].values[0]

            for fight_id, corner in blue_fights:
                for column in strike_columns:
                    blue_fighter_stats[column] += fight_df.loc[fight_df['fight_id'] == fight_id, f'{corner}_{column}'].values[0]

                for column in strike_columns:
                    blue_fighter_stats[f'{column}_opponent'] += fight_df.loc[fight_df['fight_id'] == fight_id, f'{opponent_corner[corner]}_{column}'].values[0]

            # save data in results dict
            for column in strike_columns:
                target_df.at[idx, f'red_{column}'] = red_fighter_stats[column]

            for column in strike_columns:
                target_df.at[idx, f'red_{column}_opponent'] = red_fighter_stats[f'{column}_opponent']

            for column in strike_columns:
                target_df.at[idx, f'blue_{column}'] = blue_fighter_stats[column]

            for column in strike_columns:
                target_df.at[idx, f'blue_{column}_opponent'] = blue_fighter_stats[f'{column}_opponent']

            #
            # if fight['fight_id'] == "d3be5a4e0ec273e2":
            #     print(f"Red fighter: {red_fighter_strikes}")
            #     print(f"Blue fighter: {blue_fighter_strikes}")

            if idx % 100 == 0 and idx > 0:
                logger.info(f"Processed {idx} fights...")
                # return target_df

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

    def engineer_features(self, target_df: pd.DataFrame) -> pd.DataFrame:
        """
        Create new features for prediction
        
        Args:
            df: DataFrame
            
        Returns:
            DataFrame with engineered features
        """
        logger.info("Engineering new features...")

        #
        # basic differences and efficiencies
        #

        # calculate experience difference
        target_df['experience_diff'] = target_df['red_total_ufc_fights'] - target_df['blue_total_ufc_fights']

        # calculate win rate differences
        target_df['win_rate_diff'] = (target_df['red_wins_in_ufc'] / target_df['red_total_ufc_fights'].where(target_df['red_total_ufc_fights'] > 0, 1)) - \
                                     (target_df['blue_wins_in_ufc'] / target_df['blue_total_ufc_fights'].where(target_df['blue_total_ufc_fights'] > 0, 1))

        # calculate takedown differentials
        target_df['takedown_diff'] = target_df['red_takedowns_landed'] - target_df['blue_takedowns_landed']

        #
        # striking differentials from here:
        #

        # total strikes, per round, per minute
        target_df['total_strike_diff'] = target_df['red_strikes_landed'] - target_df['blue_strikes_landed']
        target_df['total_strike_diff_per_round'] = target_df['red_strikes_landed_per_round'] - target_df['blue_strikes_landed_per_round']
        target_df['total_strike_diff_per_minute'] = target_df['red_strikes_landed_per_minute'] - target_df['blue_strikes_landed_per_minute']

        # location differentials
        target_df['total_head_strike_diff'] = target_df['red_head_strikes_landed'] - target_df['blue_head_strikes_landed']
        target_df['total_body_strike_diff'] = target_df['red_body_strikes_landed'] - target_df['blue_body_strikes_landed']
        target_df['total_leg_strike_diff'] = target_df['red_leg_strikes_landed'] - target_df['blue_leg_strikes_landed']

        # position differentirals
        target_df['distance_strike_diff'] = target_df['red_distance_strikes_landed'] - target_df['blue_distance_strikes_landed']
        target_df['clinch_strike_diff'] = target_df['red_clinch_strikes_landed'] - target_df['blue_clinch_strikes_landed']
        target_df['ground_strike_diff'] = target_df['red_ground_strikes_landed'] - target_df['blue_ground_strikes_landed']

        # strike accuracy
        for corner in ['red', 'blue']:
            # head strike accuracy
            target_df[f'{corner}_head_strike_accuracy'] = target_df[f'{corner}_head_strikes_landed'] / target_df[
                f'{corner}_head_strikes_thrown'].where(target_df[f'{corner}_head_strikes_thrown'] > 0, 1)

            # body strike accuracy
            target_df[f'{corner}_body_strike_accuracy'] = target_df[f'{corner}_body_strikes_landed'] / target_df[
                f'{corner}_body_strikes_thrown'].where(target_df[f'{corner}_body_strikes_thrown'] > 0, 1)

            # leg strike accuracy
            target_df[f'{corner}_leg_strike_accuracy'] = target_df[f'{corner}_leg_strikes_landed'] / target_df[
                f'{corner}_leg_strikes_thrown'].where(target_df[f'{corner}_leg_strikes_thrown'] > 0, 1)

            # distance strikes
            target_df[f'{corner}_distance_strike_accuracy'] = target_df[f'{corner}_distance_strikes_landed'] / \
                                                              target_df[f'{corner}_distance_strikes_thrown'].where(
                                                                  target_df[f'{corner}_distance_strikes_thrown'] > 0, 1)

            # clinch strike accuracy
            target_df[f'{corner}_clinch_strike_accuracy'] = target_df[f'{corner}_clinch_strikes_landed'] / target_df[
                f'{corner}_clinch_strikes_thrown'].where(target_df[f'{corner}_clinch_strikes_thrown'] > 0, 1)

            # ground strikes accuracy
            target_df[f'{corner}_ground_strike_accuracy'] = target_df[f'{corner}_ground_strikes_landed'] / target_df[
                f'{corner}_ground_strikes_thrown'].where(target_df[f'{corner}_ground_strikes_thrown'] > 0, 1)

        # accuracy differentials
        target_df['head_accuracy_diff'] = target_df['red_head_strike_accuracy'] - target_df['blue_head_strike_accuracy']
        target_df['body_accuracy_diff'] = target_df['red_body_strike_accuracy'] - target_df['blue_body_strike_accuracy']
        target_df['leg_accuracy_diff'] = target_df['red_leg_strike_accuracy'] - target_df['blue_leg_strike_accuracy']
        target_df['distance_accuracy_diff'] = target_df['red_distance_strike_accuracy'] - target_df['blue_distance_strike_accuracy']
        target_df['clinch_accuracy_diff'] = target_df['red_clinch_strike_accuracy'] - target_df['blue_clinch_strike_accuracy']
        target_df['ground_accuracy_diff'] = target_df['red_ground_strike_accuracy'] - target_df['blue_ground_strike_accuracy']

        #
        # strike distribution
        #

        for corner in ['red', 'blue']:
            # calculate total strikes thrown to each target
            total_strikes_thrown = (
                    target_df[f'{corner}_head_strikes_thrown'] +
                    target_df[f'{corner}_body_strikes_thrown'] +
                    target_df[f'{corner}_leg_strikes_thrown']
            ).where(
                (target_df[f'{corner}_head_strikes_thrown'] +
                 target_df[f'{corner}_body_strikes_thrown'] +
                 target_df[f'{corner}_leg_strikes_thrown']) > 0, 1
            )

            # save total strikes thrown
            target_df[f'{corner}_strikes_thrown'] = total_strikes_thrown

            # calculate percent of strikes thrown to each target
            target_df[f'{corner}_head_strike_pct'] = target_df[f'{corner}_head_strikes_thrown'] / total_strikes_thrown
            target_df[f'{corner}_body_strike_pct'] = target_df[f'{corner}_body_strikes_thrown'] / total_strikes_thrown
            target_df[f'{corner}_leg_strike_pct'] = target_df[f'{corner}_leg_strikes_thrown'] / total_strikes_thrown

            # calculate total strikes thrown from each position
            total_position_strikes = (
                    target_df[f'{corner}_distance_strikes_thrown'] +
                    target_df[f'{corner}_clinch_strikes_thrown'] +
                    target_df[f'{corner}_ground_strikes_thrown']
            ).where(
                (target_df[f'{corner}_distance_strikes_thrown'] +
                 target_df[f'{corner}_clinch_strikes_thrown'] +
                 target_df[f'{corner}_ground_strikes_thrown']) > 0, 1
            )

            # save position strikes thrown
            target_df[f'{corner}_position_strikes_thrown'] = total_position_strikes

            # save total strikes thrown
            target_df[f'{corner}_total_strikes_thrown'] = total_strikes_thrown + total_position_strikes

            # percent of strikes from each position
            target_df[f'{corner}_distance_strike_pct'] = target_df[
                                                             f'{corner}_distance_strikes_thrown'] / total_position_strikes
            target_df[f'{corner}_clinch_strike_pct'] = target_df[
                                                           f'{corner}_clinch_strikes_thrown'] / total_position_strikes
            target_df[f'{corner}_ground_strike_pct'] = target_df[
                                                           f'{corner}_ground_strikes_thrown'] / total_position_strikes

        # calculate striking efficiency
        target_df['red_strike_efficiency'] = target_df['red_strikes_landed'] / target_df['red_strikes_thrown'].where(target_df['red_strikes_thrown'] > 0, 1)
        target_df['blue_strike_efficiency'] = target_df['blue_strikes_landed'] / target_df['blue_strikes_thrown'].where(target_df['blue_strikes_thrown'] > 0, 1)
        target_df['strike_efficiency_diff'] = target_df['red_strike_efficiency'] - target_df['blue_strike_efficiency']

        # finish rates
        for corner in ['red', 'blue']:
            finish_wins = target_df[f'{corner}_wins_by_ko'] + target_df[f'{corner}_wins_by_sub']
            total_wins = target_df[f'{corner}_wins_in_ufc']
            target_df[f'{corner}_finish_rate'] = finish_wins / total_wins.where(total_wins > 0, 1)

            # ko rate
            target_df[f'{corner}_ko_rate'] = target_df[f'{corner}_wins_by_ko'] / total_wins.where(total_wins > 0, 1)

            # sub rate
            target_df[f'{corner}_sub_rate'] = target_df[f'{corner}_wins_by_sub'] / total_wins.where(total_wins > 0, 1)

            # decision rate
            target_df[f'{corner}_decision_rate'] = target_df[f'{corner}_wins_by_dec'] / total_wins.where(total_wins > 0, 1)

            # loss methods
            total_losses = target_df[f'{corner}_losses_in_ufc']

            target_df[f'{corner}_ko_loss_rate'] = target_df[f'{corner}_losses_by_ko'] / total_losses.where(total_losses > 0, 1)
            target_df[f'{corner}_sub_loss_rate'] = target_df[f'{corner}_losses_by_sub'] / total_losses.where(total_losses > 0, 1)
            target_df[f'{corner}_decision_loss_rate'] = target_df[f'{corner}_losses_by_dec'] / total_losses.where(total_losses > 0, 1)

        # finish rate differentials
        target_df['finish_rate_diff'] = target_df['red_finish_rate'] - target_df['blue_finish_rate']
        target_df['ko_rate_diff'] = target_df['red_ko_rate'] - target_df['blue_ko_rate']
        target_df['sub_rate_diff'] = target_df['red_sub_rate'] - target_df['blue_sub_rate']
        target_df['decision_rate_diff'] = target_df['red_decision_rate'] - target_df['blue_decision_rate']

        # activity
        for corner in ['red', 'blue']:
            # striking volume
            target_df[f'{corner}_strike_volume'] = target_df[f'{corner}_total_strikes_thrown'] / target_df[
                f'{corner}_total_time_minutes'].where(target_df[f'{corner}_total_time_minutes'] > 0, 1)

            # sub attempt frequency
            target_df[f'{corner}_sub_attempt_frequency'] = target_df[f'{corner}_sub_attempts_landed'] / target_df[
                f'{corner}_total_time_minutes'].where(target_df[f'{corner}_total_time_minutes'] > 0, 1)

        # activity differentials
        target_df['strike_volume_diff'] = target_df['red_strike_volume'] - target_df['blue_strike_volume']
        target_df['sub_attempt_frequency_diff'] = (target_df['red_sub_attempt_frequency'] - target_df['blue_sub_attempt_frequency'])

        # fight style
        for corner in ['red', 'blue']:
            # striking vs grappling preference
            total_offensive_actions = (target_df[f'{corner}_strikes_thrown'] +
                                       target_df[f'{corner}_takedowns_landed'] +
                                       target_df[f'{corner}_sub_attempts_landed'])

            # striking preference
            target_df[f'{corner}_striking_preference'] = (target_df[ f'{corner}_strikes_thrown'] /
                                                          total_offensive_actions.where(total_offensive_actions > 0, 1))

            # grappling preference (takedowns and submissions)
            target_df[f'{corner}_grappling_preference'] = ((target_df[f'{corner}_takedowns_landed'] +
                                                           target_df[f'{corner}_sub_attempts_landed']) /
                                                           total_offensive_actions.where(total_offensive_actions > 0, 1))

            # ground vs standing preference
            target_df[f'{corner}_ground_preference'] = target_df[f'{corner}_ground_strikes_thrown'] / target_df[
                f'{corner}_total_strikes_thrown'].where(target_df[f'{corner}_total_strikes_thrown'] > 0, 1)

            # distance vs clinch pref
            target_df[f'{corner}_distance_preference'] = target_df[f'{corner}_distance_strikes_thrown'] / (
                    target_df[f'{corner}_distance_strikes_thrown'] + target_df[f'{corner}_clinch_strikes_thrown']).where(
                (target_df[f'{corner}_distance_strikes_thrown'] + target_df[f'{corner}_clinch_strikes_thrown']) > 0, 1)

        # fighting style differentials
        target_df['striking_preference_diff'] = target_df['red_striking_preference'] - target_df['blue_striking_preference']
        target_df['grappling_preference_diff'] = target_df['red_grappling_preference'] - target_df['blue_grappling_preference']
        target_df['ground_preference_diff'] = target_df['red_ground_preference'] - target_df['blue_ground_preference']
        target_df['distance_preference_diff'] = target_df['red_distance_preference'] - target_df['blue_distance_preference']

        # damage metrics
        for corner in ['red', 'blue']:
            # knockdown ratio (knockdowns landed / knockdowns absorbed)
            target_df[f'{corner}_knockdown_ratio'] = target_df[f'{corner}_knockdowns_landed'] / target_df[
                f'{corner}_knockdowns_absorbed'].where(target_df[f'{corner}_knockdowns_absorbed'] > 0, 1)

            # damage efficiency (knockdowns per strike landed)
            target_df[f'{corner}_damage_efficiency'] = target_df[f'{corner}_knockdowns_landed'] / target_df[
                f'{corner}_strikes_landed'].where(target_df[f'{corner}_strikes_landed'] > 0, 1)

            # head strike damage ratio
            target_df[f'{corner}_head_strike_damage_ratio'] = target_df[f'{corner}_head_strikes_landed'] / target_df[
                f'{corner}_strikes_landed'].where(target_df[f'{corner}_strikes_landed'] > 0, 1)

        # damage differentials
        target_df['knockdown_ratio_diff'] = target_df['red_knockdown_ratio'] - target_df['blue_knockdown_ratio']
        target_df['damage_efficiency_diff'] = target_df['red_damage_efficiency'] - target_df['blue_damage_efficiency']
        target_df['head_strike_damage_ratio_diff'] = target_df['red_head_strike_damage_ratio'] - target_df['blue_head_strike_damage_ratio']

        # fight pace
        for corner in ['red', 'blue']:
            # avg fight length
            target_df[f'{corner}_avg_fight_length'] = target_df[f'{corner}_total_time_minutes'] / target_df[
                f'{corner}_total_ufc_fights'].where(target_df[f'{corner}_total_ufc_fights'] > 0, 1)

            # fight pace (total offensive action per minute)
            offensive_actions = (target_df[f'{corner}_strikes_thrown'] +
                                 target_df[f'{corner}_takedowns_landed'] +
                                 target_df[f'{corner}_sub_attempts_landed'])

            target_df[f'{corner}_fight_pace'] = (offensive_actions /
                    target_df[f'{corner}_total_time_minutes'].where(target_df[f'{corner}_total_time_minutes'] > 0, 1))

        # fight pace differentials
        target_df['avg_fight_length_diff'] = target_df['red_avg_fight_length'] - target_df['blue_avg_fight_length']
        target_df['fight_pace_diff'] = target_df['red_fight_pace'] - target_df['blue_fight_pace']

        # strike defense
        for corner in ['red', 'blue']:
            # head strike defense
            target_df[f'{corner}_head_strike_defense'] = (1 -
                            (target_df[f'{corner}_head_strikes_landed_opponent'] /
                            target_df[ f'{corner}_head_strikes_thrown_opponent']).where(
                            target_df[f'{corner}_head_strikes_thrown_opponent'] > 0, 1))

            # body strike defense
            target_df[f'{corner}_body_strike_defense'] = (1 -
                            (target_df[f'{corner}_body_strikes_landed_opponent'] /
                            target_df[f'{corner}_body_strikes_thrown_opponent']).where(
                            target_df[f'{corner}_body_strikes_thrown_opponent'] > 0, 1))

            # leg strike defense
            target_df[f'{corner}_leg_strike_defense'] = 1 - (target_df[f'{corner}_leg_strikes_landed_opponent'] /
                target_df[f'{corner}_leg_strikes_thrown_opponent']).where(target_df[f'{corner}_leg_strikes_thrown_opponent'] > 0, 1)

        # strike defense differentials
        target_df['head_strike_defense_diff'] = target_df['red_head_strike_defense'] - target_df['blue_head_strike_defense']
        target_df['body_strike_defense_diff'] = target_df['red_body_strike_defense'] - target_df['blue_body_strike_defense']
        target_df['leg_strike_defense_diff'] = target_df['red_leg_strike_defense'] - target_df['blue_leg_strike_defense']

        # compound metrics
        for corner in ['red', 'blue']:
            # striking effectiveness (combines offense and defense)
            target_df[f'{corner}_overall_striking_effectiveness'] = (
                    target_df[f'{corner}_strike_efficiency'] * 0.6 +
                    (1 - (target_df[f'{corner}_strikes_absorbed'] / target_df[f'{corner}_strikes_thrown'].where(
                        target_df[f'{corner}_strikes_thrown'] > 0, 1))) * 0.4
            )

            # grappling effectiveness
            target_df[f'{corner}_overall_grappling_effectiveness'] = (
                    target_df[f'{corner}_sub_attempts_landed_per_round'] * 0.6 +
                    (1 - target_df[f'{corner}_takedowns_absorbed_per_round']) * 0.4
            )

            # fighter durability
            target_df[f'{corner}_durability'] = 1 - (
                    target_df[f'{corner}_knockdowns_absorbed'] / target_df[f'{corner}_strikes_absorbed'].where(
                target_df[f'{corner}_strikes_absorbed'] > 0, 1)
            )

        # compound metrics differentials
        target_df['overall_striking_effectiveness_diff'] = (
                target_df['red_overall_striking_effectiveness'] - target_df['blue_overall_striking_effectiveness']
        )
        target_df['overall_grappling_effectiveness_diff'] = (
                target_df['red_overall_grappling_effectiveness'] - target_df['blue_overall_grappling_effectiveness']
        )
        target_df['durability_diff'] = target_df['red_durability'] - target_df['blue_durability']

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
            swapped_df['result'] = swapped_df['result'].map({"red": "blue", "blue": "red", "draw": "draw"})

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
            'total_rounds': fights_df['total_rounds'],
            })



        self.output_df = self.copy_fighter_stats(self.output_df, fights_df)
        self.output_df = self.calculate_career_stats(self.output_df, fights_df)
        self.output_df = self.get_all_strike_data(self.output_df, fights_df)
        self.output_df = self.engineer_features(self.output_df)

        self.output_df = self.mirror_data(self.output_df)

        self.output_df = self.scale_features(self.output_df)

        target = self.output_df['result'].copy()
        
        if 'result' in self.output_df.columns:
            self.output_df = self.output_df.drop(columns=['result'])
        
        le = LabelEncoder()
        target = pd.Series(le.fit_transform(target.astype(str)), index=target.index)
        self.label_encoders['result'] = le

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
