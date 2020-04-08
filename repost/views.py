from django.shortcuts import render
from django.http import HttpResponse
import os
import json
import pandas as pd
import pymongo
import jieba.analyse
from pyecharts.charts import Graph
from pyecharts import options as opts
import datetime

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.weibo

def get_symbolSize(follower_count):
    if follower_count < 100:
        return 5
    elif follower_count < 1000:
        return 10
    elif follower_count < 10000:
        return 15
    elif follower_count < 100000:
        return 20
    elif follower_count < 1000000:
        return 25
    elif follower_count < 10000000:
        return 30
    else:
        return 35


def get_repost_chart(request):
    if db.repost.find({"_id": int(request.GET['mid'])}).count() > 0:
        data = db.repost.find_one({"_id": int(request.GET['mid'])}, {"list"})
        author = db.repost.find_one({"_id": int(request.GET['mid'])}, {"author"})['author']
        reposts = db.repost.find_one({"_id": int(request.GET['mid'])}, {"reposts"})['reposts']
        followers = db.repost.find_one({"_id": int(request.GET['mid'])}, {"followers_count"})['followers_count']
        data = pd.DataFrame(data['list'])
        data = data.drop_duplicates(subset=['name'], keep='first')

        father = []
        for index, row in data.iterrows():
            if row['raw_text'].find('//@') >= 0:
                father.append(row['raw_text'][row['raw_text'].find('//@') + 3:][
                              :row['raw_text'][row['raw_text'].find('//@') + 3:].find(':')].replace(' ', ''))
            else:
                father.append(author)

        data['father'] = pd.DataFrame({'father': father})

        nodes = [{'name': author, 'category': author, 'value': reposts, 'symbolSize': get_symbolSize(followers)}]
        links = []
        category = []

        for index, row in data.iterrows():
            nodes.append({'name': row['name'], 'category': row['father'], 'value': row['reposts_count'],
                          'symbolSize': get_symbolSize(row['followers_count'])})
            links.append({'source': row['father'], 'target': row['name']})
            category.append(row['father'])

        category = set(category)
        category_set = []
        for i in category:
            category_set.append({'name': i})

        c = (
            Graph()
                .add(
                "",
                nodes,
                links,
                category_set,
                repulsion=50,
                linestyle_opts=opts.LineStyleOpts(curve=0.2),
                label_opts=opts.LabelOpts(is_show=False),
            )
                .set_global_opts(
                legend_opts=opts.LegendOpts(is_show=False),
            )
        )

        return HttpResponse(json.dumps({'Code': 1, 'Data': c.render_embed()}))

    else:
        db.repost_entry.insert_one(
            {'mid': int(request.GET['mid']), 'time': datetime.datetime.now(), 'is_update': False})
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))


def get_repost_card(request):
    if db.repost.find({"_id": int(request.GET['mid'])}).count() > 0:
        author = db.repost.find_one({"_id": int(request.GET['mid'])}, {"author"})['author']
        gender = db.repost.find_one({"_id": int(request.GET['mid'])}, {"gender"})['gender']
        urank = db.repost.find_one({"_id": int(request.GET['mid'])}, {"urank"})['urank']
        phone = db.repost.find_one({"_id": int(request.GET['mid'])}, {"phone"})['phone']
        reposts = db.repost.find_one({"_id": int(request.GET['mid'])}, {"reposts"})['reposts']
        follow_count = db.repost.find_one({"_id": int(request.GET['mid'])}, {"follow_count"})['follow_count']
        followers_count = db.repost.find_one({"_id": int(request.GET['mid'])}, {"followers_count"})['followers_count']
        statuses_count = db.repost.find_one({"_id": int(request.GET['mid'])}, {"statuses_count"})['statuses_count']
        text = db.repost.find_one({"_id": int(request.GET['mid'])}, {"text"})['text']
        repost_card_obj = {
            "author": author,
            "gender": gender,
            "urank": urank,
            "phone": phone,
            "reposts": reposts,
            "follow_count": follow_count,
            "followers_count": followers_count,
            "statuses_count": statuses_count,
            "text": text,
        }

        return HttpResponse(json.dumps({'Code': 1, 'Data': repost_card_obj}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))
