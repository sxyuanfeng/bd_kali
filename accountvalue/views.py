from django.shortcuts import render
from django.http import HttpResponse
import os
import json
import pandas as pd
import pymongo

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.weibo

def get_fan_gender(request):
    fans_gender = db.account_value.find_one({"master_name": request.GET['master_name']}, {"fans_info"})
    fans_gender_df = pd.DataFrame(fans_gender['fans_info'])
    female_count = len(fans_gender_df[fans_gender_df['fan_gender'] == 'f'])
    male_count = len(fans_gender_df[fans_gender_df['fan_gender'] == 'm'])
    gender_obj = [{"item": "女", "count": female_count, "percent": female_count/(female_count+male_count)},
                  {"item": "男", "count": male_count, "percent": male_count/(female_count+male_count)}]

    return HttpResponse(json.dumps(gender_obj))

def get_master_base_info(request):
    master_base_info = db.account_value.find_one({"master_name": request.GET['master_name']}, {"master_name", "master_gender", "master_avatar", "master_urank", "master_desc", "master_fans_count", "master_follow_count", "master_statuses_count", "master_profile_url"})
    base_info_obj = {"master_name": master_base_info['master_name'],
                     "master_gender": master_base_info['master_gender'],
                     "master_avatar": master_base_info['master_avatar'],
                     "master_urank": master_base_info['master_urank'],
                     "master_desc": master_base_info['master_desc'],
                     "master_fans_count": master_base_info['master_fans_count'],
                     "master_follow_count": master_base_info['master_follow_count'],
                     "master_statuses_count": master_base_info['master_statuses_count'],
                     "master_profile_url": master_base_info['master_profile_url']}

    return HttpResponse(json.dumps(base_info_obj))

def get_follow_gender(request):
    follow_gender = db.account_value.find_one({"master_name": request.GET['master_name']}, {"follow_info"})
    follow_gender_df = pd.DataFrame(follow_gender['follow_info'])
    female_count = len(follow_gender_df[follow_gender_df['follow_gender'] == 'f'])
    male_count = len(follow_gender_df[follow_gender_df['follow_gender'] == 'm'])
    gender_obj = [{"item": "女", "count": female_count, "percent": female_count/(female_count+male_count)},
                  {"item": "男", "count": male_count, "percent": male_count/(female_count+male_count)}]

    return HttpResponse(json.dumps(gender_obj))

def get_follow_rank(request):
    follow_rank = db.account_value.find_one({"master_name": request.GET['master_name']}, {"follow_info"})
    follow_rank_df = pd.DataFrame(follow_rank['follow_info'])
    under_10 = len(follow_rank_df[follow_rank_df['follow_urank'] <= 10])
    under_20 = len(follow_rank_df[(follow_rank_df['follow_urank'] <= 20) & (follow_rank_df['follow_urank'] > 10)])
    under_30 = len(follow_rank_df[(follow_rank_df['follow_urank'] <= 30) & (follow_rank_df['follow_urank'] > 20)])
    under_40 = len(follow_rank_df[(follow_rank_df['follow_urank'] <= 40) & (follow_rank_df['follow_urank'] > 30)])
    under_50 = len(follow_rank_df[(follow_rank_df['follow_urank'] <= 50) & (follow_rank_df['follow_urank'] > 40)])
    than_50 = len(follow_rank_df[follow_rank_df['follow_urank'] > 50])
    follow_rank_obj = [{"type": "小于10", "value": under_10, "percent": under_10/len(follow_rank_df)},
                       {"type": "大于10小于20", "value": under_20, "percent": under_20/len(follow_rank_df)},
                       {"type": "大于20小于30", "value": under_30, "percent": under_30/len(follow_rank_df)},
                       {"type": "大于30小于40", "value": under_40, "percent": under_40/len(follow_rank_df)},
                       {"type": "大于40小于50", "value": under_50, "percent": under_50/len(follow_rank_df)},
                       {"type": "大于50", "value": than_50, "percent": than_50/len(follow_rank_df)}]

    return HttpResponse(json.dumps(follow_rank_obj))


