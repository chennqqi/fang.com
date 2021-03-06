# -*- coding:utf-8 -*-

import urllib
import re
import pandas as pd
from time import ctime, sleep
import json, pymysql
import traceback




def sqldb(city):
    con = pymysql.connect(host='********', port=****, user="s*****", passwd="******", db="******",
                          charset='utf8')
    df1 = pd.read_sql('SELECT id,位置,经纬度 FROM %s'%city, con)#,index_col = 'id')
    con.close()
    get_api(df1,key_list)



def get_api(a,key_list):
    change_info = 0
    rep = {}
    key_num = 0
    data_info = []
    for q in range(len(a)):
        print(rep)
        id = a.iloc[q,0]
        local = a.iloc[q,1]
        local_data = a.iloc[q,2]
        #print(id,local,local_data)
        if local_data == '无数据' or local_data == 'OVER_QUERY_LIMIT':
            if local in rep:
                data_info.append([id,rep['%s' % local][0]])
            else:
                sleep(1)
                local = local.strip(' ')
                key = key_list[key_num]
                url = 'https://maps.googleapis.com/maps/api/geocode/json?address=%s&key=%s'%(local,key)
                url1 = urllib.request.quote(url,safe=':/&?=')
                print('已经更改%s条数据  '%change_info,url)
                sleep(0.5)
                req = urllib.request.Request(url1)
                req.add_header('User-Agent','Mozilla/5.0 (iPhone; CPU iPhone OS 9_1 like Mac OS X) AppleWebKit/601.1.46 (KHTML, like Gecko) Version/9.0 Mobile/13B143 Safari/601.1')
                try:
                    data = urllib.request.urlopen(url1).read().decode('utf-8')
                except Exception as e:
                    print('正在睡眠3s')
                    print(traceback.format_exc())
                    sleep(3)
                    try:
                        data = urllib.request.urlopen(url1).read().decode('utf-8')
                    except Exception as e:
                        print('第二次睡眠')
                        sleep(3)
                        data = urllib.request.urlopen(url1).read().decode('utf-8')
                hjson = json.loads(data)
                state = hjson["status"]
                if state == 'OK':
                    rep['%s' % local] = []
                    info = hjson["results"][-1]['geometry']['location']
                    address = str(info['lat'])+','+str(info['lng'])
                    data_info.append([id, address])
                    change_info += 1
                    rep['%s' % local].append(address)
                elif state == 'OVER_QUERY_LIMIT':
                    truelen = len(key_list) - 1
                    if key_num == truelen:
                        print('key已用完')
                        break
                    else:
                        key_num += 1
                        print('正在使用第%s个key：%s' % (key_num,key_list[key_num]))
                else:
                    rep['%s' % local] = []
                    data_info.append([id, str(state)])
                    change_info += 1
                    rep['%s' % local].append(state)
                if data_info:
                    print(data_info[-1])
        else:
            pass

        if len(data_info)>=500:
            post(data_info)
            data_info=[]
            print(rep)
        #print(data_info)
    if data_info:
        post(data_info)


def replace(data_info,rep):#当keys用尽时，遍历数据，替换rep中所有数据
    post(data_info)

    pass
def post(data_info):
    print('正在输入到MySQL')
    d = str(data_info).replace('[', '(').replace(']', ')').replace('((', '(').replace('))', ')')
    con = pymysql.connect(host='***********', port=****, user="***********, passwd="***********", db="****", charset='utf8')
    cur = con.cursor()
    sql = 'insert into %s (id,经纬度) values %s on duplicate key update id=values(id),经纬度=values(经纬度)' % (city, d)
    cur.execute(sql)
    cur.close()
    con.commit()
    con.close()


if __name__ == '__main__':
    key_list = [{YOUR KEY}]
    city = '深圳'
    sqldb(city)
