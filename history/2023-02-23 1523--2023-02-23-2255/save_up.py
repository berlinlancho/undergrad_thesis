import pandas as pd
import requests
import json
import time
import random
up = pd.read_csv('up.csv')
up.index = up['mid']
up_name = {}
up_sex = {}
up_level = {}
up_sign = {}
for flag,mid in zip(up['name'].notnull(),up.index):
    if flag:
        up_name[mid] = up['name'][mid]
        up_sex[mid] = up['sex'][mid]
        up_level[mid] = up['level'][mid]
        up_sign[mid] = up['sign'][mid]
        continue
    url = f'https://api.bilibili.com/x/space/acc/info?mid={mid}'
    header = {
        'user-agent': 'Mozilla/5.0 (iPad; CPU OS 11_0 like Mac OS X) AppleWebKit/604.1.34 (KHTML, like Gecko) Version/11.0 Mobile/15A5341f Safari/604.1',
        'cookie' : "buvid3=9EFC8B56-9028-BBB1-877E-B6BD76009D7983729infoc; b_nut=1671844983; i-wanna-go-back=-1; _uuid=93775A44-1EC9-CE78-C10D9-B13102EF6642D84046infoc; buvid4=1ED29B0A-AD3D-5482-2F49-8869A44C3F2E84607-022122409-1QAaTsQbRARaiMnqBdpTfg%3D%3D; rpdid=|(k||lJlmukR0J'uY~u)Rl|lR; nostalgia_conf=-1; blackside_state=1; buvid_fp_plain=undefined; CURRENT_BLACKGAP=0; is-2022-channel=1; b_ut=5; CURRENT_QUALITY=112; LIVE_BUVID=AUTO8116757556919215; PVID=1; i-wanna-go-channel-back=2; hit-new-style-dyn=0; hit-dyn-v2=1; header_theme_version=CLOSE; DedeUserID=3461579714595323; DedeUserID__ckMd5=42ed1e374f580b6d; CURRENT_FNVAL=4048; fingerprint=ba3738446149ac218714e7800f183440; buvid_fp=ba3738446149ac218714e7800f183440; SESSDATA=94d946d2%2C1692630503%2C4092d%2A21; bili_jct=0af73cdfa5669b634c34752520845390; innersign=1; sid=8usc7f86; bp_video_offset_3461579714595323=765510906367967200; b_lsid=AE713D7D_1867C92508C"
    }
    response = requests.get(url, headers=header)
    data = json.loads(response.text)
    print(data)
    time.sleep(random.random() / 6)

    data_up_basic_info = data['data']
    up_name[mid] = data_up_basic_info['name']
    up_sex[mid] = data_up_basic_info['sex']
    up_level[mid] = data_up_basic_info['level']
    up_sign[mid] = data_up_basic_info['sign'].replace('\n', '。')
up['name'] = pd.Series(up_name)
up['sex'] = pd.Series(up_sex)
up['level'] = pd.Series(up_level)
up['sign'] = pd.Series(up_sign)
up.to_csv('up_.csv')