def get_fan_rank(request):
    fan_rank = db.account_value.find_one({"master_name": request.GET['master_name']}, {"fans_info"})
    fan_rank_df = pd.DataFrame(fan_rank['fans_info'])
    under_10 = len(fan_rank_df[fan_rank_df['fan_urank'] <= 10])
    under_20 = len(fan_rank_df[(fan_rank_df['fan_urank'] <= 20) & (fan_rank_df['fan_urank'] > 10)])
    under_30 = len(fan_rank_df[(fan_rank_df['fan_urank'] <= 30) & (fan_rank_df['fan_urank'] > 20)])
    under_40 = len(fan_rank_df[(fan_rank_df['fan_urank'] <= 40) & (fan_rank_df['fan_urank'] > 30)])
    under_50 = len(fan_rank_df[(fan_rank_df['fan_urank'] <= 50) & (fan_rank_df['fan_urank'] > 40)])
    than_50 = len(fan_rank_df[fan_rank_df['fan_urank'] > 50])
    fan_rank_obj = [{"type": "小于10", "value": under_10, "percent": under_10 / len(fan_rank_df)},
                       {"type": "大于10小于20", "value": under_20, "percent": under_20 / len(fan_rank_df)},
                       {"type": "大于20小于30", "value": under_30, "percent": under_30 / len(fan_rank_df)},
                       {"type": "大于30小于40", "value": under_40, "percent": under_40 / len(fan_rank_df)},
                       {"type": "大于40小于50", "value": under_50, "percent": under_50 / len(fan_rank_df)},
                       {"type": "大于50", "value": than_50, "percent": than_50 / len(fan_rank_df)}]

    return HttpResponse(json.dumps(fan_rank_obj))

def get_follow_follow_count(request):
    follow_follow_count = db.account_value.find_one({"master_name": request.GET['master_name']}, {"follow_info"})
    follow_follow_count_df = pd.DataFrame(follow_follow_count['follow_info'])
    under_200 = len(follow_follow_count_df[follow_follow_count_df['follow_follow_count'] <= 200])
    under_400 = len(follow_follow_count_df[(follow_follow_count_df['follow_follow_count'] <= 400) & (follow_follow_count_df['follow_follow_count'] > 200)])
    under_600 = len(follow_follow_count_df[(follow_follow_count_df['follow_follow_count'] <= 600) & (follow_follow_count_df['follow_follow_count'] > 400)])
    under_800 = len(follow_follow_count_df[(follow_follow_count_df['follow_follow_count'] <= 800) & (follow_follow_count_df['follow_follow_count'] > 600)])
    under_1000 = len(follow_follow_count_df[(follow_follow_count_df['follow_follow_count'] <= 1000) & (follow_follow_count_df['follow_follow_count'] > 800)])
    than_1000 = len(follow_follow_count_df[follow_follow_count_df['follow_follow_count'] > 1000])
    follow_obj = [{"type": "小于200", "value": under_200, "percent": under_200 / len(follow_follow_count_df)},
                    {"type": "大于200小于400", "value": under_400, "percent": under_400 / len(follow_follow_count_df)},
                    {"type": "大于400小于600", "value": under_600, "percent": under_600 / len(follow_follow_count_df)},
                    {"type": "大于600小于8000", "value": under_800, "percent": under_800 / len(follow_follow_count_df)},
                    {"type": "大于800小于1000", "value": under_1000, "percent": under_1000 / len(follow_follow_count_df)},
                    {"type": "大于1000", "value": than_1000, "percent": than_1000 / len(follow_follow_count_df)}]

    return HttpResponse(json.dumps(follow_obj))

def get_follow_follower_count(request):
    follow_follower_count = db.account_value.find_one({"master_name": request.GET['master_name']}, {"follow_info"})
    follow_follower_count_df = pd.DataFrame(follow_follower_count['follow_info'])
    under_200 = len(follow_follower_count_df[follow_follower_count_df['follow_followers_count'] <= 200])
    under_400 = len(follow_follower_count_df[(follow_follower_count_df['follow_followers_count'] <= 400) & (follow_follower_count_df['follow_followers_count'] > 200)])
    under_600 = len(follow_follower_count_df[(follow_follower_count_df['follow_followers_count'] <= 600) & (follow_follower_count_df['follow_followers_count'] > 400)])
    under_800 = len(follow_follower_count_df[(follow_follower_count_df['follow_followers_count'] <= 800) & (follow_follower_count_df['follow_followers_count'] > 600)])
    under_1000 = len(follow_follower_count_df[(follow_follower_count_df['follow_followers_count'] <= 1000) & (follow_follower_count_df['follow_followers_count'] > 800)])
    than_1000 = len(follow_follower_count_df[follow_follower_count_df['follow_followers_count'] > 1000])
    follower_obj = [{"type": "小于200", "value": under_200, "percent": under_200 / len(follow_follower_count_df)},
                    {"type": "大于200小于400", "value": under_400, "percent": under_400 / len(follow_follower_count_df)},
                    {"type": "大于400小于600", "value": under_600, "percent": under_600 / len(follow_follower_count_df)},
                    {"type": "大于600小于8000", "value": under_800, "percent": under_800 / len(follow_follower_count_df)},
                    {"type": "大于800小于1000", "value": under_1000, "percent": under_1000 / len(follow_follower_count_df)},
                    {"type": "大于1000", "value": than_1000, "percent": than_1000 / len(follow_follower_count_df)}]

    return HttpResponse(json.dumps(follower_obj))

