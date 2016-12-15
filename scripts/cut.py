# coding: utf-8
import cv2
import os
import numpy as np

def _optimizeClothingMask(mask, debug):
    """
    优化上装分割掩膜

    Args:
        mask 待优化掩膜
        debug 函数
    Return:
        dstMask 优化后掩膜
    """
    # Step 4.1: 形态学闭操作：填充衣物mask中的洞，修复那些被误认为是背景的衣物上的图案
    debug('4.1_before_close', mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (13, 13))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    debug('4.1_after_close', mask)

    # Step 4.2: 形态学开操作去除衣物四周的吊饰
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    debug('4.1_after_open', mask)

    # Step 4.3: 填充最大轮廓，
    contours, hierachy = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]
    if len(contours) > 0:
        maxContour = contours[0]
        for contour in contours:
            if(len(contour) > len(maxContour)):
                maxContour = contour
        cv2.drawContours(mask, [maxContour], 0, (255, 255, 255), cv2.FILLED)

    # Step 4.4: 进行一定的腐蚀操作，去除背景边界
    debug('4.4_before_erode', mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.erode(mask, kernel)
    debug('4.4_after_erode', mask)
    return mask


def _optimizePantsMask(mask, debug):
    """
    优化下装分割掩膜

    Args:
        mask 待优化掩膜
        debug debug函数
    Return:
        dstMask 优化后掩膜
    """
    # Step 4.1: 进行一定的腐蚀操作，去除背景边界
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    mask = cv2.erode(mask, kernel)
    return mask


def _cutClothing(image, gray, edges, debug):
    """
    上装分割

    Args:
        image 原图像
        gray 灰度图像
        edges 边缘灰度图像
        debug debug函数
    Return:
        mask 分割掩膜
    """
    rows, cols = edges.shape

    # Step 3.1: 人脸检测，应用grabcut圈定矩形框的时候需要去除人脸
    faceCascade = cv2.CascadeClassifier(
        "cascades/haarcascade_frontalface_default.xml")
    faces = faceCascade.detectMultiScale(gray, 1.1, 20)
    if len(faces) > 0:
        face = faces[0]
    else:
        face = None

    # Step 3.2: 查找最大外轮廓
    # cv2.findContours是原地的
    contours, hierachy = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]
    maxContour = contours[0]
    for contour in contours:
        if(len(contour) > len(maxContour)):
            maxContour = contour
    # 最终返回的mask
    dstMask = None
    # Step 3.3: 获得分割掩膜
    if face is None:
        # 如果不存在人脸，则填充最大外轮廓即可
        cv2.drawContours(edges, [maxContour], 0, (255, 255, 255), cv2.FILLED)
        _, dstMask = cv2.threshold(edges, 0, 255, cv2.THRESH_BINARY)
        debug('pure_mask', edges)
    else:
        cv2.drawContours(edges, [maxContour], 0, (255, 255, 255), 3)

        # Step 3.3.1: 一定程度的形态学腐蚀操作，去除衣物的粘连
        debug('3.3.1_before_erode', edges)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        edges = cv2.erode(edges, kernel)
        debug('3.3.1_after_erode', edges)

        # Step 3.3.2: 均值滤波，抹除形态学操作后分散的盐噪声
        edges = cv2.medianBlur(edges, 5)
        debug('3.3.2_after_median_blur', edges)

        # Step 3.3.3: 框定grabcut需要的矩形框
        # 获得最小外接矩形
        drawing = np.zeros((rows, cols), np.uint8)
        boundingRect = cv2.boundingRect(maxContour)
        cv2.rectangle(drawing, (boundingRect[0], boundingRect[1]),
                      (boundingRect[0] + boundingRect[2],
                       boundingRect[1] + boundingRect[3]),
                      (255, 0, 0), 2)
        debug('bouding_rectangle', drawing)

        # 利用多边形拟合外轮廓的形状，并获得外轮廓的凸包
        # 绘制出凸包包住拟合多边形的区域
        epsilon = 0.01 * cv2.arcLength(maxContour, True)
        approx = cv2.approxPolyDP(maxContour, epsilon, True)
        hull = cv2.convexHull(maxContour)
        cv2.drawContours(drawing, [hull], 0, (255, 255, 255), cv2.FILLED)
        cv2.drawContours(drawing, [approx], 0, (0, 0, 255), cv2.FILLED)
        # 获得这些区域的外轮廓
        contours, hierachy = cv2.findContours(
            drawing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]
        # 遍历各个轮廓，获得各个轮廓的最小外接矩形
        # 进而获得最深的外接矩形，最深的外接矩形往往反映了与上装黏着的下装部分
        deepestRect = boundingRect
        for contour in contours:
            rect = cv2.boundingRect(contour)
            if rect[3] > 5:
                x, y, w, h = rect
                # 绘制外接矩形
                cv2.rectangle(drawing, (x,y), (x+w, y+h), (255, 255, 255), 2)
                if y > deepestRect[1]:
                    deepestRect = rect
        debug('finding_deepest_rectangle', drawing)

        # 最终用于grabcut的矩形框将排除人脸及裤装（最深矩形
        x, y, w, h = boundingRect
        y = face[1] + face[3]
        h = h - deepestRect[3] - face[3] - face[1]
        # grabcut需要的mask
        grabMask = np.zeros((rows, cols), np.uint8)
        drawing = np.zeros((rows, cols, 3), np.uint8)
        cv2.rectangle(drawing, (x, y), (x+w, y+h), (0, 255, 0), 2)
        debug('rectangle_for_grabcut', drawing)
        try:
            cv2.grabCut(image, grabMask, (x, y, w, h), None,
                        None, 5, cv2.GC_INIT_WITH_RECT)
        except:
            try:
                cv2.grabCut(image, grabMask, boundingRect, None,
                            None, 5, cv2.GC_INIT_WITH_RECT)
            except:
                cv2.grabCut(image, grabMask, (20, 20, rows - 40, cols - 40), None,
                            None, 5, cv2.GC_INIT_WITH_RECT)
        # 将背景颜色设置为0，前景置为255
        dstMask = np.where((grabMask == 2) | (
            grabMask == 0), 0, 255).astype('uint8')
        debug('model_mask', dstMask)
    return dstMask


