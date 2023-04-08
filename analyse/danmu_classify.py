import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt
import os
from sklearn.cluster import KMeans
import numpy as np
os.environ["OMP_NUM_THREADS"] = '1'
mpl.rcParams['font.sans-serif'] = ['KaiTi']
mpl.rcParams['font.serif'] = ['KaiTi']

# 弹幕画图
def draw_danmu(i,idd):
    danmu = pd.read_csv('../history/danmus/'+idd+'.csv')
    plt.figure(i,figsize=(14,4))
    plt.subplot(1,2,1)
    danmu['视频内弹幕出现时间'].plot.hist(bins=20)
    plt.figure(i)
    plt.subplot(1,2,2)
    plt.xlim((danmu['视频内弹幕出现时间'].min(),danmu['视频内弹幕出现时间'].max()))
    danmu['视频内弹幕出现时间'].plot.density()

def danmu_classify(danmu_cids):
    # 弹幕分析
    danmu_cdf = []
    # [df_video['播放数']<1000000].sort_values(by='播放数')
    for i, idd in enumerate(danmu_cids):

        danmu = pd.read_csv('../history/danmus/'+idd+'.csv')
        if len(danmu.values) == 0:
            continue
        d_cut = pd.cut(danmu['视频内弹幕出现时间'], bins=20,
                       labels=['p00', 'p01', 'p02', 'p03', 'p04', 'p05', 'p06', 'p07', 'p08', 'p09',
                               'p10', 'p11', 'p12', 'p13', 'p14', 'p15', 'p16', 'p17', 'p18', 'p19'])
        d_cut = pd.Series(d_cut)
        d_cut.name = idd
        danmu_cdf.append(d_cut)
    # 弹幕分析2 聚类
    df_dan = pd.DataFrame()
    for i in danmu_cdf:
        d = i.value_counts()
        d = d / d.sum()
        df_dan = pd.concat([df_dan, d], axis=1)
    df_dan = df_dan.T
    # kmeas聚类手肘法决定k = 3
    X = df_dan.values
    plt.figure(figsize=(20, 6))
    sc = []
    for i in range(1, 100):
        kmeans = KMeans(n_clusters=i, n_init=10).fit(X)
        sc.append(kmeans.inertia_)
    plt.plot(np.arange(1, 100), sc)

    # 开始聚类
    kmeans = KMeans(n_clusters=5, n_init=10).fit(X)
    classfied_dan = pd.Series(kmeans.labels_, index=df_dan.index.values)
    classfied_dan.to_csv('../history/cluster_result.csv')

    print(kmeans.labels_)
    print(kmeans.inertia_)
    classfied_distance = pd.DataFrame(kmeans.transform(X), index=df_dan.index.values, columns=[i for i in range(5)])

    # 给每一种类型画图
    for i in range(5):
        idd = classfied_distance[i].idxmin()
        draw_danmu(i, idd)
        plt.title('类' + str(i))
        plt.show()

    for i, idd in enumerate(classfied_distance.sort_values(by=1).index):
        draw_danmu(i + 8, idd)
        if i > 10 : break
    plt.show()

if __name__ == '__main__':
    source_path = '../history/danmus'
    root, dirs, files  =  zip(*os.walk(source_path))
    files = files[0]
    danmu_cids = []
    for i in files:
        danmu_cids.append(i[:-4])
    print('开始')
    danmu_classify(danmu_cids)