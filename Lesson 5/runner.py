from scrapy.crawler import CrawlerProcess
from scrapy.settings import Settings

from habr import HabrPostSpider,HabrAuthorSpider
import settings

if __name__ == '__main__':
    crawler_settings = Settings()
    crawler_settings.setmodule(settings)
    process = CrawlerProcess(settings=crawler_settings)
    process.crawl(HabrPostSpider, mark='')
    process.crawl(HabrAuthorSpider, mark='')
    process.start()
