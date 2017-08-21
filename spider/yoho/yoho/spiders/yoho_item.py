# coding: utf8
"""
YoHo衣裤特征爬取
"""

import scrapy
from pymongo import *
from yoho.items import ClothingItem, PantsItem

# 配置数据库连接
client = MongoClient("localhost", 27017)
db = client.paper

# 获得所有衣物
items = db.yoho_items.find()
startUrls = []
yohoItems = []
for item in items:
    if item['category'] == u'上衣':
        yohoItem = ClothingItem()
    else:
        yohoItem = PantsItem()
    yohoItem["id"] = item["_id"]
    yohoItem["matching_id"] = item["matching"]["id"]
    yohoItem["category"] = item["category"]
    yohoItem["style"] = item["style"]
    yohoItem["url"] = item["product_url"]
    yohoItems.append(yohoItem)
    startUrls.append(item["product_url"])

KEYS_MAP = {
    u'经典款型': 'model',
    u'颜色': 'color',
    u'衣长':  'length',
    u'裤长': 'length',
    u'袖长': 'sleeve_length',
    u'版型': 'type_version',
    u'厚度': 'thickness',
    u'腰型': 'waist_type'
}

KEYS = KEYS_MAP.keys()

class YohoItemSpider(scrapy.Spider):
    name = "yoho_item"
    allowed_domains = ["yohobuy.com"]
    start_urls = startUrls

    def parse(self, response):
        index = startUrls.index(response.url)
        yohoItem = yohoItems[index]
        self.logger.info("------parse product: %s", yohoItem['id'])
        keys = yohoItem.keys()
        # 选择器
        descs = response.xpath("//div[@class='description-content']/ul[@class='basic clearfix']/li")
        for desc in descs:
            key = desc.xpath("em/span[@class='keySpace']/text()").extract_first()
            value = desc.xpath("em/span[@class='valueSpace']/text()").extract_first()
            if key:
                key = key.replace(u"\u3000", "").replace(":", "").replace(" ", "")
            if value:
                value = value.replace(u"\u3000", "").replace(" ", "")
            itemKey = KEYS_MAP.get(key)
            if itemKey:
                yohoItem[itemKey] = value
            self.logger.info("Description %s=>%s", key, value)
        yield yohoItem
