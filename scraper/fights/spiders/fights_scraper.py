import requests
import csv
import logging
import time
from typing import Set, Optional
from bs4 import BeautifulSoup
LOGGER = logging.getLogger(__name__)

# FOR TESTING, ONLY ONE PAGE
TEST_RUN = False

class UFCFightsSpider:
    """
    Spider for scraping UFC fights from ufcstats.com.
    """
    
    name = "ufc_fights_spider"

    def __init__(self):
        """Initialize the spider with output file, HTTP session, and header configurations"""
        self.output_file = 'fights.csv'
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
                'fight_id', 'blue_fighter_id', 'red_fighter_id', 'blue_fighter_name', 'red_fighter_name',
                'event_name', 'event_date', 'location', 'result', 'win_method', 'time', 'round',
                # fight stats
                'blue_knockdowns_landed', 'blue_knockdowns_absorbed', 'blue_strikes_landed', 'blue_strikes_absorbed',
                'blue_sig_strike_percent', 'blue_takedowns_landed', 'blue_takedowns_absorbed', 'blue_takedowns_attempted', 
                'blue_takedowns_percent', 'blue_sub_attempts_landed', 'blue_sub_attempts_absorbed', 'blue_reversals', 'blue_control_time',

                'red_knockdowns_landed', 'red_knockdowns_absorbed', 'red_strikes_landed', 'red_strikes_absorbed',
                'red_sig_strike_percent', 'red_takedowns_landed', 'red_takedowns_absorbed', 'red_takedowns_attempted',
                'red_takedowns_percent', 'red_sub_attempts_landed', 'red_sub_attempts_absorbed', 'red_reversals', 'red_control_time',

                # snapshot of blue fighter stats
                'blue_total_ufc_fights', 'blue_wins_in_ufc', 'blue_losses_in_ufc', 'blue_draws_in_ufc',
                'blue_wins_by_dec','blue_losses_by_dec','blue_wins_by_sub','blue_losses_by_sub','blue_wins_by_ko','blue_losses_by_ko',
                'blue_knockdowns_landed', 'blue_knockdowns_absorbed', 'blue_strikes_landed', 'blue_strikes_absorbed',
                'blue_takedowns_landed', 'blue_takedowns_absorbed', 'blue_sub_attempts_landed', 'blue_sub_attempts_absorbed',
                'blue_total_rounds', 'blue_total_time_minutes', 'blue_last_fight_date', 'blue_last_win_date',
                'blue_avg_knockdowns_landed', 'blue_avg_knockdowns_absorbed', 'blue_avg_strikes_landed', 'blue_avg_strikes_absorbed',
                'blue_avg_takedowns_landed', 'blue_avg_takedowns_absorbed', 'blue_avg_submission_attempts_landed',
                'blue_avg_submission_attempts_absorbed', 'blue_avg_fight_time_min',
                # snapshot of red fighter stats
                'red_total_ufc_fights', 'red_wins_in_ufc', 'red_losses_in_ufc', 'red_draws_in_ufc',
                'red_wins_by_dec','red_losses_by_dec','red_wins_by_sub','red_losses_by_sub','red_wins_by_ko','red_losses_by_ko',
                'red_knockdowns_landed', 'red_knockdowns_absorbed', 'red_strikes_landed', 'red_strikes_absorbed',
                'red_takedowns_landed', 'red_takedowns_absorbed', 'red_sub_attempts_landed', 'red_sub_attempts_absorbed',
                'red_total_rounds', 'red_total_time_minutes', 'red_last_fight_date', 'red_last_win_date',
                'red_avg_knockdowns_landed', 'red_avg_knockdowns_absorbed', 'red_avg_strikes_landed', 'red_avg_strikes_absorbed',
                'red_avg_takedowns_landed', 'red_avg_takedowns_absorbed', 'red_avg_submission_attempts_landed',
                'red_avg_submission_attempts_absorbed', 'red_avg_fight_time_min',

                'updated_timestamp'
            ])

    def run(self) -> None:
        """
        Execute the spider's main workflow:
        1. Collect all fight links
        2. Process each fight's page
        """
        all_fight_links = self.collect_all_fight_links()
        LOGGER.info(f"Found {len(all_fight_links)} unique fight links")

        # for fight_url in all_fight_links:
        #     self.parse_fight_stats(fight_url)
        #     time.sleep(1)
            
    def collect_all_fight_links(self) -> Set[str]:
        """
        Collects links to all fight profile pages
        
        Returns:
            Set of unique fight profile URLs
        """

        all_links = set()

        url = f"http://ufcstats.com/statistics/events/completed{'&page=all' if not TEST_RUN else ''}"

        html = self.fetch_page(url)
        if not html:
            return all_links

        links = self.extract_fight_page_links(html)
        all_links.update(links)

        LOGGER.info(f"Found {len(all_links)} unique links")
        return all_links

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
    
    def extract_fight_page_links(self, html: str) -> Set[str]:
        """
        Extracts fight profile links from a listing page
        
        Args:
            html: HTML content of the listing page
        
        Returns:
            Set of unique fight profile URLs
        """

        links = set()
        soup = BeautifulSoup(html, 'html.parser')
        fight_rows = soup.select('table.b-statistics__table-events tbody tr')
        
        if not fight_rows:
            fight_rows = soup.select('table.b-statistics__table-events tbody tr')

        LOGGER.info(f"Found {len(fight_rows)} fight rows")

        for fight_row in fight_rows:
            link_elem = fight_row.select_one('td a')
            if link_elem and link_elem.get('href'):
                fight_url = link_elem.get('href')
                links.add(fight_url)

        return links

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    spider = UFCFightsSpider()
    spider.run()