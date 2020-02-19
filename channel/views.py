from django.shortcuts import render
from django.http import HttpResponse
import os
import json
import pandas as pd
import pymongo

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.weibo

def get_hottag(request):
    data = db.channel.find_one({"label": "热搜"}, {"list"})
    data = pd.DataFrame(data['list'])
    print(data)
    return HttpResponse('11')
