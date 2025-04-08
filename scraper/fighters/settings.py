BOT_NAME = 'ufc_stats'

SPIDER_MODULES = ['ufc_stats.spiders']
NEWSPIDER_MODULE = 'ufc_stats.spiders'

ROBOTSTXT_OBEY = True

CONCURRENT_REQUESTS = 8

DOWNLOAD_DELAY = 1.5
RANDOMIZE_DOWNLOAD_DELAY = True

COOKIES_ENABLED = False

USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'

LOG_LEVEL = 'INFO'

HTTPCACHE_ENABLED = True
HTTPCACHE_EXPIRATION_SECS = 86400
HTTPCACHE_DIR = 'httpcache'
HTTPCACHE_IGNORE_HTTP_CODES = []
HTTPCACHE_STORAGE = 'scrapy.extensions.httpcache.FilesystemCacheStorage'
