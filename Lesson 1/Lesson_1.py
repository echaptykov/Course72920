'''
    Урок 1 Задание 1
'''
import requests
import json

url_categories = 'https://5ka.ru/api/v2/categories/'
headers = {'User-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)' }

response = requests.get(url_categories, headers)
data = response.json()
for category in data:
    products = []
    cat_code = category['parent_group_code']
    # Нижние две строчки - чтобы убрать \n и ** из наименования категорий (Йогурты)
    cat_name = category['parent_group_name'].replace('*\n*','')
    cat_name = cat_name.replace('"','')

    url = 'https://5ka.ru/api/v2/special_offers/?store=&categories=' + cat_code + \
          '&ordering=&price_promo__gte=&price_promo__lte=&search='
    response = requests.get(url, headers)
    data_products = response.json()
    if data_products['results'] != []:          # есть категории без товаров
        for product in data_products['results']:
            products.append(product['name'])    # создаю список имен

        with open(f'{cat_name}.json', 'w', encoding='UTF-8') as file:
            json.dump(products, file, ensure_ascii= False)

print(f'Работа завершена')