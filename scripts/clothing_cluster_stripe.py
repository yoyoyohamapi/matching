# coding: utf8
"""
上装聚类---条纹
"""

print(__doc__)

import pandas
from clothing_cluster import clustering

data = pandas.read_csv("../features/clothings.csv").values
data = data[:, [0, 4,5,6,7]]

# 条纹聚类：条纹衫、疑似条纹衫（再进行手动筛选）、非条纹衫
nClusters = 3
directory = '../clothings_cluster_stripe_'

clustering(data, nClusters, directory)
