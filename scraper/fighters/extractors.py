import datetime
import logging
from typing import Dict, Any, Optional, Tuple

import requests
from bs4 import BeautifulSoup
from scraper.fighters.utils import (
    convert_height_to_cm,
    convert_weight_to_kg,
    convert_reach_to_cm,
    parse_date_of_birth,
    clean_string,
)

from scraper.utils import safe_int_convert

logger = logging.getLogger(__name__)

def extract_physical_data(soup: BeautifulSoup) -> Dict[str, Any]:
    """
    Extracts the physical data for a fighter from their profile page
    
    Args:
        soup: The fighter's page
        
    Returns:
        Dictionary containing physical attributes (height, weight, reach, stance, date of birth)
    """
    result = {
        "height_cm": None,
        "weight_kg": None,
        "reach_cm": None,
        "stance": None,
        "date_of_birth": None
    }
    
    try:
        # get the physical info box
        info_box = soup.select_one('.b-list__info-box.b-list__info-box_style_small-width')
        if not info_box:
            return result
        
        # extract the data using li identifier
        info_items = info_box.select('li')
        
        for item in info_items:
            item_text = item.get_text(strip=True)
            
            if "Height:" in item_text:
                height_value = item_text.replace("Height:", "").strip()
                result["height_cm"] = convert_height_to_cm(height_value)
                
            elif "Weight:" in item_text:
                weight_value = item_text.replace("Weight:", "").strip()
                result["weight_kg"] = convert_weight_to_kg(weight_value)
                
            elif "Reach:" in item_text:
                reach_value = item_text.replace("Reach:", "").strip()
                result["reach_cm"] = convert_reach_to_cm(reach_value)
                
            elif "STANCE:" in item_text:
                stance_value = item_text.replace("STANCE:", "").strip()
                result["stance"] = clean_string(stance_value)
                
            elif "DOB:" in item_text:
                dob_value = item_text.replace("DOB:", "").strip()
                result["date_of_birth"] = parse_date_of_birth(dob_value)
                
        logger.debug(f"Extracted physical data: {result}")
        
    except Exception as e:
        logger.warning(f"Exception in extract_physical_data: {e}")
    
    return result

def extract_fighter_name_and_nickname(soup: BeautifulSoup) -> Tuple[Optional[str], Optional[str]]:
    """
    extract fighter name and nickname from the fighter's profile page
    
    Args:
        soup: Fighter's page
        
    Returns:
        Tuple of (fighter_name, nickname)
    """
    fighter_name = None
    nickname = None
    
    try:
        name_elem = soup.select_one('span.b-content__title-highlight')
        if name_elem:
            fighter_name = name_elem.get_text(strip=True)
    except Exception as e:
        logger.warning(f"Exception extracting fighter name: {e}")
    
    try:
        nickname_elem = soup.select_one('.b-content__Nickname')
        if nickname_elem:
            nickname_text = nickname_elem.get_text(strip=True)
            nickname = nickname_text if nickname_text else None
    except Exception as e:
        logger.warning(f"Exception extracting nickname: {e}")
    
    return fighter_name, nickname

def extract_fighter_record(soup: BeautifulSoup) -> Tuple[Optional[int], Optional[int], Optional[int]]:
    """
    extract fighter record (wins, losses, draws) from the fighter's profile page
    
    Args:
        soup: Fighter's page
        
    Returns:
        Tuple of (wins, losses, draws)
    """
    wins, losses, draws = None, None, None
    
    try:
        record_elem = soup.select_one('span.b-content__title-record')
        if record_elem:
            record_text = record_elem.get_text(strip=True)
            record_part = record_text.split(' ', maxsplit=1)[-1].strip().split(' ')[0].strip()
            if '-' in record_part:
                record_numbers = record_part.split('-')
                if len(record_numbers) >= 3:
                    wins = int(record_numbers[0])
                    losses = int(record_numbers[1])
                    draws = int(record_numbers[2])
    except Exception as e:
        logger.warning(f"Exception extracting fighter record: {e}")
    
    return wins, losses, draws

