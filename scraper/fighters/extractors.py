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
            
        data_text = info_box.get_text(strip=True, separator='_').split('_')
        
        # extract values using index positions
        extract_value = lambda idx: data_text[idx] if idx < len(data_text) else None
        
        height = extract_value(1)
        weight = extract_value(3)
        reach = extract_value(5)
        stance = extract_value(7)
        dob = extract_value(9)
        
        # convert and clean values
        result["height_cm"] = convert_height_to_cm(height)
        result["weight_kg"] = convert_weight_to_kg(weight)
        result["reach_cm"] = convert_reach_to_cm(reach)
        result["stance"] = clean_string(stance)
        result["date_of_birth"] = parse_date_of_birth(dob)
        
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