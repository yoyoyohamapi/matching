# coding: utf8
"""
批量图像替换

该应急程序程序用于替换分割不佳的文件
"""

import os
import cv2
import re
from pymongo import *
from optparse import OptionParser
from bson.objectid import ObjectId
import shutil
parser = OptionParser()
parser.add_option("-r", "--root", dest="root",
                  help="image directory")

def scan(root):
    clothingPattern = re.compile(".*上衣")
    pantsPattern = re.compile(".*裤装")
    filePattern = re.compile("^[a-zA-Z0-9]+$")
    dstDir = '../images'
    # 配置数据库连接
    client = MongoClient("localhost", 27017)
    db = client.paper
    collection = db.yoho_items
    for dp, dn, fs in os.walk(root):
        for f in fs:
            filename = f.split('.')[0]
            srcPath = os.path.join(dp, f)

            if filePattern.match(filename):
                cutPath = os.path.join(dp, filename+'_cut.jpg')
                maskPath = os.path.join(dp, filename+'_mask.jpg')
                item = collection.find_one({"_id": ObjectId(filename)})
                matchingId = item["matching"]["id"]
                # 复制目标
                if clothingPattern.match(dp):
                    dstPath = os.path.join(dstDir, matchingId, u'上衣', f)
                    dstCutPath = os.path.join(dstDir, matchingId, u'上衣', filename+'_cut.jpg')
                    dstMaskPath = os.path.join(dstDir, matchingId, u'上衣', filename+'_mask.jpg')
                elif pantsPattern.match(dp):
                    dstPath = os.path.join(dstDir, matchingId, u'裤装', f)
                    dstCutPath = os.path.join(dstDir, matchingId, u'裤装', filename+'_cut.jpg')
                    dstMaskPath = os.path.join(dstDir, matchingId, u'裤装', filename+'_mask.jpg')
                shutil.copy(srcPath, dstPath)
                shutil.copy(cutPath, dstCutPath)
                shutil.copy(maskPath, dstMaskPath)

if __name__ == "__main__":
    (options, args) = parser.parse_args()
    scan(options.root)
