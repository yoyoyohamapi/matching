# coding: utf8
from skimage import feature
import numpy as np
import cv2

numPoints = 24
radius = 8
image = cv2.imread("../docs/colorful.jpg", 0)

lbp = feature.local_binary_pattern(
        image,
        numPoints,
        radius,
        method="default"
    )
cv2.imwrite("../docs/LBP图谱.jpg", lbp)