def extract_career_statistics(soup: BeautifulSoup) -> Dict[str, float]:
    """
    Extracts the career statistics table from fighter's page

    Args:
        soup: Fighter's page

    Returns:
        Dictionary that returns fighter's career statistics
    """

    result = {
        "SLpM": None,
        "str_acc": None,
        "SApM": None,
        "str_def": None,
        "td_avg": None,
        "td_acc": None,
        "td_def": None,
        "sub_avg": None,
    }

    try:
        # get career box element
        career_box_left = soup.select_one('.b-list__info-box.b-list__info-box_style_middle-width')
        if not career_box_left:
            return result

        career_box_right = career_box_left.select_one('.b-list__info-box-right')
        if not career_box_right:
            return result

        #get list items for left section
        career_items_left = career_box_left.select('li')

        #extract data from left
        for item in career_items_left:
            item_text = item.get_text(strip=True)

            if "SLpM:" in item_text:
                slpm_value = item_text.replace("SLpM:", "").strip()
                result["SLpM"] = float(slpm_value) if slpm_value else None

            elif "Str. Acc.:" in item_text:
                str_acc_value = item_text.replace("Str. Acc.:", "").strip()
                result["str_acc"] = float(str_acc_value.replace("%", "")) if str_acc_value else None

            elif "SApM:" in item_text:
                sapm_value = item_text.replace("SApM:", "").strip()
                result["SApM"] = float(sapm_value) if sapm_value else None

            elif "Str. Def:" in item_text:
                str_def_value = item_text.replace("Str. Def:", "").strip()
                result["str_def"] = float(str_def_value.replace("%", "")) if str_def_value else None

        # get list items for right section
        if career_box_right:
            right_items = career_box_right.select('li.b-list__box-list-item')

            for item in right_items:
                item_text = item.get_text(strip=True)

                if "TD Avg.:" in item_text:
                    td_avg_value = item_text.replace("TD Avg.:", "").strip()
                    result["td_avg"] = float(td_avg_value) if td_avg_value and td_avg_value != '' else None

                elif "TD Acc.:" in item_text:
                    td_acc_value = item_text.replace("TD Acc.:", "").strip()
                    result["td_acc"] = float(
                        td_acc_value.replace("%", "")) if td_acc_value and td_acc_value != '' else None

                elif "TD Def.:" in item_text:
                    td_def_value = item_text.replace("TD Def.:", "").strip()
                    result["td_def"] = float(
                        td_def_value.replace("%", "")) if td_def_value and td_def_value != '' else None

                elif "Sub. Avg.:" in item_text:
                    sub_avg_value = item_text.replace("Sub. Avg.:", "").strip()
                    result["sub_avg"] = float(sub_avg_value) if sub_avg_value and sub_avg_value != '' else None

    except Exception as e:
        logger.warning(f"Exception extracting career statistics for fighter, {e}")

    return result

