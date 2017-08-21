#coding: utf8

import cv2
import numpy as np

image =  cv2.imread("../docs/colorful.jpg")
gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)

# SIFT检测
sift = cv2.xfeatures2d.SIFT_create()
kp = sift.detect(gray,None)
dst = image.copy()
cv2.drawKeypoints(gray,kp,dst)
cv2.imwrite("../docs/SIFT检测结果.jpg", dst)

# SURF检测
surf = cv2.xfeatures2d.SURF_create(8000)
kp= surf.detect(gray, None)
dst = image.copy()
cv2.drawKeypoints(gray,kp,dst)
cv2.imwrite("../docs/SURF检测结果.jpg", dst)
