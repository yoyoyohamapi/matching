# coding: utf8
"""
上装聚类---条纹
"""

print(__doc__)

import pandas
import numpy as np
from clothing_cluster import clustering

data = pandas.read_csv("../features/clothings.csv").values
data = np.delete(data, 1, 1)

nClusters = 4
directory = '../clothings_cluster_all'

clustering(data, nClusters, directory, methods=[
    'Kmeans',
    'AC-Complete',
    'AC-Average',
    'AC-Ward',
    'SpectralClustering',
    'BIRCH',
    'DBSCAN'
])
