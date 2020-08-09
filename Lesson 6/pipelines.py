# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: https://docs.scrapy.org/en/latest/topics/item-pipeline.html


# useful for handling different item types with a single interface
from itemadapter import ItemAdapter
from scrapy import Request
from scrapy.pipelines.images import ImagesPipeline
from pymongo import MongoClient


class DataBasePipeline:

    def __init__(self):
        client = MongoClient(
            "mongodb+srv://DBUser:Mongo1234@cluster0.kb7nh.mongodb.net/gb_base?retryWrites=true&w=majority")
        self.mongo_base = client.gb_base

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item


class ImgPipeline(ImagesPipeline):

    def get_media_requests(self, item, info):
        for url in item.get('photo_url', []):
            try:
                print(url)
                yield Request(url)
            except ValueError as e:
                print(e)

    def item_completed(self, results, item, info):
        i = 0
        while i < len(results):
            if i == 0:
                item['photo_file'][i] = [itm[1] for itm in results][i]['path']
            else:
                item['photo_file'].append([itm[1] for itm in results][i]['path'])
            i += 1
        return item