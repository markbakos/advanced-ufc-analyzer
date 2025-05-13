import numpy as np
import pandas as pd
import logging

from sklearn.impute import SimpleImputer

logger = logging.getLogger(__name__)

class FighterDataPreprocessing:
    def __init__(self, fighter_path: str = "../scraper/fighters/spiders/fighters.csv", output_dir = "data/processed"):
        """
        Initialize the FighterDataPreprocessing class
        """
        self.fighters_df = fighter_path

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

    def prepare_data(self) -> pd.DataFrame:
        """
        Handles the preprocessing
        """

        logger.info("Preparing fighter data")

        # load data
        fighters_df = self.load_data()

        # calculate days since dates
        fighters_df = self.calculate_days_since(fighters_df)

        # drop unnecessary columns
        fighters_df = self.drop_unnecessary_columns(fighters_df)

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