def get_fan_follow_count(request):
    fan_follow_count = db.account_value.find_one({"master_name": request.GET['master_name']}, {"fans_info"})
    fan_follow_count_df = pd.DataFrame(fan_follow_count['fans_info'])
    under_200 = len(fan_follow_count_df[fan_follow_count_df['fan_follow_count'] <= 200])
    under_400 = len(fan_follow_count_df[(fan_follow_count_df['fan_follow_count'] <= 400) & (fan_follow_count_df['fan_follow_count'] > 200)])
    under_600 = len(fan_follow_count_df[(fan_follow_count_df['fan_follow_count'] <= 600) & (fan_follow_count_df['fan_follow_count'] > 400)])
    under_800 = len(fan_follow_count_df[(fan_follow_count_df['fan_follow_count'] <= 800) & (fan_follow_count_df['fan_follow_count'] > 600)])
    under_1000 = len(fan_follow_count_df[(fan_follow_count_df['fan_follow_count'] <= 1000) & (fan_follow_count_df['fan_follow_count'] > 800)])
    than_1000 = len(fan_follow_count_df[fan_follow_count_df['fan_follow_count'] > 1000])
    follow_obj = [{"type": "小于200", "value": under_200, "percent": under_200 / len(fan_follow_count_df)},
                    {"type": "大于200小于400", "value": under_400, "percent": under_400 / len(fan_follow_count_df)},
                    {"type": "大于400小于600", "value": under_600, "percent": under_600 / len(fan_follow_count_df)},
                    {"type": "大于600小于8000", "value": under_800, "percent": under_800 / len(fan_follow_count_df)},
                    {"type": "大于800小于1000", "value": under_1000, "percent": under_1000 / len(fan_follow_count_df)},
                    {"type": "大于1000", "value": than_1000, "percent": than_1000 / len(fan_follow_count_df)}]

    return HttpResponse(json.dumps(follow_obj))

def get_fan_follower_count(request):
    fan_follower_count = db.account_value.find_one({"master_name": request.GET['master_name']}, {"fans_info"})
    fan_follower_count_df = pd.DataFrame(fan_follower_count['fans_info'])
    under_200 = len(fan_follower_count_df[fan_follower_count_df['fan_followers_count'] <= 200])
    under_400 = len(fan_follower_count_df[(fan_follower_count_df['fan_followers_count'] <= 400) & (fan_follower_count_df['fan_followers_count'] > 200)])
    under_600 = len(fan_follower_count_df[(fan_follower_count_df['fan_followers_count'] <= 600) & (fan_follower_count_df['fan_followers_count'] > 400)])
    under_800 = len(fan_follower_count_df[(fan_follower_count_df['fan_followers_count'] <= 800) & (fan_follower_count_df['fan_followers_count'] > 600)])
    under_1000 = len(fan_follower_count_df[(fan_follower_count_df['fan_followers_count'] <= 1000) & (fan_follower_count_df['fan_followers_count'] > 800)])
    than_1000 = len(fan_follower_count_df[fan_follower_count_df['fan_followers_count'] > 1000])
    follower_obj = [{"type": "小于200", "value": under_200, "percent": under_200 / len(fan_follower_count_df)},
                    {"type": "大于200小于400", "value": under_400, "percent": under_400 / len(fan_follower_count_df)},
                    {"type": "大于400小于600", "value": under_600, "percent": under_600 / len(fan_follower_count_df)},
                    {"type": "大于600小于8000", "value": under_800, "percent": under_800 / len(fan_follower_count_df)},
                    {"type": "大于800小于1000", "value": under_1000, "percent": under_1000 / len(fan_follower_count_df)},
                    {"type": "大于1000", "value": than_1000, "percent": than_1000 / len(fan_follower_count_df)}]

    return HttpResponse(json.dumps(follower_obj))

