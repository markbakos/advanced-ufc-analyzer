import logging
from typing import Dict, Any
from bs4 import BeautifulSoup

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
            result['round'] = round_text
        
        # extract time
        time_item = fight_details_text.select_one('i.b-fight-details__text-item:has(i.b-fight-details__label:-soup-contains("Time:"))')
        if time_item:
            time_text = time_item.get_text(strip=True).replace('Time:', '').strip()
            result['time'] = time_text
        
        # extract time format
        time_format_item = fight_details_text.select_one('i.b-fight-details__text-item:has(i.b-fight-details__label:-soup-contains("Time format:"))')
        if time_format_item:
            time_format_text = time_format_item.get_text(strip=True).replace('Time format:', '').strip()
            result['total_rounds'] = time_format_text.split(' ')[0]
        
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