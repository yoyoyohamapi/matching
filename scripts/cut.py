# coding: utf-8
import cv2
import os
import numpy as np

def _noop(*args):
    return None

def _findMaxContour(edges):
    """
    获得边缘灰度图的最大轮廓

    Args:
        edges 边缘图像
    Return:
        maxContour zui'da
    """
    contours, hierachy = cv2.findContours(
        edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_NONE)[-2:]
    if len(contours) <= 0:
        return None
    maxContour = contours[0]
    for contour in contours:
        if(cv2.contourArea(contour) > cv2.contourArea(maxContour)):
            maxContour = contour
    return maxContour


def _createDebug(dp, filename):
    """
    创建debug函数

    Args:
        dp 文件目录
        filename 文件名
    Return:
        _debug 调试函数
    """
    def _debug(suffix, image):
        dstPath = os.path.join(dp, "%s_%s.jpg" % (filename, suffix))
        cv2.imwrite(dstPath, image)
    return _debug


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
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel, iterations=2)
    debug('4.1_after_close', mask)

    # Step 4.2: 形态学开操作去除衣物四周的吊饰
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel, iterations=2)
    debug('4.1_after_open', mask)

    # Step 4.3: 填充最大轮廓，
    maxContour = _findMaxContour(mask)
    if maxContour is not None:
        cv2.drawContours(mask, [maxContour], 0, (255, 255, 255), cv2.FILLED)

    # Step 4.4: 进行一定的腐蚀操作，去除背景边界
    debug('4.4_before_erode', mask)
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
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
    # Step 4.1: 形态学开操作去除衣物四周的吊饰
    kernel = cv2.getStructuringElement(cv2.MORPH_RECT, (5, 5))
    mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
    debug('4.1_after_open', mask)

    # Step 4.2: 进行一定的腐蚀操作，去除背景边界
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (5, 5))
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

    # Step 3.1: 头部检测，应用grabcut圈定矩形框的时候需要去除头部
    withModel = False

    # Step 3.2: 查找最大外轮廓
    # cv2.findContours是原地的
    maxContour = _findMaxContour(edges)
    boundingRect = cv2.boundingRect(maxContour)

    # 情境判断，下方含有较大面积时考虑为Model情境
    bottomRoi = edges[rows-10:rows, :]
    maxContourInBottom = _findMaxContour(bottomRoi)
    if maxContourInBottom is not None and cv2.contourArea(maxContourInBottom) > 150:
        withModel = True

    if withModel:
        cv2.drawContours(edges, [maxContour], 0, (255, 255, 255), 3)
        # Step 3.3.1: 一定程度的形态学腐蚀操作，去除衣物的粘连
        debug('3.3.1_before_erode', edges)
        kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
        edges = cv2.erode(edges, kernel)
        debug('3.3.1_after_erode', edges)

        # Step 3.3.2: 均值滤波，抹除形态学操作后分散的盐噪声
        edges = cv2.medianBlur(edges, 5)
        debug('3.3.2_after_median_blur', edges)
        # 进行缺陷检测，确定头部和衣物的分界
        hull = cv2.convexHull(maxContour, returnPoints=False)
        hullForDraw = cv2.convexHull(maxContour, returnPoints=True)
        defects = cv2.convexityDefects(maxContour, hull)

        hullDrawing = np.zeros((rows, cols,3), np.uint8)
        cv2.drawContours(hullDrawing, [hullForDraw], 0, (208,188,44), 3)
        cv2.drawContours(hullDrawing, [maxContour], 0, (255,255,255), 2)

        head = [0, 0, cols, 0]
        for defect in defects:
            s, e, f, d = defect[0]
            cv2.circle(hullDrawing, tuple(maxContour[f][0]), 8, (0,255,255), -1)
            if d > 6000:
                farW, farD = maxContour[f][0]
                if farD < rows / 2 and farW > 100 and farW < cols - 100:
                    height = farD
                    if head[3] < height:
                        head[3] = height
        head[3] = head[3] - 5
        debug('hull', hullDrawing)

    else:
        head = None

    contourDrawing = np.zeros((rows, cols), np.uint8)
    cv2.drawContours(contourDrawing, [maxContour],
                     0, (255, 255, 255), cv2.FILLED)
    debug('max_contour', contourDrawing)
    # 最终返回的mask
    dstMask = None
    # Step 3.3: 获得分割掩膜
    if head is None:
        # 如果不存在头部，则填充最大外轮廓即可
        cv2.drawContours(edges, [maxContour], 0, (255, 255, 255), cv2.FILLED)
        _, dstMask = cv2.threshold(edges, 0, 255, cv2.THRESH_BINARY)
    else:
        # Step 3.3.3: 框定grabcut需要的矩形框
        # 获得最小外接矩形
        drawing = np.zeros((rows, cols), np.uint8)
        colorDrawing = np.zeros((rows, cols, 3), np.uint8)

        boundingRect = cv2.boundingRect(maxContour)
        # 直接grabcut查看结果
        grabMask = np.zeros((rows, cols), np.uint8)
        cv2.grabCut(image, grabMask, (20, 20, rows - 40, cols - 40), None,
                    None, 5, cv2.GC_INIT_WITH_RECT)
        dstMask = np.where((grabMask == 2) | (
            grabMask == 0), 0, 255).astype('uint8')
        debug('mask_without_opt', dstMask)
        dst = image * (dstMask[:, :, np.newaxis] / 255)
        debug('without_opt', dst)

        cv2.rectangle(drawing, (boundingRect[0], boundingRect[1]),
                      (boundingRect[0] + boundingRect[2],
                       boundingRect[1] + boundingRect[3]),
                      (255, 0, 0), 2)

        # 利用多边形拟合外轮廓的形状，并获得外轮廓的凸包
        # 绘制出凸包包住拟合多边形的区域
        epsilon = 0.01 * cv2.arcLength(maxContour, True)
        approx = cv2.approxPolyDP(maxContour, epsilon, True)
        approxDrawing = np.zeros((rows, cols, 3), np.uint8)
        cv2.drawContours(approxDrawing, [maxContour], 0, (255, 255, 255), 3)
        cv2.drawContours(approxDrawing, [approx], 0, (199, 138, 208), 3)
        debug("approx", approxDrawing)
        hull = cv2.convexHull(maxContour)
        cv2.drawContours(colorDrawing, [hull], 0, (208,188,44), cv2.FILLED)
        cv2.drawContours(drawing, [hull], 0, (255, 255, 255), cv2.FILLED)
        cv2.drawContours(colorDrawing, [approx], 0, (199, 138, 208), cv2.FILLED)
        cv2.drawContours(drawing, [approx], 0, (0, 0, 255), cv2.FILLED)
        cv2.drawContours(colorDrawing, [maxContour], 0, (255, 255, 255), 3)

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
                if y > deepestRect[1]:
                    deepestRect = rect
        # cv2.rectangle(
        #     colorDrawing,
        #     (boundingRect[0], boundingRect[1]),
        #     (boundingRect[0] + boundingRect[2],
        #      boundingRect[1] + boundingRect[3]),
        #     (0, 255, 0),
        #     2
        # )
        # cv2.rectangle(
        #     colorDrawing,
        #     (head[0], head[1]),
        #     (head[0] + head[2], head[1] + head[3]),
        #     (255, 0, 255),
        #     2
        # )
        cv2.rectangle(
            colorDrawing,
            (deepestRect[0], deepestRect[1]),
            (deepestRect[0] + deepestRect[2], deepestRect[1] + deepestRect[3]),
            (255, 0, 0),
            3
        )

        debug('finding_rectangle', colorDrawing)

        # 最终用于grabcut的矩形框将排除模特头部及裤装（最深矩形
        x, y, w, h = boundingRect
        y = head[1] + head[3]
        h = h - deepestRect[3] - head[3] - head[1]
        # grabcut需要的mask
        grabMask = np.zeros((rows, cols), np.uint8)
        drawing = np.zeros((rows, cols, 3), np.uint8)
        cv2.drawContours(drawing, [maxContour], 0, (255,255,255), 3)
        cv2.rectangle(drawing, (x, y), (x + w, y + h), (0, 255, 0), 3)
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
    debug('mask', dstMask)
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
    withModel = False
    # Step 3.1: 获得最大轮廓及其外接矩形
    maxContour = _findMaxContour(edges)
    boundingRect = cv2.boundingRect(maxContour)

    # 情境判断，上方含有较大面积时考虑为Model情境
    topRoi = edges[rows-10:rows, :]
    maxContourInTop = _findMaxContour(topRoi)
    if maxContourInTop is not None and cv2.contourArea(maxContourInTop) > 150:
        withModel = True

    # 最终返回的mask
    dstMask = None
    colorDrawing = np.zeros((rows, cols, 3), np.uint8)
    contourDrawing = np.zeros((rows, cols), np.uint8)
    if not withModel:
        # 如果不存在头部，则填充最大外轮廓即可
        dstMask = contourDrawing
        debug('pure_mask', contourDrawing)
    else:
        # 轮廓增强
        contours, hierachy = cv2.findContours(
            edges, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)[-2:]
        for contour in contours:
            cv2.drawContours(edges, [contour],
                             0, (255, 255, 255), 3)
        debug('fill_contour', edges)
        maxContour = _findMaxContour(edges)
        boundingRect = cv2.boundingRect(maxContour)

        epsilon = 10
        approx = cv2.approxPolyDP(maxContour, epsilon, False)
        hull = cv2.convexHull(approx)
        # 蓝色描述凸包
        cv2.drawContours(colorDrawing, [hull], 0, (255, 0, 0), 3)
        # 红色描述多边形拟合
        cv2.drawContours(colorDrawing, [approx], 0, (0, 0, 255), 3)
        # approx = _findMaxContour(cv2.cvtColor(colorDrawing.copy(), cv2.COLOR_BGR2GRAY))
        approxImage = np.zeros((rows,cols), np.uint8)
        cv2.drawContours(approxImage, [approx], 0, 255, -1)
        debug('approx_image', approxImage)
        # 四个ROI进行特征点查找
        x,y,w,h = boundingRect
        leftEnd = x + w*2/5
        rightBegin = x + w*3/5
        topEnd = y + h*2/5
        bottomBegin = y + h*3/5
        leftClothingRoi = approxImage[y:topEnd, x:leftEnd].copy()
        rightClothingRoi = approxImage[y:topEnd, rightBegin:x+w].copy()
        leftShoesRoi = approxImage[bottomBegin:y+h, x:leftEnd].copy()
        rightShoesRoi = approxImage[bottomBegin:y+h, rightBegin:x+w].copy()
        leftClothingContour = _findMaxContour(leftClothingRoi)
        rightClothingContour = _findMaxContour(rightClothingRoi)
        leftShoesContour = _findMaxContour(leftShoesRoi)
        rightShoesContour = _findMaxContour(leftShoesRoi)
        # 初始化衣物分界线两端
        leftClothingBoundary = [x, y]
        rightClothingBoundary = [x+w, y]
        # 初始化鞋子分界线两端
        leftShoesBoundary = [x, y+h]
        rightShoesBoundary = [x+w, y+h]
        # 初始化最终用于grabCut的矩形
        grabRect = list((boundingRect))
        # 找到上衣和下装的分界线
        hull = cv2.convexHull(leftClothingContour, returnPoints=False)
        defects = cv2.convexityDefects(leftClothingContour, hull)
        for defect in defects:
            s, e, f, d = defect[0]
            farW, farD = leftClothingContour[f][0]
            farW = farW + x
            cv2.circle(colorDrawing, (farW, farD), 5, (255,255,255), -1)
            # 选择最深的
            if leftClothingBoundary[1] < farD:
                leftClothingBoundary = [farW, farD]
        hull = cv2.convexHull(rightClothingContour, returnPoints=False)
        defects = cv2.convexityDefects(rightClothingContour, hull)
        for defect in defects:
            s, e, f, d = defect[0]
            farW, farD = rightClothingContour[f][0]
            farW = farW + rightBegin
            cv2.circle(colorDrawing, (farW, farD), 5, (255,255,255), 2)
            # 选择最深的
            if rightClothingBoundary[1] < farD:
                cv2.circle(colorDrawing, (farW, farD), 5, (255,255,255), -1)
                rightClothingBoundary = [farW, farD]
        grabRect[0] = leftClothingBoundary[0]
        grabRect[2] = rightClothingBoundary[0] - leftClothingBoundary[0]
        if leftClothingBoundary[1] > rightClothingBoundary[1]:
            grabRect[1] = rightClothingBoundary[1]
        else:
            grabRect[1] = leftClothingBoundary[1]
        # 找到下装和鞋子的分界线
        hull = cv2.convexHull(leftShoesContour, returnPoints=False)
        defects = cv2.convexityDefects(leftShoesContour, hull)
        for defect in defects:
            s, e, f, d = defect[0]
            farW, farD = leftShoesContour[f][0]
            farW = farW + x
            farD = farD + bottomBegin
            cv2.circle(colorDrawing, (farW, farD), 5, (255,255,255), -1)
            # 找寻较浅的
            if leftShoesBoundary[1] > farD:
                leftShoesBoundary = [farW, farD]
        hull = cv2.convexHull(rightClothingContour, returnPoints=False)
        defects = cv2.convexityDefects(rightClothingContour, hull)
        for defect in defects:
            s, e, f, d = defect[0]
            farW, farD = rightClothingContour[f][0]
            farW = farW + rightBegin
            farD = farD + bottomBegin
            cv2.circle(colorDrawing, (farW, farD), 5, (255,255,255), -1)
            # 找寻较浅的
            if rightShoesBoundary[1] > farD:
                rightShoesBoundary = [farW, farD]
        if leftShoesBoundary[1] > rightShoesBoundary[1]:
            grabRect[3] = leftShoesBoundary[1] - grabRect[1]
        else:
            grabRect[3] = rightShoesBoundary[1] - grabRect[1]
        # 稍微放缩矩形
        grabRect[0] = grabRect[0] - 20
        grabRect[2] = grabRect[2] + 40
        grabRect[1] = grabRect[1] - 20
        grabRect[3] = grabRect[3] + 40
        # 绘制原外接矩形及最终用于grabCut的矩形
        cv2.rectangle(
            colorDrawing,
            (boundingRect[0], boundingRect[1]),
            (boundingRect[0] + boundingRect[2], boundingRect[1] + boundingRect[3]),
            (255, 0, 0),
            2
        )
        cv2.rectangle(
            colorDrawing,
            (grabRect[0], grabRect[1]),
            (grabRect[0] + grabRect[2], grabRect[1] + grabRect[3]),
            (0, 255, 0),
            2
        )
        debug("finding_rectangle", colorDrawing)

        # 用于grabcut的mask
        grabMask = np.zeros((rows, cols), np.uint8)
        try:
            cv2.grabCut(image, grabMask, tuple(grabRect), None,
                        None, 5, cv2.GC_INIT_WITH_RECT)
        except:
            cv2.grabCut(image, grabMask, boundingRect, None,
                        None, 5, cv2.GC_INIT_WITH_RECT)
        dstMask = np.where((grabMask == 2) | (
            grabMask == 0), 0, 255).astype('uint8')
    cv2.drawContours(contourDrawing, [maxContour],
        0, (255, 255, 255), cv2.FILLED)
    debug('max_contour', contourDrawing)
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
    edges = cv2.Canny(gray, 1, 20, apertureSize=3)
    # 边缘增强
    x = cv2.Sobel(edges, cv2.CV_16S,1,0)
    y = cv2.Sobel(edges, cv2.CV_16S,0,1)
    absX = cv2.convertScaleAbs(x)   # 转回uint8
    absY = cv2.convertScaleAbs(y)
    edges = cv2.addWeighted(absX,0.5,absY,0.5,0)
    _, edges = cv2.threshold(edges, 50, 255, cv2.THRESH_BINARY)
    # 形态学闭操作修复断线
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    debug('edges', edges)
    return edges


