import requests
import csv
import logging
import time
from typing import Set, Optional, Dict, Any
from bs4 import BeautifulSoup
from scraper.fights.extractors import (
    extract_fighters,
    extract_fight_data
)

LOGGER = logging.getLogger(__name__)

# FOR TESTING, ONLY ONE PAGE
TEST_RUN = True

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
                # fighter data
                'fight_id', 'event_name', 'event_date', 'location', 'red_fighter_name', 'blue_fighter_name',
                'red_fighter_id', 'blue_fighter_id',

                # fight data
                'result', 'win_method', 'time', 'round',

                # fight stats
                'red_knockdowns_landed', 'red_strikes_landed', 'red_sig_strike_percent', 'red_takedowns_landed', 'red_takedowns_attempted',
                'red_takedowns_percent', 'red_sub_attempts_landed', 'red_reversals', 'red_control_time',

                'blue_knockdowns_landed', 'blue_strikes_landed', 'blue_sig_strike_percent', 'blue_takedowns_landed', 'blue_takedowns_attempted', 
                'blue_takedowns_percent', 'blue_sub_attempts_landed', 'blue_reversals', 'blue_control_time',

                # snapshot of red fighter stats
                'career_red_total_ufc_fights', 'career_red_wins_in_ufc', 'career_red_losses_in_ufc', 'career_red_draws_in_ufc',
                'career_red_wins_by_dec','career_red_losses_by_dec','career_red_wins_by_sub','career_red_losses_by_sub','career_red_wins_by_ko','career_red_losses_by_ko',
                'career_red_knockdowns_landed', 'career_red_knockdowns_absorbed', 'career_red_strikes_landed', 'career_red_strikes_absorbed',
                'career_red_takedowns_landed', 'career_red_takedowns_absorbed', 'career_red_sub_attempts_landed', 'career_red_sub_attempts_absorbed',
                'career_red_total_rounds', 'career_red_total_time_minutes', 'career_red_last_fight_date', 'career_red_last_win_date',
                'career_red_avg_knockdowns_landed', 'career_red_avg_knockdowns_absorbed', 'career_red_avg_strikes_landed', 'career_red_avg_strikes_absorbed',
                'career_red_avg_takedowns_landed', 'career_red_avg_takedowns_absorbed', 'career_red_avg_submission_attempts_landed',
                'career_red_avg_submission_attempts_absorbed', 'career_red_avg_fight_time_min',

                # snapshot of blue fighter stats
                'career_blue_total_ufc_fights', 'career_blue_wins_in_ufc', 'career_blue_losses_in_ufc', 'career_blue_draws_in_ufc',
                'career_blue_wins_by_dec','career_blue_losses_by_dec','career_blue_wins_by_sub','career_blue_losses_by_sub','career_blue_wins_by_ko','career_blue_losses_by_ko',
                'career_blue_knockdowns_landed', 'career_blue_knockdowns_absorbed', 'career_blue_strikes_landed', 'career_blue_strikes_absorbed',
                'career_blue_takedowns_landed', 'career_blue_takedowns_absorbed', 'career_blue_sub_attempts_landed', 'career_blue_sub_attempts_absorbed',
                'career_blue_total_rounds', 'career_blue_total_time_minutes', 'career_blue_last_fight_date', 'career_blue_last_win_date',
                'career_blue_avg_knockdowns_landed', 'career_blue_avg_knockdowns_absorbed', 'career_blue_avg_strikes_landed', 'career_blue_avg_strikes_absorbed',
                'career_blue_avg_takedowns_landed', 'career_blue_avg_takedowns_absorbed', 'career_blue_avg_submission_attempts_landed',
                'career_blue_avg_submission_attempts_absorbed', 'career_blue_avg_fight_time_min',

                'updated_timestamp'
            ])

    def run(self) -> None:
        """
        Execute the spider's main workflow:
        1. Collect all event links
        2. Process each event's page to extract fights
        """
        all_event_links = self.collect_all_event_links()
        LOGGER.info(f"Found {len(all_event_links)} unique event links")
            
    def collect_all_event_links(self) -> Set[str]:
        """
        Collects links to all event profile pages
        
        Returns:
            Set of unique event profile URLs
        """

        all_links = set()

        url = f"http://ufcstats.com/statistics/events/completed{'?page=all' if not TEST_RUN else ''}"

        html = self.fetch_page(url)
        if not html:
            return all_links

        links = self.extract_event_page_links(html)
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
    
    def extract_event_page_links(self, html: str) -> Set[str]:
        """
        Extracts event profile links from a listing page
        
        Args:
            html: HTML content of the listing page
        
        Returns:
            Set of unique events URLs
        """

        links = set()
        soup = BeautifulSoup(html, 'html.parser')
        event_rows = soup.select('table.b-statistics__table-events tbody tr')
        
        if not event_rows:
            LOGGER.warning("Could not find event rows on the page")
            return links

        LOGGER.info(f"Found {len(event_rows)} event rows")

        for event_row in event_rows:
            # skip upcoming events
            img_elem = event_row.select_one('td img')
            if img_elem:
                continue

            link_elem = event_row.select_one('td a')
            if link_elem and link_elem.get('href'):
                event_url = link_elem.get('href')
                links.add(event_url)
                LOGGER.info(f"Found event: {event_url}")
                
                # extract fights from this event
                self.extract_fight_links(event_url)
                time.sleep(1)

        return links

    def extract_fight_links(self, event_url: str) -> Set[str]:
        """
        Extracts fight links from an event page
        
        Args:
            event_url: URL of the event page
            
        Returns:
            Set of unique fight URLs
        """
        links = set()
        
        html = self.fetch_page(event_url)
        if not html:
            return links
            
        soup = BeautifulSoup(html, 'html.parser')

        # extract event details
        event_date = None
        event_location = None
        
        # find the event details box
        details_box = soup.select_one('ul.b-list__box-list')
        if details_box:
            # extract date
            date_item = details_box.select_one('li.b-list__box-list-item:has(i:contains("Date:"))')
            if date_item:
                date_text = date_item.get_text(strip=True).replace('Date:', '').strip()
                event_date = date_text
                LOGGER.info(f"Event date: {event_date}")
                
            # extract location
            location_item = details_box.select_one('li.b-list__box-list-item:has(i:contains("Location:"))')
            if location_item:
                location_text = location_item.get_text(strip=True).replace('Location:', '').strip()
                event_location = location_text
                LOGGER.info(f"Event location: {event_location}")

        # extract event name
        event_name = soup.select_one('.b-content__title-highlight')
        if event_name:
            event_name = event_name.get_text(strip=True)
            LOGGER.info(f"Event name: {event_name}")
        
        # extract fight links
        fight_table = soup.select_one('table.b-fight-details__table.b-fight-details__table_style_margin-top.b-fight-details__table_type_event-details')
        if not fight_table:
            LOGGER.warning(f"Could not find fight table on page: {event_url}")
            return links
                
        fight_rows = fight_table.select('tbody tr:not(.b-fight-details__table-row__head)')
        
        LOGGER.info(f"Found {len(fight_rows)} fight rows on event page: {event_url}")
        
        for fight_row in fight_rows:
            fight_link = fight_row.select_one('td:first-child a.b-flag')
            if fight_link and fight_link.get('href'):
                fight_url = fight_link.get('href')
                links.add(fight_url)
                LOGGER.info(f"Found fight: {fight_url}")
                
                # process this fight
                self.parse_fight_stats(fight_url, event_date, event_location, event_name)
                time.sleep(1)
        
        return links

    def parse_fight_stats(self, fight_url: str, event_date: str, event_location: str, event_name: str) -> None:
        """
        Parses and saves statistics for a single fight
        
        Args:
            fight_url: URL of the fight page
            event_date: Date of the event
            event_location: Location of the event
            event_name: Name of the event
        """
        
        html = self.fetch_page(fight_url)
        if not html:
            return

        soup = BeautifulSoup(html, 'html.parser')

        event_data = {
            'event_date': event_date,
            'event_location': event_location,
            'event_name': event_name
        }

        fight_id = fight_url.split('/')[-1]

        # extract fight data
        fighters_data = extract_fighters(soup)

        self._save_fight_data(fight_id, event_data, fighters_data)

    def _save_fight_data(self, fight_id: str, event_data: Dict[str, Any], fighters_data: Dict[str, Any]) -> None:
        """
        Saves the fight data to the CSV file
        """

        LOGGER.info(f"{event_data} + {fighters_data}")
        
        with open(self.output_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                fight_id,
                event_data['event_name'],
                event_data['event_date'],
                event_data['event_location'],
                fighters_data['red_fighter'],
                fighters_data['blue_fighter'],
                fighters_data['red_fighter_id'],
                fighters_data['blue_fighter_id'],
                fighters_data['result']
            ])

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    spider = UFCFightsSpider()
    spider.run()