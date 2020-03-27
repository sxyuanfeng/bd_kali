from django.shortcuts import render
from django.http import HttpResponse
import os
import json
import pandas as pd
import pymongo
import datetime

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.weibo

verified_type_dict = {'-1': '普通用户', '0': '名人', '1': '政府', '2': '企业', '3': '媒体', '4': '校园', '5': '网站',
                      '6': '应用', '7': '团体或机构', '10': '微博女郎', '200': '初级达人', '220': '中高级达人'}

def get_fan_gender(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        fans_gender = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {"fans_info"})
        fans_gender_df = pd.DataFrame(fans_gender['fans_info'])
        female_count = len(fans_gender_df[fans_gender_df['fan_gender'] == 'f'])
        male_count = len(fans_gender_df[fans_gender_df['fan_gender'] == 'm'])
        gender_obj = {"man": round(male_count*100/(female_count+male_count), 2),
                      "woman": round(female_count*100/(female_count+male_count), 2)}

        return HttpResponse(json.dumps({'Code': 1, 'Data': gender_obj}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_fan_addv(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        fans_addv = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {"fans_info"})
        fans_addv_df = pd.DataFrame(fans_addv['fans_info'])
        addv_count = len(fans_addv_df[fans_addv_df['fan_verified'] == True])
        unaddv_count = len(fans_addv_df[fans_addv_df['fan_verified'] == False])
        addv_obj = [{"type": '未加V', "value": round((unaddv_count*100 / (addv_count+unaddv_count)), 2)},
                    {"type": '加V', "value": round((addv_count*100 / (addv_count+unaddv_count)), 2)}]

        return HttpResponse(json.dumps({'Code': 1, 'Data': addv_obj}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_alive_fans(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        all_fans = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {'master_fans_count'})['master_fans_count']
        alive_fans = len(db.account_value.find_one({"_id": int(request.GET['master_id'])}, {'fans_info'})['fans_info'])
        alive_fans_obj = [{'type': "已销号", 'value': round((all_fans - alive_fans)*100 / all_fans, 2)},
                          {'type': "存活", 'value': round(alive_fans*100 / all_fans, 2)}]

        return HttpResponse(json.dumps({'Code': 1, 'Data': alive_fans_obj}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_true_fans(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        alive_fans = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {'fans_info'})['fans_info']
        alive_fans_df = pd.DataFrame(alive_fans)
        fake_fans_count = len(alive_fans_df[((alive_fans_df['fan_urank'] < 1) & (alive_fans_df['fan_followers_count'] < 1)
                                & (alive_fans_df['fan_follow_count'] < 3)) | (alive_fans_df['fan_statuses_count'] < 1)])
        return HttpResponse(json.dumps({'Code': 1, 'Data': [{'type': '水军', 'value': round((fake_fans_count*100 / len(alive_fans_df)), 2)},
                                                            {'type': '真粉', 'value': round(((len(alive_fans_df) - fake_fans_count)*100 / len(alive_fans_df)), 2)}]}))
    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_fan_measure(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        alive_fans = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {'fans_info'})['fans_info']
        alive_fans_df = pd.DataFrame(alive_fans)
        alive_fans_count = len(alive_fans_df)
        under100 = len(alive_fans_df[alive_fans_df['fan_followers_count'] <= 100])
        under500 = len(alive_fans_df[(alive_fans_df['fan_followers_count'] <= 500) & (alive_fans_df['fan_followers_count'] > 100)])
        under1000 = len(alive_fans_df[(alive_fans_df['fan_followers_count'] <= 1000) & (alive_fans_df['fan_followers_count'] > 500)])
        under5000 = len(alive_fans_df[(alive_fans_df['fan_followers_count'] <= 5000) & (alive_fans_df['fan_followers_count'] > 1000)])
        under10000 = len(alive_fans_df[(alive_fans_df['fan_followers_count'] <= 10000) & (alive_fans_df['fan_followers_count'] > 5000)])
        under100000 = len(alive_fans_df[(alive_fans_df['fan_followers_count'] <= 100000) & (alive_fans_df['fan_followers_count'] > 10000)])
        than100000 = len(alive_fans_df[alive_fans_df['fan_followers_count'] > 100000])
        return HttpResponse(json.dumps({'Code': 1, 'Data': [
            {'amount': '0-100', 'percent': round((under100 * 100 / alive_fans_count), 2)},
            {'amount': '100-500', 'percent': round((under500 * 100 / alive_fans_count), 2)},
            {'amount': '500-1000', 'percent': round((under1000 * 100 / alive_fans_count), 2)},
            {'amount': '1000-5000', 'percent': round((under5000 * 100 / alive_fans_count), 2)},
            {'amount': '5000-10000', 'percent': round((under10000 * 100 / alive_fans_count), 2)},
            {'amount': '1万-10万', 'percent': round((under100000 * 100 / alive_fans_count), 2)},
            {'amount': '10万以上', 'percent': round((than100000 * 100 / alive_fans_count), 2)},
        ]}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_fan_verified_type(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        alive_fan = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {'fans_info'})['fans_info']
        alive_fan_df = pd.DataFrame(alive_fan)
        alive_fan_count = len(alive_fan_df)
        verified_type = alive_fan_df['fan_verified_type'].value_counts()
        verified_type_list = []
        for index in verified_type.index:
            verified_type_list.append({'item': verified_type_dict[str(index)], 'percent': round((verified_type[index]*100 / alive_fan_count), 2)})
        return HttpResponse(json.dumps({'Code': 1, 'Data': verified_type_list}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_master_base_info(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        master_base_info = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {"master_name", "master_gender", "master_avatar", "master_urank", "master_desc", "master_fans_count", "master_follow_count", "master_statuses_count", "master_profile_url", "current_time"})
        base_info_obj = {"master_name": master_base_info['master_name'],
                         "master_gender": master_base_info['master_gender'],
                         "master_avatar": master_base_info['master_avatar'],
                         "master_urank": master_base_info['master_urank'],
                         "master_desc": master_base_info['master_desc'],
                         "master_fans_count": master_base_info['master_fans_count'],
                         "master_follow_count": master_base_info['master_follow_count'],
                         "master_statuses_count": master_base_info['master_statuses_count'],
                         "master_profile_url": master_base_info['master_profile_url'],
                         "current_time": str(master_base_info['current_time'])}

        return HttpResponse(json.dumps({'Code': 1, 'Data': base_info_obj}))

    else:
        db.account_value_entry.insert_one(
            {'master_id': int(request.GET['master_id']), 'time': datetime.datetime.now(), 'is_update': False})
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))


def get_follow_gender(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        follow_gender = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {"follow_info"})
        follow_gender_df = pd.DataFrame(follow_gender['follow_info'])
        female_count = len(follow_gender_df[follow_gender_df['follow_gender'] == 'f'])
        male_count = len(follow_gender_df[follow_gender_df['follow_gender'] == 'm'])
        gender_obj = {"man": round(male_count*100/(female_count+male_count), 2),
                      "woman": round(female_count*100/(female_count+male_count), 2)}

        return HttpResponse(json.dumps({'Code': 1, 'Data': gender_obj}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_follow_addv(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        follow_addv = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {"follow_info"})
        follow_addv_df = pd.DataFrame(follow_addv['follow_info'])
        addv_count = len(follow_addv_df[follow_addv_df['follow_verified'] == True])
        unaddv_count = len(follow_addv_df[follow_addv_df['follow_verified'] == False])
        addv_obj = [{"type": '未加V', "value": round((unaddv_count*100 / (addv_count+unaddv_count)), 2)},
                    {"type": '加V', "value": round((addv_count*100 / (addv_count+unaddv_count)), 2)}]

        return HttpResponse(json.dumps({'Code': 1, 'Data': addv_obj}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_follow_measure(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        alive_follow = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {'follow_info'})['follow_info']
        alive_follow_df = pd.DataFrame(alive_follow)
        alive_follow_count = len(alive_follow_df)
        under100 = len(alive_follow_df[alive_follow_df['follow_followers_count'] <= 100])
        under500 = len(alive_follow_df[(alive_follow_df['follow_followers_count'] <= 500) & (alive_follow_df['follow_followers_count'] > 100)])
        under1000 = len(alive_follow_df[(alive_follow_df['follow_followers_count'] <= 1000) & (alive_follow_df['follow_followers_count'] > 500)])
        under5000 = len(alive_follow_df[(alive_follow_df['follow_followers_count'] <= 5000) & (alive_follow_df['follow_followers_count'] > 1000)])
        under10000 = len(alive_follow_df[(alive_follow_df['follow_followers_count'] <= 10000) & (alive_follow_df['follow_followers_count'] > 5000)])
        under100000 = len(alive_follow_df[(alive_follow_df['follow_followers_count'] <= 100000) & (alive_follow_df['follow_followers_count'] > 10000)])
        than100000 = len(alive_follow_df[alive_follow_df['follow_followers_count'] > 100000])
        return HttpResponse(json.dumps({'Code': 1, 'Data': [
            {'amount': '0-100', 'percent': round((under100*100 / alive_follow_count), 2)},
            {'amount': '100-500', 'percent': round((under500 * 100 / alive_follow_count), 2)},
            {'amount': '500-1000', 'percent': round((under1000 * 100 / alive_follow_count), 2)},
            {'amount': '1000-5000', 'percent': round((under5000 * 100 / alive_follow_count), 2)},
            {'amount': '5000-10000', 'percent': round((under10000 * 100 / alive_follow_count), 2)},
            {'amount': '1万-10万', 'percent': round((under100000 * 100 / alive_follow_count), 2)},
            {'amount': '10万以上', 'percent': round((than100000 * 100 / alive_follow_count), 2)},
        ]}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_follow_verified_type(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        alive_follow = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {'follow_info'})['follow_info']
        alive_follow_df = pd.DataFrame(alive_follow)
        alive_follow_count = len(alive_follow_df)
        verified_type = alive_follow_df['follow_verified_type'].value_counts()
        verified_type_list = []
        for index in verified_type.index:
            verified_type_list.append({'item': verified_type_dict[str(index)], 'percent': round((verified_type[index]*100 / alive_follow_count), 2)})
        return HttpResponse(json.dumps({'Code': 1, 'Data': verified_type_list}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_master_statuses_timeline(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        master_statuses_timeline = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {"master_statuses"})
        master_statuses_timeline_df = pd.DataFrame(master_statuses_timeline['master_statuses'])
        statuses_timeline_list = list(master_statuses_timeline_df['status_created_at'])

        return HttpResponse(json.dumps({'Code': 1, 'Data': statuses_timeline_list}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

