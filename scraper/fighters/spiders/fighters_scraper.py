import csv
import datetime
import re
import string
import logging
import requests
from bs4 import BeautifulSoup
import time

LOGGER = logging.getLogger(__name__)

# FOR TESTING, ONLY ONE LETTER
TEST_RUN = True

class UFCStatsSpider:
    name = "ufc_fighter_spider"
    base_url = "http://ufcstats.com/statistics/fighters"

    letters = string.ascii_lowercase

    def __init__(self):
        self.output_file = 'fighters.csv'
        self.session = requests.Session()
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                'fighter_id', 'fighter_name', 'birth_year', 'height_cm', 'weight_kg', 'reach_cm',
                'stance', 'fighter_style', 'wins', 'losses', 'draws', 'win_percentage', 'momentum',
                'SLpM', 'str_acc', 'SApM', 'str_def', 'td_avg', 'td_acc', 'td_def', 'sub_avg',
                'total_dec_wins', 'total_sub_wins', 'total_ko_wins', 'total_knockdowns',
                'total_strikes_landed', 'total_strikes_absorbed', 'total_takedowns_landed',
                'total_takedowns_absorbed', 'total_sub_attempts_landed', 'total_sub_attempts_absorbed',
                'total_fight_time_min', 'avg_knockdowns', 'avg_strikes_landed', 'avg_strikes_absorbed',
                'avg_takedowns_landed', 'avg_takedowns_absorbed', 'avg_submission_attempts_landed',
                'avg_submission_attempts_absorbed', 'avg_fight_time_min', 'updated_timestamp'
            ])

    def run(self):
        all_fighter_links = self.collect_all_fighter_links()
        LOGGER.info(f"Found {len(all_fighter_links)} unique fighter links")
        
        for fighter_url in all_fighter_links:
            self.parse_fighter_stats(fighter_url)
            time.sleep(1)

    def fetch_page(self, url):
        try:
            LOGGER.info(f"Fetching page: {url}")
            response = self.session.get(url, headers=self.headers)
            response.raise_for_status()
            return response.text
        except Exception as e:
            LOGGER.error(f"Error fetching page {url}: {e}")
            return None

    def collect_all_fighter_links(self):
        all_links = set()
        
        for letter in self.letters:
            LOGGER.info(f"Collecting fighters for letter: {letter}")
            url = f"{self.base_url}?char={letter}{"&page=all" if not TEST_RUN else ""}"
            
            html = self.fetch_page(url)
            if not html:
                continue
                
            links = self.extract_fighter_page_links(html)
            all_links.update(links)
            
            if TEST_RUN:
                break
                
        LOGGER.info(f"Found {len(all_links)} unique links")
        return all_links

    def extract_fighter_page_links(self, html):
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

    def parse_fighter_stats(self, url):
        html = self.fetch_page(url)
        if not html:
            return
            
        soup = BeautifulSoup(html, 'html.parser')

        fighter_id = url.split('/')[-1]
        
        fighter_name_elem = soup.select_one('span.b-content__title-highlight')
        if fighter_name_elem:
            fighter_name = fighter_name_elem.text.strip()
            LOGGER.info(f"Processing fighter: {fighter_name} (ID: {fighter_id})")


        fighter_record = soup.select_one('span.b-content__title-record').text.strip()
        LOGGER.info(f"Fighter Record: {fighter_record}")
            
        with open(self.output_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([fighter_id, fighter_name] + [''] * 38)


if __name__ == "__main__":
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    spider = UFCStatsSpider()
    spider.run()

        
