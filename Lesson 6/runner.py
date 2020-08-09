from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from instagram import InstagramSpider
import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(InstagramSpider,'','',[''])
    process.start()
