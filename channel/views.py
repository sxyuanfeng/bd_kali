from django.shortcuts import render
from django.http import HttpResponse
import os
import json
import pandas as pd
import pymongo
import jieba.analyse

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.weibo

def get_hottag(request):
    data = db.channel.find_one({"label": "热搜"}, {"list"})
    data = pd.DataFrame(data['list'])
    tag_list = []
    value = 51
    for desc in data['desc']:
        tag_line = jieba.analyse.extract_tags(desc, topK=2, allowPOS=('n'))
        if len(tag_line) > 0:
            for item in tag_line:
                tag_list.append({'name': item, 'value': value})
        else:
            pass
        value = value - 1
    return HttpResponse(json.dumps(tag_list))


