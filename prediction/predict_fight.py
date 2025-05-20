import os
import pickle

import pandas as pd
from keras import models
import numpy as np
from prediction.engineer_features import calculate_differentials
from prediction.model import handle_nan_values

class UFCPredictor:
    def __init__(self, model_dir = "models/", data_dir = "data/processed/",
                 artifacts_path="data/artifacts/preprocessing_artifacts.pkl",
                 fighter1: str = None, fighter2: str = None, test_run: bool = False):
        """
        Initialize the UFCPredictor
        """
        self.model = None
        self.model_dir = model_dir
        self.data_dir = data_dir
        self.artifacts_dir = artifacts_path
        self.base_dir = os.path.dirname(os.path.abspath(__file__))

        self.fighter1 = fighter1
        self.fighter2 = fighter2

        self.test_run = test_run

    def load_model(self):
        """
        Load the pre-trained model from the specified directory.
        """
        try:
            model_path = os.path.join(self.base_dir, self.model_dir, "model.keras")
            return models.load_model(model_path, custom_objects={'handle_nan_values': handle_nan_values}, safe_mode=False)
        except FileNotFoundError:
            print(f"Model file not found at {model_path}")
            raise FileNotFoundError

    def load_preprocessing_artifacts(self):
        with open(os.path.join(self.base_dir, self.artifacts_dir), 'rb') as f:
            artifacts = pickle.load(f)
        return artifacts

    def load_fighter_data(self):
        """
        Load the processed fighter data used for training.
        """
        try:
            return pd.read_csv(os.path.join(self.base_dir, self.data_dir, "processed_fighters.csv"))
        except FileNotFoundError:
            print(f"Fighter data file not found at {self.data_dir}/processed_fighters.csv")
            raise FileNotFoundError

    def find_fighter(self, fighter_id, fighter_data):
        """Find a fighter in the dataset by id."""
        matches = fighter_data[fighter_data['fighter_id'].str.contains(fighter_id)]

        try:
            return matches.iloc[0]
        except ValueError:
            print(f"Fighter {fighter_id} not found in the dataset.")
            return None

    def prepare_prediction_data(self, red_fighter, blue_fighter):
        """
        Prepare the data for prediction by combining red and blue fighter data.
        """
        matchup_data = pd.DataFrame({
            # Red fighter data
            'red_height_cm': [red_fighter['height_cm']],
            'red_weight_kg': [red_fighter['weight_kg']],
            'red_reach_cm': [red_fighter['reach_cm']],
            'red_stance': [red_fighter['stance']],
            'red_total_ufc_fights': [red_fighter['total_ufc_fights']],
            'red_wins_in_ufc': [red_fighter['wins_in_ufc']],
            'red_losses_in_ufc': [red_fighter['losses_in_ufc']],
            'red_draws_in_ufc': [red_fighter['draws_in_ufc']],
            'red_wins_by_dec': [red_fighter['wins_by_dec']],
            'red_losses_by_dec': [red_fighter['losses_by_dec']],
            'red_wins_by_sub': [red_fighter['wins_by_sub']],
            'red_losses_by_sub': [red_fighter['losses_by_sub']],
            'red_wins_by_ko': [red_fighter['wins_by_ko']],
            'red_losses_by_ko': [red_fighter['losses_by_ko']],
            'red_knockdowns_landed': [red_fighter['knockdowns_landed']],
            'red_knockdowns_absorbed': [red_fighter['knockdowns_absorbed']],
            'red_strikes_landed': [red_fighter['strikes_landed']],
            'red_strikes_absorbed': [red_fighter['strikes_absorbed']],
            'red_takedowns_landed': [red_fighter['takedowns_landed']],
            'red_takedowns_absorbed': [red_fighter['takedowns_absorbed']],
            'red_sub_attempts_landed': [red_fighter['sub_attempts_landed']],
            'red_sub_attempts_absorbed': [red_fighter['sub_attempts_absorbed']],
            'red_total_rounds': [red_fighter['total_rounds']],
            'red_total_time_minutes': [red_fighter['total_time_minutes']],
            'red_avg_knockdowns_landed': [red_fighter['avg_knockdowns_landed']],
            'red_avg_knockdowns_absorbed': [red_fighter['avg_knockdowns_absorbed']],
            'red_avg_strikes_landed': [red_fighter['avg_strikes_landed']],
            'red_avg_strikes_absorbed': [red_fighter['avg_strikes_absorbed']],
            'red_avg_takedowns_landed': [red_fighter['avg_takedowns_landed']],
            'red_avg_takedowns_absorbed': [red_fighter['avg_takedowns_absorbed']],
            'red_avg_submission_attempts_landed': [red_fighter['avg_submission_attempts_landed']],
            'red_avg_submission_attempts_absorbed': [red_fighter['avg_submission_attempts_absorbed']],
            'red_avg_fight_time_min': [red_fighter['avg_fight_time_min']],
            'red_last_fight_days_since': [red_fighter['last_fight_days_since']],
            'red_last_win_days_since': [red_fighter['last_win_days_since']],
            'red_age_in_days': [red_fighter['age_in_days']],
            'red_head_strikes_landed': [red_fighter['head_strikes_landed']],
            'red_head_strikes_thrown': [red_fighter['head_strikes_thrown']],
            'red_body_strikes_landed': [red_fighter['body_strikes_landed']],
            'red_body_strikes_thrown': [red_fighter['body_strikes_thrown']],
            'red_leg_strikes_landed': [red_fighter['leg_strikes_landed']],
            'red_leg_strikes_thrown': [red_fighter['leg_strikes_thrown']],
            'red_distance_strikes_landed': [red_fighter['distance_strikes_landed']],
            'red_distance_strikes_thrown': [red_fighter['distance_strikes_thrown']],
            'red_clinch_strikes_landed': [red_fighter['clinch_strikes_landed']],
            'red_clinch_strikes_thrown': [red_fighter['clinch_strikes_thrown']],
            'red_ground_strikes_landed': [red_fighter['ground_strikes_landed']],
            'red_ground_strikes_thrown': [red_fighter['ground_strikes_thrown']],
            'red_head_strikes_landed_opponent': [red_fighter['head_strikes_landed_opponent']],
            'red_head_strikes_thrown_opponent': [red_fighter['head_strikes_thrown_opponent']],
            'red_body_strikes_landed_opponent': [red_fighter['body_strikes_landed_opponent']],
            'red_body_strikes_thrown_opponent': [red_fighter['body_strikes_thrown_opponent']],
            'red_leg_strikes_landed_opponent': [red_fighter['leg_strikes_landed_opponent']],
            'red_leg_strikes_thrown_opponent': [red_fighter['leg_strikes_thrown_opponent']],
            'red_distance_strikes_landed_opponent': [red_fighter['distance_strikes_landed_opponent']],
            'red_distance_strikes_thrown_opponent': [red_fighter['distance_strikes_thrown_opponent']],
            'red_clinch_strikes_landed_opponent': [red_fighter['clinch_strikes_landed_opponent']],
            'red_clinch_strikes_thrown_opponent': [red_fighter['clinch_strikes_thrown_opponent']],
            'red_ground_strikes_landed_opponent': [red_fighter['ground_strikes_landed_opponent']],
            'red_ground_strikes_thrown_opponent': [red_fighter['ground_strikes_thrown_opponent']],
            'red_knockdowns_landed_per_minute': [red_fighter['knockdowns_landed_per_minute']],
            'red_knockdowns_landed_per_round': [red_fighter['knockdowns_landed_per_round']],
            'red_knockdowns_absorbed_per_minute': [red_fighter['knockdowns_absorbed_per_minute']],
            'red_knockdowns_absorbed_per_round': [red_fighter['knockdowns_absorbed_per_round']],
            'red_strikes_landed_per_minute': [red_fighter['strikes_landed_per_minute']],
            'red_strikes_landed_per_round': [red_fighter['strikes_landed_per_round']],
            'red_strikes_absorbed_per_minute': [red_fighter['strikes_absorbed_per_minute']],
            'red_strikes_absorbed_per_round': [red_fighter['strikes_absorbed_per_round']],
            'red_takedowns_landed_per_minute': [red_fighter['takedowns_landed_per_minute']],
            'red_takedowns_landed_per_round': [red_fighter['takedowns_landed_per_round']],
            'red_takedowns_absorbed_per_minute': [red_fighter['takedowns_absorbed_per_minute']],
            'red_takedowns_absorbed_per_round': [red_fighter['takedowns_absorbed_per_round']],
            'red_sub_attempts_landed_per_minute': [red_fighter['sub_attempts_landed_per_minute']],
            'red_sub_attempts_landed_per_round': [red_fighter['sub_attempts_landed_per_round']],
            'red_sub_attempts_absorbed_per_minute': [red_fighter['sub_attempts_absorbed_per_minute']],
            'red_sub_attempts_absorbed_per_round': [red_fighter['sub_attempts_absorbed_per_round']],
            'red_head_strike_accuracy': [red_fighter['head_strike_accuracy']],
            'red_body_strike_accuracy': [red_fighter['body_strike_accuracy']],
            'red_leg_strike_accuracy': [red_fighter['leg_strike_accuracy']],
            'red_distance_strike_accuracy': [red_fighter['distance_strike_accuracy']],
            'red_clinch_strike_accuracy': [red_fighter['clinch_strike_accuracy']],
            'red_ground_strike_accuracy': [red_fighter['ground_strike_accuracy']],
            'red_head_strike_defense': [red_fighter['head_strike_defense']],
            'red_body_strike_defense': [red_fighter['body_strike_defense']],
            'red_leg_strike_defense': [red_fighter['leg_strike_defense']],

            # Blue fighter data
            'blue_height_cm': [blue_fighter['height_cm']],
            'blue_weight_kg': [blue_fighter['weight_kg']],
            'blue_reach_cm': [blue_fighter['reach_cm']],
            'blue_stance': [blue_fighter['stance']],
            'blue_total_ufc_fights': [blue_fighter['total_ufc_fights']],
            'blue_wins_in_ufc': [blue_fighter['wins_in_ufc']],
            'blue_losses_in_ufc': [blue_fighter['losses_in_ufc']],
            'blue_draws_in_ufc': [blue_fighter['draws_in_ufc']],
            'blue_wins_by_dec': [blue_fighter['wins_by_dec']],
            'blue_losses_by_dec': [blue_fighter['losses_by_dec']],
            'blue_wins_by_sub': [blue_fighter['wins_by_sub']],
            'blue_losses_by_sub': [blue_fighter['losses_by_sub']],
            'blue_wins_by_ko': [blue_fighter['wins_by_ko']],
            'blue_losses_by_ko': [blue_fighter['losses_by_ko']],
            'blue_knockdowns_landed': [blue_fighter['knockdowns_landed']],
            'blue_knockdowns_absorbed': [blue_fighter['knockdowns_absorbed']],
            'blue_strikes_landed': [blue_fighter['strikes_landed']],
            'blue_strikes_absorbed': [blue_fighter['strikes_absorbed']],
            'blue_takedowns_landed': [blue_fighter['takedowns_landed']],
            'blue_takedowns_absorbed': [blue_fighter['takedowns_absorbed']],
            'blue_sub_attempts_landed': [blue_fighter['sub_attempts_landed']],
            'blue_sub_attempts_absorbed': [blue_fighter['sub_attempts_absorbed']],
            'blue_total_rounds': [blue_fighter['total_rounds']],
            'blue_total_time_minutes': [blue_fighter['total_time_minutes']],
            'blue_avg_knockdowns_landed': [blue_fighter['avg_knockdowns_landed']],
            'blue_avg_knockdowns_absorbed': [blue_fighter['avg_knockdowns_absorbed']],
            'blue_avg_strikes_landed': [blue_fighter['avg_strikes_landed']],
            'blue_avg_strikes_absorbed': [blue_fighter['avg_strikes_absorbed']],
            'blue_avg_takedowns_landed': [blue_fighter['avg_takedowns_landed']],
            'blue_avg_takedowns_absorbed': [blue_fighter['avg_takedowns_absorbed']],
            'blue_avg_submission_attempts_landed': [blue_fighter['avg_submission_attempts_landed']],
            'blue_avg_submission_attempts_absorbed': [blue_fighter['avg_submission_attempts_absorbed']],
            'blue_avg_fight_time_min': [blue_fighter['avg_fight_time_min']],
            'blue_last_fight_days_since': [blue_fighter['last_fight_days_since']],
            'blue_last_win_days_since': [blue_fighter['last_win_days_since']],
            'blue_age_in_days': [blue_fighter['age_in_days']],
            'blue_head_strikes_landed': [blue_fighter['head_strikes_landed']],
            'blue_head_strikes_thrown': [blue_fighter['head_strikes_thrown']],
            'blue_body_strikes_landed': [blue_fighter['body_strikes_landed']],
            'blue_body_strikes_thrown': [blue_fighter['body_strikes_thrown']],
            'blue_leg_strikes_landed': [blue_fighter['leg_strikes_landed']],
            'blue_leg_strikes_thrown': [blue_fighter['leg_strikes_thrown']],
            'blue_distance_strikes_landed': [blue_fighter['distance_strikes_landed']],
            'blue_distance_strikes_thrown': [blue_fighter['distance_strikes_thrown']],
            'blue_clinch_strikes_landed': [blue_fighter['clinch_strikes_landed']],
            'blue_clinch_strikes_thrown': [blue_fighter['clinch_strikes_thrown']],
            'blue_ground_strikes_landed': [blue_fighter['ground_strikes_landed']],
            'blue_ground_strikes_thrown': [blue_fighter['ground_strikes_thrown']],
            'blue_head_strikes_landed_opponent': [blue_fighter['head_strikes_landed_opponent']],
            'blue_head_strikes_thrown_opponent': [blue_fighter['head_strikes_thrown_opponent']],
            'blue_body_strikes_landed_opponent': [blue_fighter['body_strikes_landed_opponent']],
            'blue_body_strikes_thrown_opponent': [blue_fighter['body_strikes_thrown_opponent']],
            'blue_leg_strikes_landed_opponent': [blue_fighter['leg_strikes_landed_opponent']],
            'blue_leg_strikes_thrown_opponent': [blue_fighter['leg_strikes_thrown_opponent']],
            'blue_distance_strikes_landed_opponent': [blue_fighter['distance_strikes_landed_opponent']],
            'blue_distance_strikes_thrown_opponent': [blue_fighter['distance_strikes_thrown_opponent']],
            'blue_clinch_strikes_landed_opponent': [blue_fighter['clinch_strikes_landed_opponent']],
            'blue_clinch_strikes_thrown_opponent': [blue_fighter['clinch_strikes_thrown_opponent']],
            'blue_ground_strikes_landed_opponent': [blue_fighter['ground_strikes_landed_opponent']],
            'blue_ground_strikes_thrown_opponent': [blue_fighter['ground_strikes_thrown_opponent']],
            'blue_knockdowns_landed_per_minute': [blue_fighter['knockdowns_landed_per_minute']],
            'blue_knockdowns_landed_per_round': [blue_fighter['knockdowns_landed_per_round']],
            'blue_knockdowns_absorbed_per_minute': [blue_fighter['knockdowns_absorbed_per_minute']],
            'blue_knockdowns_absorbed_per_round': [blue_fighter['knockdowns_absorbed_per_round']],
            'blue_strikes_landed_per_minute': [blue_fighter['strikes_landed_per_minute']],
            'blue_strikes_landed_per_round': [blue_fighter['strikes_landed_per_round']],
            'blue_strikes_absorbed_per_minute': [blue_fighter['strikes_absorbed_per_minute']],
            'blue_strikes_absorbed_per_round': [blue_fighter['strikes_absorbed_per_round']],
            'blue_takedowns_landed_per_minute': [blue_fighter['takedowns_landed_per_minute']],
            'blue_takedowns_landed_per_round': [blue_fighter['takedowns_landed_per_round']],
            'blue_takedowns_absorbed_per_minute': [blue_fighter['takedowns_absorbed_per_minute']],
            'blue_takedowns_absorbed_per_round': [blue_fighter['takedowns_absorbed_per_round']],
            'blue_sub_attempts_landed_per_minute': [blue_fighter['sub_attempts_landed_per_minute']],
            'blue_sub_attempts_landed_per_round': [blue_fighter['sub_attempts_landed_per_round']],
            'blue_sub_attempts_absorbed_per_minute': [blue_fighter['sub_attempts_absorbed_per_minute']],
            'blue_sub_attempts_absorbed_per_round': [blue_fighter['sub_attempts_absorbed_per_round']],
            'blue_head_strike_accuracy': [blue_fighter['head_strike_accuracy']],
            'blue_body_strike_accuracy': [blue_fighter['body_strike_accuracy']],
            'blue_leg_strike_accuracy': [blue_fighter['leg_strike_accuracy']],
            'blue_distance_strike_accuracy': [blue_fighter['distance_strike_accuracy']],
            'blue_clinch_strike_accuracy': [blue_fighter['clinch_strike_accuracy']],
            'blue_ground_strike_accuracy': [blue_fighter['ground_strike_accuracy']],
            'blue_head_strike_defense': [blue_fighter['head_strike_defense']],
            'blue_body_strike_defense': [blue_fighter['body_strike_defense']],
            'blue_leg_strike_defense': [blue_fighter['leg_strike_defense']]
        })

        differentials = calculate_differentials(red_fighter, blue_fighter)

        for key, value in differentials.items():
            matchup_data[key] = value

        return matchup_data

    def make_prediction(self, prediction_data):
        """Make prediction using model"""

        #convert data to numpy array
        X = prediction_data.values

        prediction = self.model.predict(X)

        return prediction

    def _calculate_results(self, prediction, artifacts):
        result_probs = prediction[0][0]
        win_method_probs = prediction[1][0]

        result_class_idx = np.argmax(result_probs)
        win_method_class_idx = np.argmax(win_method_probs)

        result_class = artifacts['label_encoders']['result'].inverse_transform(np.array([result_class_idx]))[0]
        win_method_class = artifacts['label_encoders']['win_method'].inverse_transform(np.array([win_method_class_idx]))[0]

        result_percentage = result_probs[result_class_idx] * 100
        win_method_percentage = win_method_probs[win_method_class_idx] * 100

        return result_class, result_percentage, win_method_class, win_method_percentage

    def _display_results(self, result_class, result_percentage, win_method_class, win_method_percentage):

        print(f"result: winner: {result_class}, prob: {result_percentage}")

        print(f"win method: {win_method_class}, prob: {win_method_percentage}")

    def main(self):
        """
        Main function to load the model and fighter data.
        """
        self.model = self.load_model()
        artifacts = self.load_preprocessing_artifacts()
        fighter_data = self.load_fighter_data()

        # find fighters
        fighter1 = self.find_fighter(self.fighter1, fighter_data) # Alex Pereira
        fighter2 = self.find_fighter(self.fighter2, fighter_data) # Caio Borralho

        # if atleast one fighter not found
        if fighter1 is None or fighter2 is None:
            print("Can't make prediction without both fighter data")
            return

        # prepare prediction
        prediction_data = self.prepare_prediction_data(fighter1, fighter2)

        prediction_data['total_rounds'] = 5

        prediction = self.make_prediction(prediction_data)

        result_class, result_percentage, win_method_class, win_method_percentage = self._calculate_results(prediction, artifacts)

        if self.test_run:
            prediction_data.to_csv("data/prediction.csv", index=False)
            self._display_results(result_class, result_percentage, win_method_class, win_method_percentage)

        return {
            "result": {
                "winner": result_class,
                "probability": result_percentage
            },
            "win_method": {
                "method": win_method_class,
                "probability": win_method_percentage
            }
        }

if __name__ == '__main__':
    predictor = UFCPredictor(fighter1="e5549c82bfb5582d", fighter2="4126a78111c0855a", test_run=True)
    predictor.main()
