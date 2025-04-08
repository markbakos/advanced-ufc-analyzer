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
        for letter in ['a']:
            LOGGER.info(f"extracting letter: {letter}")
            url = f"http://ufcstats.com/statistics/fighters?char={letter}&page=all"
            yield Request(url, callback=self.parse_fighters_list)

    def parse_fighters_list(self, response):
        fighters = response.css('table.b-statistics__table tr')

        for fighter_row in fighters[1:]:
            cells = fighter_row.css('td')
            if len(cells) < 2:
                continue

            fighter_link = cells[0].css('a::attr(href)').get()
            if fighter_link:
                yield Request(fighter_link, callback=self.parse_fighter_details)

    def parse_fighter_details(self, response):
        fighter_id = response.url.split('/')[-1]
        fighter_name = response.css('h2.b-content__title-highlight::text').get()
        if fighter_name:
            fighter_name = fighter_name.strip()

        record_text = response.css('span.b-content__title-record::text').get()
        wins, losses, draws = 0, 0, 0
        if record_text:
            record_match = re.search(r'Record: (\d+)-(\d+)-(\d+)', record_text)
            if record_match:
                wins = int(record_match.group(1))
                losses = int(record_match.group(2))
                draws = int(record_match.group(3))

        total_fights = wins + losses + draws
        win_percentage = round((wins/total_fights * 100), 2) if total_fights > 0 else 0

        height_str = self.extract_info(response, 'Height:')
        weight_str = self.extract_info(response, 'Weight:')
        reach_str = self.extract_info(response, 'Reach:')
        stance = self.extract_info(response, 'STANCE:')
        dob_str = self.extract_info(response, 'DOB:')

        height_cm = None
        if height_str and "'" in height_str:
            height_parts = height_str.split("'")
            feet = int(height_parts[0].strip())
            inches = int(height_parts[1].strip('"').strip())
            height_cm = round((feet * 30.48) + (inches * 2.54), 2)

        weight_kg = None
        if weight_str and "lbs" in weight_str:
            weight_lbs = float(weight_str.replace('lbs.', '').strip())
            weight_kg = round(weight_lbs * 0.453592, 2)

        reach_cm = None
        if reach_str and '"' in reach_str:
            reach_inches = float(reach_str.replace('"', '').strip())
            reach_cm = round(reach_inches * 2.54, 2)

        birth_year = None
        if dob_str:
            try:
                dob_str = dob_str.strip()
                birth_year = int(dob_str.split(', ')[-1])
            except (ValueError, IndexError):
                pass

        slpm = self.extract_stat(response, 'SLpM:')
        str_acc = self.extract_stat(response, 'Str. Acc.:')
        sapm = self.extract_stat(response, 'SApM:')
        str_def = self.extract_stat(response, 'Str. Def:')
        td_avg = self.extract_stat(response, 'TD Avg.:')
        td_acc = self.extract_stat(response, 'TD Acc.:')
        td_def = self.extract_stat(response, 'TD Def.:')
        sub_avg = self.extract_stat(response, 'Sub. Avg.:')

        fight_rows = response.css('table.b-fight-details__table tbody tr.b-fight-details__table-row')

        total_dec_wins = 0
        total_sub_wins = 0
        total_ko_wins = 0
        total_knockdowns = 0
        total_strikes_landed = 0
        total_strikes_absorbed = 0
        total_takedowns_landed = 0
        total_takedowns_absorbed = 0
        total_sub_attempts_landed = 0
        total_sub_attempts_absorbed = 0
        total_fight_time_min = 0

        fight_rows = [row for row in fight_rows if row.css('td:first-child p.b-fight-details__table-text a')]

        for fight_row in fight_rows:
            is_win = 'b-flag_style_green' in fight_row.css('td:first-child a::attr(class)').get('')

            method = fight_row.css('td.l-page_align_left p.b-fight-details__table-text::text').getall()
            method = [m.strip() for m in method if m.strip()]

            if is_win:
                if any(m in method for m in ['KO/TKO', 'KO']):
                    total_ko_wins += 1
                elif 'SUB' in method:
                    total_sub_wins += 1
                elif any(m in method for m in ['U-DEC', 'S-DEC', 'M-DEC', 'DEC']):
                    total_dec_wins += 1

            knockdowns_text = fight_row.css('td:nth-child(3) p.b-fight-details__table-text::text').getall()
            if len(knockdowns_text) >= 2:
                if is_win:
                    try:
                        total_knockdowns += int(knockdowns_text[0].strip())
                    except (ValueError, IndexError):
                        pass

            strikes_text = fight_row.css('td:nth-child(4) p.b-fight-details__table-text::text').getall()
            if len(strikes_text) >= 2:
                try:
                    if is_win:
                        total_strikes_landed += int(strikes_text[0].strip())
                        total_strikes_absorbed += int(strikes_text[1].strip())
                    else:
                        total_strikes_landed += int(strikes_text[1].strip())
                        total_strikes_absorbed += int(strikes_text[0].strip())
                except (ValueError, IndexError):
                    pass

            takedowns_text = fight_row.css('td:nth-child(5) p.b-fight-details__table-text::text').getall()
            if len(takedowns_text) >= 2:
                try:
                    if is_win:
                        total_takedowns_landed += int(takedowns_text[0].strip())
                        total_takedowns_absorbed += int(takedowns_text[1].strip())
                    else:
                        total_takedowns_landed += int(takedowns_text[1].strip())
                        total_takedowns_absorbed += int(takedowns_text[0].strip())
                except (ValueError, IndexError):
                    pass

            submissions_text = fight_row.css('td:nth-child(6) p.b-fight-details__table-text::text').getall()
            if len(submissions_text) >= 2:
                try:
                    if is_win:
                        total_sub_attempts_landed += int(submissions_text[0].strip())
                        total_sub_attempts_absorbed += int(submissions_text[1].strip())
                    else:
                        total_sub_attempts_landed += int(submissions_text[1].strip())
                        total_sub_attempts_absorbed += int(submissions_text[0].strip())
                except (ValueError, IndexError):
                    pass

            round_text = fight_row.css('td:nth-child(9) p.b-fight-details__table-text::text').get('').strip()
            time_text = fight_row.css('td:nth-child(10) p.b-fight-details__table-text::text').get('').strip()

            try:
                round_num = int(round_text)
                time_parts = time_text.split(':')
                minutes = int(time_parts[0])
                seconds = int(time_parts[1])

                fight_time = (round_num - 1) * 5 + minutes + (seconds / 60)
                total_fight_time_min += fight_time
            except (ValueError, IndexError):
                pass

        num_fights = len(fight_rows)
        avg_knockdowns = round(total_knockdowns / num_fights, 2) if num_fights > 0 else 0
        avg_strikes_landed = round(total_strikes_landed / num_fights, 2) if num_fights > 0 else 0
        avg_strikes_absorbed = round(total_strikes_absorbed / num_fights, 2) if num_fights > 0 else 0
        avg_takedowns_landed = round(total_takedowns_landed / num_fights, 2) if num_fights > 0 else 0
        avg_takedowns_absorbed = round(total_takedowns_absorbed / num_fights, 2) if num_fights > 0 else 0
        avg_submission_attempts_landed = round(total_sub_attempts_landed / num_fights, 2) if num_fights > 0 else 0
        avg_submission_attempts_absorbed = round(total_sub_attempts_absorbed / num_fights, 2) if num_fights > 0 else 0
        avg_fight_time_min = round(total_fight_time_min / num_fights, 2) if num_fights > 0 else 0

        momentum = 0
        if num_fights >= 3:
            recent_fights = fight_rows[:3]
            for fight in recent_fights:
                is_win = 'b-flag_style_green' in fight.css('td:first-child a::attr(class)').get('')
                momentum += 1 if is_win else -1

        fighter_data = {
            'fighter_id': fighter_id,
            'fighter_name': fighter_name,
            'birth_year': birth_year,
            'height_cm': height_cm,
            'weight_kg': weight_kg,
            'reach_cm': reach_cm,
            'stance': stance,
            'fighter_style': None,
            'wins': wins,
            'losses': losses,
            'draws': draws,
            'win_percentage': win_percentage,
            'momentum': momentum,
            'SLpM': self.convert_to_float(slpm),
            'str_acc': self.convert_percentage(str_acc),
            'SApM': self.convert_to_float(sapm),
            'str_def': self.convert_percentage(str_def),
            'td_avg': self.convert_to_float(td_avg),
            'td_acc': self.convert_percentage(td_acc),
            'td_def': self.convert_percentage(td_def),
            'sub_avg': self.convert_to_float(sub_avg),
            'total_dec_wins': total_dec_wins,
            'total_sub_wins': total_sub_wins,
            'total_ko_wins': total_ko_wins,
            'total_knockdowns': total_knockdowns,
            'total_strikes_landed': total_strikes_landed,
            'total_strikes_absorbed': total_strikes_absorbed,
            'total_takedowns_landed': total_takedowns_landed,
            'total_takedowns_absorbed': total_takedowns_absorbed,
            'total_sub_attempts_landed': total_sub_attempts_landed,
            'total_sub_attempts_absorbed': total_sub_attempts_absorbed,
            'total_fight_time_min': round(total_fight_time_min, 2),
            'avg_knockdowns': avg_knockdowns,
            'avg_strikes_landed': avg_strikes_landed,
            'avg_strikes_absorbed': avg_strikes_absorbed,
            'avg_takedowns_landed': avg_takedowns_landed,
            'avg_takedowns_absorbed': avg_takedowns_absorbed,
            'avg_submission_attempts_landed': avg_submission_attempts_landed,
            'avg_submission_attempts_absorbed': avg_submission_attempts_absorbed,
            'avg_fight_time_min': avg_fight_time_min,
            'updated_timestamp': datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        }

        with open(self.output_file, 'a', newline='', encoding='utf-8') as csvfile:
            writer = csv.writer(csvfile)
            writer.writerow([
                fighter_data['fighter_id'], fighter_data['fighter_name'], fighter_data['birth_year'],
                fighter_data['height_cm'], fighter_data['weight_kg'], fighter_data['reach_cm'],
                fighter_data['stance'], fighter_data['fighter_style'], fighter_data['wins'],
                fighter_data['losses'], fighter_data['draws'], fighter_data['win_percentage'],
                fighter_data['momentum'], fighter_data['SLpM'], fighter_data['str_acc'],
                fighter_data['SApM'], fighter_data['str_def'], fighter_data['td_avg'],
                fighter_data['td_acc'], fighter_data['td_def'], fighter_data['sub_avg'],
                fighter_data['total_dec_wins'], fighter_data['total_sub_wins'], fighter_data['total_ko_wins'],
                fighter_data['total_knockdowns'], fighter_data['total_strikes_landed'],
                fighter_data['total_strikes_absorbed'], fighter_data['total_takedowns_landed'],
                fighter_data['total_takedowns_absorbed'], fighter_data['total_sub_attempts_landed'],
                fighter_data['total_sub_attempts_absorbed'], fighter_data['total_fight_time_min'],
                fighter_data['avg_knockdowns'], fighter_data['avg_strikes_landed'],
                fighter_data['avg_strikes_absorbed'], fighter_data['avg_takedowns_landed'],
                fighter_data['avg_takedowns_absorbed'], fighter_data['avg_submission_attempts_landed'],
                fighter_data['avg_submission_attempts_absorbed'], fighter_data['avg_fight_time_min'],
                fighter_data['updated_timestamp']
            ])

        return fighter_data

    def extract_info(self, response, label):
        info_items = response.css('li.b-list__box-list-item')
        for item in info_items:
            if label in item.css('i.b-list__box-item-title::text').get('').strip():
                value = item.xpath('text()').get()
                if value:
                    return value.strip()
        return None

    def extract_stat(self, response, label):
        stat_items = response.css('li.b-list__box-list-item')
        for item in stat_items:
            if label in item.css('i.b-list__box-item-title::text').get('').strip():
                value = item.xpath('text()').get()
                if value:
                    return value.strip()
        return None

    def convert_to_float(self, value):
        if value:
            try:
                return float(value)
            except ValueError:
                pass
        return None

    def convert_percentage(self, value):
        if value and '%' in value:
            try:
                return float(value.replace('%', ''))
            except ValueError:
                pass
        return None