def _pantsEdgeDetect(gray, debug):
    """
    边缘提取

    Args:
        gray 灰度图像
        debug debug函数
    Return:
        edges 边缘图像
    """
    # Canny边缘检测
    edges = cv2.Canny(gray, 1, 20, apertureSize = 3)
    # 边缘增强
    x = cv2.Sobel(edges, cv2.CV_16S,1,0)
    y = cv2.Sobel(edges, cv2.CV_16S,0,1)
    absX = cv2.convertScaleAbs(x)   # 转回uint8
    absY = cv2.convertScaleAbs(y)
    edges = cv2.addWeighted(absX,0.5,absY,0.5,0)
    _, edges = cv2.threshold(edges, 50, 255, cv2.THRESH_BINARY)

    # 形态学闭操作修复断线
    kernel = cv2.getStructuringElement(cv2.MORPH_ELLIPSE, (3, 3))
    edges = cv2.morphologyEx(edges, cv2.MORPH_CLOSE, kernel)
    debug('edges', edges)
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
    gray = cv2.cvtColor(image, cv2.COLOR_BGR2GRAY)
    debug('after_gaussian_blur', gray)
    return gray


def cut(image, isClothing, dp, filename, isDebug=False):
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
    if isDebug:
        debug = _createDebug(dp, filename)
    else:
        debug = _noop
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
