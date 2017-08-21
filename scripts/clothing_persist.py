#coding: utf8
"""
将衣物数据持久化到mongo
"""
print (__doc__)

from pymongo import *
from bson.objectid import ObjectId
import pandas

# 配置数据库连接
client = MongoClient("localhost", 27017)
db = client.paper

data = pandas.read_csv("../clothings.csv").values
data = data[:, [0, 2, 4]]

for oid, color, pattern in data:
    item = db.yoho_items.find_one({"_id": ObjectId(oid)})
    clothing = {}
    clothing["url"] = item["product_url"]
    clothing["color"] = color
    clothing["image"] = "https:"+item["img_url"]
    clothing["category"] = item["style"]
    clothing["style"] = pattern
    db.clothings.insert_one(clothing)
