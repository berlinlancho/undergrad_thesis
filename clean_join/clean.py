from datetime import datetime

import numpy as np
import pandas as pd
import time
def getdanmu(dirr,id):
    return pd.read_csv(dirr+f'danmu/{id}.csv')
def getreply(dirr,id):
    a = pd.DataFrame()
    try:
        a = pd.read_csv(dirr+f'reply/{id}.csv')
    except:
        print(f'{id} 获取错误')
    return a

def clean(d):
    # 读取文件
    dirr = f'../history/{d}/'
    big_table = pd.read_csv(dirr+'video.csv',index_col='video_aid')
    df_video = pd.read_csv(dirr+'video.csv')
    df_video.index = df_video['video_aid']
    df_video_re = pd.read_csv(dirr+'video_recollect.csv',index_col='video_aid')
    df_tags = pd.read_csv(dirr+'tags.csv',index_col='tag_id')
    df_up = pd.read_csv(dirr+'up.csv',index_col='mid')
    # 整理 big_table
    for cname in ['up_id', 'up_name', '简介', '标签分区id', '使用标签', '使用标签id',
           '点踩数', '跳转链接', '跳转app', '链接文本']:
        del big_table[cname]

    # 2023-02-16 9点52分前的数据因为cookie失效而没有及时爬到准确24小时后的
    a = 1
    if a == 0:
        t = '2023-2-16 09:52:00'
        s_t = time.strptime(t, "%Y-%m-%d %H:%M:%S")  # 返回元祖
        mkt = int(time.mktime(s_t))
        df_video = df_video[df_video['爬取时间'] > mkt]

    # 去除重复值
    big_table = big_table[~big_table.index.duplicated()]
    df_video = df_video[~df_video.index.duplicated()]
    df_video_re = df_video_re[~df_video_re.index.duplicated()]

    # 连接24小时后的数据
    # 有重复行拼接不了
    df_video_re.columns = 'beh_' + df_video_re.columns
    big_table = pd.concat([big_table,df_video_re[[ 'beh_硬币数', 'beh_弹幕数',
                                                  'beh_点踩数','beh_收藏数','beh_点赞数',
                                                  'beh_评论数','beh_分享数','beh_播放数']]], axis='columns')

    # 连接up数据
    up_join = pd.merge(df_video,df_up,left_on='up_id',right_on='mid',how='inner')
    up_join.index = up_join['video_aid']
    big_table['up等级'] = up_join['level']
    big_table['up粉丝数'] = up_join['up粉丝数']
    big_table['up投稿数'] = up_join['up投稿数']
    big_table['up平均每个视频播放量'] = up_join['up总播放量']/up_join['up投稿数']
    big_table['up平均每个视频点赞数'] = up_join['up总点赞数']/up_join['up投稿数']

    # 视频基本信息处理
    # 审核时长极短
    # check_time = df_video['审核时间']- df_video['上传时间']
    # check_time[check_time > 0]

    # 有无简介
    df_video['简介'][df_video['简介'].isnull()] = '-'
    df_video['有无简介'] = ~(df_video['简介'].map(len)==1)*1

    # 标题样式
    df_video['标题样式'] = '。'

    df_video['标题样式'][df_video['标题'].str.contains('！')] = '！'
    df_video['标题样式'][df_video['标题'].str.contains('？')] = '？'

    # 跳转链接
    df_video['有无广告'] = 0

    # 已存留时长
    df_video['存留时长'] = (df_video['爬取时间'] - df_video['上传时间'])/(24*60*60)

    cdt = (df_video['跳转链接']!='无')&(df_video['跳转链接'].str.contains('http'))&\
    (df_video['链接文本'].str.contains(r'[京东|淘宝|拼多多]'))|\
    (df_video['跳转app']!='无')&df_video['跳转app'].notnull()
    df_video['有无广告'][cdt] = 1

    #赋值给big_table
    big_table['有无简介'] = df_video['有无简介']
    big_table['标题样式'] = df_video['标题样式']
    big_table['有无广告'] = df_video['有无广告']
    big_table['存留时长'] =  df_video['存留时长']

    # 标签处理
    tag_aver_atten = {} # 平均意义上每一个使用该标签的视频获得的关注量
    for i,idd in enumerate(df_video.sort_values(by='播放数').index):
        tag_ids = df_video['使用标签id'].loc[idd].split(';')
        tag_ids = list(map(int,tag_ids))
        try:
            tags = df_tags.loc[tag_ids]
        except:
            tag_aver_atten[idd] = np.nan
            continue
        average_atten = tags['订阅数']
        # 取其中最大的那一个
        tag_aver_atten[idd] = average_atten.sum()/df_video['标签个数'][idd]
    big_table['平均标签订阅数'] = pd.Series(tag_aver_atten)

    # 评论分析
    up_reply_rate = {}  # up在最热前500条评论的回复率
    up_like_rate = {}  # up 在最热前500条评论的点赞率
    average_reply = {}  # 最热前500条评论中平均每条评论的回复数
    average_like = {}  # 最热前500条评论中平均每条评论的点赞数
    for i, idd in enumerate(df_video['video_aid']):
        try:
            r = getreply(dirr,idd)
        except:
            continue
        if len(r) == 0:
            up_reply_rate[idd] = 0
            up_like_rate[idd] = 0
            average_reply[idd] = 0
            average_like[idd] = 0
            continue
        # 去除错误记录
        cdt = r['up是否回复'] == 'up是否回复'
        r.drop(r.index[cdt], inplace=True, axis='index')
        # 转换类型
        r = r.astype({'上传时间': int, '回复数': int, '点赞数': int})

        # 计算回复率和点赞率
        rate_data = r['up是否回复']
        rate_data = rate_data.map({True: 1, False: 0})
        up_reply_rate[idd] = rate_data.sum()
        rate_data = r['up是否点赞']
        rate_data = rate_data.map({True: 1, False: 0})
        up_like_rate[idd] = rate_data.sum()

        # 计算平均回复与平均点赞
        average_reply[idd] = r['回复数'].sum() / len(r)
        average_like[idd] = r['点赞数'].sum() / len(r)
    big_table['up在最热前500条评论的回复数'] = pd.Series(up_reply_rate)
    big_table['up在最热前500条评论的点赞数'] = pd.Series(up_like_rate)
    big_table['最热前500条评论中平均每条评论的回复数'] = pd.Series(average_reply)
    big_table['最热前500条评论中平均每条评论的点赞数'] = pd.Series(average_like)

    # 把分类变量转换为虚拟变量
    # bigtable中的分类变量  是否原创，是否合作，有无简介，有无广告，弹幕模式,标题样式
    # binary = ['是否原创', '是否合作', '有无简介', '有无广告', '标题样式']
    # for aname in binary:
    #     dummies = pd.get_dummies(big_table[aname], prefix=aname)
    #     dum_name = dummies.columns.values.tolist()
    #     big_table = big_table.join(dummies[dum_name])

    big_table.dropna().to_csv('../history/all/' + f'{d}.csv')




if __name__ == '__main__':
    # 2023-02-16 0853-- 2023-02-16 1526
    # 2023-02-15 2330--2023-02-16 0244
    # 2023-02-15 1528--2023-02-15 1834
    # 2023-02-23 0809--2023-02-23 1227
    clean('2023-02-23 0809--2023-02-23 1227')