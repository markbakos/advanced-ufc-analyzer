import pandas as pd

def engineer_features(target_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create new features for prediction

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
