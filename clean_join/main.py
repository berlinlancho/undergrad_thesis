import pandas as pd

from clean import clean
import os
source_path = '../history'
root, dirs, files = zip(*os.walk(source_path))
for i in dirs[0][:-2]:
    clean(i)


# 合并文件
root, dirs, files = zip(*os.walk('../history/all'))
df = pd.DataFrame()
for f in files[0]:
    df = pd.concat([df,pd.read_csv("../history/all/"+f,index_col='video_aid')],axis=0)
df[~df.index.duplicated()].to_csv('../history/bigtable')