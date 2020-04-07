from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import pymongo
from datetime import datetime
import json

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.weibo

'''
def tran_time(created, current):
    if created == '刚刚':
        return current
    elif created[-3:] == '分钟前':
        return
    elif created[-3:] == '小时前':
        return
    elif created[0:2] == '昨天':
        return
    elif created
'''

def get_mblog_info(request):
    if db.repost.find({"_id": int(request.GET['mid'])}).count() > 0:
        mblog_info = db.repost.find_one({"_id": int(request.GET['mid'])}, {"author", "avatar", "follow_count",
                                                                                  "followers_count", "statuses_count",
                                                                                  "text", "created_at", "phone",
                                                                                  "attitudes", "comments", "reposts",
                                                                                  "current_time"})
        mblog_info_obj = {"author": mblog_info['author'],
                          "avatar": mblog_info['avatar'],
                          "follow_count": mblog_info['follow_count'],
                          "followers_count": mblog_info['followers_count'],
                          "statuses_count": mblog_info['statuses_count'],
                          "text": mblog_info['text'],
                          "created_at": mblog_info['created_at'],
                          "phone": mblog_info['phone'],
                          "attitudes": mblog_info['attitudes'],
                          "comments": mblog_info['comments'],
                          "reposts": mblog_info['reposts'],
                          "current_time": str(mblog_info['current_time']).split('.')[0]}

        return HttpResponse(json.dumps({'Code': 1, 'Data': mblog_info_obj}))

    else:
        db.repost_entry.insert_one(
            {'mid': int(request.GET['mid']), 'time': datetime.now(), 'is_update': False})
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))
