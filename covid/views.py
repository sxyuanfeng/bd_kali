from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import pymongo
import json
from pyecharts.charts import Map
from pyecharts import options as opts
import jieba
import re
import os
from datetime import datetime

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.weibo

country_chinese_english = {}
country_ce = pd.read_excel('country_ce.xls')
for index, row in country_ce.iterrows():
    country_chinese_english.update({row['中文名称']: row['英文名称']})


def get_covid_timeline(request):
    all_covid = db.covid_19.find({}, {'created_at'})
    all_time = []
    for item in all_covid:
        time_item_list = item['created_at'].split(' ')
        new_time_item_list = [time_item_list[0], time_item_list[1], time_item_list[2], time_item_list[3], time_item_list[5]]
        new_time_item = ' '.join(new_time_item_list)
        all_time.append(datetime.strptime(new_time_item, '%c').strftime('%Y-%m-%d'))
    data = pd.DataFrame({'time': all_time})
    time_serise = data['time'].value_counts()
    time_list = []
    for i in time_serise.index:
        time_list.append({'time': str(i), 'value': int(time_serise[i])})
    return HttpResponse(json.dumps({'Code': 1, 'Data': time_list}))

def get_covid_active_user(request):
    all_covid = db.covid_19.find({}, {'name'})
    all_user = []
    for item in all_covid:
        all_user.append(item['name'])
    data = pd.DataFrame({'name': all_user})
    name_serise = data['name'].value_counts()
    name_list = []
    index = 1
    for i in name_serise.index:
        if index < 21:
            name_list.append({'name': str(i), 'value': int(name_serise[i])})
            index += 1
    return HttpResponse(json.dumps({'Code': 1, 'Data': name_list}))

def get_covid_oversea_country(request):
    file = open("country.txt", encoding='UTF-8')
    country_list = []
    while 1:
        line = file.readline()
        if not line:
            break
        else:
            country_list.append(line.replace("\n", ""))
    file.close()
    all_covid = db.covid_oversea.find({}, {'text'}).limit(500)
    all_text = ''
    for item in all_covid:
        all_text = all_text + item['text']
    jieba.load_userdict('country.txt')
    all_text = re.sub("[A-Za-z0-9\!\%\[\]\,\。\<\>\#\@\&\/\-\=\"\:\?\'\;\.\➕\_\～\，\·\！\）\（\？\{\}\【\】\°\(\)]", "", all_text)
    words = jieba.cut(all_text)
    word_list = []
    for word in words:
        if word in country_list:
            word_list.append(word)
    data = pd.DataFrame({'country': word_list})
    country_serise = data['country'].value_counts()
    country_name_list = []
    country_value_list = []
    for i in country_serise.index:
        country_name_list.append(country_chinese_english[str(i)])
        country_value_list.append(int(country_serise[i]))

    c = (
        Map(init_opts=opts.InitOpts(width="1000px", height="580px"))
            .add("国家", [list(z) for z in zip(country_name_list, country_value_list)], "world", is_roam=False,
                 is_map_symbol_show=False)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
            title_opts=opts.TitleOpts(title=""),
            visualmap_opts=opts.VisualMapOpts(
                item_height=150,
                item_width=20,
                pos_left=100,
                pos_bottom=50
            ),
            legend_opts=opts.LegendOpts(
                is_show=False
            )
        )
    )

    return HttpResponse(json.dumps({'Code': 1, 'Data': c.render_embed()}))
