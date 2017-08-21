# coding: utf8
"""
批量图像分割

"""

import os
import cv2
import re
from cut import cut
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-r", "--root", dest="root",
                  help="image directory")
parser.add_option("-d", "--debug", dest="debug", default=False,
                  help="debug mode")

def scan(root, debug):
    # 文件名正则
    filePattern = re.compile("^[a-zA-Z0-9]+$")
    # 上衣文件名正则
    clothingPattern = re.compile(".*上衣")
    clothingCount = 0
    pantsCount = 0
    # 先删除文件
    for dp, dn, fs in os.walk(root):
        for f in fs:
            # 分割图像并进行存储
            filename = f.split('.')[0]
            srcPath = os.path.join(dp, f)
            if not filePattern.match(filename):
                os.remove(srcPath)
    for dp, dn, fs in os.walk(root):
        for f in fs:
            # 分割图像并进行存储
            filename = f.split('.')[0]
            srcPath = os.path.join(dp, f)
            if filePattern.match(filename):
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
                mask, cutImage = cut(image, isClothing, dp, filename, isDebug = debug)
                cv2.imwrite(cutPath, cutImage)
                cv2.imwrite(maskPath, mask)
                print '<----'
            else:
                os.remove(srcPath)
    print '----------completed!    ----------'
    print '----------clothings: %d ----------'%clothingCount
    print '----------pants:     %d ----------'%pantsCount

if __name__ == "__main__":
    (options, args) = parser.parse_args()
    scan(options.root, options.debug)
