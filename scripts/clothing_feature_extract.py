# coding: utf8
"""
上衣特征提取
"""
print(__doc__)

import os
import re
import clothing_feature as feature
import csv
import cv2
import shutil
from pymongo import *
from bson.objectid import ObjectId
from optparse import OptionParser

parser = OptionParser()
parser.add_option("-r", "--root", dest="root", help="image directory")

# 配置数据库连接
client = MongoClient("localhost", 27017)
db = client.paper
collection = db.yoho_items

csvFile = open("../features/clothings.csv", 'wb')
csvWriter = csv.writer(csvFile)

categories = [
    u'背心',
    u'衬衫',
    u'大衣/风衣',
    u'防风外套',
    u'夹克',
    u'马甲',
    u'毛衣/针织',
    u'棉衣',
    u'皮衣',
    u'套装',
    u'卫衣',
    u'西装',
    u'羽绒服',
    u'POLO',
    u'T恤'
]
csvFiles = [ open('../features/'+category.split('/')[0]+'.csv', 'wb') for category in categories ]
print csvFiles
csvWriters = [ csv.writer(csvFile) for csvFile in csvFiles ]

def scan(root):
    # 文件名正则
    filePattern = re.compile("^[a-zA-Z0-9]+$")
    # 上衣文件名正则
    clothingPattern = re.compile(".*上衣")
    extractors = []
    def extractFeature(extractor):
        # 显示正在处理的图像
        path = extractor["path"]
        print path
        # 保存每个图像的特征
        features = extractor["extract"]()
        row = [path] + features
        csvWriter.writerow(row)
        # 特征写到单独衣物体系下
        clothingId = path.split('/')[-1].split('.')[0]
        item = collection.find_one({"_id": ObjectId(clothingId)})
        try :
            itemIndex = categories.index(item['style'])
            writer = csvWriters[itemIndex]
            writer.writerow(row)
        except:
            print item['style']

    for dp, dn, fs, in os.walk(root):
        for f in fs:
            filename = f.split('.')[0]
            srcPath = os.path.join(dp, f)
            maskPath = os.path.join(dp, "%s_mask.jpg"%filename)
            if filePattern.match(filename) and clothingPattern.match(srcPath):
                image = cv2.imread(srcPath)
                mask = cv2.imread(maskPath)
                mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
                extractor = feature.createFeatureExtractor(image, mask, None, filename)
                extractors.append({
                    "image": image,
                    "path": srcPath,
                    "extract": extractor["extract"]
                })

    map(extractFeature, extractors)

if __name__ == "__main__":
    (options, args) = parser.parse_args()
    scan(options.root)
