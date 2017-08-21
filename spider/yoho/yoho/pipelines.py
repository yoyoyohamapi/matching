# coding: utf8

from scrapy import signals
from scrapy.xlib.pydispatch import dispatcher
from scrapy.contrib.exporter import CsvItemExporter
from yoho.items import ClothingItem, PantsItem

class MultiCSVItemPipeline(object):
    SaveTypes = [u'上衣', u'裤装']

    def __init__(self):
        self.files = {}
        self.clothingExporter = CsvItemExporter(fields_to_export=ClothingItem.fields.keys(),file=open("clothing.csv",'wb'))
        self.pantsExporter = CsvItemExporter(fields_to_export=PantsItem.fields.keys(),file=open("pants.csv",'wb'))

	@classmethod
	def from_crawler(cls, crawler):
		pipeline = cls()
		crawler.signals.connect(pipeline.spider_opened, signals.spider_opened)
		crawler.signals.connect(pipeline.spider_closed, signals.spider_closed)
		return pipeline

    def spider_opened(self, spider):
    	self.clothingExporter.start_exporting()
    	self.pantsExporter.start_exporting()

    def spider_closed(self, spider):
        self.clothingExporter.finish_exporting()
        self.pantsExporter.finish_exporting()
        file = self.files.pop(spider)
        file.close()

    def process_item(self, item, spider):
        if item['category'] == u'上衣':
            self.clothingExporter.export_item(item)
        else:
            self.pantsExporter.export_item(item)
        return item
