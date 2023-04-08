import time
from datetime import datetime
import pandas as pd
import numpy as np
import statsmodels.api as sm
import matplotlib as mpl
import matplotlib.pyplot as plt
import seaborn as sns
import os

op = 1
os.environ["OMP_NUM_THREADS"] = '1'
mpl.rcParams['font.sans-serif'] = ['YouYuan']
mpl.rcParams['font.serif'] = ['YouYuan']
plt.rcParams['axes.unicode_minus'] = False
plt.rc('font', family='Youyuan', size='9')

'''
1.弹幕，评论，点赞，硬币为0的视频记录特别多
2.除了存留时长有周期特征，标签个数相对均匀，up等级相对正态，其他全部的变量都是右偏分布
3.进行正态检验，log对数转换
4.变量之间相关性分析，离散变量的方差分析
5.把弹幕，评论，点赞，硬币分割范围分别回归
6.为了解决多重共线性问题引入岭回归
7.弹幕分析
8.文本分析
'''
# 读入
# 2023-02-23 0809--2023-02-23 1227
# 2023-02-16 0853-- 2023-02-16 1526.csv
# 2023-02-15 2330--2023-02-16 0244.csv
# 2023-02-15 1528--2023-02-15 1834.csv
bigtable = pd.read_csv('../history/all/2023-02-16 0853-- 2023-02-16 1526.csv')

# 打印
# print(bigtable.columns)
'''
1.要删除的：
'video_aid', '爬取时间', 'video_cid', '上传时间', '审核时间',  '标签分区', '历史最高排名',
2.因变量：
'beh_硬币数', 'beh_弹幕数', 'beh_点踩数', 'beh_收藏数', 'beh_点赞数',
'beh_评论数', 'beh_分享数', 'beh_播放数','播放数',
3.视频连续变量：
'播放时长', '硬币数', '弹幕数', '收藏数', '点赞数', '评论数', '分享数', '存留时长','平均标签订阅数',
4.视频离散变量：
'是否原创', '是否合作', '标签个数','有无简介', '标题样式', '有无广告',
'是否原创_1', '是否原创_2','是否合作_0', '是否合作_1', '有无简介_0', '有无简介_1', '有无广告_0', '有无广告_1',
'标题样式_。','标题样式_！', '标题样式_？'
5.up主变量：
'up等级', 
'up粉丝数', 'up投稿数','up平均每个视频播放量', 'up平均每个视频点赞数',
6.评论区变量：  
'up在最热前500条评论的回复数', 'up在最热前500条评论的点赞数',
'最热前500条评论中平均每条评论的回复数', '最热前500条评论中平均每条评论的点赞数', 
'''
print(bigtable.shape)
''' 1951,40  '''
# print(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(bigtable['上传时间'].max())))
'''  2023-02-08 14:53:12   2023-02-14 21:39:59'''


# 最近日均播放，点赞，硬币，弹幕，评论，分享，收藏
l = ['硬币数', '弹幕数', '收藏数', '点赞数', '评论数', '分享数', '播放数',
     '播放时长', '平均标签订阅数', 'up粉丝数', 'up投稿数',
     'up在最热前500条评论的回复数', 'up在最热前500条评论的点赞数',
     '最热前500条评论中平均每条评论的回复数', '最热前500条评论中平均每条评论的点赞数', 'y'
     ]
l1 = ['存留时长','日均评论','日均点赞','日均硬币', '日均弹幕', '日均收藏', '日均分享', '日均播放',
     '最热前500条评论中平均每条评论的点赞数','最热前500条评论中平均每条评论的回复数',
      '平均标签订阅数','up粉丝数', 'up投稿数','播放时长',
      'up在最热前500条评论的回复数', 'up在最热前500条评论的点赞数','y'
      ]
re_name = {
    '存留时长': '已发布天数', '日均评论': '历史日均评论量', '日均点赞': '历史日均点赞量',
    '日均硬币': '历史日均硬币量', '日均弹幕': '历史日均弹幕量', '日均收藏': '历史日均收藏量',
    '日均分享': '历史日均分享量', '日均播放': '历史日均播放量',
    '最热前500条评论中平均每条评论的点赞数': '评论区平均点赞量',
    '最热前500条评论中平均每条评论的回复数': '评论区平均回复量',
    '平均标签订阅数': '平均视频标签订阅量', 'up粉丝数': 'up粉丝量', 'up投稿数': 'up投稿量',
    '播放时长': '视频时长', 'up在最热前500条评论的回复数': 'up主评论区回复量之和',
    'up在最热前500条评论的点赞数': 'up主评论区点赞量之和', 'y': '24小时后播放增量'
}

