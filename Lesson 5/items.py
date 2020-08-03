import scrapy

class HabrPostItem(scrapy.Item):
    _id = scrapy.Field()
    title = scrapy.Field()
    images = scrapy.Field()
    comments = scrapy.Field()
    author_nickname = scrapy.Field()
    author_url = scrapy.Field()
    post_url = scrapy.Field()
    pass

class HabrAuthorItem(scrapy.Item):
    _id = scrapy.Field()
    author_name = scrapy.Field()
    author_birthdate = scrapy.Field()
    author_rating = scrapy.Field()
    author_specialization = scrapy.Field()
    author_activity = scrapy.Field()
    author_registered = scrapy.Field()
    author_posts = scrapy.Field()
    pass



