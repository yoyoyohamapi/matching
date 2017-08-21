# coding: utf8
"""
上装聚类---条纹
"""

print(__doc__)

import pandas
from clothing_cluster import clustering

data = pandas.read_csv("../clothings.csv").values
data = data[:, [1, 3,4,5,6,7,8]]

nClusters = 3
directory = '../clothings_cluster_style'

clustering(data, nClusters, directory)
