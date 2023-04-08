# 用于数值计算的库
import numpy as np
import pandas as pd
import scipy as sp
from scipy import stats
from statsmodels.stats.anova import anova_lm
from statsmodels.stats.stattools import durbin_watson
# 用于绘图的库
from pandas.plotting import lag_plot
from matplotlib import pyplot as plt
import matplotlib as mpl
import seaborn as sns
sns.set()
import os
os.environ["OMP_NUM_THREADS"] = '1'
mpl.rcParams['font.sans-serif'] = ['YouYuan']
mpl.rcParams['font.serif'] = ['YouYuan']
plt.rcParams['axes.unicode_minus'] = False
plt.rc('font', family='Youyuan', size='9')
# 用于估计统计模型的库（部分版本会报出警告信息）
import statsmodels.formula.api as smf
import statsmodels.api as sm
op = 1
bigtable = pd.read_csv('../history/describe_result/bigtable.csv')
# 改名
re_name = {
    '存留时长': '已发布天数', '日均评论': '历史日均评论增量', '日均点赞': '历史日均点赞增量',
    '日均硬币': '历史日均硬币增量', '日均弹幕': '历史日均弹幕增量', '日均收藏': '历史日均收藏增量',
    '日均分享': '历史日均分享增量', '日均播放': '历史日均播放增量',
    '最热前500条评论中平均每条评论的点赞数': '评论区平均点赞量',
    '最热前500条评论中平均每条评论的回复数': '评论区平均回复量',
    '平均标签订阅数': '平均视频标签订阅量', 'up粉丝数': 'up粉丝量', 'up投稿数': 'up投稿量',
    '播放时长': '视频时长', 'up在最热前500条评论的回复数': 'up主评论区回复量之和',
    'up在最热前500条评论的点赞数': 'up主评论区点赞量之和'
}
for i in re_name.keys():
    bigtable[re_name[i]] = bigtable[i]
    del bigtable[i]
# y_std = bigtable['y'].std()
# y_mean = bigtable['y'].mean()
# y_up = y_mean + 3*y_std
# y_d = y_mean - 3*y_std
# bigtable = bigtable[(bigtable.y > y_d)&(bigtable.y < y_up)]

def step():

    in_ = ['历史日均评论增量','历史日均点赞增量','历史日均硬币增量',
            '历史日均弹幕增量','历史日均收藏增量','历史日均分享增量',
            '历史日均播放增量','评论区平均点赞量','评论区平均回复量',
            '标题样式','up等级']
    last_aic_min = smf.ols('y~'+'+'.join(in_),data=bigtable).fit().aic
    aic_min = last_aic_min
    print(sorted(in_))
    d_aic = {}
    out_ = []

    while True:
        for i in range(len(in_)):
            x_out = in_[0]
            in_.remove(x_out)
            lm = smf.ols('y~'+'+'.join(in_),data=bigtable).fit()
            d_aic[(lm.aic,'-')] = x_out
            in_.append(x_out)
        for i in range(len(out_)):
            x_in = out_[i]
            in_.append(x_in)
            lm = smf.ols('y~'+'+'.join(in_),data=bigtable).fit()
            d_aic[(lm.aic,'+')] = x_in
            in_.remove(x_in)
        keys = list(d_aic.keys())
        aic_min = keys[0][0]
        tup_min = keys[0]
        print(d_aic)
        for tup in keys:
            if tup[0] < aic_min:
                aic_min = tup[0]
                tup_min = tup

        if tup_min[1] == '-':
            print('-',' ',d_aic[tup_min])
            in_.remove(d_aic[tup_min])
            out_.append(d_aic[tup_min])
        else:
            print('+', ' ', d_aic[tup_min])
            in_.append(d_aic[tup_min])
            out_.remove(d_aic[tup_min])
        print(sorted(in_),"min_aic:",aic_min)
        d_aic.clear()
        if aic_min>=last_aic_min:
            print('y~'+'+'.join(in_))
            print(smf.ols('y~'+'+'.join(in_),data=bigtable).fit().summary())
            break
        else:
            last_aic_min = aic_min


if op == 0:
    step()




print(bigtable['已发布天数'].min(),'  ',bigtable['已发布天数'].max())
l = ['标题样式','有无简介','up等级']
if op == 0:
    for i in range(3):
        plt.subplot(2,2,i+1)
        sns.boxplot(x = l[i],y = "y",
                    data = bigtable, color='gray')
        plt.ylabel('24小时后播放增量对数')
    plt.subplots_adjust(left=None, bottom=None, right=None, top=None, wspace=0.2, hspace=0.43)
    plt.show()
if op == 1:
    in_ = ['历史日均评论增量','历史日均点赞增量','历史日均硬币增量',
            '历史日均弹幕增量','历史日均收藏增量','历史日均分享增量',
            '历史日均播放增量','评论区平均点赞量','评论区平均回复量',
            '标题样式','up等级']
    lm_y = smf.ols("y~"+'+'.join(in_),
                   data = bigtable).fit()
    print(lm_y.summary())

    if op == 0:
        bigtable['re'] = lm_y.resid
        resid = bigtable.sort_values(by='存留时长')['re']
        print('自相关系数', sm.tsa.stattools.acf(resid, nlags=4, adjusted=True))
        print('dw', durbin_watson(resid))
        plt.figure(figsize=(8, 5))
        lag_plot(resid, lag=1)
        bigtable['re'] = (bigtable['re'] - bigtable['re'].mean()) / bigtable['re'].std()
        plt.figure(2)
        bigtable['re'].plot.density()
        plt.figure(3)
        plt.scatter(lm_y.fittedvalues, bigtable['re'])
        plt.show()

if op == 0:
    for i in l:
        lm = smf.ols(f'y~{i}',data = bigtable).fit()
        anova_model = anova_lm(lm)
        print(anova_model)
