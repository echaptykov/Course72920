import scrapy
from scrapy.http import HtmlResponse
from items import AvitoparserItem
from scrapy.loader import ItemLoader
import json

class AvitoSpider(scrapy.Spider):
    name = 'avito'
    allowed_domains = ['avito.ru']

    def __init__(self, mark):
        # Выбираю все объявления о продаже квартир из г.Абаза 74 объявления, 2 страницы
        self.start_urls = [f'https://www.avito.ru/abaza/kvartiry/prodam-ASgBAgICAUSSA8YQ']

        # Выбирал и просто квартиры, но туда попадают объявления куплю
        #self.start_urls = [f'https://www.avito.ru/abaza/kvartiry']
        # Запускал и на Абакане, но там 2000 объявлений - долго.
        # self.start_urls = [f'https://www.avito.ru/abakan/kvartiry']

    def parse(self, response: HtmlResponse):
        # определяем общее количество страниц
        pages = int(response.xpath('//span[@class="pagination-item-1WyVp"]/text()').extract()[-1])
        for page in range(2, pages + 1):
            page_url = self.start_urls[0] +'?p='+str(page) # адрес следующей страницы
            yield response.follow(page_url, self.parse_page)
        yield from self.parse_page(response)

    def parse_page(self,response: HtmlResponse):
        ads_links = response.xpath('//a[@class="snippet-link"]/@href').extract()
        for link in ads_links:
            if self.check_link(link):
                yield response.follow(link, callback=self.parse_ads)

    def parse_ads(self, response: HtmlResponse):
        url = response.url
        name = response.css('h1.title-info-title span.title-info-title-text::text').extract()
        price = response.xpath('//span[@class="js-item-price"][1]/text()').extract()[0]
        description = response.xpath('//div[@class="item-description-text"]/p/text()').extract()
        yield AvitoparserItem(name=name, price=price,description=description, url = url)
        print(url, name, price)

    # Вместе с ссылками на страницы объявлений попадаются ссылки например "Активы Сбербанка" или "Этажи"
    # Не использую их.
    #
    def check_link(self,link):
        if link.find('et.') != -1:
            return True
        return False