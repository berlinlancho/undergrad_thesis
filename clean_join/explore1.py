import pandas as pd
import matplotlib as mpl
import matplotlib.pyplot as plt

mpl.rcParams['font.sans-serif'] = ['KaiTi']
mpl.rcParams['font.serif'] = ['KaiTi']
# 读取文件
roor_dir = '../history/第三次_177条/'
df_video = pd.read_csv(roor_dir+'video.csv')
df_video_re = pd.read_csv(roor_dir+'video_recollect.csv')
df_tags = pd.read_csv(roor_dir+'tags.csv')
df_up = pd.read_csv(roor_dir+'up.csv', index_col = 'mid')


def getdanmu(id):
    return pd.read_csv(roor_dir+f'danmu/{id}.csv')


def getreply(id):
    return pd.read_csv(roor_dir+f'reply/{id}.csv')


# 弹幕分析
for i, idd in enumerate(df_video[df_video['播放数'] < 1000000].sort_values(by='播放数')['video_cid']):
    if i % 3 != 0: continue
    plt.figure(i, figsize=(18, 6))
    plt.subplot(1, 3, 1)
    getdanmu(idd)['视频内弹幕出现时间'].plot.hist(bins=55)
    plt.figure(i)
    plt.subplot(1, 3, 2)
    getdanmu(idd)['视频内弹幕出现时间'].plot.density()
    plt.figure(i)
    plt.subplot(1, 3, 3)
    xydata = df_video[df_video['video_cid'] == idd][['播放数', '点赞数', '硬币数', '收藏数', '弹幕数', '评论数']].iloc[0]
    x, y = xydata.index, xydata.values
    rects = plt.bar(x, y, color='dodgerblue', width=0.35, label='label1')
    for rect in rects:  # rects 是三根柱子的集合
        height = rect.get_height()
        plt.text(rect.get_x() + rect.get_width() / 2, height, str(height), size=15, ha='center', va='bottom')
    plt.show()


