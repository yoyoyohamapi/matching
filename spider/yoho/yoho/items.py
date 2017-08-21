# -*- coding: utf-8 -*-

# Define here the models for your scraped items
#
# See documentation in:
# http://doc.scrapy.org/en/latest/topics/items.html

import scrapy

class Item(scrapy.Item):
    # mongo id
    id = scrapy.Field()
    # 风格
    style = scrapy.Field()
    # 分类
    category = scrapy.Field()
    # 所属搭配
    matching_id = scrapy.Field()
    # 颜色
    color = scrapy.Field()
    # 版型
    type_version = scrapy.Field()
    # 厚度
    thickness = scrapy.Field()
    # 长度
    length = scrapy.Field()
    # 经典款型
    model = scrapy.Field()
    # 产品链接
    url = scrapy.Field()

class ClothingItem(Item):
    # 袖长
    sleeve_length = scrapy.Field()

class PantsItem(Item):
    # 腰型
    waist_type = scrapy.Field()
