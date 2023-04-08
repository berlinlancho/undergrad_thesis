import requests
import json
import pprint
import time
import random
from xml.dom.minidom import parseString
import csv
from get_header import get_header
from get_up_info import get_up_info
from threading import Thread


'''
https://api.bilibili.com/x/web-interface/view?aid=519207437
视频信息
https://api.bilibili.com/x/web-interface/wbi/index/top/feed/rcmd?ps=30
'''
'''
https://api.bilibili.com/x/web-interface/newlist?rid=157&type=0&pn=1&ps=20&jsonp=jsonp
rid是分区的编号
视频的维度： 
aid, bvid, cid(可以用于获取弹幕),
ctime,duration,
pub_location(上传地点), puddate(上传时间)，
title(标题)，desc(简介),
owner.mid(上传up主的id)，owner.name(上传up主昵称)

视频的度量：
view(播放量)，
danmaku(弹幕数),reply(评论数),
like,cion(硬币数),favorite(收藏),
share,
dislike,

视频的相关文本：
http://api.bilibili.com/x/tag/archive/tags?aid=302852807&jsonp=jsonp
视频标签(id 是 aid)

url = f'https://api.bilibili.com/x/v1/dm/list.so?oid={id}'
弹幕(id 是 cid)

url = f'https://api.bilibili.com/x/v2/reply/main?mode=3&next=0&oid=45382106&plat=1&seek_rpid=&type=1'
第一页评论(id 是 aid)

up主的相关信息(id 是 mid)
https://api.bilibili.com/x/space/acc/info?mid={}
mid(up主id),name(up主昵称),sex,sign,tags
https://api.bilibili.com/x/relation/stat?vmid={}&jsonp=jsonp
following(关注数),follower(粉丝数)
https://api.bilibili.com/x/space/upstat?mid={}&jsonp=jsonp
view(播放量),likes(点赞数)
https://api.bilibili.com/x/space/arc/search?mid={}&ps=30&tid=0&pn=1&keyword=&order=pubdate&jsonp=jsonp
data.list.tlist() (各个分区的投稿数)

'''

