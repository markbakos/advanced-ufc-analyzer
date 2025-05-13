import pandas as pd
import logging

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
                              'td_def', 'sub_avg', 'updated_timestamp'])

        return df

    def prepare_data(self) -> pd.DataFrame:
        """
        Handles the preprocessing
        """

        logger.info("Preparing fighter data")

        # load data
        fighters_df = self.load_data()

        # drop unnecessary columns
        fighters_df = self.drop_unnecessary_columns(fighters_df)

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