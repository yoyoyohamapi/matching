# coding: utf8
"""
上装聚类模块
"""
import time
import pandas
import os
import shutil

import numpy as np
import matplotlib.pyplot as plt
from sklearn import cluster
from sklearn.neighbors import kneighbors_graph
from sklearn.preprocessing import StandardScaler
from sklearn.decomposition import PCA

from sklearn.feature_selection import SelectKBest, chi2

from sklearn.cluster import KMeans


def clustering(data, nClusters, directory, methods=None):
    """
    聚类

    Args:
        data 数据，第一列默认为图片所在路径
        nClusters 聚类数
        directory 目标文件夹
        methods 需要调用的聚类方法
    """
    paths = data[:, 0]
    dataset = data[:, 1:]
    reducedData = PCA(n_components=2).fit_transform(dataset)
    nSamples, nFeatures = dataset.shape
    if nSamples < nClusters:
        return
    # 创建聚类目标文件夹
    directory = directory + '%d' % (time.time())
    os.mkdir(directory)
    np.random.seed(0)

    # Generate datasets. We choose the size big enough to see the scalability
    # of the algorithms, but not too big to avoid too long running times
    colors = np.array([x for x in 'bgrcmykbgrcmykbgrcmykbgrcmyk'])
    colors = np.hstack([colors] * 20)
    if methods is not None:
        clustering_names = methods
    else:

        if nSamples > 10:
            clustering_names = [
                'MiniBatchKMeans',
                'SpectralClustering',
                'Ward'
            ]
        else:
            clustering_names = [
                'MiniBatchKMeans',
                'Ward'
            ]

    plt.figure(figsize=(len(clustering_names) * 2 + 3, 9.5))
    plt.subplots_adjust(left=.02, right=.98, bottom=.001, top=.96, wspace=.05,
                        hspace=.01)
    plot_num = 1

    X = dataset
    # normalize dataset for easier parameter selection
    X = StandardScaler().fit_transform(X)

    # connectivity matrix for structured Ward
    if nSamples > 10:
        nNeighbors = 10
    else:
        nNeighbors = nSamples - 1
    print nNeighbors
    connectivity = kneighbors_graph(
        X, n_neighbors=nNeighbors, include_self=False)
    # make connectivity symmetric
    connectivity = 0.5 * (connectivity + connectivity.T)

    # create clustering estimators
    twoMeans = cluster.MiniBatchKMeans(n_clusters=nClusters)

    spectral = cluster.SpectralClustering(n_clusters=nClusters,
                                          eigen_solver='arpack',
                                          affinity="nearest_neighbors")
    dbscan = cluster.DBSCAN()
    birch = cluster.Birch(n_clusters=nClusters)
    affinity_propagation = cluster.AffinityPropagation(damping=.9,
                                                       preference=-200)
    averageLinkage = cluster.AgglomerativeClustering(
        linkage="average", affinity="cityblock", n_clusters=nClusters,
        connectivity=connectivity)
    wardLinkage = cluster.AgglomerativeClustering(n_clusters=nClusters, linkage='ward',
                                                  connectivity=connectivity)
    completeLinkage = cluster.AgglomerativeClustering(n_clusters=nClusters, linkage='complete',
                                                  connectivity=connectivity)
    methodsMap = {
        'Kmeans': twoMeans,
        'SpectralClustering': spectral,
        'DBSCAN': dbscan,
        'BIRCH': birch,
        'AC-Ward': completeLinkage,
        'AC-Average': averageLinkage,
        'AC-Complete': completeLinkage
    }

    if methods is not None:
        clustering_algorithms = [methodsMap[method] for method in methods]
    else:
        if nSamples > 10:
            clustering_algorithms = [
                twoMeans, spectral, wardLinkage
            ]
        else:
            clustering_algorithms = [
                twoMeans, wardLinkage
            ]
    # 聚类及绘制
    for name, algorithm in zip(clustering_names, clustering_algorithms):
        data = reducedData
        # predict cluster memberships
        t0 = time.time()
        algorithm.fit(data)
        t1 = time.time()
        if hasattr(algorithm, 'labels_'):
            y_pred = algorithm.labels_.astype(np.int)
        else:
            y_pred = algorithm.predict(data)
        # plot
        # Plot the decision boundary. For that, we will assign a color to each
        x_min, x_max = data[:, 0].min() - 1, data[:, 0].max() + 1
        y_min, y_max = data[:, 1].min() - 1, data[:, 1].max() + 1

        plt.subplot(4, len(clustering_algorithms), plot_num)
        plt.title(name, size=18)

        plt.scatter(data[:, 0], data[:, 1], color=colors[y_pred].tolist(), s=10)

        if hasattr(algorithm, 'cluster_centers_'):
            centers = algorithm.cluster_centers_
            center_colors = colors[:len(centers)]
            plt.scatter(centers[:, 0], centers[:, 1],
                        s=200, marker='x',c='black', linewidths=5)
        plt.xlim(x_min, x_max)
        plt.ylim(y_min, y_max)
        plt.xticks(())
        plt.yticks(())
        plt.text(.4, .7, ('%.1fms' % ((t1 - t0)*1000)),
                 transform=plt.gca().transAxes, size=15,
                 bbox={'facecolor':'red', 'alpha':0.5, 'pad':10},
                 horizontalalignment='center')
        plot_num += 1

        for n in range(nSamples):
            path = paths[n]
            center = y_pred[n]
            dst = directory + '/%s/%d/' % (name, center)
            if not os.path.exists(dst):
                os.makedirs(dst)
            shutil.copy(path, dst)

    plt.show()
