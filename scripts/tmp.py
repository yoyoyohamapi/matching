# coding: utf-8
import json
import os
import cv2
import clothing_feature as feature
import re

from optparse import OptionParser
parser = OptionParser()
parser.add_option("-r", "--root", dest="root", help="image directory")
parser.add_option("-d", "--debugDir", dest="debugDir", help="debug directory")

def scan(root, debugDir):
    # 文件名正则
    filePattern = re.compile("^[a-zA-Z0-9]+$")
    # 先删除debug下的文件
    for dp, dn, fs, in os.walk(debugDir):
        for f in fs:
            os.remove(os.path.join(dp, f))
    for dp, dn, fs, in os.walk(root):
        for f in fs:
            filename = f.split('.')[0]
            srcPath = os.path.join(dp, f)
            maskPath = os.path.join(dp+'_mask', f)
            if filePattern.match(filename):
                print filename
                image = cv2.imread(srcPath)
                mask = cv2.imread(maskPath)
                mask = cv2.cvtColor(mask, cv2.COLOR_BGR2GRAY)
                extractor = feature.createFeatureExtractor(image, mask, debugDir, filename, True)
                features = extractor["extract"]()
                print features

if __name__ == "__main__":
    (options, args) = parser.parse_args()
    scan(options.root, options.debugDir)
