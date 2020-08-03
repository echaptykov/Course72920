import scrapy
from scrapy.http import HtmlResponse
from items import HabrPostItem, HabrAuthorItem
from scrapy.loader import ItemLoader

class HabrPostSpider(scrapy.Spider):
    name = 'habr_post'
    allowed_domains = ['habr.com']
    start_urls = ['http://habr.com/ru/']

    def parse(self,response: HtmlResponse):
        print('url:', response.url)
        posts = response.xpath('//a[@class="post__title_link"]/@href').extract()
        for post_url in posts:
            yield response.follow(post_url, callback = self.parse_post)

    def parse_post(self,response: HtmlResponse):
        l = ItemLoader(item = HabrPostItem(),response = response)
        l.add_xpath('title','//span[@class = "post__title-text"]/text()')
        l.add_xpath('author_url','//a[@class = "post__user-info user-info"]/@href')
        l.add_xpath('author_nickname','//span[@class = "user-info__nickname user-info__nickname_small"]/text()')
        l.add_xpath('images','//div[@class = "post__text post__text-html post__text_v1"]/img/@src')
        l.add_xpath('comments','//span[@class = "post-stats__comments-count"]/text()')
        l.add_value('post_url',response.url)
        yield l.load_item()

class HabrAuthorSpider(scrapy.Spider):
    name = 'habr_author'
    allowed_domains = ['habr.com']
    start_urls = ['http://habr.com/ru/']

    def parse(self,response: HtmlResponse):
        authors_urls = response.xpath('//a[@class="post__user-info user-info"]/@href').getall()
        unique_authors = list(set(authors_urls))
        for url in unique_authors:
            posts_url = url + 'posts/'
            yield response.follow(posts_url, callback = self.parse_author)

    def parse_author(self, response: HtmlResponse):
        l = ItemLoader(item = HabrAuthorItem(), response = response)
        l.add_xpath('author_name','//a[@class="user-info__fullname user-info__fullname_medium"]/text()')
        l.add_xpath('author_rating','//a[@class="defination-list__link"]/text()')
        l.add_xpath('author_birthdate','//div[@class="default-block__content default-block__content_profile-summary"]'
                                       '//li[3]//span[2]/text()')
        l.add_xpath('author_activity','//div[@class="default-block__content default-block__content_profile-summary"]'
                                      '//li[4]//span[2]/text()')
        l.add_xpath('author_registered','//div[@class="default-block__content default-block__content_profile-summary"]'
                                        '//li[5]//span[2]/text()')
        l.add_xpath('author_specialization','//div[@class="user-info__specialization"]/text()')

        l.add_value('author_posts',self.parse_page(response))

        yield l.load_item()

    def parse_page(self,response: HtmlResponse):
        posts = response.xpath('//a[@class="post__title_link"]/@href').extract()
        return posts
