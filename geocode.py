# part 5 geocode
import pandas as pd
import numpy as np
import requests
import time
from bs4 import BeautifulSoup


key1 = 'AIzaSyC_vcarGfMvLtfT9Hzgn1Q8ZgUbShHDSjk'
key2 = 'AIzaSyBQlgzxJoj-bFlT1HkIY6rAYeTFrT_YcSE'
key3 = 'AIzaSyArwew-mKF3WtQ_TSOvCTJl-2PfSatDvaQ'
key4 = 'AIzaSyBnoc6s57rpUmrzXyGkeXvjteWKhXL8VKI'
key5 = 'AIzaSyDDUiVULyAhtJ_RJSyP3TUOTk_fK9ir6YI'
key6 = 'AIzaSyD5X8K0uC3aLMuJ6crbbc0djiyEIWJb9kk'
key7 = 'AIzaSyCO0xnAgE7AT1a6c29A_PZWDsQl_yXIlI8'
key8 = 'AIzaSyCoF0hPC9XSwprvJ7QTn9sRsnNceo9j-tE'

key_list = [key1, key2, key3, key4, key5, key6, key7, key8]

# open the file
def open_house_temp():
    global forname
    forname = input("請輸入檔名 ")
    fullname = forname + '.csv'
    df = pd.read_csv(fullname)
    return df
df = open_house_temp()

# transform
def geoc(df):
    df['lan'] = pd.Series(np.zeros(len(df)), index=df.index)
    df['long'] = pd.Series(np.zeros(len(df)), index=df.index)
    df['vil'] = pd.Series(np.zeros(len(df)), index=df.index)
    total = 0
    key_num1 = input("keyFirst ")
    key_num2 = input("keySecond ")
    for i in range(len(df)):
        print(i)
        total+=1
        addr = df['Address'][i]
        url = 'https://maps.googleapis.com/maps/api/geocode/xml?address=' + addr + '&key=' + key_list[int(key_num1)]
        r = requests.get(url)
        content = r.content
        bsobj = BeautifulSoup(content, 'html.parser')
        status = bsobj.find('status').get_text()
        if status == 'OVER_QUERY_LIMIT':
            print('need to change key, the current number = ' + str(i))
            df.to_csv('house_temp.csv', index=False)
            break
        elif status == 'OK':
            lan = bsobj.find_all('lat')[0].get_text()    
            long = bsobj.find_all('lng')[0].get_text()
        else:
            print('address is not vlaid')
            lan = 0
            long = 0
        df['lan'][i] = lan
        df['long'][i] = long
        print('緯度為: ' + str(lan))
        print('經度為: ' + str(long))
        
        time.sleep(1)
        
        t_url = 'https://maps.googleapis.com/maps/api/geocode/xml?latlng=' + lan + ',' + long + '&key=' + key_list[int(key_num2)]
        r = requests.get(t_url)
        content = r.content
        bsobj = BeautifulSoup(content, 'html.parser')
        if status == 'OVER_QUERY_LIMIT':
            print('need to change key, the current number = ' + str(i))
            df.to_csv('house_temp.csv', index=False)
            break
        elif status == 'OK':
            vil = bsobj.find(text='administrative_area_level_4').parent.parent.long_name.get_text()
        else:
            vil = 0
        df['vil'][i] = vil
        print('里名為: ' + str(vil))    
        
        if total == 300:
            df.to_csv('house_temp.csv', index=False)
            total = 0
            print('==============================')
#     df['geo'] = pd.Series(np.zeros(len(df)), index=df.index)
#     for i in range(len(df)):
#         df['geo'][i] = int(str(int(df['lan'][i]*100)) + str(int(df['long'][i]*100)))
    return df
df = geoc(df)

def save_house_temp():
    df.to_csv(forname + '_done.csv', index=False)
save_house_temp()