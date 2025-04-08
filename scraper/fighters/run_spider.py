from scrapy.crawler import CrawlerProcess
from scrapy.utils.project import get_project_settings
from spiders.fighters_scraper import UFCStatsSpider


def main():
    settings = get_project_settings()
    process = CrawlerProcess(settings)
    process.crawl(UFCStatsSpider)
    process.start()

if __name__ == '__main__':
    main()