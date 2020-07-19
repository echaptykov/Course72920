from bs4 import BeautifulSoup as bs
import requests
import json

''' Эта переменная указывает на количество постов, данные по которым собираем, потому что очень долго работает.
    Если нужно выбрать все, то можно присвоить ей значение, например 2000'''

POST_COUNT = 10

''' Не совсем понял про ссылки на теги, поэтому выбираю ключевые слова. Ссылки на теги имеют общий вид:
    https://geekbrains.ru/posts?tag=ключевое слово
    
    Сергей,я не совсем понял, про запись информации в файл. Нужен один для всех или для каждого поста - свой?
    Я создаю один файл и сохраняю там данные.  
'''

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

    ''' Добавил две функции к примеру из урока'''
   # Получаем информацию со страницы поста
    def get_post_info(self, url = None):
        post_info = {}
        url = url or self.__url
        soup = self.get_page_soup(url)

#        post_info['title'] = soup.find_all('h1', attrs = {'class':'blogpost-title text-left text-dark m-t-sm', 'itemprop':'headline'})[0].text
        post_info['title'] = soup.find_all('h1', attrs = {'itemprop':'headline'})[0].text
        post_info['post_url'] = url
        post_info['writer'] = soup.find_all('div', attrs = {'itemprop':"author"})[0].text
        post_info['writer_url'] = soup.find('div', attrs = {'class':"col-md-5 col-sm-12 col-lg-8 col-xs-12 padder-v"}).find('a').get('href')
        # есть посты без ключевых слов
        try:
            post_info['tags'] = soup.find('i',attrs={'class':'i i-tag m-r-xs text-muted text-xs'}).get('keywords')
        except AttributeError:
            post_info['tags'] = ''
        return post_info

    # Получаем данные о всех постах и сохраняем в файл
    def get_posts_info_and_dump(self):
        i = 0
        posts_data = {'posts':[]}
        data_list = posts_data['posts']
        for post in self.posts_urls:
            data_list.append(self.get_post_info(post))
            i+=1
            if i > POST_COUNT:
                break
        with open(f'geekbrains_post_info.json', 'w', encoding='UTF-8') as file:
                json.dump(posts_data, file, ensure_ascii= False)

if __name__ == '__main__':
    parser = GbBlogParse()
    parser.run()
    parser.get_posts_info_and_dump()
    print('Работа завершена')