def get_follow_status_count(request):
    follow_status_count = db.account_value.find_one({"master_name": request.GET['master_name']}, {"follow_info"})
    follow_status_count_df = pd.DataFrame(follow_status_count['follow_info'])
    under_100 = len(follow_status_count_df[follow_status_count_df['follow_statuses_count'] <= 100])
    under_200 = len(follow_status_count_df[(follow_status_count_df['follow_statuses_count'] <= 200) & (follow_status_count_df[
        'follow_statuses_count'] > 100)])
    under_300 = len(follow_status_count_df[(follow_status_count_df['follow_statuses_count'] <= 300) & (follow_status_count_df[
        'follow_statuses_count'] > 200)])
    under_400 = len(follow_status_count_df[(follow_status_count_df['follow_statuses_count'] <= 400) & (follow_status_count_df[
        'follow_statuses_count'] > 300)])
    under_500 = len(follow_status_count_df[(follow_status_count_df['follow_statuses_count'] <= 500) & (follow_status_count_df[
        'follow_statuses_count'] > 400)])
    than_500 = len(follow_status_count_df[follow_status_count_df['follow_statuses_count'] > 500])
    status_obj = [{"type": "小于100", "value": under_100, "percent": under_100 / len(follow_status_count_df)},
                    {"type": "大于100小于200", "value": under_200, "percent": under_200 / len(follow_status_count_df)},
                    {"type": "大于200小于300", "value": under_300, "percent": under_300 / len(follow_status_count_df)},
                    {"type": "大于300小于400", "value": under_400, "percent": under_400 / len(follow_status_count_df)},
                    {"type": "大于400小于500", "value": under_500, "percent": under_500 / len(follow_status_count_df)},
                    {"type": "大于500", "value": than_500, "percent": than_500 / len(follow_status_count_df)}]

    return HttpResponse(json.dumps(status_obj))


def get_fan_status_count(request):
    fan_status_count = db.account_value.find_one({"master_name": request.GET['master_name']}, {"fans_info"})
    fan_status_count_df = pd.DataFrame(fan_status_count['fans_info'])
    under_100 = len(fan_status_count_df[fan_status_count_df['fan_statuses_count'] <= 100])
    under_200 = len(
        fan_status_count_df[(fan_status_count_df['fan_statuses_count'] <= 200) & (fan_status_count_df[
            'fan_statuses_count'] > 100)])
    under_300 = len(
        fan_status_count_df[(fan_status_count_df['fan_statuses_count'] <= 300) & (fan_status_count_df[
            'fan_statuses_count'] > 200)])
    under_400 = len(
        fan_status_count_df[(fan_status_count_df['fan_statuses_count'] <= 400) & (fan_status_count_df[
            'fan_statuses_count'] > 300)])
    under_500 = len(
        fan_status_count_df[(fan_status_count_df['fan_statuses_count'] <= 500) & (fan_status_count_df[
            'fan_statuses_count'] > 400)])
    than_500 = len(fan_status_count_df[fan_status_count_df['fan_statuses_count'] > 500])
    status_obj = [{"type": "小于100", "value": under_100, "percent": under_100 / len(fan_status_count_df)},
                  {"type": "大于100小于200", "value": under_200, "percent": under_200 / len(fan_status_count_df)},
                  {"type": "大于200小于300", "value": under_300, "percent": under_300 / len(fan_status_count_df)},
                  {"type": "大于300小于400", "value": under_400, "percent": under_400 / len(fan_status_count_df)},
                  {"type": "大于400小于500", "value": under_500, "percent": under_500 / len(fan_status_count_df)},
                  {"type": "大于500", "value": than_500, "percent": than_500 / len(fan_status_count_df)}]

    return HttpResponse(json.dumps(status_obj))

def get_master_statuses_timeline(request):
    master_statuses_timeline = db.account_value.find_one({"master_name": request.GET['master_name']}, {"master_statuses"})
    master_statuses_timeline_df = pd.DataFrame(master_statuses_timeline['master_statuses'])
    statuses_timeline_list = list(master_statuses_timeline_df['status_created_at'])

    return HttpResponse(json.dumps(statuses_timeline_list))

def get_master_statuses_index(request):
    master_statuses_index = db.account_value.find_one({"master_name": request.GET['master_name']}, {"master_statuses"})
    master_statuses_index_df = pd.DataFrame(master_statuses_index['master_statuses'])
    master_statuses_index_list = []
    for index, row in master_statuses_index_df.iterrows():
        master_statuses_index_list.append({'time': row['status_created_at'], 'attitudes': row['status_attitudes_count'],
        'comments': row['status_comments_count'], 'reposts': row['status_reposts_count']})

    return HttpResponse(json.dumps(master_statuses_index_list))


