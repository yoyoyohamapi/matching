# coding: utf-8
import os
import csv
import time
import sys
import re

csvName = sys.argv[1]

def copyFile(source, target):
    print source
    open(target, "wb").write(open(source, "rb").read())

if __name__ == "__main__":
    clothingPattern = re.compile(".*上衣")
    # 每次生成新的错误文件目录
    rootDir = '../images_%s'%csvName.split('.')[0]
    # 构建clothings及pants目录
    clothingDir = '%s/clothings'%rootDir
    pantsDir = '%s/pants'%rootDir
    if not os.path.exists(rootDir):
        os.makedirs(clothingDir)
        os.makedirs(pantsDir)
    # 从csv文件中读取到错误分类的图像
    # 统计分割效果不好的
    with open(csvName, 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ')
        for row in reader:
            # 获得文件路径
            path = row[0]
            source = '../images/%s'%path
            arr = path.split('/')
            if clothingPattern.match(path):
                target = '%s/%s'%(clothingDir, arr[2])
            else:
                target = '%s/%s'%(pantsDir, arr[2])
            copyFile(source, target)
