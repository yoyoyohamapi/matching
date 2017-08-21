# coding: utf8
"""
上装聚类---图案
"""

print(__doc__)

import pandas
import os
import re
import numpy as np
from clothing_cluster import clustering

categories = [
    u'背心',
    u'衬衫',
    u'大衣/风衣',
    u'防风外套',
    u'夹克',
    u'马甲',
    u'毛衣/针织',
    u'棉衣',
    u'皮衣',
    u'套装',
    u'卫衣',
    u'西装',
    u'羽绒服',
    u'POLO',
    u'T恤'
]

def _cluster(category):
    cateName = category.split('/')[0]
    csvFile = '../features/'+cateName+'.csv'
    try:
        data = pandas.read_csv(csvFile).values
        # 从数据集中抛去条纹衫
        data = data[:,]
        rows = []
        for dp, dn, fs, in os.walk('../clothings/stripes'):
            for f in fs:
                clothingId = f.split('.')[0]
                for rowId, row in enumerate(data):
                    path = row[0]
                    if path.find(clothingId) >= 0:
                        rows.append(rowId)
        rows = list(set(range(data.shape[0])) - set(rows))
        data = data[rows, :]
        # 上装聚类： 简单图案，花哨图案，纯色
        nClusters = 3
        directory = '../clothings_cluster_pattern_%s_'%cateName
        clustering(data, nClusters, directory)
    except pandas.io.common.EmptyDataError:
        print "no columns in category:%s"%cateName
map(_cluster, categories)
