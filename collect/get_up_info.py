import random
import time
import json
import requests
from project.undergrad_thesis.collect.get_header import get_header
def get_json_up(url):
    response = requests.get(url,headers = get_header())
    data = json.loads(response.text)
    if data == None:
        print(url)
        print(data)
        raise Exception
    return data
def get_up_info(mid):
    up = {}
    up_basic_info = f'https://api.bilibili.com/x/space/acc/info?mid={mid}'
    data_up_basic_info = get_json_up(up_basic_info)
    time.sleep(random.random()/6)

    data_up_basic_info = data_up_basic_info['data']
    up['mid'] = mid
    up['name'] = data_up_basic_info['name']
    up['sex'] = data_up_basic_info['sex']
    up['level'] = data_up_basic_info['level']
    up['sign'] = data_up_basic_info['sign'].replace('\n', '。')


    up_follow_info = f'https://api.bilibili.com/x/relation/stat?vmid={mid}&jsonp=jsonp'
    data_up_follow_info = get_json_up(up_follow_info)
    time.sleep(random.random()/6)

    data_up_follow_info = data_up_follow_info['data']
    up['up关注数'] = data_up_follow_info['following']
    up['up粉丝数'] = data_up_follow_info['follower']
    if up['up粉丝数'] < 30000:
        print('up粉丝数小于10000取消爬取')
        time.sleep(1)
        return 0


    up_video_info = f'https://api.bilibili.com/x/space/upstat?mid={mid}&jsonp=jsonp'
    data_up_video_info = json.loads(requests.get(up_video_info,headers = get_header()).text)

    data_up_video_info = data_up_video_info['data']
    up['up总播放量'] = data_up_video_info['archive']['view']
    up['up总点赞数'] = data_up_video_info['likes']
    print(up['up总播放量'],'   ',up['up总点赞数'],'  ',end='')


    up_upload_info = f'https://api.bilibili.com/x/space/arc/search?mid={mid}&ps=30&tid=0&pn=1&keyword=&order=pubdate&jsonp=jsonp'
    data_up_upload_info = get_json_up(up_upload_info)
    try:
        data_up_upload_info = data_up_upload_info['data']
        data_tlist = data_up_upload_info['list']['tlist']
        counts = 0
        tlist = []
        for i in data_tlist:
            counts += data_tlist[i]['count']
            tlist.append(data_tlist[i]['name'] + ':' + str(data_tlist[i]['count']))
        up['投稿分区及其投稿数量'] = ';'.join(tlist)
        up['up投稿数'] = counts
    except Exception as t:
        up['投稿分区及其投稿数量'] = -1
        up['up投稿数'] = -1
        with open("out_up.txt", 'a') as f:
            f.write(f'\n{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}up投稿异常{up_upload_info}\n')
            f.write(str(t))
    return up
