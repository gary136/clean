import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import requests
from bs4 import BeautifulSoup
import time
from pandas import Series
import os
import re

os.chdir('C:\\Python\\Python36-32\\examples\\house\\scrapData\\Taipei\\raw')

def transform(df):
    # part 1 cut not object
    def df_cutnotobject(df):
        print("去除非目標值前總數" + str(len(df)))
        df = df[df['地址'].isnull() != True]
        df = df[~df['類型'].str.contains('純車位')]
        df = df[~df['類型'].str.contains('純土地')]
        df.to_csv('house_temp.csv', index=False)
        df = pd.read_csv('house_temp.csv')
        df['地址'] = df['地址'].apply(lambda x: 'x' if len(x) <= 4 else x)
        df = df[df['地址'] != 'x']
        df.to_csv('house_temp.csv', index=False)
        df = pd.read_csv('house_temp.csv')
        print("去除非目標值後總數" + str(len(df)))
        return df
    df = df_cutnotobject(df)  
    print("part 1 finished")

    # part 2 deal special condition
    def df_simplifyKind(df):
        def spec(x):
            if '朋友' in x or '親' in x or '師生' in x or '債' in x or '祖' in x or '父' in x or '母' in x or '急' in x or '兄' in x or '弟' in x or '姐' in x or '妹' in x or '鄰居' in x or '特殊' in x or '繼承' in x:
                return '特殊關係間交易'
            elif '瑕疵' in x:
                return '瑕疵物件'
            elif '增建' in x or '頂' in x or '外推' in x or '陽台' in x or '加蓋' in x or '未登記' in x or '雨遮' in x:
                return '含增建或未登記建物'
            elif '承購' in x  or '公共' in x or '標購' in x:
                return '向政府機關承購/公共設施保留地之交易'
            elif '合建' in x:
                return '建商與地主合建案'
            elif '預售' in x:
                return '預售屋'
            elif '毛胚' in x or '毛坯' in x:
                return '毛胚屋'
            elif '徵收' in x:
                return '徵收地'
            elif '備註' in x:
                return '其他'
            return '無'
        df['特殊'] = df['特殊'].apply(spec)
        df.to_csv('house_temp.csv', index=False)
        df = pd.read_csv('house_temp.csv')
        return df
    df = df_simplifyKind(df)
    print("part 2 finished")

    # part 3 cleaning
    def df_clean(df):
        # time
        def time(x):
            y = x.split('年')[0]
            new_y = str(int(y) + 1911)
            x = new_y + '-' + x.split('年')[1]
            x = x.replace('月','-01')
            return x
        df['年月'] = df['年月'].apply(time)
        print("time done")
        # address
        df['地址'] = df['地址'].apply(lambda x: x.split('~')[0] + '號' if '~' in x else x)
        df['行政區'] = df['地址'].apply(lambda x:x[:3])
        df['地址'] = df['地址'].apply(lambda x:x[3:])
        print("address done")
        # price
        df['每坪單價'] = df['每坪單價'].apply(lambda x: x[2:] if '*' in x else x)
        def priceClean(x):
            if ')' in x:
                return x[:-12]
            elif '--' in x:
                return '000萬'
            else:
                return x
        df['每坪單價'] = df['每坪單價'].apply(priceClean)
        df['每坪單價'] = df['每坪單價'].apply(lambda x: int(float(x[:-1])*10000))
        print("price done")
        # car place / house area
        df['車位'] = df['建坪'].apply(lambda x: '含車位' if '含車位' in x else '無車位')
        df['類型'] = df['類型'].apply(lambda x: x[:-4] if '含車位' in x else x)
        df['建坪'] = df['建坪'].apply(lambda x: x.split('(')[0][:-3] if '含車位' in x else x[:-1])
        df.drop('總價', axis = 1, inplace=True)
        print("car place / house area done")
        # neighbor
        df['社區'] = df['格局'].apply(lambda x: '有社區' if '社區' in x else '無社區')
        df.drop('格局', axis = 1, inplace=True)
        print("neighbor done")
        # house age / land area
        df['屋齡'] = df['屋齡'].apply(lambda x: x[:-1])
        df['地坪'] = df['地坪'].apply(lambda x: x[:-1])
        print("house age / land area  done")
        # floor
        df['所在樓層'] = df['樓層'].apply(lambda x: x.split(' /')[0])
        df['總樓層'] = df['樓層'].apply(lambda x: x.split('共')[1][:-1])
        df.drop('樓層', axis = 1, inplace=True)
        print("floor done")
        df.to_csv('house_temp.csv', index=False)
        df = pd.read_csv('house_temp.csv')
        return df
    df = df_clean(df)
    print("part 3 finished")

    # part 4 cutoutliners
    def df_cutoutliners(df):
        print("去除極端值前總數" + str(len(df)))
        df = df[df['每坪單價'] < df['每坪單價'].mean() + df['每坪單價'].std() * 3]
        print("去除高極端值後總數" + str(len(df)))
        df = df[df['每坪單價'] > df['每坪單價'].mean() - df['每坪單價'].std() * 2]
        print("去除低極端值後總數" + str(len(df)))
        df.to_csv('house_temp.csv', index=False)
        df = pd.read_csv('house_temp.csv')
        df_num = df[~df['屋齡'].str.contains('--')] 
        house_age_median = df_num['屋齡'].median()
        df['屋齡'] = df['屋齡'].apply(lambda x: house_age_median if '--' in x else float(x))
        df['建坪'] = df['建坪'].apply(lambda x: float(x))
        df['地坪'] = df['地坪'].apply(lambda x: float(x))
        df['所在樓層'] = df['所在樓層'].apply(lambda x: int(x))
        df['總樓層'] = df['總樓層'].apply(lambda x: int(x))
        def age(x):
            if x <= 5:
                return '5年以下'
            elif x > 5 and x <= 10:
                return '5~10年'
            elif x > 10 and x <= 15:
                return '10~15年'
            elif x > 15 and x <= 20:
                return '15~20年'
            elif x > 20 and x <= 25:
                return '20~25年'
            elif x > 25 and x <= 30:
                return '25~30年'
            elif x > 30 and x <= 35:
                return '30~35年'
            elif x > 35 and x <= 40:
                return '35~40年'
            elif x > 40:
                return '40年以上'
        df['屋齡'] = df['屋齡'].apply(age)
        def kind(x):   
            if '店面' in x:
                return '店面(店鋪)'
            if x.startswith('透天厝'):
                return '透天厝'
            if x.startswith('華廈'):
                return '華廈'
            if x.startswith('無電梯公寓'):
                return '無電梯公寓'
            if x.startswith('電梯大樓'):
                return '電梯大樓'
            if x.startswith('多層樓組合'):
                return '多層樓組合'
        df['類型'] = df['類型'].apply(kind)
        df = df[['年月', '行政區', '地址', '類型', '每坪單價', '屋齡', '特殊', '建坪', '地坪', '車位', '社區', '所在樓層', '總樓層']]
        df.columns = ['dealTime', 'district', 'address', 'houseType', 'unitPrice', 
                  'houseAge', 'special', 'housearea', 'landArea', 'carPlace', 'neighbor', 'floor', 'floorSum']
        df.to_csv('house_temp.csv', index=False)
        df = pd.read_csv('house_temp.csv')
        return df
    df = df_cutoutliners(df)
    print("part 4 finished")
    return df

if __name__ == '__main__':
    os.chdir('C:\\Python\\Python36-32\\examples\\house\\scrapData\\Taipei\\raw')
    data = []
    for root, dirs, files in os.walk(".", topdown=False):
        for name in files:
    #         print(os.path.join(root, name))
    #         fullname = os.path.join(root, name)
    #         data.append(fullname)
            data.append(name)
    if not os.path.exists('.\\cleaned'):
        os.makedirs('.\\cleaned')        
    for name in data:
        print(name)
        new_name = name.split('.')[0]+'_transformed.'+name.split('.')[1]
        path = os.path.join('.\\cleaned', new_name)
        df = pd.read_csv(name)
        df = transform(df)
        df.to_csv(path, index=False)