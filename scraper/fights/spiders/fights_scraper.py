import requests
import csv
import logging
import time
import datetime
import asyncio
import aiohttp
from typing import Set, Optional, Dict, Any
from bs4 import BeautifulSoup
from scraper.fights.extractors import (
    extract_fighters,
    extract_fight_data,
    extract_total_stats,
    extract_strike_data
)

from scraper.fighters.extractors import extract_career_statistics, extract_fights, extract_physical_data

LOGGER = logging.getLogger(__name__)

# FOR TESTING, ONLY ONE PAGE
TEST_RUN = True

MAX_CONCURRENT_REQUESTS = 5

class UFCFightsSpider:
    """
    Spider for scraping UFC fights from ufcstats.com.
    """
    
    name = "ufc_fights_spider"

    def __init__(self):
        """Initialize the spider with output file, HTTP session, and header configurations"""
        self.output_file = 'fights.csv'
        self.headers = {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }

        # declare variables for tracking extraction time avgs
        self.total_extraction_time = 0
        self.fight_count = 0

        self._initialize_csv()

    def _initialize_csv(self) -> None:
        """Creates the CSV file and writes the header row"""
        with open(self.output_file, 'w', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                # fighter data
                'fight_id', 'event_name', 'event_date', 'location', 'red_fighter_name', 'blue_fighter_name',
                'red_fighter_id', 'blue_fighter_id', 'result', 

                # fight data
                'win_method', 'time', 'round', 'total_rounds', 'referee',

                # fight stats
                'red_knockdowns_landed', 'red_sig_strikes_landed', 'red_sig_strikes_thrown', 'red_sig_strike_percent', 'red_total_strikes_landed', 
                'red_total_strikes_thrown', 'red_takedowns_landed', 'red_takedowns_attempted', 'red_takedowns_percent', 'red_sub_attempts', 'red_reversals', 'red_control_time',

                'blue_knockdowns_landed', 'blue_sig_strikes_landed', 'blue_sig_strikes_thrown', 'blue_sig_strike_percent', 'blue_total_strikes_landed', 
                'blue_total_strikes_thrown', 'blue_takedowns_landed', 'blue_takedowns_attempted', 'blue_takedowns_percent', 'blue_sub_attempts', 'blue_reversals', 'blue_control_time',

                # fight round stats
                'red_knockdowns_landed_rd1', 'red_sig_strikes_landed_rd1', 'red_sig_strikes_thrown_rd1', 'red_sig_strike_percent_rd1', 'red_total_strikes_landed_rd1', 'red_total_strikes_thrown_rd1',
                'red_takedowns_landed_rd1', 'red_takedowns_attempted_rd1', 'red_takedowns_percent_rd1', 'red_sub_attempts_rd1', 'red_reversals_rd1', 'red_control_time_rd1',

                'red_knockdowns_landed_rd2', 'red_sig_strikes_landed_rd2', 'red_sig_strikes_thrown_rd2', 'red_sig_strike_percent_rd2', 'red_total_strikes_landed_rd2', 'red_total_strikes_thrown_rd2',
                'red_takedowns_landed_rd2', 'red_takedowns_attempted_rd2', 'red_takedowns_percent_rd2', 'red_sub_attempts_rd2', 'red_reversals_rd2', 'red_control_time_rd2',

                'red_knockdowns_landed_rd3', 'red_sig_strikes_landed_rd3', 'red_sig_strikes_thrown_rd3', 'red_sig_strike_percent_rd3', 'red_total_strikes_landed_rd3', 'red_total_strikes_thrown_rd3',
                'red_takedowns_landed_rd3', 'red_takedowns_attempted_rd3', 'red_takedowns_percent_rd3', 'red_sub_attempts_rd3', 'red_reversals_rd3', 'red_control_time_rd3',

                'red_knockdowns_landed_rd4', 'red_sig_strikes_landed_rd4', 'red_sig_strikes_thrown_rd4', 'red_sig_strike_percent_rd4', 'red_total_strikes_landed_rd4', 'red_total_strikes_thrown_rd4',
                'red_takedowns_landed_rd4', 'red_takedowns_attempted_rd4', 'red_takedowns_percent_rd4', 'red_sub_attempts_rd4', 'red_reversals_rd4', 'red_control_time_rd4',

                'red_knockdowns_landed_rd5', 'red_sig_strikes_landed_rd5', 'red_sig_strikes_thrown_rd5', 'red_sig_strike_percent_rd5', 'red_total_strikes_landed_rd5', 'red_total_strikes_thrown_rd5',
                'red_takedowns_landed_rd5', 'red_takedowns_attempted_rd5', 'red_takedowns_percent_rd5', 'red_sub_attempts_rd5', 'red_reversals_rd5', 'red_control_time_rd5',

                
                'blue_knockdowns_landed_rd1', 'blue_sig_strikes_landed_rd1', 'blue_sig_strikes_thrown_rd1', 'blue_sig_strike_percent_rd1', 'blue_total_strikes_landed_rd1', 'blue_total_strikes_thrown_rd1',
                'blue_takedowns_landed_rd1', 'blue_takedowns_attempted_rd1', 'blue_takedowns_percent_rd1', 'blue_sub_attempts_rd1', 'blue_reversals_rd1', 'blue_control_time_rd1',

                'blue_knockdowns_landed_rd2', 'blue_sig_strikes_landed_rd2', 'blue_sig_strikes_thrown_rd2', 'blue_sig_strike_percent_rd2', 'blue_total_strikes_landed_rd2', 'blue_total_strikes_thrown_rd2',
                'blue_takedowns_landed_rd2', 'blue_takedowns_attempted_rd2', 'blue_takedowns_percent_rd2', 'blue_sub_attempts_rd2', 'blue_reversals_rd2', 'blue_control_time_rd2',

                'blue_knockdowns_landed_rd3', 'blue_sig_strikes_landed_rd3', 'blue_sig_strikes_thrown_rd3', 'blue_sig_strike_percent_rd3', 'blue_total_strikes_landed_rd3', 'blue_total_strikes_thrown_rd3',
                'blue_takedowns_landed_rd3', 'blue_takedowns_attempted_rd3', 'blue_takedowns_percent_rd3', 'blue_sub_attempts_rd3', 'blue_reversals_rd3', 'blue_control_time_rd3',

                'blue_knockdowns_landed_rd4', 'blue_sig_strikes_landed_rd4', 'blue_sig_strikes_thrown_rd4', 'blue_sig_strike_percent_rd4', 'blue_total_strikes_landed_rd4', 'blue_total_strikes_thrown_rd4',
                'blue_takedowns_landed_rd4', 'blue_takedowns_attempted_rd4', 'blue_takedowns_percent_rd4', 'blue_sub_attempts_rd4', 'blue_reversals_rd4', 'blue_control_time_rd4',

                'blue_knockdowns_landed_rd5', 'blue_sig_strikes_landed_rd5', 'blue_sig_strikes_thrown_rd5', 'blue_sig_strike_percent_rd5', 'blue_total_strikes_landed_rd5', 'blue_total_strikes_thrown_rd5',
                'blue_takedowns_landed_rd5', 'blue_takedowns_attempted_rd5', 'blue_takedowns_percent_rd5', 'blue_sub_attempts_rd5', 'blue_reversals_rd5', 'blue_control_time_rd5',

                # fight strike stats
                'red_head_strikes_landed', 'red_head_strikes_thrown', 'red_body_strikes_landed', 'red_body_strikes_thrown', 'red_leg_strikes_landed', 'red_leg_strikes_thrown',
                'red_distance_strikes_landed', 'red_distance_strikes_thrown', 'red_clinch_strikes_landed', 'red_clinch_strikes_thrown', 'red_ground_strikes_landed', 'red_ground_strikes_thrown',

                'blue_head_strikes_landed', 'blue_head_strikes_thrown', 'blue_body_strikes_landed', 'blue_body_strikes_thrown', 'blue_leg_strikes_landed', 'blue_leg_strikes_thrown', 
                'blue_distance_strikes_landed', 'blue_distance_strikes_thrown', 'blue_clinch_strikes_landed', 'blue_clinch_strikes_thrown', 'blue_ground_strikes_landed', 'blue_ground_strikes_thrown',

                # fight round strike stats
                'red_head_strikes_landed_rd1', 'red_head_strikes_thrown_rd1', 'red_body_strikes_landed_rd1', 'red_body_strikes_thrown_rd1', 'red_leg_strikes_landed_rd1', 'red_leg_strikes_thrown_rd1',
                'red_distance_strikes_landed_rd1', 'red_distance_strikes_thrown_rd1', 'red_clinch_strikes_landed_rd1', 'red_clinch_strikes_thrown_rd1', 'red_ground_strikes_landed_rd1', 'red_ground_strikes_thrown_rd1',

                'red_head_strikes_landed_rd2', 'red_head_strikes_thrown_rd2', 'red_body_strikes_landed_rd2', 'red_body_strikes_thrown_rd2', 'red_leg_strikes_landed_rd2', 'red_leg_strikes_thrown_rd2',
                'red_distance_strikes_landed_rd2', 'red_distance_strikes_thrown_rd2', 'red_clinch_strikes_landed_rd2', 'red_clinch_strikes_thrown_rd2', 'red_ground_strikes_landed_rd2', 'red_ground_strikes_thrown_rd2',

                'red_head_strikes_landed_rd3', 'red_head_strikes_thrown_rd3', 'red_body_strikes_landed_rd3', 'red_body_strikes_thrown_rd3', 'red_leg_strikes_landed_rd3', 'red_leg_strikes_thrown_rd3',
                'red_distance_strikes_landed_rd3', 'red_distance_strikes_thrown_rd3', 'red_clinch_strikes_landed_rd3', 'red_clinch_strikes_thrown_rd3', 'red_ground_strikes_landed_rd3', 'red_ground_strikes_thrown_rd3',

                'red_head_strikes_landed_rd4', 'red_head_strikes_thrown_rd4', 'red_body_strikes_landed_rd4', 'red_body_strikes_thrown_rd4', 'red_leg_strikes_landed_rd4', 'red_leg_strikes_thrown_rd4',
                'red_distance_strikes_landed_rd4', 'red_distance_strikes_thrown_rd4', 'red_clinch_strikes_landed_rd4', 'red_clinch_strikes_thrown_rd4', 'red_ground_strikes_landed_rd4', 'red_ground_strikes_thrown_rd4',

                'red_head_strikes_landed_rd5', 'red_head_strikes_thrown_rd5', 'red_body_strikes_landed_rd5', 'red_body_strikes_thrown_rd5', 'red_leg_strikes_landed_rd5', 'red_leg_strikes_thrown_rd5',
                'red_distance_strikes_landed_rd5', 'red_distance_strikes_thrown_rd5', 'red_clinch_strikes_landed_rd5', 'red_clinch_strikes_thrown_rd5', 'red_ground_strikes_landed_rd5', 'red_ground_strikes_thrown_rd5',
                

                'blue_head_strikes_landed_rd1', 'blue_head_strikes_thrown_rd1', 'blue_body_strikes_landed_rd1', 'blue_body_strikes_thrown_rd1', 'blue_leg_strikes_landed_rd1', 'blue_leg_strikes_thrown_rd1',
                'blue_distance_strikes_landed_rd1', 'blue_distance_strikes_thrown_rd1', 'blue_clinch_strikes_landed_rd1', 'blue_clinch_strikes_thrown_rd1', 'blue_ground_strikes_landed_rd1', 'blue_ground_strikes_thrown_rd1',
                
                'blue_head_strikes_landed_rd2', 'blue_head_strikes_thrown_rd2', 'blue_body_strikes_landed_rd2', 'blue_body_strikes_thrown_rd2', 'blue_leg_strikes_landed_rd2', 'blue_leg_strikes_thrown_rd2',
                'blue_distance_strikes_landed_rd2', 'blue_distance_strikes_thrown_rd2', 'blue_clinch_strikes_landed_rd2', 'blue_clinch_strikes_thrown_rd2', 'blue_ground_strikes_landed_rd2', 'blue_ground_strikes_thrown_rd2',

                'blue_head_strikes_landed_rd3', 'blue_head_strikes_thrown_rd3', 'blue_body_strikes_landed_rd3', 'blue_body_strikes_thrown_rd3', 'blue_leg_strikes_landed_rd3', 'blue_leg_strikes_thrown_rd3',
                'blue_distance_strikes_landed_rd3', 'blue_distance_strikes_thrown_rd3', 'blue_clinch_strikes_landed_rd3', 'blue_clinch_strikes_thrown_rd3', 'blue_ground_strikes_landed_rd3', 'blue_ground_strikes_thrown_rd3',
                
                'blue_head_strikes_landed_rd4', 'blue_head_strikes_thrown_rd4', 'blue_body_strikes_landed_rd4', 'blue_body_strikes_thrown_rd4', 'blue_leg_strikes_landed_rd4', 'blue_leg_strikes_thrown_rd4',
                'blue_distance_strikes_landed_rd4', 'blue_distance_strikes_thrown_rd4', 'blue_clinch_strikes_landed_rd4', 'blue_clinch_strikes_thrown_rd4', 'blue_ground_strikes_landed_rd4', 'blue_ground_strikes_thrown_rd4',
                
                'blue_head_strikes_landed_rd5', 'blue_head_strikes_thrown_rd5', 'blue_body_strikes_landed_rd5', 'blue_body_strikes_thrown_rd5', 'blue_leg_strikes_landed_rd5', 'blue_leg_strikes_thrown_rd5',
                'blue_distance_strikes_landed_rd5', 'blue_distance_strikes_thrown_rd5', 'blue_clinch_strikes_landed_rd5', 'blue_clinch_strikes_thrown_rd5', 'blue_ground_strikes_landed_rd5', 'blue_ground_strikes_thrown_rd5',

                # snapshot of red fighter stats
                'career_red_total_ufc_fights', 'career_red_wins_in_ufc', 'career_red_losses_in_ufc', 'career_red_draws_in_ufc',
                'career_red_wins_by_dec','career_red_losses_by_dec','career_red_wins_by_sub','career_red_losses_by_sub','career_red_wins_by_ko','career_red_losses_by_ko',
                'career_red_knockdowns_landed', 'career_red_knockdowns_absorbed', 'career_red_strikes_landed', 'career_red_strikes_absorbed',
                'career_red_takedowns_landed', 'career_red_takedowns_absorbed', 'career_red_sub_attempts_landed', 'career_red_sub_attempts_absorbed',
                'career_red_total_rounds', 'career_red_total_time_minutes', 'career_red_last_fight_date', 'career_red_last_win_date',
                'career_red_SLpM', 'career_red_str_acc', 'career_red_SApM', 'career_red_str_def', 'career_red_td_avg', 'career_red_td_acc', 'career_red_td_def', 'career_red_sub_avg',
                'career_red_height_cm', 'career_red_weight_kg', 'career_red_reach_cm', 'career_red_stance', 'career_red_date_of_birth',
                'career_red_avg_knockdowns_landed', 'career_red_avg_knockdowns_absorbed', 'career_red_avg_strikes_landed', 'career_red_avg_strikes_absorbed',
                'career_red_avg_takedowns_landed', 'career_red_avg_takedowns_absorbed', 'career_red_avg_submission_attempts_landed',
                'career_red_avg_submission_attempts_absorbed', 'career_red_avg_fight_time_min',

                # snapshot of blue fighter stats
                'career_blue_total_ufc_fights', 'career_blue_wins_in_ufc', 'career_blue_losses_in_ufc', 'career_blue_draws_in_ufc',
                'career_blue_wins_by_dec','career_blue_losses_by_dec','career_blue_wins_by_sub','career_blue_losses_by_sub','career_blue_wins_by_ko','career_blue_losses_by_ko',
                'career_blue_knockdowns_landed', 'career_blue_knockdowns_absorbed', 'career_blue_strikes_landed', 'career_blue_strikes_absorbed',
                'career_blue_takedowns_landed', 'career_blue_takedowns_absorbed', 'career_blue_sub_attempts_landed', 'career_blue_sub_attempts_absorbed',
                'career_blue_total_rounds', 'career_blue_total_time_minutes', 'career_blue_last_fight_date', 'career_blue_last_win_date',
                'career_blue_SLpM', 'career_blue_str_acc', 'career_blue_SApM', 'career_blue_str_def', 'career_blue_td_avg', 'career_blue_td_acc', 'career_blue_td_def', 'career_blue_sub_avg',
                'career_blue_height_cm', 'career_blue_weight_kg', 'career_blue_reach_cm', 'career_blue_stance', 'career_blue_date_of_birth',
                'career_blue_avg_knockdowns_landed', 'career_blue_avg_knockdowns_absorbed', 'career_blue_avg_strikes_landed', 'career_blue_avg_strikes_absorbed',
                'career_blue_avg_takedowns_landed', 'career_blue_avg_takedowns_absorbed', 'career_blue_avg_submission_attempts_landed',
                'career_blue_avg_submission_attempts_absorbed', 'career_blue_avg_fight_time_min',

                'updated_timestamp'
            ])

    async def run(self) -> None:
        """
        Execute the spider's main workflow:
        1. Collect all event links
        2. Process each event's page to extract fights
        """
        async with aiohttp.ClientSession(headers=self.headers) as session:
            self.session = session
            all_event_links = await self.collect_all_event_links()
            LOGGER.info(f"Found {len(all_event_links)} unique event links")
            
    async def collect_all_event_links(self) -> Set[str]:
        """
        Collects links to all event profile pages
        
        Returns:
            Set of unique event profile URLs
        """
        all_links = set()

        url = f"http://ufcstats.com/statistics/events/completed{'?page=all' if not TEST_RUN else ''}"

        html = await self.fetch_page(url)
        if not html:
            return all_links

        links = await self.extract_event_page_links(html)
        all_links.update(links)

        LOGGER.info(f"Found {len(all_links)} unique links")
        return all_links

    async def fetch_page(self, url: str) -> Optional[str]:
        """
        Helper function to fetch the HTML content of a page
        
        Args:
            url: The URL to fetch
            
        Returns:
            HTML content as string or None if request fails
        """
        try:
            LOGGER.info(f"Fetching page: {url}")
            async with self.session.get(url) as response:
                if response.status == 200:
                    return await response.text()
                response.raise_for_status()
        except Exception as e:
            LOGGER.error(f"Error fetching page {url}: {e}")
            return None
    
    async def extract_event_page_links(self, html: str) -> Set[str]:
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
                await self.extract_fight_links(event_url)
                await asyncio.sleep(1)

        return links

    async def extract_fight_links(self, event_url: str) -> Set[str]:
        """
        Extracts fight links from an event page
        
        Args:
            event_url: URL of the event page
            
        Returns:
            Set of unique fight URLs
        """
        links = set()
        
        html = await self.fetch_page(event_url)
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
            date_item = details_box.select_one('li.b-list__box-list-item:has(i:-soup-contains("Date:"))')
            if date_item:
                date_text = date_item.get_text(strip=True).replace('Date:', '').strip()
                event_date = date_text
                LOGGER.info(f"Event date: {event_date}")
                
            # extract location
            location_item = details_box.select_one('li.b-list__box-list-item:has(i:-soup-contains("Location:"))')
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
        
        # process fights in batches
        tasks = []
        for fight_row in fight_rows:
            fight_link = fight_row.select_one('td:first-child a.b-flag')
            if fight_link and fight_link.get('href'):
                fight_url = fight_link.get('href')
                links.add(fight_url)
                LOGGER.info(f"Found fight: {fight_url}")
                
                # task to process this fight
                task = asyncio.create_task(self.parse_fight_stats(fight_url, event_date, event_location, event_name))
                tasks.append(task)
                
                if len(tasks) >= MAX_CONCURRENT_REQUESTS:
                    await asyncio.gather(*tasks)
                    tasks = []
                    await asyncio.sleep(1)
        
        # process any remaining tasks
        if tasks:
            await asyncio.gather(*tasks)
        
        return links

    async def parse_fight_stats(self, fight_url: str, event_date: str, event_location: str, event_name: str) -> None:
        """
        Parses and saves statistics for a single fight
        
        Args:
            fight_url: URL of the fight page
            event_date: Date of the event
            event_location: Location of the event
            event_name: Name of the event
        """

        start_time = time.time()

        html = await self.fetch_page(fight_url)
        if not html:
            LOGGER.error(f"Could not fetch fight page: {fight_url}")
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
        fight_data = extract_fight_data(soup)
        fight_total_stats = extract_total_stats(soup, int(fight_data['round']))
        fight_strike_stats = extract_strike_data(soup, int(fight_data['round']))

        fight_date_limit = datetime.datetime.strptime(event_date, "%B %d, %Y")
            
        red_html, blue_html = await asyncio.gather(
            self.fetch_page(f"http://ufcstats.com/fighter-details/{fighters_data['red_fighter_id']}"),
            self.fetch_page(f"http://ufcstats.com/fighter-details/{fighters_data['blue_fighter_id']}")
        )

        red_soup = BeautifulSoup(red_html, 'html.parser') if red_html else None
        blue_soup = BeautifulSoup(blue_html, 'html.parser') if blue_html else None

        red_fighter_snapshot = extract_fights(red_soup, fight_date_limit)
        red_fighter_snapshot.update(extract_career_statistics(red_soup))
        red_fighter_snapshot.update(extract_physical_data(red_soup))
        
        blue_fighter_snapshot = extract_fights(blue_soup, fight_date_limit)
        blue_fighter_snapshot.update(extract_career_statistics(blue_soup))
        blue_fighter_snapshot.update(extract_physical_data(blue_soup))

        async with asyncio.Lock():
            self._save_fight_data(fight_id, event_data, fighters_data, fight_data, fight_total_stats, fight_strike_stats, red_fighter_snapshot, blue_fighter_snapshot)

        end_time = time.time()
        extraction_time = end_time - start_time
        LOGGER.info(f"Extraction time for fight {fight_id}: {extraction_time:.2f} seconds")

        self._update_average_extraction_time(extraction_time)
    
    def _update_average_extraction_time(self, extraction_time: float) -> None:
        """
        Updates the running average of extraction times
        
        Args:
            extraction_time: Time taken for the current extraction
        """
        self.total_extraction_time += extraction_time
        self.fight_count += 1
        
        if self.fight_count > 0:
            average_time = self.total_extraction_time / self.fight_count
            LOGGER.info(f"Average extraction time across {self.fight_count} fights: {average_time:.2f} seconds")

    def _save_fight_data(self, fight_id: str, event_data: Dict[str, Any], fighters_data: Dict[str, Any], fight_data: Dict[str, Any],
                         fight_total_stats: Dict[str, Any], fight_strike_stats: Dict[str, Any], red_fighter_snapshot: Dict[str, Any], blue_fighter_snapshot: Dict[str, Any]) -> None:
        """
        Saves the fight data to the CSV file
        """
        
        with open(self.output_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)

            red_total_fights = red_fighter_snapshot.get('total_ufc_fights', 0)

            if red_total_fights > 0:
                red_avg_knockdowns_landed = round(red_fighter_snapshot.get('knockdowns_landed', 0) / red_total_fights, 2)
                red_avg_knockdowns_absorbed = round(red_fighter_snapshot.get('knockdowns_absorbed', 0) / red_total_fights, 2)
                red_avg_strikes_landed = round(red_fighter_snapshot.get('strikes_landed', 0) / red_total_fights, 2)
                red_avg_strikes_absorbed = round(red_fighter_snapshot.get('strikes_absorbed', 0) / red_total_fights, 2)
                red_avg_takedowns_landed = round(red_fighter_snapshot.get('takedowns_landed', 0) / red_total_fights, 2)
                red_avg_takedowns_absorbed = round(red_fighter_snapshot.get('takedowns_absorbed', 0) / red_total_fights, 2)
                red_avg_submission_attempts_landed = round(red_fighter_snapshot.get('sub_attempts_landed', 0) / red_total_fights, 2)
                red_avg_submission_attempts_absorbed = round(red_fighter_snapshot.get('sub_attempts_absorbed', 0) / red_total_fights, 2)

                red_avg_fight_time_min = round(red_fighter_snapshot.get('total_time_minutes', 0) / red_total_fights, 2)
            else:
                red_avg_knockdowns_landed = 0
                red_avg_knockdowns_absorbed = 0
                red_avg_strikes_landed = 0
                red_avg_strikes_absorbed = 0
                red_avg_takedowns_landed = 0
                red_avg_takedowns_absorbed = 0
                red_avg_submission_attempts_landed = 0
                red_avg_submission_attempts_absorbed = 0
                red_avg_fight_time_min = 0
                
            blue_total_fights = blue_fighter_snapshot.get('total_ufc_fights', 0)

            if blue_total_fights > 0:
                blue_avg_knockdowns_landed = round(blue_fighter_snapshot.get('knockdowns_landed', 0) / blue_total_fights, 2)
                blue_avg_knockdowns_absorbed = round(blue_fighter_snapshot.get('knockdowns_absorbed', 0) / blue_total_fights, 2)
                blue_avg_strikes_landed = round(blue_fighter_snapshot.get('strikes_landed', 0) / blue_total_fights, 2)
                blue_avg_strikes_absorbed = round(blue_fighter_snapshot.get('strikes_absorbed', 0) / blue_total_fights, 2)
                blue_avg_takedowns_landed = round(blue_fighter_snapshot.get('takedowns_landed', 0) / blue_total_fights, 2)
                blue_avg_takedowns_absorbed = round(blue_fighter_snapshot.get('takedowns_absorbed', 0) / blue_total_fights, 2)
                blue_avg_submission_attempts_landed = round(blue_fighter_snapshot.get('sub_attempts_landed', 0) / blue_total_fights, 2)
                blue_avg_submission_attempts_absorbed = round(blue_fighter_snapshot.get('sub_attempts_absorbed', 0) / blue_total_fights, 2)

                blue_avg_fight_time_min = round(blue_fighter_snapshot.get('total_time_minutes', 0) / blue_total_fights, 2)
            else:
                blue_avg_knockdowns_landed = 0
                blue_avg_knockdowns_absorbed = 0
                blue_avg_strikes_landed = 0
                blue_avg_strikes_absorbed = 0
                blue_avg_takedowns_landed = 0
                blue_avg_takedowns_absorbed = 0
                blue_avg_submission_attempts_landed = 0
                blue_avg_submission_attempts_absorbed = 0
                blue_avg_fight_time_min = 0

            writer.writerow([
                fight_id,

                event_data['event_name'],
                event_data['event_date'],
                event_data['event_location'],

                fighters_data['red_fighter'],
                fighters_data['blue_fighter'],
                fighters_data['red_fighter_id'],
                fighters_data['blue_fighter_id'],
                fighters_data['result'],

                fight_data['win_method'],
                fight_data['time'],
                fight_data['round'],
                fight_data['total_rounds'],
                fight_data['referee'],

                fight_total_stats['red_knockdowns_landed'],
                fight_total_stats['red_sig_strikes_landed'],
                fight_total_stats['red_sig_strikes_thrown'],
                fight_total_stats['red_sig_strike_percent'],
                fight_total_stats['red_total_strikes_landed'],
                fight_total_stats['red_total_strikes_thrown'],
                fight_total_stats['red_takedowns_landed'],
                fight_total_stats['red_takedowns_attempted'],
                fight_total_stats['red_takedowns_percent'],
                fight_total_stats['red_sub_attempts'],
                fight_total_stats['red_reversals'],
                fight_total_stats['red_control_time'],

                fight_total_stats['blue_knockdowns_landed'],
                fight_total_stats['blue_sig_strikes_landed'],
                fight_total_stats['blue_sig_strikes_thrown'],
                fight_total_stats['blue_sig_strike_percent'],
                fight_total_stats['blue_total_strikes_landed'],
                fight_total_stats['blue_total_strikes_thrown'],
                fight_total_stats['blue_takedowns_landed'],
                fight_total_stats['blue_takedowns_attempted'],
                fight_total_stats['blue_takedowns_percent'],
                fight_total_stats['blue_sub_attempts'],
                fight_total_stats['blue_reversals'],
                fight_total_stats['blue_control_time'],

                fight_total_stats['red_knockdowns_landed_rd1'],
                fight_total_stats['red_sig_strikes_landed_rd1'],
                fight_total_stats['red_sig_strikes_thrown_rd1'],
                fight_total_stats['red_sig_strike_percent_rd1'],
                fight_total_stats['red_total_strikes_landed_rd1'],
                fight_total_stats['red_total_strikes_thrown_rd1'],
                fight_total_stats['red_takedowns_landed_rd1'],
                fight_total_stats['red_takedowns_attempted_rd1'],
                fight_total_stats['red_takedowns_percent_rd1'],
                fight_total_stats['red_sub_attempts_rd1'],
                fight_total_stats['red_reversals_rd1'],
                fight_total_stats['red_control_time_rd1'],

                fight_total_stats['red_knockdowns_landed_rd2'],
                fight_total_stats['red_sig_strikes_landed_rd2'],
                fight_total_stats['red_sig_strikes_thrown_rd2'],
                fight_total_stats['red_sig_strike_percent_rd2'],
                fight_total_stats['red_total_strikes_landed_rd2'],
                fight_total_stats['red_total_strikes_thrown_rd2'],
                fight_total_stats['red_takedowns_landed_rd2'],
                fight_total_stats['red_takedowns_attempted_rd2'],
                fight_total_stats['red_takedowns_percent_rd2'],
                fight_total_stats['red_sub_attempts_rd2'],
                fight_total_stats['red_reversals_rd2'],
                fight_total_stats['red_control_time_rd2'],

                fight_total_stats['red_knockdowns_landed_rd3'],
                fight_total_stats['red_sig_strikes_landed_rd3'],
                fight_total_stats['red_sig_strikes_thrown_rd3'],
                fight_total_stats['red_sig_strike_percent_rd3'],
                fight_total_stats['red_total_strikes_landed_rd3'],
                fight_total_stats['red_total_strikes_thrown_rd3'],
                fight_total_stats['red_takedowns_landed_rd3'],
                fight_total_stats['red_takedowns_attempted_rd3'],
                fight_total_stats['red_takedowns_percent_rd3'],
                fight_total_stats['red_sub_attempts_rd3'],
                fight_total_stats['red_reversals_rd3'],
                fight_total_stats['red_control_time_rd3'],

                fight_total_stats['red_knockdowns_landed_rd4'],
                fight_total_stats['red_sig_strikes_landed_rd4'],
                fight_total_stats['red_sig_strikes_thrown_rd4'],
                fight_total_stats['red_sig_strike_percent_rd4'],
                fight_total_stats['red_total_strikes_landed_rd4'],
                fight_total_stats['red_total_strikes_thrown_rd4'],
                fight_total_stats['red_takedowns_landed_rd4'],
                fight_total_stats['red_takedowns_attempted_rd4'],
                fight_total_stats['red_takedowns_percent_rd4'],
                fight_total_stats['red_sub_attempts_rd4'],
                fight_total_stats['red_reversals_rd4'],
                fight_total_stats['red_control_time_rd4'],

                fight_total_stats['red_knockdowns_landed_rd5'],
                fight_total_stats['red_sig_strikes_landed_rd5'],
                fight_total_stats['red_sig_strikes_thrown_rd5'],
                fight_total_stats['red_sig_strike_percent_rd5'],
                fight_total_stats['red_total_strikes_landed_rd5'],
                fight_total_stats['red_total_strikes_thrown_rd5'],
                fight_total_stats['red_takedowns_landed_rd5'],
                fight_total_stats['red_takedowns_attempted_rd5'],
                fight_total_stats['red_takedowns_percent_rd5'],
                fight_total_stats['red_sub_attempts_rd5'],
                fight_total_stats['red_reversals_rd5'],
                fight_total_stats['red_control_time_rd5'],

                fight_total_stats['blue_knockdowns_landed_rd1'],
                fight_total_stats['blue_sig_strikes_landed_rd1'],
                fight_total_stats['blue_sig_strikes_thrown_rd1'],   
                fight_total_stats['blue_sig_strike_percent_rd1'],
                fight_total_stats['blue_total_strikes_landed_rd1'],
                fight_total_stats['blue_total_strikes_thrown_rd1'],
                fight_total_stats['blue_takedowns_landed_rd1'],
                fight_total_stats['blue_takedowns_attempted_rd1'],
                fight_total_stats['blue_takedowns_percent_rd1'],
                fight_total_stats['blue_sub_attempts_rd1'],
                fight_total_stats['blue_reversals_rd1'],
                fight_total_stats['blue_control_time_rd1'],

                fight_total_stats['blue_knockdowns_landed_rd2'],
                fight_total_stats['blue_sig_strikes_landed_rd2'],
                fight_total_stats['blue_sig_strikes_thrown_rd2'],
                fight_total_stats['blue_sig_strike_percent_rd2'],
                fight_total_stats['blue_total_strikes_landed_rd2'],
                fight_total_stats['blue_total_strikes_thrown_rd2'],
                fight_total_stats['blue_takedowns_landed_rd2'],
                fight_total_stats['blue_takedowns_attempted_rd2'],
                fight_total_stats['blue_takedowns_percent_rd2'],
                fight_total_stats['blue_sub_attempts_rd2'],
                fight_total_stats['blue_reversals_rd2'],
                fight_total_stats['blue_control_time_rd2'],

                fight_total_stats['blue_knockdowns_landed_rd3'],
                fight_total_stats['blue_sig_strikes_landed_rd3'],
                fight_total_stats['blue_sig_strikes_thrown_rd3'],
                fight_total_stats['blue_sig_strike_percent_rd3'],
                fight_total_stats['blue_total_strikes_landed_rd3'],
                fight_total_stats['blue_total_strikes_thrown_rd3'],
                fight_total_stats['blue_takedowns_landed_rd3'],
                fight_total_stats['blue_takedowns_attempted_rd3'],
                fight_total_stats['blue_takedowns_percent_rd3'],
                fight_total_stats['blue_sub_attempts_rd3'],
                fight_total_stats['blue_reversals_rd3'],
                fight_total_stats['blue_control_time_rd3'],

                fight_total_stats['blue_knockdowns_landed_rd4'],
                fight_total_stats['blue_sig_strikes_landed_rd4'],
                fight_total_stats['blue_sig_strikes_thrown_rd4'],
                fight_total_stats['blue_sig_strike_percent_rd4'],
                fight_total_stats['blue_total_strikes_landed_rd4'],
                fight_total_stats['blue_total_strikes_thrown_rd4'],
                fight_total_stats['blue_takedowns_landed_rd4'],
                fight_total_stats['blue_takedowns_attempted_rd4'],
                fight_total_stats['blue_takedowns_percent_rd4'],
                fight_total_stats['blue_sub_attempts_rd4'],
                fight_total_stats['blue_reversals_rd4'],
                fight_total_stats['blue_control_time_rd4'],

                fight_total_stats['blue_knockdowns_landed_rd5'],
                fight_total_stats['blue_sig_strikes_landed_rd5'],
                fight_total_stats['blue_sig_strikes_thrown_rd5'],
                fight_total_stats['blue_sig_strike_percent_rd5'],
                fight_total_stats['blue_total_strikes_landed_rd5'],
                fight_total_stats['blue_total_strikes_thrown_rd5'],
                fight_total_stats['blue_takedowns_landed_rd5'],
                fight_total_stats['blue_takedowns_attempted_rd5'],
                fight_total_stats['blue_takedowns_percent_rd5'],
                fight_total_stats['blue_sub_attempts_rd5'],
                fight_total_stats['blue_reversals_rd5'],
                fight_total_stats['blue_control_time_rd5'],

                fight_strike_stats['red_head_strikes_landed'],
                fight_strike_stats['red_head_strikes_thrown'],
                fight_strike_stats['red_body_strikes_landed'],
                fight_strike_stats['red_body_strikes_thrown'],
                fight_strike_stats['red_leg_strikes_landed'],
                fight_strike_stats['red_leg_strikes_thrown'],
                fight_strike_stats['red_distance_strikes_landed'],
                fight_strike_stats['red_distance_strikes_thrown'],
                fight_strike_stats['red_clinch_strikes_landed'],
                fight_strike_stats['red_clinch_strikes_thrown'],
                fight_strike_stats['red_ground_strikes_landed'],
                fight_strike_stats['red_ground_strikes_thrown'],

                fight_strike_stats['blue_head_strikes_landed'],
                fight_strike_stats['blue_head_strikes_thrown'],
                fight_strike_stats['blue_body_strikes_landed'],
                fight_strike_stats['blue_body_strikes_thrown'],
                fight_strike_stats['blue_leg_strikes_landed'],
                fight_strike_stats['blue_leg_strikes_thrown'],
                fight_strike_stats['blue_distance_strikes_landed'],
                fight_strike_stats['blue_distance_strikes_thrown'],
                fight_strike_stats['blue_clinch_strikes_landed'],
                fight_strike_stats['blue_clinch_strikes_thrown'],
                fight_strike_stats['blue_ground_strikes_landed'],
                fight_strike_stats['blue_ground_strikes_thrown'],

                fight_strike_stats['red_head_strikes_landed_rd1'],
                fight_strike_stats['red_head_strikes_thrown_rd1'],
                fight_strike_stats['red_body_strikes_landed_rd1'],
                fight_strike_stats['red_body_strikes_thrown_rd1'],
                fight_strike_stats['red_leg_strikes_landed_rd1'],
                fight_strike_stats['red_leg_strikes_thrown_rd1'],
                fight_strike_stats['red_distance_strikes_landed_rd1'],
                fight_strike_stats['red_distance_strikes_thrown_rd1'],
                fight_strike_stats['red_clinch_strikes_landed_rd1'],
                fight_strike_stats['red_clinch_strikes_thrown_rd1'],
                fight_strike_stats['red_ground_strikes_landed_rd1'],
                fight_strike_stats['red_ground_strikes_thrown_rd1'],

                fight_strike_stats['red_head_strikes_landed_rd2'],
                fight_strike_stats['red_head_strikes_thrown_rd2'],
                fight_strike_stats['red_body_strikes_landed_rd2'],
                fight_strike_stats['red_body_strikes_thrown_rd2'],
                fight_strike_stats['red_leg_strikes_landed_rd2'],
                fight_strike_stats['red_leg_strikes_thrown_rd2'],
                fight_strike_stats['red_distance_strikes_landed_rd2'],
                fight_strike_stats['red_distance_strikes_thrown_rd2'],
                fight_strike_stats['red_clinch_strikes_landed_rd2'],
                fight_strike_stats['red_clinch_strikes_thrown_rd2'],
                fight_strike_stats['red_ground_strikes_landed_rd2'],
                fight_strike_stats['red_ground_strikes_thrown_rd2'],

                fight_strike_stats['red_head_strikes_landed_rd3'],
                fight_strike_stats['red_head_strikes_thrown_rd3'],
                fight_strike_stats['red_body_strikes_landed_rd3'],
                fight_strike_stats['red_body_strikes_thrown_rd3'],
                fight_strike_stats['red_leg_strikes_landed_rd3'],
                fight_strike_stats['red_leg_strikes_thrown_rd3'],
                fight_strike_stats['red_distance_strikes_landed_rd3'],
                fight_strike_stats['red_distance_strikes_thrown_rd3'],
                fight_strike_stats['red_clinch_strikes_landed_rd3'],
                fight_strike_stats['red_clinch_strikes_thrown_rd3'],
                fight_strike_stats['red_ground_strikes_landed_rd3'],
                fight_strike_stats['red_ground_strikes_thrown_rd3'],

                fight_strike_stats['red_head_strikes_landed_rd4'],
                fight_strike_stats['red_head_strikes_thrown_rd4'],
                fight_strike_stats['red_body_strikes_landed_rd4'],
                fight_strike_stats['red_body_strikes_thrown_rd4'],
                fight_strike_stats['red_leg_strikes_landed_rd4'],
                fight_strike_stats['red_leg_strikes_thrown_rd4'],
                fight_strike_stats['red_distance_strikes_landed_rd4'],
                fight_strike_stats['red_distance_strikes_thrown_rd4'],
                fight_strike_stats['red_clinch_strikes_landed_rd4'],
                fight_strike_stats['red_clinch_strikes_thrown_rd4'],
                fight_strike_stats['red_ground_strikes_landed_rd4'],
                fight_strike_stats['red_ground_strikes_thrown_rd4'],

                fight_strike_stats['red_head_strikes_landed_rd5'],
                fight_strike_stats['red_head_strikes_thrown_rd5'],
                fight_strike_stats['red_body_strikes_landed_rd5'],
                fight_strike_stats['red_body_strikes_thrown_rd5'],
                fight_strike_stats['red_leg_strikes_landed_rd5'],
                fight_strike_stats['red_leg_strikes_thrown_rd5'],
                fight_strike_stats['red_distance_strikes_landed_rd5'],
                fight_strike_stats['red_distance_strikes_thrown_rd5'],
                fight_strike_stats['red_clinch_strikes_landed_rd5'],
                fight_strike_stats['red_clinch_strikes_thrown_rd5'],
                fight_strike_stats['red_ground_strikes_landed_rd5'],
                fight_strike_stats['red_ground_strikes_thrown_rd5'],

                fight_strike_stats['blue_head_strikes_landed_rd1'],
                fight_strike_stats['blue_head_strikes_thrown_rd1'],
                fight_strike_stats['blue_body_strikes_landed_rd1'],
                fight_strike_stats['blue_body_strikes_thrown_rd1'],
                fight_strike_stats['blue_leg_strikes_landed_rd1'],
                fight_strike_stats['blue_leg_strikes_thrown_rd1'],
                fight_strike_stats['blue_distance_strikes_landed_rd1'],
                fight_strike_stats['blue_distance_strikes_thrown_rd1'],
                fight_strike_stats['blue_clinch_strikes_landed_rd1'],
                fight_strike_stats['blue_clinch_strikes_thrown_rd1'],
                fight_strike_stats['blue_ground_strikes_landed_rd1'],
                fight_strike_stats['blue_ground_strikes_thrown_rd1'],

                fight_strike_stats['blue_head_strikes_landed_rd2'],
                fight_strike_stats['blue_head_strikes_thrown_rd2'],
                fight_strike_stats['blue_body_strikes_landed_rd2'],
                fight_strike_stats['blue_body_strikes_thrown_rd2'],
                fight_strike_stats['blue_leg_strikes_landed_rd2'],
                fight_strike_stats['blue_leg_strikes_thrown_rd2'],  
                fight_strike_stats['blue_distance_strikes_landed_rd2'],
                fight_strike_stats['blue_distance_strikes_thrown_rd2'],
                fight_strike_stats['blue_clinch_strikes_landed_rd2'],
                fight_strike_stats['blue_clinch_strikes_thrown_rd2'],
                fight_strike_stats['blue_ground_strikes_landed_rd2'],
                fight_strike_stats['blue_ground_strikes_thrown_rd2'],

                fight_strike_stats['blue_head_strikes_landed_rd3'],
                fight_strike_stats['blue_head_strikes_thrown_rd3'],
                fight_strike_stats['blue_body_strikes_landed_rd3'],
                fight_strike_stats['blue_body_strikes_thrown_rd3'],
                fight_strike_stats['blue_leg_strikes_landed_rd3'],
                fight_strike_stats['blue_leg_strikes_thrown_rd3'],
                fight_strike_stats['blue_distance_strikes_landed_rd3'],
                fight_strike_stats['blue_distance_strikes_thrown_rd3'],
                fight_strike_stats['blue_clinch_strikes_landed_rd3'],
                fight_strike_stats['blue_clinch_strikes_thrown_rd3'],
                fight_strike_stats['blue_ground_strikes_landed_rd3'],
                fight_strike_stats['blue_ground_strikes_thrown_rd3'],

                fight_strike_stats['blue_head_strikes_landed_rd4'],
                fight_strike_stats['blue_head_strikes_thrown_rd4'],
                fight_strike_stats['blue_body_strikes_landed_rd4'],
                fight_strike_stats['blue_body_strikes_thrown_rd4'],
                fight_strike_stats['blue_leg_strikes_landed_rd4'],
                fight_strike_stats['blue_leg_strikes_thrown_rd4'],
                fight_strike_stats['blue_distance_strikes_landed_rd4'],
                fight_strike_stats['blue_distance_strikes_thrown_rd4'],
                fight_strike_stats['blue_clinch_strikes_landed_rd4'],
                fight_strike_stats['blue_clinch_strikes_thrown_rd4'],
                fight_strike_stats['blue_ground_strikes_landed_rd4'],
                fight_strike_stats['blue_ground_strikes_thrown_rd4'],

                fight_strike_stats['blue_head_strikes_landed_rd5'],
                fight_strike_stats['blue_head_strikes_thrown_rd5'],
                fight_strike_stats['blue_body_strikes_landed_rd5'],
                fight_strike_stats['blue_body_strikes_thrown_rd5'],
                fight_strike_stats['blue_leg_strikes_landed_rd5'],
                fight_strike_stats['blue_leg_strikes_thrown_rd5'],
                fight_strike_stats['blue_distance_strikes_landed_rd5'],
                fight_strike_stats['blue_distance_strikes_thrown_rd5'],
                fight_strike_stats['blue_clinch_strikes_landed_rd5'],
                fight_strike_stats['blue_clinch_strikes_thrown_rd5'],
                fight_strike_stats['blue_ground_strikes_landed_rd5'],
                fight_strike_stats['blue_ground_strikes_thrown_rd5'],

                red_fighter_snapshot['total_ufc_fights'],
                red_fighter_snapshot['wins_in_ufc'],
                red_fighter_snapshot['losses_in_ufc'],
                red_fighter_snapshot['draws_in_ufc'],
                red_fighter_snapshot['wins_by_dec'],
                red_fighter_snapshot['losses_by_dec'],
                red_fighter_snapshot['wins_by_sub'],
                red_fighter_snapshot['losses_by_sub'],
                red_fighter_snapshot['wins_by_ko'],
                red_fighter_snapshot['losses_by_ko'],
                red_fighter_snapshot['knockdowns_landed'],
                red_fighter_snapshot['knockdowns_absorbed'],
                red_fighter_snapshot['strikes_landed'],
                red_fighter_snapshot['strikes_absorbed'],
                red_fighter_snapshot['takedowns_landed'],
                red_fighter_snapshot['takedowns_absorbed'],
                red_fighter_snapshot['sub_attempts_landed'],
                red_fighter_snapshot['sub_attempts_absorbed'],
                red_fighter_snapshot['total_rounds'],
                red_fighter_snapshot['total_time_minutes'],
                red_fighter_snapshot['last_fight_date'],
                red_fighter_snapshot['last_win_date'],
                red_fighter_snapshot['SLpM'],
                red_fighter_snapshot['str_acc'],
                red_fighter_snapshot['SApM'],
                red_fighter_snapshot['str_def'],
                red_fighter_snapshot['td_avg'],
                red_fighter_snapshot['td_acc'],
                red_fighter_snapshot['td_def'],
                red_fighter_snapshot['sub_avg'],
                red_fighter_snapshot['height_cm'],
                red_fighter_snapshot['weight_kg'],
                red_fighter_snapshot['reach_cm'],
                red_fighter_snapshot['stance'],
                red_fighter_snapshot['date_of_birth'],
                red_avg_knockdowns_landed,
                red_avg_knockdowns_absorbed,
                red_avg_strikes_landed,
                red_avg_strikes_absorbed,
                red_avg_takedowns_landed,
                red_avg_takedowns_absorbed,
                red_avg_submission_attempts_landed,
                red_avg_submission_attempts_absorbed,
                red_avg_fight_time_min,

                blue_fighter_snapshot['total_ufc_fights'],
                blue_fighter_snapshot['wins_in_ufc'],
                blue_fighter_snapshot['losses_in_ufc'],
                blue_fighter_snapshot['draws_in_ufc'],
                blue_fighter_snapshot['wins_by_dec'],
                blue_fighter_snapshot['losses_by_dec'],
                blue_fighter_snapshot['wins_by_sub'],
                blue_fighter_snapshot['losses_by_sub'],
                blue_fighter_snapshot['wins_by_ko'],
                blue_fighter_snapshot['losses_by_ko'],
                blue_fighter_snapshot['knockdowns_landed'],
                blue_fighter_snapshot['knockdowns_absorbed'],
                blue_fighter_snapshot['strikes_landed'],
                blue_fighter_snapshot['strikes_absorbed'],
                blue_fighter_snapshot['takedowns_landed'],
                blue_fighter_snapshot['takedowns_absorbed'],
                blue_fighter_snapshot['sub_attempts_landed'],
                blue_fighter_snapshot['sub_attempts_absorbed'],
                blue_fighter_snapshot['total_rounds'],
                blue_fighter_snapshot['total_time_minutes'],
                blue_fighter_snapshot['last_fight_date'],
                blue_fighter_snapshot['last_win_date'],
                blue_fighter_snapshot['SLpM'],  
                blue_fighter_snapshot['str_acc'],
                blue_fighter_snapshot['SApM'],
                blue_fighter_snapshot['str_def'],
                blue_fighter_snapshot['td_avg'],
                blue_fighter_snapshot['td_acc'],
                blue_fighter_snapshot['td_def'],
                blue_fighter_snapshot['sub_avg'],
                blue_fighter_snapshot['height_cm'],
                blue_fighter_snapshot['weight_kg'],
                blue_fighter_snapshot['reach_cm'],
                blue_fighter_snapshot['stance'],
                blue_fighter_snapshot['date_of_birth'],
                blue_avg_knockdowns_landed,
                blue_avg_knockdowns_absorbed,
                blue_avg_strikes_landed,
                blue_avg_strikes_absorbed,
                blue_avg_takedowns_landed,
                blue_avg_takedowns_absorbed,
                blue_avg_submission_attempts_landed,
                blue_avg_submission_attempts_absorbed,
                blue_avg_fight_time_min,
                datetime.datetime.now().isoformat()
            ])

if __name__ == '__main__':
    logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
    spider = UFCFightsSpider()
    asyncio.run(spider.run())