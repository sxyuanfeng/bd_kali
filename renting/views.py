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

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.weibo

def get_country_city_renting(request):
    all_city_renting = db.zufang.find({}, {'city', 'total'})
    city_list = []
    total_list = []
    for i in all_city_renting:
        city_list.append(i['city'])
        total_list.append(i['total'])
    c = (
        Map(init_opts=opts.InitOpts(width="1000px", height="580px"))
            .add("城市", [list(z) for z in zip(city_list, total_list)], "china-cities", is_roam=False,
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

def get_renting_wordcloud(request):
    renting_list = db.zufang.find_one({"city": request.GET['city']}, {"info_list"})
    renting_list_df = pd.DataFrame(renting_list['info_list'])
    word = ''.join(list(renting_list_df['text']))
    word = re.sub("[A-Za-z0-9\!\%\[\]\,\。\<\>\#\@\&\/\-\=\"\:\?\'\;\.\➕\_\～\，\·\！\）\（\？\{\}\【\】\°\(\)]", "的", word)
    words = jieba.cut(word)
    word_list = []
    for word in words:
        word_list.append(word)
    word_list_df = pd.DataFrame({'word': word_list})
    stopwords = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/stopword.txt'), index_col=False, quoting=3, sep='，', names=['stopword'],
                                encoding="utf-8")
    word_list_df = word_list_df[~word_list_df['word'].isin(stopwords.stopword)]
    wordcloud_list = []
    word_serise = word_list_df['word'].value_counts()
    for index in word_serise.index:
        wordcloud_list.append({'name': index, 'value': int(word_serise[index])})
    return HttpResponse(json.dumps({'Code': 1, 'Data': wordcloud_list}))

def get_renting_hunting_list(request):
    renting_hunting_list = db.zufang.find_one({"city": request.GET['city']}, {"info_list"})
    renting_hunting_list_df = pd.DataFrame(renting_hunting_list['info_list'])
    hunting_list = []
    for index, row in renting_hunting_list_df.iterrows():
        if row['pics'] == None:
            pics = []
        else:
            pics = []
            for item in row['pics']:
                pics.append(item['url'])
        hunting_list.append({
            'avatar': row['user_avatar'],
            'name': row['user_name'],
            'profile': row['user_profile_url'],
            'rank': row['user_urank'],
            'time': row['latest_update'],
            'text': row['text'],
            'pics': pics,
            'scheme': row['scheme']
        })
    return HttpResponse(json.dumps({'Code': 1, 'Data': hunting_list}))


def get_renting_out_list(request):
    renting_out_list = db.zufang.find_one({"city": request.GET['city']}, {"info_list"})
    renting_out_list_df = pd.DataFrame(renting_out_list['info_list'])
    out_list = []
    for index, row in renting_out_list_df.iterrows():
        if row['pics'] == None:
            pics = []
        else:
            pics = []
            for item in row['pics']:
                pics.append(item['url'])
        out_list.append({
            'avatar': row['user_avatar'],
            'name': row['user_name'],
            'profile': row['user_profile_url'],
            'rank': row['user_urank'],
            'time': row['latest_update'],
            'text': row['text'],
            'pics': pics,
            'scheme': row['scheme']
        })
    return HttpResponse(json.dumps({'Code': 1, 'Data': out_list}))


