# coding: utf-8
"""
提取肤色脚本

"""

import cv2
import numpy as np
import sys
import os
import color
import json
from optparse import OptionParser
parser = OptionParser()
parser.add_option("-i", "--image", dest="image",
                    help="image path")

with open("../config/face_color.json") as faceColorFile:
    faceColorMap = json.load(faceColorFile)

def _detectFace(image):
    """
    面部检测
    """
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    dirname, _ = os.path.split(os.path.abspath(sys.argv[0]))
    cascadesPath = os.path.join(dirname, 'cascades/haarcascade_frontalface_default.xml')
    faceCascade = cv2.CascadeClassifier(cascadesPath)
    faces = faceCascade.detectMultiScale(gray, 1.3, 5)
    if len(faces) > 0:
        return faces[0]
    else:
        return None

if __name__ == "__main__":
    (options, args) = parser.parse_args()
    image = cv2.imread(options.image)
    face = _detectFace(image)
    if face is None:
        raise Exception("No face detected!")
    else:
        # 提取颜色
        rows, cols, _ = image.shape
        mask = np.zeros((rows, cols), np.uint8)
        x, y, w, h = face
        mask[y:y+h, x:x+w] = 255
        mainColor, mainColorHex = color.extractMainColor(image, mask)
        # 获得肤色
        skinColor, colorName = color.mapColor(faceColorMap, mainColor)
        print "%s:%s"%(colorName, skinColor)
