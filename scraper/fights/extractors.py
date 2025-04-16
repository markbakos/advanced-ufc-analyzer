import logging
from typing import Dict, Any
from bs4 import BeautifulSoup
from scraper.utils import safe_int_convert, safe_float_convert

LOGGER = logging.getLogger(__name__)

def extract_fighters(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extracts the fighters from the soup
    
    Returns:
        Dictionary containing fighter information:
        - red_fighter: Name of the red corner fighter
        - blue_fighter: Name of the blue corner fighter
        - red_fighter_id: ID of the red corner fighter
        - blue_fighter_id: ID of the blue corner fighter
        - result: Result of the fight (blue/red/draw)
    """
    result = {
        'red_fighter': None,
        'blue_fighter': None,
        'red_fighter_id': None,
        'blue_fighter_id': None,
        'result': None,
    }

    try:
        fighters_result = soup.select_one('div.b-fight-details__persons')
        if not fighters_result:
            LOGGER.warning(f"Could not find fighters result on page")
            return result
            
        # extract both fighter divs
        fighter_divs = fighters_result.select('div.b-fight-details__person')
        if len(fighter_divs) < 2:
            LOGGER.warning(f"Could not find both fighter divs on page")
            return result
            
        # first div is red corner fighter
        red_fighter_div = fighter_divs[0]
        # second div is blue corner fighter
        blue_fighter_div = fighter_divs[1]
        
        # extract red fighter info
        red_status = red_fighter_div.select_one('i.b-fight-details__person-status')
        red_name_elem = red_fighter_div.select_one('a.b-fight-details__person-link')
        
        if red_name_elem:
            result['red_fighter'] = red_name_elem.get_text(strip=True)
            result['red_fighter_id'] = red_name_elem.get('href', '').split('/')[-1]
            
        # extract blue fighter info
        blue_name_elem = blue_fighter_div.select_one('a.b-fight-details__person-link')
        
        if blue_name_elem:
            result['blue_fighter'] = blue_name_elem.get_text(strip=True)
            result['blue_fighter_id'] = blue_name_elem.get('href', '').split('/')[-1]
            
        # determine result
        blue_status = blue_fighter_div.select_one('i.b-fight-details__person-status')
        if red_status and blue_status:
            red_result = red_status.get_text(strip=True)
            blue_result = blue_status.get_text(strip=True)
            
            if red_result == 'W' and blue_result == 'L':
                result['result'] = 'red'
            elif red_result == 'L' and blue_result == 'W':
                result['result'] = 'blue'
            elif red_result == 'D' and blue_result == 'D':
                result['result'] = 'draw'
            else:
                result['result'] = 'unknown'

    except Exception as e:
        LOGGER.error(f"Error extracting fighters: {e}")
        return result
                
    return result

def extract_fight_data(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extracts the fight data from the soup
    """
    result = {
        'win_method': None,
        'round': None,
        'total_rounds': None,
        'time': None,
        'referee': None
    }

    try:
        fight_details_content = soup.select_one('div.b-fight-details__content')
        if not fight_details_content:
            LOGGER.warning(f"Could not find fight details content on page")
            return result
        
        fight_details_text = fight_details_content.select_one('p.b-fight-details__text')
        if not fight_details_text:
            LOGGER.warning(f"Could not find fight details text on page")
            return result
        
        # extract method
        method_item = fight_details_text.select_one('i.b-fight-details__text-item_first:has(i.b-fight-details__label:-soup-contains("Method:"))')
        if method_item:
            method_text = method_item.select_one('i[style="font-style: normal"]')
            if method_text:
                result['win_method'] = method_text.get_text(strip=True)
        
        # extract round
        round_item = fight_details_text.select_one('i.b-fight-details__text-item:has(i.b-fight-details__label:-soup-contains("Round:"))')
        if round_item:
            round_text = round_item.get_text(strip=True).replace('Round:', '').strip()
            result['round'] = safe_int_convert(round_text)
        
        # extract time
        time_item = fight_details_text.select_one('i.b-fight-details__text-item:has(i.b-fight-details__label:-soup-contains("Time:"))')
        if time_item:
            time_text = time_item.get_text(strip=True).replace('Time:', '').strip()
            result['time'] = time_text
        
        # extract time format
        time_format_item = fight_details_text.select_one('i.b-fight-details__text-item:has(i.b-fight-details__label:-soup-contains("Time format:"))')
        if time_format_item:
            time_format_text = time_format_item.get_text(strip=True).replace('Time format:', '').strip().split(' ')[0]
            result['total_rounds'] = safe_int_convert(time_format_text)
        
        # extract referee
        referee_item = fight_details_text.select_one('i.b-fight-details__text-item:has(i.b-fight-details__label:-soup-contains("Referee:"))')
        if referee_item:
            referee_span = referee_item.select_one('span')
            if referee_span:
                result['referee'] = referee_span.get_text(strip=True)

    except Exception as e:
        LOGGER.error(f"Error extracting fight data: {e}")
        return result

    return result

def extract_fight_stats(soup: BeautifulSoup, rounds: int) -> Dict[str, Any]:
    """
    Extracts the fight stats from the soup
    """
    result = {
            'red_knockdowns_landed': None,
            'red_sig_strikes_landed': None,
            'red_sig_strikes_thrown': None,
            'red_sig_strike_percent': None,
            'red_total_strikes_landed': None,
            'red_total_strikes_thrown': None,
            'red_takedowns_landed': None,
            'red_takedowns_attempted': None,
            'red_takedowns_percent': None,
            'red_sub_attempts': None,
            'red_reversals': None,
            'red_control_time': None,

            'blue_knockdowns_landed': None,
            'blue_sig_strikes_landed': None,
            'blue_sig_strikes_thrown': None,
            'blue_sig_strike_percent': None,
            'blue_total_strikes_landed': None,
            'blue_total_strikes_thrown': None,
            'blue_takedowns_landed': None,
            'blue_takedowns_attempted': None,
            'blue_takedowns_percent': None,
            'blue_sub_attempts': None,
            'blue_reversals': None,
            'blue_control_time': None,

            'red_head_strikes_landed': None,
            'red_head_strikes_thrown': None,
            'red_body_strikes_landed': None,
            'red_body_strikes_thrown': None,
            'red_leg_strikes_landed': None,
            'red_leg_strikes_thrown': None,
            'red_distance_strikes_landed': None,
            'red_distance_strikes_thrown': None,
            'red_clinch_strikes_landed': None,
            'red_clinch_strikes_thrown': None,
            'red_ground_strikes_landed': None,
            'red_ground_strikes_thrown': None,

            'blue_head_strikes_landed': None,
            'blue_head_strikes_thrown': None,
            'blue_body_strikes_landed': None,
            'blue_body_strikes_thrown': None,
            'blue_leg_strikes_landed': None,
            'blue_leg_strikes_thrown': None,
            'blue_distance_strikes_landed': None,
            'blue_distance_strikes_thrown': None,
            'blue_clinch_strikes_landed': None,
            'blue_clinch_strikes_thrown': None,
            'blue_ground_strikes_landed': None,
            'blue_ground_strikes_thrown': None,
        }

    try:
        stats_tables = soup.select('table tbody.b-fight-details__table-body tr.b-fight-details__table-row')
        if not stats_tables or len(stats_tables) < 2:
            LOGGER.warning(f"Could not find stats table on page")
            return result

        # get the first table which contains both fighter total stats
        total_stats_table = stats_tables[0]
        if not total_stats_table:
            LOGGER.warning(f"Could not find total stats table on page")
            return result

        # extract all table cells
        table_cells = total_stats_table.select('td.b-fight-details__table-col')
        if len(table_cells) < 10:  # we expect at least 10 columns of data
            LOGGER.warning(f"Could not find all required table cells on page")
            return result

        # extract knockdowns (second column)
        knockdowns_cell = table_cells[1]
        knockdowns_texts = knockdowns_cell.select('p.b-fight-details__table-text')
        if len(knockdowns_texts) >= 2:
            result['red_knockdowns_landed'] = safe_int_convert(knockdowns_texts[0].get_text(strip=True))
            result['blue_knockdowns_landed'] = safe_int_convert(knockdowns_texts[1].get_text(strip=True))

        # extract significant strikes landed (third column)
        sig_strikes_cell = table_cells[2]
        sig_strikes_texts = sig_strikes_cell.select('p.b-fight-details__table-text')
        if len(sig_strikes_texts) >= 2:
            result['red_sig_strikes_landed'] = safe_int_convert(sig_strikes_texts[0].get_text(strip=True).split(' ')[0])
            result['blue_sig_strikes_landed'] = safe_int_convert(sig_strikes_texts[1].get_text(strip=True).split(' ')[0])

            result['red_sig_strikes_thrown'] = safe_int_convert(sig_strikes_texts[0].get_text(strip=True).split(' ')[-1])
            result['blue_sig_strikes_thrown'] = safe_int_convert(sig_strikes_texts[1].get_text(strip=True).split(' ')[-1])

        # extract significant strike percentage (fourth column)
        sig_strike_percent_cell = table_cells[3]
        sig_strike_percent_texts = sig_strike_percent_cell.select('p.b-fight-details__table-text')
        if len(sig_strike_percent_texts) >= 2:
            result['red_sig_strike_percent'] = safe_float_convert(sig_strike_percent_texts[0].get_text(strip=True).replace('%', ''))
            result['blue_sig_strike_percent'] = safe_float_convert(sig_strike_percent_texts[1].get_text(strip=True).replace('%', ''))

        # extract total strikes (fifth column)
        total_strikes_cell = table_cells[4]
        total_strikes_texts = total_strikes_cell.select('p.b-fight-details__table-text')
        if len(total_strikes_texts) >= 2:
            result['red_total_strikes_landed'] = safe_int_convert(total_strikes_texts[0].get_text(strip=True).split(' ')[0])
            result['blue_total_strikes_landed'] = safe_int_convert(total_strikes_texts[1].get_text(strip=True).split(' ')[0])

            result['red_total_strikes_thrown'] = safe_int_convert(total_strikes_texts[0].get_text(strip=True).split(' ')[-1])
            result['blue_total_strikes_thrown'] = safe_int_convert(total_strikes_texts[1].get_text(strip=True).split(' ')[-1])

        # extract takedowns landed (sixth column)
        takedowns_cell = table_cells[5]
        takedowns_texts = takedowns_cell.select('p.b-fight-details__table-text')
        if len(takedowns_texts) >= 2:
            result['red_takedowns_landed'] = safe_int_convert(takedowns_texts[0].get_text(strip=True).split(' ')[0])
            result['blue_takedowns_landed'] = safe_int_convert(takedowns_texts[1].get_text(strip=True).split(' ')[0])

            result['red_takedowns_attempted'] = safe_int_convert(takedowns_texts[0].get_text(strip=True).split(' ')[-1])
            result['blue_takedowns_attempted'] = safe_int_convert(takedowns_texts[1].get_text(strip=True).split(' ')[-1])

        # extract takedown percentage (seventh column)
        takedown_percent_cell = table_cells[6]
        takedown_percent_texts = takedown_percent_cell.select('p.b-fight-details__table-text')
        if len(takedown_percent_texts) >= 2:
            result['red_takedowns_percent'] = safe_float_convert(takedown_percent_texts[0].get_text(strip=True).replace('%', ''))
            result['blue_takedowns_percent'] = safe_float_convert(takedown_percent_texts[1].get_text(strip=True).replace('%', ''))

        # extract submission attempts (eighth column)
        sub_attempts_cell = table_cells[7]
        sub_attempts_texts = sub_attempts_cell.select('p.b-fight-details__table-text')
        if len(sub_attempts_texts) >= 2:
            result['red_sub_attempts'] = safe_int_convert(sub_attempts_texts[0].get_text(strip=True))
            result['blue_sub_attempts'] = safe_int_convert(sub_attempts_texts[1].get_text(strip=True))

        # extract reversals (ninth column)
        reversals_cell = table_cells[8]
        reversals_texts = reversals_cell.select('p.b-fight-details__table-text')
        if len(reversals_texts) >= 2:
            result['red_reversals'] = safe_int_convert(reversals_texts[0].get_text(strip=True))
            result['blue_reversals'] = safe_int_convert(reversals_texts[1].get_text(strip=True))

        # extract control time (tenth column)
        control_time_cell = table_cells[9]
        control_time_texts = control_time_cell.select('p.b-fight-details__table-text')
        if len(control_time_texts) >= 2:
            result['red_control_time'] = control_time_texts[0].get_text(strip=True)
            result['blue_control_time'] = control_time_texts[1].get_text(strip=True)

        # extract strike detail table

        total_strike_detail_table = stats_tables[1+rounds]
        if not total_strike_detail_table:
            LOGGER.warning(f"Could not find strike detail table on page")
            return result

        # extract all table cells
        strike_detail_table_cells = total_strike_detail_table.select('td.b-fight-details__table-col')
        if len(strike_detail_table_cells) < 9:
            LOGGER.warning(f"Could not find all required table cells on page")
            return result

        # extract head strikes landed (fourth column)
        head_strikes_landed_cell = strike_detail_table_cells[3]
        head_strikes_landed_texts = head_strikes_landed_cell.select('p.b-fight-details__table-text')
        if len(head_strikes_landed_texts) >= 2:
            result['red_head_strikes_landed'] = safe_int_convert(head_strikes_landed_texts[0].get_text(strip=True).split(' ')[0])
            result['blue_head_strikes_landed'] = safe_int_convert(head_strikes_landed_texts[1].get_text(strip=True).split(' ')[0])

            result['red_head_strikes_thrown'] = safe_int_convert(head_strikes_landed_texts[0].get_text(strip=True).split(' ')[-1])
            result['blue_head_strikes_thrown'] = safe_int_convert(head_strikes_landed_texts[1].get_text(strip=True).split(' ')[-1])
            
        # extract body strikes landed (fifth column)
        body_strikes_landed_cell = strike_detail_table_cells[4]
        body_strikes_landed_texts = body_strikes_landed_cell.select('p.b-fight-details__table-text')
        if len(body_strikes_landed_texts) >= 2:
            result['red_body_strikes_landed'] = safe_int_convert(body_strikes_landed_texts[0].get_text(strip=True).split(' ')[0])
            result['blue_body_strikes_landed'] = safe_int_convert(body_strikes_landed_texts[1].get_text(strip=True).split(' ')[0])

            result['red_body_strikes_thrown'] = safe_int_convert(body_strikes_landed_texts[0].get_text(strip=True).split(' ')[-1])
            result['blue_body_strikes_thrown'] = safe_int_convert(body_strikes_landed_texts[1].get_text(strip=True).split(' ')[-1])
        
        # extract leg strikes landed (sixth column)
        leg_strikes_landed_cell = strike_detail_table_cells[5]
        leg_strikes_landed_texts = leg_strikes_landed_cell.select('p.b-fight-details__table-text')
        if len(leg_strikes_landed_texts) >= 2:
            result['red_leg_strikes_landed'] = safe_int_convert(leg_strikes_landed_texts[0].get_text(strip=True).split(' ')[0])
            result['blue_leg_strikes_landed'] = safe_int_convert(leg_strikes_landed_texts[1].get_text(strip=True).split(' ')[0])

            result['red_leg_strikes_thrown'] = safe_int_convert(leg_strikes_landed_texts[0].get_text(strip=True).split(' ')[-1])
            result['blue_leg_strikes_thrown'] = safe_int_convert(leg_strikes_landed_texts[1].get_text(strip=True).split(' ')[-1])
        
        # extract distance strikes landed (seventh column)
        distance_strikes_landed_cell = strike_detail_table_cells[6]
        distance_strikes_landed_texts = distance_strikes_landed_cell.select('p.b-fight-details__table-text')
        if len(distance_strikes_landed_texts) >= 2:
            result['red_distance_strikes_landed'] = safe_int_convert(distance_strikes_landed_texts[0].get_text(strip=True).split(' ')[0])
            result['blue_distance_strikes_landed'] = safe_int_convert(distance_strikes_landed_texts[1].get_text(strip=True).split(' ')[0])

            result['red_distance_strikes_thrown'] = safe_int_convert(distance_strikes_landed_texts[0].get_text(strip=True).split(' ')[-1])
            result['blue_distance_strikes_thrown'] = safe_int_convert(distance_strikes_landed_texts[1].get_text(strip=True).split(' ')[-1])

        # extract clinch strikes landed (eighth column)
        clinch_strikes_landed_cell = strike_detail_table_cells[7]
        clinch_strikes_landed_texts = clinch_strikes_landed_cell.select('p.b-fight-details__table-text')
        if len(clinch_strikes_landed_texts) >= 2:
            result['red_clinch_strikes_landed'] = safe_int_convert(clinch_strikes_landed_texts[0].get_text(strip=True).split(' ')[0])
            result['blue_clinch_strikes_landed'] = safe_int_convert(clinch_strikes_landed_texts[1].get_text(strip=True).split(' ')[0])

            result['red_clinch_strikes_thrown'] = safe_int_convert(clinch_strikes_landed_texts[0].get_text(strip=True).split(' ')[-1])
            result['blue_clinch_strikes_thrown'] = safe_int_convert(clinch_strikes_landed_texts[1].get_text(strip=True).split(' ')[-1])

        # extract ground strikes landed (ninth column)
        ground_strikes_landed_cell = strike_detail_table_cells[8]
        ground_strikes_landed_texts = ground_strikes_landed_cell.select('p.b-fight-details__table-text')
        if len(ground_strikes_landed_texts) >= 2:
            result['red_ground_strikes_landed'] = safe_int_convert(ground_strikes_landed_texts[0].get_text(strip=True).split(' ')[0])
            result['blue_ground_strikes_landed'] = safe_int_convert(ground_strikes_landed_texts[1].get_text(strip=True).split(' ')[0])

            result['red_ground_strikes_thrown'] = safe_int_convert(ground_strikes_landed_texts[0].get_text(strip=True).split(' ')[-1])
            result['blue_ground_strikes_thrown'] = safe_int_convert(ground_strikes_landed_texts[1].get_text(strip=True).split(' ')[-1])

    except Exception as e:
        LOGGER.error(f"Error extracting fight stats: {e}")
        return result

    return result


def extract_total_stats(soup: BeautifulSoup, rounds: int) -> Dict[str, Any]:
    """
    Extracts the round stats from the soup
    """
    result = {
            # total stats
            'red_knockdowns_landed': None,
            'red_sig_strikes_landed': None,
            'red_sig_strikes_thrown': None,
            'red_sig_strike_percent': None,
            'red_total_strikes_landed': None,
            'red_total_strikes_thrown': None,
            'red_takedowns_landed': None,
            'red_takedowns_attempted': None,
            'red_takedowns_percent': None,
            'red_sub_attempts': None,
            'red_reversals': None,
            'red_control_time': None,

            'blue_knockdowns_landed': None,
            'blue_sig_strikes_landed': None,
            'blue_sig_strikes_thrown': None,
            'blue_sig_strike_percent': None,
            'blue_total_strikes_landed': None,
            'blue_total_strikes_thrown': None,
            'blue_takedowns_landed': None,
            'blue_takedowns_attempted': None,
            'blue_takedowns_percent': None,
            'blue_sub_attempts': None,
            'blue_reversals': None,
            'blue_control_time': None,

            #red round stats
            'red_knockdowns_landed_rd1': None,
            'red_sig_strikes_landed_rd1': None,
            'red_sig_strikes_thrown_rd1': None,
            'red_sig_strike_percent_rd1': None,
            'red_total_strikes_landed_rd1': None,
            'red_total_strikes_thrown_rd1': None,
            'red_takedowns_landed_rd1': None,
            'red_takedowns_attempted_rd1': None,
            'red_takedowns_percent_rd1': None,
            'red_sub_attempts_rd1': None,
            'red_reversals_rd1': None,
            'red_control_time_rd1': None,

            'red_knockdowns_landed_rd2': None,
            'red_sig_strikes_landed_rd2': None,
            'red_sig_strikes_thrown_rd2': None,
            'red_sig_strike_percent_rd2': None,
            'red_total_strikes_landed_rd2': None,
            'red_total_strikes_thrown_rd2': None,
            'red_takedowns_landed_rd2': None,
            'red_takedowns_attempted_rd2': None,
            'red_takedowns_percent_rd2': None,
            'red_sub_attempts_rd2': None,
            'red_reversals_rd2': None,
            'red_control_time_rd2': None,

            'red_knockdowns_landed_rd3': None,
            'red_sig_strikes_landed_rd3': None,
            'red_sig_strikes_thrown_rd3': None,
            'red_sig_strike_percent_rd3': None,
            'red_total_strikes_landed_rd3': None,
            'red_total_strikes_thrown_rd3': None,
            'red_takedowns_landed_rd3': None,
            'red_takedowns_attempted_rd3': None,
            'red_takedowns_percent_rd3': None,
            'red_sub_attempts_rd3': None,
            'red_reversals_rd3': None,
            'red_control_time_rd3': None,

            'red_knockdowns_landed_rd4': None,
            'red_sig_strikes_landed_rd4': None,
            'red_sig_strikes_thrown_rd4': None,
            'red_sig_strike_percent_rd4': None,
            'red_total_strikes_landed_rd4': None,
            'red_total_strikes_thrown_rd4': None,
            'red_takedowns_landed_rd4': None,
            'red_takedowns_attempted_rd4': None,
            'red_takedowns_percent_rd4': None,
            'red_sub_attempts_rd4': None,
            'red_reversals_rd4': None,
            'red_control_time_rd4': None,

            'red_knockdowns_landed_rd5': None,
            'red_sig_strikes_landed_rd5': None,
            'red_sig_strikes_thrown_rd5': None,
            'red_sig_strike_percent_rd5': None,
            'red_total_strikes_landed_rd5': None,
            'red_total_strikes_thrown_rd5': None,
            'red_takedowns_landed_rd5': None,
            'red_takedowns_attempted_rd5': None,
            'red_takedowns_percent_rd5': None,
            'red_sub_attempts_rd5': None,
            'red_reversals_rd5': None,
            'red_control_time_rd5': None,

            #blue round stats
            
            'blue_knockdowns_landed_rd1': None,
            'blue_sig_strikes_landed_rd1': None,
            'blue_sig_strikes_thrown_rd1': None,
            'blue_sig_strike_percent_rd1': None,
            'blue_total_strikes_landed_rd1': None,
            'blue_total_strikes_thrown_rd1': None,
            'blue_takedowns_landed_rd1': None,
            'blue_takedowns_attempted_rd1': None,
            'blue_takedowns_percent_rd1': None,
            'blue_sub_attempts_rd1': None,
            'blue_reversals_rd1': None,
            'blue_control_time_rd1': None,
        
            'blue_knockdowns_landed_rd2': None,
            'blue_sig_strikes_landed_rd2': None,
            'blue_sig_strikes_thrown_rd2': None,
            'blue_sig_strike_percent_rd2': None,
            'blue_total_strikes_landed_rd2': None,
            'blue_total_strikes_thrown_rd2': None,
            'blue_takedowns_landed_rd2': None,
            'blue_takedowns_attempted_rd2': None,
            'blue_takedowns_percent_rd2': None,
            'blue_sub_attempts_rd2': None,
            'blue_reversals_rd2': None,
            'blue_control_time_rd2': None,
        
            'blue_knockdowns_landed_rd3': None,
            'blue_sig_strikes_landed_rd3': None,
            'blue_sig_strikes_thrown_rd3': None,
            'blue_sig_strike_percent_rd3': None,
            'blue_total_strikes_landed_rd3': None,
            'blue_total_strikes_thrown_rd3': None,
            'blue_takedowns_landed_rd3': None,
            'blue_takedowns_attempted_rd3': None,
            'blue_takedowns_percent_rd3': None,
            'blue_sub_attempts_rd3': None,
            'blue_reversals_rd3': None,
            'blue_control_time_rd3': None,
        
            'blue_knockdowns_landed_rd4': None,
            'blue_sig_strikes_landed_rd4': None,
            'blue_sig_strikes_thrown_rd4': None,
            'blue_sig_strike_percent_rd4': None,
            'blue_total_strikes_landed_rd4': None,
            'blue_total_strikes_thrown_rd4': None,
            'blue_takedowns_landed_rd4': None,
            'blue_takedowns_attempted_rd4': None,
            'blue_takedowns_percent_rd4': None,
            'blue_sub_attempts_rd4': None,
            'blue_reversals_rd4': None,
            'blue_control_time_rd4': None,
        
            'blue_knockdowns_landed_rd5': None,
            'blue_sig_strikes_landed_rd5': None,
            'blue_sig_strikes_thrown_rd5': None,
            'blue_sig_strike_percent_rd5': None,
            'blue_total_strikes_landed_rd5': None,
            'blue_total_strikes_thrown_rd5': None,
            'blue_takedowns_landed_rd5': None,
            'blue_takedowns_attempted_rd5': None,
            'blue_takedowns_percent_rd5': None,
            'blue_sub_attempts_rd5': None,
            'blue_reversals_rd5': None,
            'blue_control_time_rd5': None,
    }
    
    for round in range(0, rounds):
        try:
            stats_tables = soup.select('table tbody.b-fight-details__table-body tr.b-fight-details__table-row')
            if not stats_tables or len(stats_tables) < 2:
                LOGGER.warning(f"Could not find stats table on page")
                return result

            # get the first table which contains both fighter total stats
            total_stats_table = stats_tables[round]
            if not total_stats_table:
                LOGGER.warning(f"Could not find total stats table on page")
                return result

            # extract all table cells
            table_cells = total_stats_table.select('td.b-fight-details__table-col')
            if len(table_cells) < 10:  # we expect at least 10 columns of data
                LOGGER.warning(f"Could not find all required table cells on page")
                return result

            # extract knockdowns (second column)
            knockdowns_cell = table_cells[1]
            knockdowns_texts = knockdowns_cell.select('p.b-fight-details__table-text')
            if len(knockdowns_texts) >= 2:
                result[('red_knockdowns_landed_rd' + str(round)) if round != 0 else 'red_knockdowns_landed'] = safe_int_convert(knockdowns_texts[0].get_text(strip=True))
                result[('blue_knockdowns_landed_rd' + str(round)) if round != 0 else 'blue_knockdowns_landed'] = safe_int_convert(knockdowns_texts[1].get_text(strip=True))

            # extract significant strikes landed (third column)
            sig_strikes_cell = table_cells[2]
            sig_strikes_texts = sig_strikes_cell.select('p.b-fight-details__table-text')
            if len(sig_strikes_texts) >= 2:
                result[('red_sig_strikes_landed_rd' + str(round)) if round != 0 else 'red_sig_strikes_landed'] = safe_int_convert(sig_strikes_texts[0].get_text(strip=True).split(' ')[0])
                result[('blue_sig_strikes_landed_rd' + str(round)) if round != 0 else 'blue_sig_strikes_landed'] = safe_int_convert(sig_strikes_texts[1].get_text(strip=True).split(' ')[0])

                result[('red_sig_strikes_thrown_rd' + str(round)) if round != 0 else 'red_sig_strikes_thrown'] = safe_int_convert(sig_strikes_texts[0].get_text(strip=True).split(' ')[-1])
                result[('blue_sig_strikes_thrown_rd' + str(round)) if round != 0 else 'blue_sig_strikes_thrown'] = safe_int_convert(sig_strikes_texts[1].get_text(strip=True).split(' ')[-1])

            # extract significant strike percentage (fourth column)
            sig_strike_percent_cell = table_cells[3]
            sig_strike_percent_texts = sig_strike_percent_cell.select('p.b-fight-details__table-text')
            if len(sig_strike_percent_texts) >= 2:
                result[('red_sig_strike_percent_rd' + str(round)) if round != 0 else 'red_sig_strike_percent'] = safe_float_convert(sig_strike_percent_texts[0].get_text(strip=True).replace('%', ''))
                result[('blue_sig_strike_percent_rd' + str(round)) if round != 0 else 'blue_sig_strike_percent'] = safe_float_convert(sig_strike_percent_texts[1].get_text(strip=True).replace('%', ''))

            # extract total strikes (fifth column)
            total_strikes_cell = table_cells[4]
            total_strikes_texts = total_strikes_cell.select('p.b-fight-details__table-text')
            if len(total_strikes_texts) >= 2:
                result[('red_total_strikes_landed_rd' + str(round)) if round != 0 else 'red_total_strikes_landed'] = safe_int_convert(total_strikes_texts[0].get_text(strip=True).split(' ')[0])
                result[('blue_total_strikes_landed_rd' + str(round)) if round != 0 else 'blue_total_strikes_landed'] = safe_int_convert(total_strikes_texts[1].get_text(strip=True).split(' ')[0])

                result[('red_total_strikes_thrown_rd' + str(round)) if round != 0 else 'red_total_strikes_thrown'] = safe_int_convert(total_strikes_texts[0].get_text(strip=True).split(' ')[-1])
                result[('blue_total_strikes_thrown_rd' + str(round)) if round != 0 else 'blue_total_strikes_thrown'] = safe_int_convert(total_strikes_texts[1].get_text(strip=True).split(' ')[-1])

            # extract takedowns landed (sixth column)
            takedowns_cell = table_cells[5]
            takedowns_texts = takedowns_cell.select('p.b-fight-details__table-text')
            if len(takedowns_texts) >= 2:
                result[('red_takedowns_landed_rd' + str(round)) if round != 0 else 'red_takedowns_landed'] = safe_int_convert(takedowns_texts[0].get_text(strip=True).split(' ')[0])
                result[('blue_takedowns_landed_rd' + str(round)) if round != 0 else 'blue_takedowns_landed'] = safe_int_convert(takedowns_texts[1].get_text(strip=True).split(' ')[0])

                result[('red_takedowns_attempted_rd' + str(round)) if round != 0 else 'red_takedowns_attempted'] = safe_int_convert(takedowns_texts[0].get_text(strip=True).split(' ')[-1])
                result[('blue_takedowns_attempted_rd' + str(round)) if round != 0 else 'blue_takedowns_attempted'] = safe_int_convert(takedowns_texts[1].get_text(strip=True).split(' ')[-1])

            # extract takedown percentage (seventh column)
            takedown_percent_cell = table_cells[6]
            takedown_percent_texts = takedown_percent_cell.select('p.b-fight-details__table-text')
            if len(takedown_percent_texts) >= 2:
                result[('red_takedowns_percent_rd' + str(round)) if round != 0 else 'red_takedowns_percent'] = safe_float_convert(takedown_percent_texts[0].get_text(strip=True).replace('%', ''))
                result[('blue_takedowns_percent_rd' + str(round)) if round != 0 else 'blue_takedowns_percent'] = safe_float_convert(takedown_percent_texts[1].get_text(strip=True).replace('%', ''))

            # extract submission attempts (eighth column)
            sub_attempts_cell = table_cells[7]
            sub_attempts_texts = sub_attempts_cell.select('p.b-fight-details__table-text')
            if len(sub_attempts_texts) >= 2:
                result[('red_sub_attempts_rd' + str(round)) if round != 0 else 'red_sub_attempts'] = safe_int_convert(sub_attempts_texts[0].get_text(strip=True))
                result[('blue_sub_attempts_rd' + str(round)) if round != 0 else 'blue_sub_attempts'] = safe_int_convert(sub_attempts_texts[1].get_text(strip=True))

            # extract reversals (ninth column)
            reversals_cell = table_cells[8]
            reversals_texts = reversals_cell.select('p.b-fight-details__table-text')
            if len(reversals_texts) >= 2:
                result[('red_reversals_rd' + str(round)) if round != 0 else 'red_reversals'] = safe_int_convert(reversals_texts[0].get_text(strip=True))
                result[('blue_reversals_rd' + str(round)) if round != 0 else 'blue_reversals'] = safe_int_convert(reversals_texts[1].get_text(strip=True))

            # extract control time (tenth column)
            control_time_cell = table_cells[9]
            control_time_texts = control_time_cell.select('p.b-fight-details__table-text')
            if len(control_time_texts) >= 2:
                result[('red_control_time_rd' + str(round)) if round != 0 else 'red_control_time'] = control_time_texts[0].get_text(strip=True)
                result[('blue_control_time_rd' + str(round)) if round != 0 else 'blue_control_time'] = control_time_texts[1].get_text(strip=True)

        except Exception as e:
            LOGGER.error(f"Error extracting fight stats: {e}")
            return result

    return result