def extract_fights(soup: BeautifulSoup, fight_date_limit : Optional[datetime.datetime] = None) -> Dict[str, Any]:
    """
    Extracts the fight data from the fighter's previous matches

    Args:
        soup: Fighter's page
        fight_date_limit: Limit to only consider fights before this date
    Returns:
        Dictionary that returns fighter's fight data statistics
    """
    fighter_stats = {
        'total_ufc_fights': 0,
        'wins_in_ufc': 0,
        'losses_in_ufc': 0,
        'draws_in_ufc': 0,
        'wins_by_dec': 0,
        'losses_by_dec': 0,
        'wins_by_sub': 0,
        'losses_by_sub': 0,
        'wins_by_ko': 0,
        'losses_by_ko': 0,
        'knockdowns_landed': 0,
        'knockdowns_absorbed': 0,
        'strikes_landed': 0,
        'strikes_absorbed': 0,
        'takedowns_landed': 0,
        'takedowns_absorbed': 0,
        'sub_attempts_landed': 0,
        'sub_attempts_absorbed': 0,
        'total_rounds': 0,
        'total_time_minutes': 0,
        'result_momentum_score': 0,
        'stats_momentum_score': 0,
        'last_fight_date': None,
        'last_win_date': None,
    }

    fight_table = soup.select_one('.b-fight-details__table_type_event-details')
    if not fight_table:
        return fighter_stats

    fight_rows = fight_table.select('tbody.b-fight-details__table-body tr:not(.b-fight-details__table-row__head)')

    for row in fight_rows:
        if not row.select('td'):
            continue

        # check if valid fight row
        cells = row.select('td')
        if len(cells) < 7:
            continue

        # win or loss
        try:
            result = row.select('td')[0].get_text(strip=True).lower()
        except IndexError:
            result = ""

        if result.lower() == "next":
            continue

        should_skip = False
        try:
            date_paragraphs = cells[6].select('p')
            if len(date_paragraphs) > 1:
                date_text = date_paragraphs[1].get_text(strip=True)
            else:
                date_text = ""

            # get last fight date and last win date
            if date_text:
                try:
                    fight_date = datetime.datetime.strptime(date_text, "%b. %d, %Y")

                    # skip if date limit is set and fight date is not before limit
                    if fight_date_limit and fight_date >= fight_date_limit:
                        should_skip = True
                        
                    if not should_skip:
                        if fighter_stats['last_fight_date'] is None:
                            fighter_stats['last_fight_date'] = fight_date

                        if result == 'win' and fighter_stats['last_win_date'] is None:
                            fighter_stats['last_win_date'] = fight_date

                except Exception as e:
                    print(f"Error parsing fight date: {date_text}, error: {e}")

        except IndexError:
            pass  # continue if date extraction fails

        if should_skip:
            continue

        fighter_stats['total_ufc_fights'] += 1

        # method of victory/defeat
        method = row.select('td')[7].select('p')[0].get_text(strip=True)

        if result.lower() == "win":
            fighter_stats['wins_in_ufc'] += 1
            if "dec" in method.lower():
                fighter_stats['wins_by_dec'] += 1
                if fighter_stats['total_ufc_fights'] <= 3:
                    fighter_stats['result_momentum_score'] += 0.75
            elif "sub" in method.lower():
                fighter_stats['wins_by_sub'] += 1
                if fighter_stats['total_ufc_fights'] <= 3:
                    fighter_stats['result_momentum_score'] += 1
            elif "ko/tko" in method.lower():
                fighter_stats['wins_by_ko'] += 1
                if fighter_stats['total_ufc_fights'] <= 3:
                    fighter_stats['result_momentum_score'] += 1
        elif result.lower() == "loss":
            fighter_stats['losses_in_ufc'] += 1
            if "dec" in method.lower():
                fighter_stats['losses_by_dec'] += 1
                if fighter_stats['total_ufc_fights'] <= 3:
                    fighter_stats['result_momentum_score'] -= 0.75
            elif "sub" in method.lower():
                fighter_stats['losses_by_sub'] += 1
                if fighter_stats['total_ufc_fights'] <= 3:
                    fighter_stats['result_momentum_score'] -= 1
            elif "ko/tko" in method.lower():
                fighter_stats['losses_by_ko'] += 1
                if fighter_stats['total_ufc_fights'] <= 3:
                    fighter_stats['result_momentum_score'] -= 1
        elif result.lower() == "draw":
            fighter_stats['draws_in_ufc'] += 1

        cols = row.select('td')

        # knockdowns
        kd_data = cols[2].select('p')
        if len(kd_data) >= 2:
            knockdowns_landed = safe_int_convert(kd_data[0].get_text(strip=True))
            fighter_stats['knockdowns_landed'] += knockdowns_landed
            if fighter_stats['total_ufc_fights'] <= 3:
                fighter_stats['stats_momentum_score'] += knockdowns_landed
            knockdowns_absorbed = safe_int_convert(kd_data[1].get_text(strip=True))
            fighter_stats['knockdowns_absorbed'] += knockdowns_absorbed
            if fighter_stats['total_ufc_fights'] <= 3:
                fighter_stats['stats_momentum_score'] -= knockdowns_absorbed

        #strikes
        strike_data = cols[3].select('p')
        if len(strike_data) >= 2:
            strikes_landed = safe_int_convert(strike_data[0].get_text(strip=True) or 0)
            fighter_stats['strikes_landed'] += strikes_landed
            if fighter_stats['total_ufc_fights'] <= 3:
                fighter_stats['stats_momentum_score'] += (strikes_landed * 0.1)
            strikes_absorbed = safe_int_convert(strike_data[1].get_text(strip=True) or 0)
            fighter_stats['strikes_absorbed'] += strikes_absorbed
            if fighter_stats['total_ufc_fights'] <= 3:
                fighter_stats['stats_momentum_score'] -= (strikes_absorbed * 0.1)

        # takedowns
        td_data = cols[4].select('p')
        if len(td_data) >= 2:
            takedowns_landed = safe_int_convert(td_data[0].get_text(strip=True) or 0)
            fighter_stats['takedowns_landed'] += takedowns_landed
            if fighter_stats['total_ufc_fights'] <= 3:
                fighter_stats['stats_momentum_score'] += (takedowns_landed * 0.2)
            takedowns_absorbed = safe_int_convert(td_data[1].get_text(strip=True) or 0)
            fighter_stats['takedowns_absorbed'] += takedowns_absorbed
            if fighter_stats['total_ufc_fights'] <= 3:
                fighter_stats['stats_momentum_score'] -= (takedowns_absorbed * 0.2)

        # sub attempts
        sub_data = cols[5].select('p')
        if len(sub_data) >= 2:
            sub_attempts_landed = safe_int_convert(sub_data[0].get_text(strip=True) or 0)
            fighter_stats['sub_attempts_landed'] += sub_attempts_landed
            if fighter_stats['total_ufc_fights'] <= 3:
                fighter_stats['stats_momentum_score'] += (sub_attempts_landed * 0.8)
            sub_attempts_absorbed = safe_int_convert(sub_data[1].get_text(strip=True) or 0)
            fighter_stats['sub_attempts_absorbed'] += sub_attempts_absorbed
            if fighter_stats['total_ufc_fights'] <= 3:
                fighter_stats['stats_momentum_score'] -= (sub_attempts_absorbed * 0.8)

        # get round and time info
        round_num = safe_int_convert(row.select('td')[8].get_text(strip=True))
        time_str = row.select('td')[9].get_text(strip=True)

        # full rounds completed
        fighter_stats['total_rounds'] += round_num if time_str == "5:00" else round_num - 1

        # calculate total fight time in minutes
        minutes, seconds = map(int, time_str.split(':'))
        total_minutes = (round_num-1) * 5 + minutes + (seconds//60)
        fighter_stats['total_time_minutes'] += total_minutes

    return fighter_stats


if __name__ == '__main__':
    # test scraping with Israel Adesanya
    fighter_url = "http://ufcstats.com/fighter-details/1338e2c7480bdf9e"
    response = requests.get(fighter_url)
    soup = BeautifulSoup(response.content, 'html.parser')

    fight_date_limit = datetime.datetime.strptime("September 09, 2023", "%B %d, %Y")
    stats = extract_fights(soup, fight_date_limit)

    print(stats)
