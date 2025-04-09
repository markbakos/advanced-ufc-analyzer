import re
import pint
import datetime
import logging
from typing import Optional

logger = logging.getLogger(__name__)
unit_registry = pint.UnitRegistry()

def convert_height_to_cm(height: str) -> Optional[float]:
    """
    Convert height from feet and inches format to centimeters
    
    Args:
        height: String in format "X' Y\"" (e.g., "5' 11\"")
        
    Returns:
        Height in centimeters or None if conversion fails
    """
    if not height or height == "--":
        return None
        
    try:
        h_feet, h_inches = height.split(' ')
        feet_value = int(re.match(r'(\d+)', h_feet).group(0))
        inches_value = int(re.match(r'(\d+)', h_inches).group(0))
        
        height_in_customary = feet_value * unit_registry.foot + inches_value * unit_registry.inch
        height_cm = height_in_customary.to(unit_registry.centimeter)
        
        return round(height_cm.magnitude, 2)
    except Exception as e:
        logger.debug(f"Failed to convert height '{height}' to cm: {e}")
        return None

def convert_weight_to_kg(weight: str) -> Optional[float]:
    """
    Converts weight from pounds to kilograms
    
    Args:
        weight: String containing weight in lbs (e.g.: "185 lbs")
        
    Returns:
        Weight in kilograms or None if conversion fails
    """
    if not weight or weight == "--":
        return None
        
    try:
        match = re.match(r'(\d+)', weight)
        if not match:
            return None
            
        weight_lbs = int(match.group(0))
        return round(weight_lbs * 0.453592, 2)
    except Exception as e:
        logger.debug(f"Failed to convert weight '{weight}' to kg: {e}")
        return None

def convert_reach_to_cm(reach: str) -> Optional[float]:
    """
    Converts reach from inches to centimeters
    
    Args:
        reach: String containing reach in inches (e.g., "72\"")
        
    Returns:
        Reach in centimeters or None if conversion fails
    """
    if not reach or reach == "--":
        return None
        
    try:
        reach_inches = reach.split('"')[0]
        return round(float(reach_inches) * 2.54, 2)
    except Exception as e:
        logger.debug(f"Failed to convert reach '{reach}' to cm: {e}")
        return None

def parse_date_of_birth(dob: str) -> Optional[str]:
    """
    Parses date of birth into a standard date format

    Args:
        dob: String containing date (e.g., "Jan 15, 1990")
        
    Returns:
        ISO format date string or None if parsing fails
    """
    if not dob or dob == "--":
        return None
        
    try:
        return str(datetime.datetime.strptime(dob, '%b %d, %Y').date())
    except Exception as e:
        logger.debug(f"Failed to parse date '{dob}': {e}")
        return None

def clean_string(text: str) -> Optional[str]:
    """
    Cleans a string value, returning None for empty or placeholder values
    
    Args:
        text: Input string to clean
        
    Returns:
        Cleaned string or None if invalid
    """
    if not text or text.strip() == "" or text.strip() == "--":
        return None
    return text.strip() 