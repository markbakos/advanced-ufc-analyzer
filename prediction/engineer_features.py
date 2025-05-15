import pandas as pd

def engineer_features_fights(target_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create new features for prediction for fights_df

    Args:
        df: DataFrame

    Returns:
        DataFrame with engineered features
    """

    ## v1 0.6462418437004089

    #
    # basic differences and efficiencies
    #

    # calculate experience difference
    target_df['experience_diff'] = target_df['red_total_ufc_fights'] - target_df['blue_total_ufc_fights']

    # calculate win rate differences
    target_df['win_rate_diff'] = (target_df['red_wins_in_ufc'] / target_df['red_total_ufc_fights'].where(
        target_df['red_total_ufc_fights'] > 0, 1)) - \
                                 (target_df['blue_wins_in_ufc'] / target_df['blue_total_ufc_fights'].where(
                                     target_df['blue_total_ufc_fights'] > 0, 1))

    # calculate takedown differentials
    target_df['takedown_diff'] = target_df['red_takedowns_landed'] - target_df['blue_takedowns_landed']

    #
    # striking differentials from here:
    #

    # total strikes, per round, per minute
    target_df['total_strike_diff'] = target_df['red_strikes_landed'] - target_df['blue_strikes_landed']
    target_df['total_strike_diff_per_round'] = target_df['red_strikes_landed_per_round'] - target_df[
        'blue_strikes_landed_per_round']
    target_df['total_strike_diff_per_minute'] = target_df['red_strikes_landed_per_minute'] - target_df[
        'blue_strikes_landed_per_minute']

    # location differentials
    target_df['total_head_strike_diff'] = target_df['red_head_strikes_landed'] - target_df['blue_head_strikes_landed']
    target_df['total_body_strike_diff'] = target_df['red_body_strikes_landed'] - target_df['blue_body_strikes_landed']
    target_df['total_leg_strike_diff'] = target_df['red_leg_strikes_landed'] - target_df['blue_leg_strikes_landed']

    # position differentirals
    target_df['distance_strike_diff'] = target_df['red_distance_strikes_landed'] - target_df[
        'blue_distance_strikes_landed']
    target_df['clinch_strike_diff'] = target_df['red_clinch_strikes_landed'] - target_df['blue_clinch_strikes_landed']
    target_df['ground_strike_diff'] = target_df['red_ground_strikes_landed'] - target_df['blue_ground_strikes_landed']

    ## v2 0.6654411554336548  -  +0.019199312

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
    target_df['distance_accuracy_diff'] = target_df['red_distance_strike_accuracy'] - target_df[
        'blue_distance_strike_accuracy']
    target_df['clinch_accuracy_diff'] = target_df['red_clinch_strike_accuracy'] - target_df[
        'blue_clinch_strike_accuracy']
    target_df['ground_accuracy_diff'] = target_df['red_ground_strike_accuracy'] - target_df[
        'blue_ground_strike_accuracy']

    ## v8

    # strike defense
    for corner in ['red', 'blue']:
        # head strike defense
        target_df[f'{corner}_head_strike_defense'] = (1 -
                                                      (target_df[f'{corner}_head_strikes_landed_opponent'] /
                                                       target_df[f'{corner}_head_strikes_thrown_opponent']).where(
                                                          target_df[f'{corner}_head_strikes_thrown_opponent'] > 0, 1))

        # body strike defense
        target_df[f'{corner}_body_strike_defense'] = (1 -
                                                      (target_df[f'{corner}_body_strikes_landed_opponent'] /
                                                       target_df[f'{corner}_body_strikes_thrown_opponent']).where(
                                                          target_df[f'{corner}_body_strikes_thrown_opponent'] > 0, 1))

        # leg strike defense
        target_df[f'{corner}_leg_strike_defense'] = 1 - (target_df[f'{corner}_leg_strikes_landed_opponent'] /
                                                         target_df[f'{corner}_leg_strikes_thrown_opponent']).where(
            target_df[f'{corner}_leg_strikes_thrown_opponent'] > 0, 1)

    # strike defense differentials
    target_df['head_strike_defense_diff'] = target_df['red_head_strike_defense'] - target_df['blue_head_strike_defense']
    target_df['body_strike_defense_diff'] = target_df['red_body_strike_defense'] - target_df['blue_body_strike_defense']
    target_df['leg_strike_defense_diff'] = target_df['red_leg_strike_defense'] - target_df['blue_leg_strike_defense']

    return target_df

def engineer_features_fighter(target_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create new features for prediction for fighters

    Args:
        df: DataFrame

    Returns:
        DataFrame with engineered features
    """

    #
    #  efficiencies
    #

    # strike accuracy

    # head strike accuracy
    target_df[f'head_strike_accuracy'] = target_df[f'head_strikes_landed'] / target_df[
        f'head_strikes_thrown'].where(target_df[f'head_strikes_thrown'] > 0, 1)

        # body strike accuracy
    target_df[f'body_strike_accuracy'] = target_df[f'body_strikes_landed'] / target_df[
        f'body_strikes_thrown'].where(target_df[f'body_strikes_thrown'] > 0, 1)

    # leg strike accuracy
    target_df[f'leg_strike_accuracy'] = target_df[f'leg_strikes_landed'] / target_df[
        f'leg_strikes_thrown'].where(target_df[f'leg_strikes_thrown'] > 0, 1)

    # distance strikes
    target_df[f'distance_strike_accuracy'] = target_df[f'distance_strikes_landed'] / \
                                                      target_df[f'distance_strikes_thrown'].where(
                                                          target_df[f'distance_strikes_thrown'] > 0, 1)

    # clinch strike accuracy
    target_df[f'clinch_strike_accuracy'] = target_df[f'clinch_strikes_landed'] / target_df[
        f'clinch_strikes_thrown'].where(target_df[f'clinch_strikes_thrown'] > 0, 1)

    # ground strikes accuracy
    target_df[f'ground_strike_accuracy'] = target_df[f'ground_strikes_landed'] / target_df[
        f'ground_strikes_thrown'].where(target_df[f'ground_strikes_thrown'] > 0, 1)

    ## v8

    # strike defense

    # head strike defense
    target_df[f'head_strike_defense'] = (1 -
                            (target_df[f'head_strikes_landed_opponent'] /
                            target_df[f'head_strikes_thrown_opponent']).where(
                            target_df[f'head_strikes_thrown_opponent'] > 0, 1))

    # body strike defense
    target_df[f'body_strike_defense'] = (1 -
                            (target_df[f'body_strikes_landed_opponent'] /
                            target_df[f'body_strikes_thrown_opponent']).where(
                            target_df[f'body_strikes_thrown_opponent'] > 0, 1))

    # leg strike defense
    target_df[f'leg_strike_defense'] = 1 - (target_df[f'leg_strikes_landed_opponent'] /
                                            target_df[f'leg_strikes_thrown_opponent']).where(
                                            target_df[f'leg_strikes_thrown_opponent'] > 0, 1)


    return target_df

def calculate_differentials(fighter1: pd.DataFrame, fighter2: pd.DataFrame) -> pd.DataFrame:
    """
    Calculate differentials between two fighters
    """
    differentials = pd.DataFrame()

    differentials['experience_diff'] = pd.Series(fighter1['total_ufc_fights']) - pd.Series(fighter2['total_ufc_fights'])

    # calculate win rate differences
    differentials['win_rate_diff'] = (fighter1['wins_in_ufc'] / (
        fighter1['total_ufc_fights'] if fighter1['total_ufc_fights'] > 0 else 1)) - \
                                     (fighter2['wins_in_ufc'] / (
                                         fighter2['total_ufc_fights'] if fighter2['total_ufc_fights'] > 0 else 1))

    # calculate takedown differentials
    differentials['takedown_diff'] = fighter1['takedowns_landed'] - fighter2['takedowns_landed']

    # total strikes, per round, per minute
    differentials['total_strike_diff'] = fighter1['strikes_landed'] - fighter2['strikes_landed']
    differentials['total_strike_diff_per_round'] = fighter1['strikes_landed_per_round'] - fighter2[
        'strikes_landed_per_round']
    differentials['total_strike_diff_per_minute'] = fighter1['strikes_landed_per_minute'] - fighter2[
        'strikes_landed_per_minute']

    # location differentials
    differentials['total_head_strike_diff'] = fighter1['head_strikes_landed'] - fighter2['head_strikes_landed']
    differentials['total_body_strike_diff'] = fighter1['body_strikes_landed'] - fighter2['body_strikes_landed']
    differentials['total_leg_strike_diff'] = fighter1['leg_strikes_landed'] - fighter2['leg_strikes_landed']

    # position differentials
    differentials['distance_strike_diff'] = fighter1['distance_strikes_landed'] - fighter2['distance_strikes_landed']
    differentials['clinch_strike_diff'] = fighter1['clinch_strikes_landed'] - fighter2['clinch_strikes_landed']
    differentials['ground_strike_diff'] = fighter1['ground_strikes_landed'] - fighter2['ground_strikes_landed']

    # accuracy differentials
    differentials['head_accuracy_diff'] = fighter1['head_strike_accuracy'] - fighter2['head_strike_accuracy']
    differentials['body_accuracy_diff'] = fighter1['body_strike_accuracy'] - fighter2['body_strike_accuracy']
    differentials['leg_accuracy_diff'] = fighter1['leg_strike_accuracy'] - fighter2['leg_strike_accuracy']
    differentials['distance_accuracy_diff'] = fighter1['distance_strike_accuracy'] - fighter2['distance_strike_accuracy']
    differentials['clinch_accuracy_diff'] = fighter1['clinch_strike_accuracy'] - fighter2['clinch_strike_accuracy']
    differentials['ground_accuracy_diff'] = fighter1['ground_strike_accuracy'] - fighter2['ground_strike_accuracy']

    # defense differentials
    differentials['head_strike_defense_diff'] = fighter1['head_strike_defense'] - fighter2['head_strike_defense']
    differentials['body_strike_defense_diff'] = fighter1['body_strike_defense'] - fighter2['body_strike_defense']
    differentials['leg_strike_defense_diff'] = fighter1['leg_strike_defense'] - fighter2['leg_strike_defense']

    return differentials