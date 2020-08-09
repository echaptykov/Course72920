import re
from copy import deepcopy
import json
import scrapy
from scrapy.http import HtmlResponse
from scrapy.loader import ItemLoader
from items import InstagramParseItem
from env import LOGIN, PASSWORD

MAX_PAGES = 0

class InstagramSpider(scrapy.Spider):
    name = 'instagram'
    allowed_domains = ['www.instagram.com']
    start_urls = ['https://www.instagram.com/']
    __login_url = 'https://www.instagram.com/accounts/login/ajax/'
    __api_url = '/graphql/query/'
    __api_query = {'post_feed': '7437567ae0de0773fd96545592359a6b',
    }
    num_pages = 0

    variables = {"id": "", "first": 12}

    def __init__(self, login: str, passwd: str, parse_users: list, *args, **kwargs):
        self.parse_users = ['natgeo']
        self.login = LOGIN
        self.passwd = PASSWORD
        super().__init__(*args, **kwargs)

    def parse(self, response):
        token = self.fetch_csrf_token(response.text)
        yield scrapy.FormRequest(
            self.__login_url,
            method='POST',
            callback=self.im_login,
            formdata={
                'username': self.login,
                'enc_password': self.passwd,
            },
            headers={'X-CSRFToken': token}
        )

    def im_login(self, response):
        data = response.json()
        if data['authenticated']:
            for user_name in self.parse_users:
                yield response.follow(f'/{user_name}',
                                      callback=self.user_parse,
                                      cb_kwargs={'user_name': user_name})

    def user_parse(self, response, user_name):
        user_id = self.fetch_user_id(response, user_name)
        variables = deepcopy(self.variables)
        variables["id"] = f'{user_id}'
        url = f"{self.__api_url}?query_hash={self.__api_query['post_feed']}&variables={json.dumps(variables, separators=(',', ':'))}"
        yield response.follow(url,
                              callback=self.user_feed_parse,
                              cb_kwargs={"user_name": user_name,
                                         "variables": variables}
                              )

    def user_feed_parse(self, response, user_name, variables):
        data = response.json()
        page_info = data['data']['user']['edge_owner_to_timeline_media']
        i = 0
        while i < 12:
            item = ItemLoader(InstagramParseItem(), response)
            item.add_value("user_name", page_info["edges"][i]["node"]["owner"]["username"])
            item.add_value("user_id", page_info["edges"][i]["node"]["owner"]["id"])
            item.add_value("like_count", page_info["edges"][i]["node"]["edge_media_preview_like"]["count"])
            item.add_value("photo_file",'')
            if "edge_sidecar_to_children" in page_info["edges"][i]["node"]:
                j = 0
                try:
                    while True:
                        item.add_value("photo_url", page_info["edges"][i]["node"]["edge_sidecar_to_children"]["edges"][j]["node"]["display_url"])
                        j += 1
                except IndexError as e:
                    print(e)
            else:
                item.add_value("photo_url", page_info["edges"][i]["node"]["display_url"])

            post_url = self.start_urls[0] + "p/" + page_info["edges"][i]["node"]["shortcode"]

            # TODO Тут должен быть вызов функции post_pub_date_parse

            yield item.load_item()
            i += 1

        if self.num_pages < MAX_PAGES:
            if page_info['page_info']['has_next_page']:
                variables["after"] = page_info['page_info']["end_cursor"]
                url = f"{self.__api_url}?query_hash={self.__api_query['post_feed']}&variables={json.dumps(variables, separators=(',', ':'))}"
                yield response.follow(url,
                                  callback=self.user_feed_parse,
                                  cb_kwargs={"user_name": user_name,
                                             "variables": variables
                                             }
                                  )
            self.num_pages += 1

    # Пробую получить дату поста с его страницы по shortcode

    def post_pub_date_parse(self, response: HtmlResponse):
        post_date = response.xpath('//time[@class = "_1o9PC Nzb55"]/title/text()').extract()

    def fetch_user_id(self, text, username):
        """Используя регулярные выражения парсит переданную строку на наличие
        `id` нужного пользователя и возвращет его."""
        matched = re.search('{\"id\":\"\\d+\",\"username\":\"%s\"}' % username, text.text).group()
        return json.loads(matched).get('id')

    def fetch_csrf_token(self, text):
        """Используя регулярные выражения парсит переданную строку на наличие
        `csrf_token` и возвращет его."""
        matched = re.search('\"csrf_token\":\"\\w+\"', text).group()
        return matched.split(':').pop().replace(r'"', '')

