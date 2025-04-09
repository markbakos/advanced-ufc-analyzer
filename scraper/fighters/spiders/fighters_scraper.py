import csv
import datetime
import re
import string
import logging
import scrapy
from scrapy import Request

LOGGER = logging.getLogger(__name__)

class UFCStatsSpider(scrapy.Spider):
    name = "ufc_stats_spider"
    allowed_domains = ["ufcstats.com"]
    start_urls = ["http://ufcstats.com/statistics/fighters"]

    letters = string.ascii_lowercase

    fighter_links = set()

    def __init__(self, *args, **kwargs):
        super(UFCStatsSpider, self).__init__(*args, **kwargs)
        self.output_file = '../fighters.csv'

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

    def start_requests(self):
        for letter in self.letters:
            LOGGER.info(f"Collecting letter: {letter}")
            url = f"http://ufcstats.com/statistics/fighters?char={letter}&page=all"
            yield Request(url, callback=self.extract_fighter_links)

    def extract_fighter_links(self, response):
        fighters = response.css('table.b-statistics__table tr')

        for fighter_row in fighters[1:]:
            cells = fighter_row.css('td')
            if len(cells) < 2:
                continue

            fighter_link = cells[0].css('a::attr(href)').get()
            if fighter_link:
                yield Request(fighter_link, callback=self.parse_fighter_stats)

        
