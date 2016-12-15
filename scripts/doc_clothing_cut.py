# coding: utf8
import os
import cv2
import re
from cut import cut

def scan(rootDir):
    # 文件名正则
    filePattern = re.compile("^[a-zA-Z0-9]+$")
    # 上衣文件名正则
    clothingPattern = re.compile(".*clothing")
    clothingCount = 0
    pantsCount = 0
    for dp, dn, fs in os.walk(rootDir):
        for f in fs:
            # 分割图像并进行存储
            filename = f.split('.')[0]
            if filePattern.match(filename):
                srcPath = os.path.join(dp, f)
                cutPath = os.path.join(dp,"%s_cut.jpg"%filename)
                maskPath = os.path.join(dp, "%s_mask.jpg"%filename)
                if clothingPattern.match(srcPath):
                    isClothing = True
                    clothingCount = clothingCount + 1
                else:
                    isClothing = False
                    pantsCount = pantsCount + 1
                print '---->'
                print '%s is cutting'%srcPath
                image = cv2.imread(srcPath)
                mask, cutImage = cut(image, isClothing, dp, filename, isDebug = True)
                cv2.imwrite(cutPath, cutImage)
                cv2.imwrite(maskPath, mask)
                print '<----'
    print '----------completed!    ----------'
    print '----------clothings: %d ----------'%clothingCount
    print '----------pants:     %d ----------'%pantsCount

if __name__ == "__main__":
    rootDir = '../doc_images'
    scan(rootDir)
