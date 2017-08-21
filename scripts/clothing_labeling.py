#coding: utf8
"""
衣物标定
"""
import cv2
import pandas
import os
import csv
import color as colorLib
import shutil
from pymongo import *
from bson.objectid import ObjectId

# 配置数据库连接
client = MongoClient("localhost", 27017)
db = client.paper
collection = db.yoho_items

data = pandas.read_csv("../features/clothings.csv").values
# 扒下的数据
scripedData = pandas.read_csv("../clothing_scriped.csv").values

print scripedData
clothings = []

paths = [
    "../clothings/patterns/0",
    "../clothings/patterns/1",
    "../clothings/patterns/2",
    "../clothings/stripes"
]

# 袖长
sleeve = ["长袖", "短袖", "7分袖", "5分袖", "无袖"]
# 厚薄
thickness = ["薄", "中", "厚"]
# 版型
typeVersion = ["宽松", "修身", "正常"]
# 长短
length = ["长款", "适中", "短款"]

def _getPatternClothings(path):
    """
    获得带图案的衣物

    Args:
        path 路径
    Returns:
        clothingIds 图像数组
    """
    clothingIds = []
    for dp, dn, fs, in os.walk(path):
        for f in fs:
            clothingId = f.split('.')[0]
            clothingIds.append(clothingId)
    return clothingIds

patternClothings = [ _getPatternClothings(path) for path in paths]

for feature in data:
    clothing = {}
    path = feature[0]
    print path
    # 保存图像地址以便后续使用
    clothing["path"] = path
    # 从数据库读出item
    filename = path.split('/')[-1]
    clothingId = filename.split('.')[0]
    clothing["id"] = clothingId
    item = collection.find_one({"_id": ObjectId(clothingId)})
    # 找到对应的扒下的数据
    for scripedItem in scripedData:
        if scripedItem[-1] == clothingId:
            scriped = scripedItem
            break
    # 标定颜色
    clothing["color"] = feature[1]
    # 标定衣物厚薄
    clothing["thickness"] = thickness.index(scriped[4])
    # 标定衣物长短
    clothing["length"] = length.index(scriped[6])
    # 标定衣物袖子
    clothing["sleeve"] = sleeve.index(scriped[3])
    # 标定衣物版型
    clothing["typeVersion"] = typeVersion.index(scriped[5])
    # 标定颜色冷暖
    if colorLib.isColdColor(clothing["color"]):
        clothing["isCold"] = 1
    else:
        clothing["isCold"] = 0
    # 标定图案复杂程度
    for idx, patterns in enumerate(patternClothings):
        if clothingId in patterns:
            clothing["pattern"] = idx
            break
    if "pattern" not in clothing:
        print path
    else:
        clothings.append(clothing)

# 写入csv
csvFile = open("../clothings.csv", 'wb')
csvWriter = csv.writer(csvFile)

for clothing in clothings:
    row = [
        clothing["id"],
        clothing["path"],
        clothing["color"],
        clothing["isCold"],
        clothing["pattern"],
        clothing["thickness"],
        clothing["length"],
        clothing["sleeve"],
        clothing["typeVersion"]
    ]
    csvWriter.writerow(row)
