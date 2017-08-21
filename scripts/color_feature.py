# coding: utf8

import cv2
import numpy as np

# 获得明暗图像的直方图

lightImg = cv2.imread('../docs/light.jpg')
lightMask = cv2.imread('../docs/light_mask.jpg', 0)

darkImg = cv2.imread('../docs/dark.jpg')
darkMask = cv2.imread('../docs/darkMask.jpg', 0)

images = [
    [lightImg, lightMask, '../docs/light_hist.jpg'],
    [darkImg, darkMask, '../docs/dark_hist.jpg']
]

def saveHist(image, mask, filename):
    hist = cv2.calcHist(
        images=[image],
        channels=[0],
        mask=mask,
        histSize=[256],
        ranges=[0.0, 255.0]
    )
    minVal, maxVal, minLoc, maxLoc = cv2.minMaxLoc(hist)
    histImg = np.zeros([256,256], np.uint8)
    hpt = int(0.9*256)

    for h in range(256):
        intensity = int(hist[h]*hpt/maxVal)
        cv2.line(histImg, (h,256), (h, 256-intensity), 255)

    cv2.imwrite(filename, histImg)

for image, mask, filename in images:
    saveHist(image, mask, filename)
