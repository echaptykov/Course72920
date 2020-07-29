import scrapy
from pymongo import MongoClient

class DataBasePipeline(object):
    def __init__(self):
        client = MongoClient("mongodb+srv://DBUser:Mongo1234@cluster0.kb7nh.mongodb.net/<dbname>?retryWrites=true&w=majority")
        self.mongo_base = client.gb_base

    def process_item(self, item, spider):
        collection = self.mongo_base[spider.name]
        collection.insert_one(item)
        return item

