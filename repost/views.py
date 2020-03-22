from django.shortcuts import render
from django.http import HttpResponse
import os
import json
import pandas as pd
import pymongo
import jieba.analyse
from pyecharts.charts import Graph
from pyecharts import options as opts

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
    mid = 4482073269995851
    data = db.repost.find_one({"mid": mid}, {"list"})
    author = db.repost.find_one({"mid": mid}, {"author"})['author']
    reposts = db.repost.find_one({"mid": mid}, {"reposts"})['reposts']
    followers = db.repost.find_one({"mid": mid}, {"followers_count"})['followers_count']
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

    return HttpResponse(json.dumps(c.render_embed()))
