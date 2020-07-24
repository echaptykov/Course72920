'''
    Урок 3
'''
from bs4 import BeautifulSoup as bs
import requests
from pymongo import MongoClient


''' Эта переменная указывает на количество постов, данные по которым собираем, потому что очень долго работает.
    Если нужно выбрать все, то можно присвоить ей значение, например 2000'''

POST_COUNT = 5

class GbBlogParse:
    __domain = 'https://geekbrains.ru'
    __url = 'https://geekbrains.ru/posts'
    __done_urls = set()

    def __init__(self):
        self.posts_urls = set()
        self.pagination_urls = set()

    def get_page_soup(self, url):
        # метод запроса страницы и создания супа
        response = requests.get(url)
        soup = bs(response.text, 'lxml')
        return soup

    def run(self, url=None):

        url = url or self.__url
        soup = self.get_page_soup(url)
        self.pagination_urls.update(self.get_pagination(soup))
        self.posts_urls.update(self.get_posts_urls(soup))

        for url in tuple(self.pagination_urls):
            if url not in self.__done_urls:
                self.__done_urls.add(url)
                self.run(url)

    # Проход пагинации ленты
    def get_pagination(self, soup):
        ul = soup.find('ul', attrs={'class': 'gb__pagination'})
        a_list = [f'{self.__domain}{a.get("href")}' for a in ul.find_all('a') if a.get("href")]
        return a_list

    # Поиск ссылок на статьи на странице ленты
    def get_posts_urls(self, soup):
        posts_wrap = soup.find('div', attrs={'class': 'post-items-wrapper'})
        a_list = [f'{self.__domain}{a.get("href")}' for a in
                  posts_wrap.find_all('a', attrs={'class': 'post-item__title'})]
        return a_list

    # Получаем информацию со страницы поста
    def get_post_info(self, url = None):
        post_info = {}
        url = url or self.__url
        soup = self.get_page_soup(url)

        post_info['title'] = soup.find_all('h1', attrs = {'itemprop':'headline'})[0].text
        post_info['post_url'] = url
        post_info['writer'] = soup.find_all('div', attrs = {'itemprop':"author"})[0].text
        post_info['writer_url'] = soup.find('div', attrs = {'class':'col-md-5 col-sm-12 col-lg-8 col-xs-12 padder-v'}).find('a').get('href')
        post_info['images'] = []
        img = soup.select('p > img')
        for i in img:
            post_info['images'].append(i.get('src'))

        # собираем текст. Теряем внутренние заголовки. Как быть, пока не придумал.
        post_info['text']= ''
        text = soup.findAll('p')
        for i in text:
            post_info['text'] += '\n' + i.getText()

        # есть посты без ключевых слов
        try:
            post_info['tags'] = soup.find('i',attrs={'class':'i i-tag m-r-xs text-muted text-xs'}).get('keywords')
        except AttributeError:
            post_info['tags'] = ''
        return post_info

    # Получаем данные о всех постах и сохраняем в БД
    def get_posts_info_and_save_to_MongoDB(self):
        try:
            client = MongoClient("mongodb+srv://DBUser:Mongo1234@cluster0.kb7nh.mongodb.net/<dbname>?retryWrites=true&w=majority")
            print('Соединение установлено')
        except:
            print('Ошибка соединения с БД')
            return
        db = client.gb_base
        collection = db.gb_collection
        i = 0
        for post in self.posts_urls:
            id = collection.insert_one(self.get_post_info(post))
            i += 1
            if i > POST_COUNT:
                break

if __name__ == '__main__':
    parser = GbBlogParse()
    parser.run()
    parser.get_posts_info_and_save_to_MongoDB()
    print('Работа завершена')

