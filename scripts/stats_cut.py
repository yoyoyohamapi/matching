# coding: utf8
import csv
import os
import re

if __name__ == "__main__":
    # 文件名正则
    filePattern = re.compile("^[a-zA-Z0-9]+$")
    # 上衣文件名正则
    clothingPattern = re.compile(".*上衣")

    # count
    wrongClothingCount = 0
    wrongPantsCount = 0
    clothingCount = 0
    pantsCount = 0

    # 统计分割效果不好的
    with open('wrong_cut.csv', 'rb') as csvfile:
        reader = csv.reader(csvfile, delimiter=' ')
        for row in reader:
            filename = row[0]
            if clothingPattern.match(filename):
                wrongClothingCount = wrongClothingCount + 1
            else:
                wrongPantsCount = wrongPantsCount + 1

    # 统计所有
    for dp, dn, fs in os.walk('../images'):
        for f in fs:
            # 分割图像并进行存储
            filename = f.split('.')[0]
            if filePattern.match(filename):
                srcPath = os.path.join(dp, f)
                cutPath = os.path.join(dp, "%s_cut.jpg" % filename)
                maskPath = os.path.join(dp, "%s_mask.jpg" % filename)
                if clothingPattern.match(srcPath):
                    isClothing = True
                    clothingCount = clothingCount + 1
                else:
                    isClothing = False
                    pantsCount = pantsCount + 1
    clothingRate = 1 - float(wrongClothingCount)/float(clothingCount)
    pantsRate = 1 - float(wrongPantsCount)/float(pantsCount)
    print '----------clothings: %d, wrongs: %d, rate: %.2f----------' % (clothingCount, wrongClothingCount, clothingRate)
    print '----------pants:     %d, wrongs: %d, rate: %.2f----------' % (pantsCount, wrongPantsCount, pantsRate)
