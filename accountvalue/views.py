from django.shortcuts import render
from django.http import HttpResponse
import os
import json
import pandas as pd
import pymongo

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.weibo #其中test改为你的数据库名

def index(request):
    fans_info = db.account_value.find_one({"master_name": "乐拉啊啊啊"}, {"fans_info"})
    fans_info_df = pd.DataFrame(fans_info['fans_info'])
    female_count = len(fans_info_df[fans_info_df['fan_gender'] == 'f'])
    male_count = len(fans_info_df[fans_info_df['fan_gender'] == 'm'])

    return HttpResponse(json.dumps([{"item": "女", "count": female_count, "percent": female_count/(female_count+male_count)}, {"item": "男", "count": male_count, "percent": male_count/(female_count+male_count)}]))

def get_master_base_info(request):
    master_base_info = db.account_value.find_one({"master_name": request.GET['master_name']}, {"master_name", "master_gender", "master_avatar", "master_urank", "master_desc", "master_fans_count", "master_follow_count", "master_statuses_count", "master_profile_url"})
    return HttpResponse(json.dumps({"master_name": master_base_info['master_name'], "master_gender": master_base_info['master_gender'], "master_avatar": master_base_info['master_avatar'], "master_urank": master_base_info['master_urank'], "master_desc": master_base_info['master_desc'], "master_fans_count": master_base_info['master_fans_count'], "master_follow_count": master_base_info['master_follow_count'], "master_statuses_count": master_base_info['master_statuses_count'], "master_profile_url": master_base_info['master_profile_url']}))

