import logging
from typing import Dict, Any, Optional, Tuple
from bs4 import BeautifulSoup
from .utils import (
    convert_height_to_cm, 
    convert_weight_to_kg, 
    convert_reach_to_cm, 
    parse_date_of_birth,
    clean_string
)

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
