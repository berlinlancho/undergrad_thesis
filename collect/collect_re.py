import csv
import random
import time
import requests
from get_header import get_header
import pandas as pd
import json
import pprint

dirr = '../history/2023-02-23 1523--2023-02-23-2255/'
df = pd.read_csv(dirr+'video.csv')
aid = df['video_aid'].values.tolist()
df.index = df['video_aid']
df = df[~df.index.duplicated()]
length = len(aid)
fv = open(dirr+'video_recollect.csv', 'w', encoding='utf-8', newline='')
c_video = csv.DictWriter(fv, fieldnames=[
    '爬取时间',
    'video_aid','标题','up_name', 'up_id',
    '硬币数', '弹幕数', '点踩数', '收藏数',
    '点赞数', '评论数', '分享数', '播放数'
])
c_video.writeheader()

# 2023-02-16 0853--2023-02-16 0244  改0952  cookie失效
for i in range(250,length):
    # time.sleep(random.random())
    crawtime = df.loc[aid[i]]['爬取时间']
    ontime = time.time()- crawtime
    while ontime < 60*60*24:
        print(f'\r{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(crawtime))}'
              f' {aid[i]}  还差{60*60*24-ontime}秒',end='')
        time.sleep(1)
        ontime = time.time() - df.loc[aid[i]]['爬取时间']
    print(f'{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(df.loc[aid[i]]["爬取时间"]))}  '
          f'\r{aid[i]} 开始爬取',end='')
    url = f"https://api.bilibili.com/x/web-interface/view?aid={aid[i]}"
    video = {}
    v_data = None
    data = None
    try:
        response = requests.get(url, headers=get_header())
        data = json.loads(response.text)
        v_data = data['data']
        video['爬取时间'] = time.time()
        video['标题'] = v_data['title']
        video['video_aid'] = aid[i]
        video['up_name'] = v_data['owner']['name']
        video['up_id'] = v_data['owner']['mid']
        video['硬币数'] = v_data['stat']['coin']
        video['弹幕数'] = v_data['stat']['danmaku']
        video['点踩数'] = v_data['stat']['dislike']
        video['收藏数'] = v_data['stat']['favorite']
        video['点赞数'] = v_data['stat']['like']
        video['评论数'] = v_data['stat']['reply']
        video['分享数'] = v_data['stat']['share']
        video['播放数'] = v_data['stat']['view']
    except:
        print(df[df['video_aid']==aid[i]].values.tolist())
        pprint.pprint(data)
        continue

    c_video.writerow(video)
    print('结束', end='')
    time.sleep(0.11)

fv.close()