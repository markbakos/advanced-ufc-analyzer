import numpy as np
import pandas as pd
import logging
from typing import List, Tuple
from data_preprocessing import UFCFightsPreprocessor
from sklearn.impute import SimpleImputer

logger = logging.getLogger(__name__)

TEST_RUN = True

class FighterDataPreprocessing:
    def __init__(self, fighter_path: str = "../scraper/fighters/spiders/fighters.csv", output_dir = "data/processed"):
        """
        Initialize the FighterDataPreprocessing class
        """
        self.fighters_df = fighter_path
        self.fight_history = {}

    def load_data(self) -> pd.DataFrame:
        """
        Load the fighter data
        """
        logger.info("Loading fighter data")

        fighters_df = pd.read_csv(self.fighters_df)

        return fighters_df

    def drop_unnecessary_columns(self, df: pd.DataFrame) -> pd.DataFrame:
        """
        Drop unnecessary columns from the fighter data
        """
        logger.info("Dropping unnecessary columns from fighter data")

        # drop unnecessary columns
        df = df.drop(columns=['fighter_id', 'fighter_name', 'nickname', 'fighter_style', 'wins', 'losses', 'draws',
                              'win_percentage', 'momentum', 'SLpM', 'str_acc', 'SApM', 'str_def', 'td_avg', 'td_acc',
                              'td_def', 'sub_avg', 'date_of_birth', 'last_fight_date', 'last_win_date', 'updated_timestamp'])

        return df

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

        date_columns = [
            'last_fight_date', 'last_win_date', 'date_of_birth',
        ]

        current_date = pd.to_datetime('today')

        for col in date_columns:
            if col in df_processed.columns:
                df_processed[col] = pd.to_datetime(df_processed[col], errors='coerce')

        for col in ['last_fight_date', 'last_win_date']:
            if col in df_processed.columns:
                days_since_col = col.replace('date', 'days_since')
                df_processed[days_since_col] = (current_date - df_processed[col]).dt.days
                df_processed[days_since_col] = df_processed[days_since_col].apply(
                    lambda x: np.nan if pd.isna(x) or x < 0 else x)

        for col in ['date_of_birth']:
            if col in df_processed.columns:
                age_col = col.replace('date_of_birth', 'age_in_days')
                df_processed[age_col] = (current_date - df_processed[col]).dt.days
                df_processed[age_col] = df_processed[age_col].apply(lambda x: np.nan if pd.isna(x) or x < 0 else x)

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

        # apply imputers only to non-round-specific columns
        if len(numeric_columns) > 0:
            df[numeric_columns] = numeric_imputer.fit_transform(df[numeric_columns])
        df[categorical_columns] = categorical_imputer.fit_transform(df[categorical_columns])

        return df

    def _get_fights_data(self, fighter_id: str) -> List[Tuple[str, str]]:
        """
        Get all fight ids for fighter

        :param fighter_id: Fighter ID to get fights for
        :param date_limit: Maximum date to limit the fights (Date NOT included)
        :return: List of Tuples (fight_id, corner)
        """
        if fighter_id not in self.fight_history:
            return []

        fights = self.fight_history[fighter_id]

        return [(fid, corner) for fid, corner, date in fights]

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

        # pre initialize all columns in fighter_df
        for column in strike_columns:
            target_df[f'{column}'] = 0
        for column in strike_columns:
            target_df[f'{column}_opponent'] = 0

        for idx, fighter in target_df.iterrows():

            # get all up-to-date fights for fighter
            fights = self._get_fights_data(fighter['fighter_id'])

            # initialize red and blue fighters columns
            fighter_stats = {column: 0 for column in strike_columns}
            fighter_stats.update({f"{column}_opponent": 0 for column in strike_columns})

            # get all strikes for using fights
            for fight_id, corner in fights:
                try:
                    fight_row = fight_df.loc[fight_df['fight_id'] == fight_id]
                    if not fight_row.empty:
                        for column in strike_columns:
                            if f'{corner}_{column}' in fight_row.columns:
                                value = fight_row[f'{corner}_{column}'].values[0]
                                if pd.notna(value):
                                    fighter_stats[column] += value

                        for column in strike_columns:
                            if f'{opponent_corner[corner]}_{column}' in fight_row.columns:
                                value = fight_row[f'{opponent_corner[corner]}_{column}'].values[0]
                                if pd.notna(value):
                                    fighter_stats[f'{column}_opponent'] += value
                except Exception as e:
                    logger.error(f"Error processing fighter's fight {fight_id}: {e}")

            # save data in results dict
            for column in strike_columns:
                target_df.loc[idx, column] = fighter_stats[column]

            for column in strike_columns:
                target_df.loc[idx, f'{column}_opponent'] = fighter_stats[f'{column}_opponent']

            #
            # if fight['fight_id'] == "d3be5a4e0ec273e2":
            #     print(f"Red fighter: {red_fighter_strikes}")
            #     print(f"Blue fighter: {blue_fighter_strikes}")

            if idx % 100 == 0 and idx > 0:
                logger.info(f"Processed {idx} fighters...")
                if TEST_RUN:
                    break

        # final check for nan values and replace with 0
        strike_related_columns = [col for col in target_df.columns if any(x in col for x in strike_columns.keys())]
        target_df[strike_related_columns] = target_df[strike_related_columns].fillna(0)

        return target_df

    def calculate_per_time_stats(self, target_df: pd.DataFrame) -> pd.DataFrame:
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
                target_df[f'{col}_per_minute'] = target_df[col] / target_df[f'total_time_minutes'].where(target_df[f'total_time_minutes'] > 0, 1)
                target_df[f'{col}_per_round'] = target_df[col] / target_df[f'total_rounds'].where(target_df[f'total_rounds'] > 0, 1)

        return target_df

    def prepare_data(self) -> pd.DataFrame:
        """
        Handles the preprocessing
        """

        logger.info("Preparing fighter data")

        fights_preprocessor = UFCFightsPreprocessor()
        fights_df = fights_preprocessor.load_data()
        self.fight_history = fights_preprocessor.get_all_fight_ids(fights_df)

        # load data
        fighters_df = self.load_data()

        # calculate days since dates
        fighters_df = self.calculate_days_since(fighters_df)

        # get all strike data
        fighters_df = self.get_all_strike_data(fighters_df, fights_df)

        # drop unnecessary columns
        fighters_df = self.drop_unnecessary_columns(fighters_df)

        fighters_df = self.calculate_per_time_stats(fighters_df)

        # handle missing values
        fighters_df = self.handle_missing_values(fighters_df)

        # save the processed data
        output_dir = "data/processed"
        fighters_df.to_csv(f"{output_dir}/processed_fighters.csv", index=False)

        return fighters_df


def main():
    """
    Main function to run fighter data preprocessing
    """
    preprocessor = FighterDataPreprocessing()

    try:
        # prepare data
        features_df = preprocessor.prepare_data()

        logger.info("Data preprocessing completed successfully")

    except Exception as e:
        logger.error(f"Error during data preprocessing: {str(e)}")
        raise


if __name__ == '__main__':
    main()