# coding: utf8
import cv2
import numpy as np
import cut

image = cv2.imread('../docs/pure.jpg')
rows, cols, _ = image.shape
resized = cv2.pyrDown(image, (rows/2, cols/2))
blured = cv2.medianBlur(resized, 3)

cutMask, cutImage = cut.cut(image, True, '../docs/cut_debug', 'pure', isDebug = True)

cv2.imwrite('../docs/分割掩膜.jpg', cutMask)
cv2.imwrite('../docs/分割后图像.jpg', cutImage)
cv2.imwrite('../docs/缩放后.jpg', resized)
cv2.imwrite('../docs/降噪后.jpg', blured)
