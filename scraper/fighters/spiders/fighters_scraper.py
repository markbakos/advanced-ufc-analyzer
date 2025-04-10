import csv
import string
import logging
import requests
from bs4 import BeautifulSoup
import time
import datetime
from typing import Set, Dict, Any, Optional

from scraper.fighters.extractors import (
    extract_physical_data,
    extract_fighter_name_and_nickname,
    extract_fighter_record,
    extract_career_statistics
)

LOGGER = logging.getLogger(__name__)

# FOR TESTING, ONLY ONE LETTER
TEST_RUN = True

class UFCStatsSpider:
    """
    Spider for scraping UFC fighter statistics from ufcstats.com.
    """
    
    name = "ufc_fighter_spider"
    base_url = "http://ufcstats.com/statistics/fighters"

    letters = string.ascii_lowercase

    def __init__(self):
        """Initialize the spider with output file, HTTP session, and header configurations"""
        self.output_file = 'fighters.csv'
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        self._initialize_csv()

    def _initialize_csv(self) -> None:
        """Creates the CSV file and writes the header row"""
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'fighter_id', 'fighter_name', 'nickname', 'date_of_birth', 'height_cm', 'weight_kg', 'reach_cm',
                'stance', 'fighter_style', 'wins', 'losses', 'draws', 'win_percentage', 'momentum',
                'SLpM', 'str_acc', 'SApM', 'str_def', 'td_avg', 'td_acc', 'td_def', 'sub_avg',
                'total_dec_wins', 'total_sub_wins', 'total_ko_wins', 'total_knockdowns',
                'total_strikes_landed', 'total_strikes_absorbed', 'total_takedowns_landed',
                'total_takedowns_absorbed', 'total_sub_attempts_landed', 'total_sub_attempts_absorbed',
                'total_fight_time_min', 'avg_knockdowns', 'avg_strikes_landed', 'avg_strikes_absorbed',
                'avg_takedowns_landed', 'avg_takedowns_absorbed', 'avg_submission_attempts_landed',
                'avg_submission_attempts_absorbed', 'avg_fight_time_min', 'updated_timestamp'
            ])

    def run(self) -> None:
        """
        Execute the spider's main workflow:
        1. Collect all fighter links
        2. Process each fighter's page
        """
        all_fighter_links = self.collect_all_fighter_links()
        LOGGER.info(f"Found {len(all_fighter_links)} unique fighter links")
        
        for fighter_url in all_fighter_links:
            self.parse_fighter_stats(fighter_url)
            time.sleep(1)

    def fetch_page(self, url: str) -> Optional[str]:
        """
        Helper function to fetch the HTML content of a page
        
        Args:
            url: The URL to fetch
            
        Returns:
            HTML content as string or None if request fails
        """
        try:
            LOGGER.info(f"Fetching page: {url}")
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except Exception as e:
            LOGGER.error(f"Error fetching page {url}: {e}")
            return None

    def collect_all_fighter_links(self) -> Set[str]:
        """
        Collects links to all fighter profile pages
        
        Returns:
            Set of unique fighter profile URLs
        """
        all_links = set()
        
        for letter in self.letters:
            LOGGER.info(f"Collecting fighters for letter: {letter}")
            url = f"{self.base_url}?char={letter}{'&page=all' if not TEST_RUN else ''}"
            
            html = self.fetch_page(url)
            if not html:
                continue
                
            links = self.extract_fighter_page_links(html)
            all_links.update(links)
            
            if TEST_RUN:
                break
                
        LOGGER.info(f"Found {len(all_links)} unique links")
        return all_links

    def extract_fighter_page_links(self, html: str) -> Set[str]:
        """
        Extracts fighter profile links from a listing page
        
        Args:
            html: HTML content of the listing page
            
        Returns:
            Set of unique fighter profile URLs
        """
        links = set()
        soup = BeautifulSoup(html, 'html.parser')
        fighter_rows = soup.select('table.b-statistics__table-col tbody tr')
        
        if not fighter_rows:
            fighter_rows = soup.select('table.b-statistics__table tbody tr')
            
        LOGGER.info(f"Found {len(fighter_rows)} fighter rows")
        
        for fighter_row in fighter_rows:
            link_elem = fighter_row.select_one('td a')
            if link_elem and link_elem.get('href'):
                fighter_url = link_elem.get('href')
                links.add(fighter_url)
                
        return links
    
    def parse_fighter_stats(self, url: str) -> None:
        """
        Parses and saves statistics for a single fighter
        
        Args:
            url: URL of the fighter's profile page
        """
        html = self.fetch_page(url)
        if not html:
            return
            
        soup = BeautifulSoup(html, 'html.parser')
        fighter_id = url.split('/')[-1]
        
        # use extractor functions to extract data
        fighter_name, nickname = extract_fighter_name_and_nickname(soup)
        wins, losses, draws = extract_fighter_record(soup)
        physical_data = extract_physical_data(soup)
        career_data = extract_career_statistics(soup)
        
        if fighter_name:
            LOGGER.info(f"Processing fighter: {fighter_name} (ID: {fighter_id})")

        # saves data to CSV
        self._save_fighter_data(fighter_id, fighter_name, nickname, physical_data, wins, losses, draws, career_data)
    
    def _save_fighter_data(self, fighter_id: str, fighter_name: Optional[str], 
                          nickname: Optional[str], physical_data: Dict[str, Any],
                          wins: Optional[int], losses: Optional[int], draws: Optional[int], career_data: Dict[str, float]) -> None:
        """
        Saves fighter data to the CSV file
        
        Args:
            fighter_id: Fighter's unique identifier
            fighter_name: Fighter's name
            nickname: Fighter's nickname
            physical_data: Dictionary of physical attributes
            wins: Number of wins
            losses: Number of losses
            draws: Number of draws
        """
        with open(self.output_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            win_percentage = round((wins/(wins+losses+draws)), 2) if (wins+losses+draws) > 0 else 0
            
            # prepare data
            row = [
                fighter_id,
                fighter_name,
                nickname,
                physical_data.get('date_of_birth'),
                physical_data.get('height_cm'),
                physical_data.get('weight_kg'),
                physical_data.get('reach_cm'),
                physical_data.get('stance'),
                '',  # fighter_style
                wins,
                losses,
                draws,
                win_percentage,
                '', # momentum
                career_data.get('SLpM'),
                career_data.get('str_acc'),
                career_data.get('SApM'),
                career_data.get('str_def'),
                career_data.get('td_avg'),
                career_data.get('td_acc'),
                career_data.get('td_def'),
                career_data.get('sub_avg'),
            ]
            
            # add placeholders
            row.extend([''] * 20)
            
            # add timestamp
            row[-1] = datetime.datetime.now().isoformat()
            
            writer.writerow(row)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    spider = UFCStatsSpider()
    spider.run()

        