if op == 1:
    l = l1
    bigtable['日均播放'] = bigtable['播放数'] / bigtable['存留时长']
    bigtable['日均点赞'] = bigtable['点赞数'] / bigtable['存留时长']
    bigtable['日均硬币'] = bigtable['硬币数'] / bigtable['存留时长']
    bigtable['日均评论'] = bigtable['评论数'] / bigtable['存留时长']
    bigtable['日均弹幕'] = bigtable['弹幕数'] / bigtable['存留时长']
    bigtable['日均分享'] = bigtable['分享数'] / bigtable['存留时长']
    bigtable['日均收藏'] = bigtable['收藏数'] / bigtable['存留时长']

    # bigtable['每万点赞转化'] = bigtable['点赞数'] * 10000 / bigtable['播放数']
    # bigtable['每万硬币转化'] = bigtable['硬币数'] * 10000 / bigtable['播放数']
    # bigtable['每万评论转化'] = bigtable['评论数'] * 10000 / bigtable['播放数']
    # bigtable['每万弹幕转化'] = bigtable['弹幕数'] * 10000 / bigtable['播放数']
    # bigtable['每万分享转化'] = bigtable['分享数'] * 10000 / bigtable['播放数']
    # bigtable['每万收藏转化'] = bigtable['收藏数'] * 10000 / bigtable['播放数']
bigtable['y'] = bigtable['beh_播放数'] - bigtable['播放数']
bigtable['24h后播放增量'] = bigtable['y']

# 去除异常值
if op ==0:
    y_std = bigtable['y'].std()**(1/2)
    y_mean = bigtable['y'].mean()
    y_up = y_mean + 3*y_std
    y_d = y_mean - 3*y_std
    bigtable = bigtable[(bigtable.y > y_d)&(bigtable.y < y_up)]
# 筛选
# (bigtable['up粉丝数'] < 5000)&(bigtable['播放时长'] > 600)
# (bigtable['up在最热前500条评论的点赞数'] != 0)  (bigtable['播放时长'] > 600)
# # (bigtable['up粉丝数'] > 39000)
#  (bigtable['硬币数']==0)&(bigtable['弹幕数']==0)&(bigtable['收藏数']==0)&\
#                 (bigtable['评论数']==0)&(bigtable['分享数']==0)&(bigtable['点赞数']==0)
if op == 1:
    condition = (bigtable['up粉丝数'] > 38000)
    bigtable = bigtable[condition]
    print(f'筛选后的数据量为{bigtable.shape}')
    print(f"最长留存了{bigtable['存留时长'].max()}")
    print(f"最短留存了{bigtable['存留时长'].min()}")
# bigtable查看
bigtable.sort_values(by='y', ascending=False).to_excel('temp.xlsx')
# 因变量正态假设检验
if op == 0:
    y = bigtable['y'][bigtable['y'] > 0].map(np.log)
    y.plot.hist(bins=30)
    plt.xlabel('24小时后的播放增量',fontdict={'weight': 'bold', 'size': 16})
    sm.qqplot(y, line='s')
    plt.show()

# 自变量取对数
if op == 1:
    for i, cname in enumerate(l[1:]):
        if len(bigtable[bigtable[cname] == 0]) > 0:
            print(cname)
            bigtable[cname] += 1
        bigtable[cname] = bigtable[cname].map(np.log)

# 变量分布图
if op == 0:
    plt.figure()
    for i, cname in enumerate(l):
        plt.subplot(6, 4, i + 1)
        bigtable[cname].plot.hist(bins=50)
        plt.title(re_name[cname])
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.2, hspace=0.43)
    plt.show()

# 相关性分析
if op == 0:
    # 改名
    for i in l:
        bigtable[re_name[i]] = bigtable[i]
        del bigtable[i]
    corr = bigtable[re_name.values()].corr(method='pearson')
    corr.to_excel('../history/describe_result/continue_corr.xlsx')
    sns.heatmap(corr, vmax=.8, square=True, annot=True)  # annot=True 显示系数
    plt.show()

# 散点图
if op == 0:
    for i, cname in enumerate(l[:-1]):
        plt.subplot(5, 4, i + 1)
        plt.scatter(bigtable[cname], bigtable.y)
        plt.title(re_name[cname])
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.2, hspace=0.43)
    # plt.figure(2)
    #     plt.scatter(bigtable[cname],bigtable.y)
    #     plt.xlim(bigtable[cname].min(),bigtable[cname].max())
    #     plt.title(cname)
    plt.show()
if op == 1:
    bigtable['发布时间星期'] = bigtable['上传时间'].map(
        lambda x: datetime.fromtimestamp(x).isoweekday()
    )
    bigtable['发布时间'] = bigtable['上传时间'].map(
        lambda x: datetime.fromtimestamp(x)
    )
    plt.figure(1)
    for i in range(1,8):
        plt.subplot(2,4,i)
        bigtable['发布时间'][bigtable['发布时间星期']==i].hist(bins=24)
        plt.title(f'星期{i}')
        plt.grid(None)
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.2, hspace=0.43)
    plt.show()

# 变量描述
bigtable.describe().to_excel('../history/describe_result/describe.xlsx')
# for i in bigtable.columns:
#     bigtable[i].value_counts().to_csv(f'../history/describe_result/{i}_valuecounts.csv', index_label='value')
bigtable.to_csv('../history/describe_result/bigtable.csv', index=False)