def _cutPants(image, gray, edges, debug):
    """
    下装分割

    Args:
        image 原图像
        gray 灰度图像
        edges 边缘灰度图像
        debug debug函数
    Return:
        mask 分割掩膜
    """
    rows, cols = edges.shape
    # Step 3.1: 获得最大轮廓及其外接矩形
    contours, hierachy = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]
    maxContour = contours[0]
    boundingRect = cv2.boundingRect(maxContour)
    grabMask = np.zeros((rows, cols), np.uint8)
    grabRect = boundingRect
    # 如果图像黏着有上装（图像轮廓没有居于中央）
    if boundingRect[1] < 20:
        # 多边形拟合
        drawing = np.zeros((rows, cols), np.uint8)
        epsilon = 0.05 * cv2.arcLength(maxContour)
        approx = cv2.approxPolyDP(maxContour, epsilon)
        hull = cv2.convexHull(maxContour)
        cv2.drawContours(drawing, [hull], 0, (255, 255, 255), cv2.FILLED)
        cv2.drawContours(drawing, [approx], 0, (0, 0, 255), cv2.FILLED)

        # 获得凸包及多边形拟合后的轮廓
        contours, hierachy = cv2.findContours(
            drawing, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]

        # 获得最深的外接矩形，以便排除鞋子的影响
        deepestRect = boundingRect
        for contour in contours:
            # 寻找疑似鞋子的部分
            rect = cv2.boundingRect(contour)
            if rect[3] > 100:
                x, y, w, h = rect
                if y > deepestRect[1]:
                    deepestRect = rect

        x, y, w, h = deepestRect
        y = y - 50
        grabRect = (x, y, w, h)
    try:
        cv2.grabCut(image, grabMask, grabRect, None,
                    None, 5, cv2.GC_INIT_WITH_RECT)
    except:
        try:
            cv2.grabCut(image, grabMask, boundingRect, None,
                        None, 5, cv2.GC_INIT_WITH_RECT)
        except:
            cv2.grabCut(image, grabMask, (20, 20, rows - 40, cols - 40), None,
                        None, 5, cv2.GC_INIT_WITH_RECT)
    dstMask = np.where((grabMask == 2) | (
        grabMask == 0), 0, 255).astype('uint8')
    return dstMask


def _clothingEdgeDetect(gray, debug):
    """
    边缘提取

    Args:
        gray 灰度图像
        debug debug函数
    Return:
        edges 边缘图像
    """
    # Canny边缘检测
    edges = cv2.Canny(gray, 100, 200, apertureSize=5)
    # 形态学闭操作修复断线
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    debug('edges', edges)
    return edges


def _pantsEdgeDetect(gray, debug):
    """
    边缘提取

    Args:
        gray 灰度图像
    Return:
        edges 边缘图像
    """
    # Canny边缘检测
    edges = cv2.Canny(gray, 100, 200, apertureSize=3)
    # 形态学闭操作修复断线
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    return edges


def _preProcess(image, debug):
    """
    图像预处理

    Args:
        image 原图像
        debug debug函数
    Return:
        gray 预处理后的灰度图
    """
    # 高斯模糊进行降噪
    image = cv2.GaussianBlur(image, (3, 3), 0)
    debug('after_guassian_blur', image)
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    return gray


def cut(image, isClothing, dp, filename, isDebug = False):
    """
    分割

    Args:
        image 原图像
        dp 当前文件所在路径
        filename 当前处理文件名
        isDebug 是否debug模式
    Return:
        dst 分割后的图像
        mask 掩膜
    """
    def debug(suffix, image):
        if isDebug:
            dstPath = os.path.join(dp,"%s_%s.jpg"%(filename, suffix))
            cv2.imwrite(dstPath, image)

    # Step 1: 图像预处理
    grayImage = _preProcess(image.copy(), debug)

    if isClothing:
        # Step 2: 边缘提取
        edges = _clothingEdgeDetect(grayImage.copy(), debug)
        # Step 3: 分割，并获得分割掩模
        mask = _cutClothing(image.copy(), grayImage.copy(),
                            edges.copy(), debug)
        # Step 4: 优化上衣掩膜
        mask = _optimizeClothingMask(mask.copy(), debug)
    else:
        # Step 2: 边缘提取
        edges = _pantsEdgeDetect(grayImage.copy(), debug)
        # Step 3: 分割，并获得分割掩模
        mask = _cutPants(image.copy(), grayImage.copy(), edges.copy(), debug)
        # Step 4: 优化下装掩膜
        mask = _optimizePantsMask(mask.copy(), debug)

    # Step 5: 生成最终图像
    dst = image * (mask[:, :, np.newaxis] / 255)
    return mask, dst
