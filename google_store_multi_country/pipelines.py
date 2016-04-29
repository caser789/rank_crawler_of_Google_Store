# -*- coding: utf-8 -*-

# Define your item pipelines here
#
# Don't forget to add your pipeline to the ITEM_PIPELINES setting
# See: http://doc.scrapy.org/en/latest/topics/item-pipeline.html
import redis


class GoogleStoreMultiCountryPipeline(object):

    def __init__(self):
        self.server = redis.Redis(host='localhost', port=6379)

    def process_item(self, item, spider):
        name = item['rank_list_name']
        key = item['rank']
        value = (item['bundle_ID'], item['title'])
        self.server.hset(name, key, value)
        return item
