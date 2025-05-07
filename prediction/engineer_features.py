import pandas as pd

def engineer_features(target_df: pd.DataFrame) -> pd.DataFrame:
    """
    Create new features for prediction

    Args:
        df: DataFrame

    Returns:
        DataFrame with engineered features
    """

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
    target_df['red_strike_efficiency'] = target_df['red_strikes_landed'] / target_df['red_strikes_thrown'].where(
        target_df['red_strikes_thrown'] > 0, 1)
    target_df['blue_strike_efficiency'] = target_df['blue_strikes_landed'] / target_df['blue_strikes_thrown'].where(
        target_df['blue_strikes_thrown'] > 0, 1)
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

        target_df[f'{corner}_ko_loss_rate'] = target_df[f'{corner}_losses_by_ko'] / total_losses.where(total_losses > 0,
                                                                                                       1)
        target_df[f'{corner}_sub_loss_rate'] = target_df[f'{corner}_losses_by_sub'] / total_losses.where(
            total_losses > 0, 1)
        target_df[f'{corner}_decision_loss_rate'] = target_df[f'{corner}_losses_by_dec'] / total_losses.where(
            total_losses > 0, 1)

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
    target_df['sub_attempt_frequency_diff'] = (
                target_df['red_sub_attempt_frequency'] - target_df['blue_sub_attempt_frequency'])

    # fight style
    for corner in ['red', 'blue']:
        # striking vs grappling preference
        total_offensive_actions = (target_df[f'{corner}_strikes_thrown'] +
                                   target_df[f'{corner}_takedowns_landed'] +
                                   target_df[f'{corner}_sub_attempts_landed'])

        # striking preference
        target_df[f'{corner}_striking_preference'] = (target_df[f'{corner}_strikes_thrown'] /
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
    target_df['grappling_preference_diff'] = target_df['red_grappling_preference'] - target_df[
        'blue_grappling_preference']
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
    target_df['head_strike_damage_ratio_diff'] = target_df['red_head_strike_damage_ratio'] - target_df[
        'blue_head_strike_damage_ratio']

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
                                             target_df[f'{corner}_total_time_minutes'].where(
                                                 target_df[f'{corner}_total_time_minutes'] > 0, 1))

    # fight pace differentials
    target_df['avg_fight_length_diff'] = target_df['red_avg_fight_length'] - target_df['blue_avg_fight_length']
    target_df['fight_pace_diff'] = target_df['red_fight_pace'] - target_df['blue_fight_pace']

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