class Spi_bli_video:
    def __init__(self):
        self.upset = set()
        self.tagset = set()
        self.videoset = set()
        self.fv = open('../data/video.csv', 'w', encoding='utf-8', newline='')
        self.ft = open('../data/tags.csv', 'w', encoding='utf-8', newline='')
        self.fu = open('../data/up.csv', 'w', encoding='utf-8', newline='')
        self.csvwriter_video = csv.DictWriter(self.fv,fieldnames=[
                                                        '爬取时间',
                                                       'video_aid', 'video_cid',  'up_id',
                                                       '标题','up_name',
                                                       '上传时间','审核时间','播放时长',
                                                       '简介','标签分区','标签分区id',
                                                       '标签个数','使用标签','使用标签id',
                                                       '硬币数', '弹幕数', '点踩数', '收藏数','历史最高排名',
                                                       '点赞数', '评论数', '分享数', '播放数',
                                                       '是否原创','是否合作',
                                                       '跳转链接','跳转app','链接文本'
                                                    ])
        self.csvwriter_tags = csv.DictWriter(self.ft,fieldnames=['tag_id', '标签名','标签描述','订阅数','使用次数'])
        self.csvwriter_up = csv.DictWriter(self.fu,fieldnames=['mid', 'name', 'sex', 'level',
                                                            'up关注数', 'up粉丝数', 'up总播放量', 'up总点赞数',
                                                            'up投稿数', '投稿分区及其投稿数量', 'sign'])

        self.csvwriter_video.writeheader()
        self.csvwriter_tags.writeheader()
        self.csvwriter_up.writeheader()

    # 传入链接，放回json数据
    def get_json(self, url):
        response = requests.get(url,headers = get_header())
        data = json.loads(response.text)
        return data

    # 首先爬取分区视频的基本信息
    # 返回aid:爬评论和标签，返回cid:爬取弹幕，返回mid:爬取up主的信息
    def get_video_info(self,fresh):
        # url = f'''https://api.bilibili.com/x/web-interface/wbi/index/top/feed/rcmd?fresh_idx={fresh}&ps=20'''
        url = f'https://api.bilibili.com/x/web-interface/newlist?rid=209&type=0&pn={fresh}&ps=20&jsonp=jsonp'
        video = {}
        data = self.get_json(url)
        num = 0
        # url2: archives url1 : item
        for each_video in data['data']['archives']:
            num += 1
            print(time.strftime("%Y-%m-%d %H:%M:%S", time.localtime()),' ',num,each_video['title'])
            aid = each_video['aid']
            cid = each_video['cid']
            mid = each_video['owner']['mid']
            if aid in self.videoset:
                print('重复视频取消爬取')
                continue
            else:
                self.videoset.add(aid)
            video['video_aid'] = aid
            video['video_cid'] = cid
            video['up_id'] = mid
            video['爬取时间'] = int(time.time())
            # 视频基本信息
            print('视频基本信息',end=' ')
            url = f"https://api.bilibili.com/x/web-interface/view?aid={aid}"
            data = self.get_json(url)
            v_data = data['data']
            if v_data['duration'] < 60 or v_data['duration'] > 1800:
                print(' 短视频取消爬取')
                continue
            video['标题'] = v_data['title']
            video['up_name'] = v_data['owner']['name']
            video['上传时间'] = v_data['pubdate']
            print(time.strftime("%Y-%m-%d %H:%M:%S",time.localtime(video['上传时间'])),end='  ')
            video['审核时间'] = v_data['ctime']
            video['播放时长'] = v_data['duration']
            video['简介'] = v_data['desc']
            video['标签分区'] = v_data['tname']
            video['标签分区id'] = v_data['tid']
            video['硬币数'] = v_data['stat']['coin']
            video['弹幕数'] = v_data['stat']['danmaku']
            video['点踩数'] = v_data['stat']['dislike']
            video['收藏数'] = v_data['stat']['favorite']
            video['历史最高排名'] = v_data['stat']['his_rank']
            video['点赞数'] = v_data['stat']['like']
            video['评论数'] = v_data['stat']['reply']
            video['分享数'] = v_data['stat']['share']
            video['播放数'] = v_data['stat']['view']
            video['是否原创'] = v_data['copyright']
            video['是否合作'] = v_data['rights']['is_cooperation']

            # 视频up主信息
            print('up信息', end=' ')
            if mid not in self.upset:
                up = get_up_info(mid)
                if up == 0:
                    continue
                self.upset.add(mid)
                self.csvwriter_up.writerow(up)


            # 视频标签
            print('视频标签信息', end=' ')
            url = f'http://api.bilibili.com/x/tag/archive/tags?aid={aid}'
            data = self.get_json(url)
            video['标签个数'] = len(data['data'])
            tag_name = []
            tag_id = []

            for t in data['data']:
                tag_id.append(str(t['tag_id']))
                tag_name.append(t['tag_name'])
                if t['tag_id'] not in self.tagset:
                    tag = {}
                    self.tagset.add(t['tag_id'])
                    tag['标签名'] = t['tag_name']
                    tag['tag_id'] = t['tag_id']
                    tag['标签描述'] = t['content']
                    tag['订阅数'] = t['count']['atten']
                    tag['使用次数'] = t['count']['use']
                    self.csvwriter_tags.writerow(tag)
            video['使用标签'] = ';'.join(tag_name)
            video['使用标签id'] = ';'.join(tag_id)

            dm = open(f'../data/danmu/{cid}.csv', 'w', encoding='utf-8', newline='')
            rp = open(f'../data/reply/{aid}.csv', 'w', encoding='utf-8', newline='')
            csv_danmu = csv.DictWriter(dm, fieldnames=['发送时间', '视频内弹幕出现时间', '弹幕文本'])
            csv_reply = csv.DictWriter(rp, fieldnames=['上传时间', '回复数', '点赞数',
                                                       'up是否回复', 'up是否点赞', '评论文本'])
            csv_danmu.writeheader()
            csv_reply.writeheader()
            # 弹幕和评论
            try:
                # 视频弹幕  当视频的弹幕量比较少的时候还是可以获取所有弹幕的
                print('弹幕信息', end=' ')
                url = f'https://api.bilibili.com/x/v1/dm/list.so?oid={cid}'
                response = requests.get(url)
                # 这里解决了乱码的问题
                doc = parseString(response.content.decode('utf-8'))
                collection = doc.documentElement
                for i in collection.getElementsByTagName("d"):
                    danmu = {}
                    danmu['弹幕文本'] = i.childNodes[0].data
                    atrribute = i.getAttribute('p').split(',')
                    danmu['视频内弹幕出现时间'] = atrribute[0]
                    danmu['发送时间'] = atrribute[4]
                    csv_danmu.writerow(danmu)

                # 视频评论
                print('评论信息', end=' ')

                for i in range(1,26):
                    print(i,end=' ')
                    time.sleep(random.random()/3)
                    url = f'https://api.bilibili.com/x/v2/reply/main?mode=3&next={i}&oid={aid}&plat=1&seek_rpid=&type=1'
                    data = self.get_json(url)
                    replies = data['data']['replies']
                    if i == 1:
                        try:
                            top_jump = data['data']['top']['upper']['content']['jump_url']
                            first_url = list(top_jump.keys())[0]
                            video['跳转链接'] = first_url
                            video['跳转app'] = top_jump[first_url]['app_name']
                            video['链接文本'] = top_jump[first_url]['title']
                        except:
                            video['跳转链接'] = '无'
                            video['跳转app'] = '无'
                            video['链接文本'] = '无'
                        finally: self.csvwriter_video.writerow(video)
                    if replies == []:break
                    for reply in replies:
                        r = {}
                        r['评论文本'] = reply['content']['message'] # 回复内容
                        r['up是否点赞'] = reply['up_action']['like'] # up是否点赞
                        r['up是否回复'] = reply['up_action']['reply'] # up是否回复
                        r['点赞数'] = reply['like'] # 该评论点赞数
                        r['回复数'] = reply['count'] # 该评论回复数
                        r['上传时间'] = reply['ctime'] # 上传时间
                        csv_reply.writerow(r)
            except Exception as e:
                dm.close()
                rp.close()
                with open("out_danmu_reply.txt", 'a') as f:
                    f.write(f'\n{time.strftime("%Y-%m-%d %H:%M:%S", time.localtime())}爬取文本异常{url}\n')
                print(e)
                for i in range(300):
                    time.sleep(random.random())
                    print(i,end=' ')
                continue
            print()

    def f_close(self):
        self.ft.close()
        self.fu.close()
        self.fv.close()



if __name__ == '__main__':
    spiv = Spi_bli_video()
    t = time.time()
    # 5 15 25
    for i in range(1,10000):
        if ((time.time() - t) // 60 ) > 600:
            print('正常退出')
            break
        print(f'********************************第{i}页 已经爬取了{(time.time() - t) // 60}分钟*****************************')
        try:
            spiv.get_video_info(i+1)
        except Exception as e:
            print(f'{i}页爬取失败')
            print(e)
            for i in range(600):
                time.sleep(random.random())
                print(i,end=' ')
            continue
    spiv.f_close()

