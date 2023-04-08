import pandas as pd
import numpy as np
import statsmodels.api as sm#实现了类似于二元中的统计模型，比如ols普通最小二乘法
import statsmodels.stats.api as sms#实现了统计工具，比如t检验、F检验...
import matplotlib as mpl
import matplotlib.pyplot as plt
import os

os.environ["OMP_NUM_THREADS"] = '1'
mpl.rcParams['font.sans-serif'] = ['KaiTi']
mpl.rcParams['font.serif'] = ['KaiTi']

bigtable = pd.read_csv('../history/describe_result/bigtable.csv')

y = bigtable.y.values
del bigtable['y']
# 'up在最热前500条评论的回复数','日均分享','日均评论_x2','日均收藏','日均硬币'
X = bigtable[['日均弹幕','日均点赞', '日均评论','最热前500条评论中平均每条评论的点赞数','存留时长',
              ]].values
X_model = sm.add_constant(X)#add_constant给矩阵加上一列常量1，主要目的：便于估计多元线性回归模型的截距，也是便于后面进行参数估计时的计算
model = sm.OLS(y, X_model)#调用OLS普通最小二乘
results = model.fit()#fit拟合，主要功能就是进行参数估计，参数估计的主要目的是估计出回归系数，根据参数估计结果来计算统计量，这些统计量主要的目的就是对我们模型的有效性或是显著性水平来进行验证
print(results.summary())#summary方法主要是为了显示拟合的结果
# s = results.summary().tables[1][1:]
# for i in s:
#     # if int(i[4]) < 0.1:
#     print(int(str(i[4])))
for i,name in enumerate(bigtable.columns):
    print(f'x{i+1}','  ',name)
