from django.shortcuts import render
from django.http import HttpResponse
import os
import json
import pandas as pd
import pymongo
from datetime import datetime
from pyecharts.charts import Map
from pyecharts import options as opts
from pyecharts.globals import ThemeType

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.weibo

verified_type_dict = {'-1': '普通用户', '0': '名人', '1': '政府', '2': '企业', '3': '媒体', '4': '校园', '5': '网站',
                      '6': '应用', '7': '团体或机构', '8': '未知', '10': '微博女郎', '200': '初级达人', '220': '中高级达人'}

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

def get_fan_mbrank(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        alive_fan = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {'fans_info'})['fans_info']
        alive_fan_df = pd.DataFrame(alive_fan)
        alive_fan_count = len(alive_fan_df)
        mbrank = alive_fan_df['fan_mbrank'].value_counts()
        mbrank_list = []
        for index in mbrank.index:
            mbrank_list.append({'item': str(index) + '级', 'percent': round((mbrank[index]*100 / alive_fan_count), 2)})
        return HttpResponse(json.dumps({'Code': 1, 'Data': mbrank_list}))

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
            {'master_id': int(request.GET['master_id']), 'time': datetime.now(), 'is_update': False})
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

def get_follow_mbrank(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        alive_follow = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {'follow_info'})['follow_info']
        alive_follow_df = pd.DataFrame(alive_follow)
        alive_follow_count = len(alive_follow_df)
        mbrank = alive_follow_df['follow_mbrank'].value_counts()
        mbrank_list = []
        for index in mbrank.index:
            mbrank_list.append({'item': str(index) + '级', 'percent': round((mbrank[index]*100 / alive_follow_count), 2)})
        return HttpResponse(json.dumps({'Code': 1, 'Data': mbrank_list}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_statuses_timeline(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        statuses_timeline = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {"all_statuses"})
        statuses_timeline_df = pd.DataFrame(statuses_timeline['all_statuses'][1:51])
        statuses_timeline_list = list(statuses_timeline_df['status_created_at'])
        attitude_mean = round(statuses_timeline_df['status_attitudes_count'].mean(), 2)
        comment_mean = round(statuses_timeline_df['status_comments_count'].mean(), 2)
        repost_mean = round(statuses_timeline_df['status_reposts_count'].mean(), 2)

        top_3_attitude = []
        statuses_timeline_df_atti = statuses_timeline_df.sort_values(["status_attitudes_count"],ascending=False)[0:3]
        for index, row in statuses_timeline_df_atti.iterrows():
            top_3_attitude.append({'time': row['status_created_at'],
                                   'text': row['status_raw_text'] or row['status_text'],
                                   'attitude': row['status_attitudes_count'],
                                   'comment': row['status_comments_count'],
                                   'repost': row['status_reposts_count']})
        top_3_comment = []
        statuses_timeline_df_comm = statuses_timeline_df.sort_values(["status_comments_count"], ascending=False)[0:3]
        for index, row in statuses_timeline_df_comm.iterrows():
            top_3_comment.append({'time': row['status_created_at'],
                                   'text': row['status_raw_text'] or row['status_text'],
                                   'attitude': row['status_attitudes_count'],
                                   'comment': row['status_comments_count'],
                                   'repost': row['status_reposts_count']})
        top_3_repost = []
        statuses_timeline_df_repo = statuses_timeline_df.sort_values(["status_reposts_count"], ascending=False)[0:3]
        for index, row in statuses_timeline_df_repo.iterrows():
            top_3_repost.append({'time': row['status_created_at'],
                                  'text': row['status_raw_text'] or row['status_text'],
                                  'attitude': row['status_attitudes_count'],
                                  'comment': row['status_comments_count'],
                                  'repost': row['status_reposts_count']})

        statuses_timeline_obj = {'days': [statuses_timeline_df.iloc[0]['status_created_at'], statuses_timeline_df.iloc[-1]['status_created_at']],
                                 'attitude_mean': attitude_mean,
                                 'comment_mean': comment_mean,
                                 'repost_mean': repost_mean,
                                 'statuses_timeline_list': statuses_timeline_list,
                                 'top_3_attitude': top_3_attitude,
                                 'top_3_comment': top_3_comment,
                                 'top_3_repost': top_3_repost,
                                 }

        return HttpResponse(json.dumps({'Code': 1, 'Data': statuses_timeline_obj}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_statuses_active_time(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        statuses_active_time = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {"all_statuses"})
        statuses_active_time_df = pd.DataFrame(statuses_active_time['all_statuses'])
        statuses_active_time_list = list(statuses_active_time_df['status_created_at'])

        return HttpResponse(json.dumps({'Code': 1, 'Data': statuses_active_time_list}))
    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_statuses_index(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        statuses_index = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {"all_statuses"})
        statuses_index_df = pd.DataFrame(statuses_index['all_statuses'][0:10])
        statuses_index_list = []
        for index, row in statuses_index_df.iterrows():
            statuses_index_list.append({
                'name': '点赞',
                'index': abs(index - 10),
                'value': row['status_attitudes_count'],
            })
            statuses_index_list.append({
                'name': '评论',
                'index': abs(index - 10),
                'value': row['status_comments_count'],
            })
            statuses_index_list.append({
                'name': '转发',
                'index': abs(index - 10),
                'value': row['status_reposts_count'],
            })

        return HttpResponse(json.dumps({'Code': 1, 'Data': statuses_index_list}))
    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_statuses_retweet(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        statuses_retweet = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {"all_statuses"})
        statuses_retweet_df = pd.DataFrame(statuses_retweet['all_statuses'])
        statuses_isretweet = len(statuses_retweet_df[statuses_retweet_df['is_retweeted'] == True])
        statuses_notretweet = len(statuses_retweet_df[statuses_retweet_df['is_retweeted'] == False])
        statuses_retweet_list = [{
            'name': 'retweet',
            'value': statuses_isretweet,
            'percent': round((statuses_isretweet*100 / (statuses_isretweet + statuses_notretweet)), 2)
        }, {
            'name': 'notretweet',
            'value': statuses_notretweet,
            'percent': round((statuses_notretweet * 100 / (statuses_isretweet + statuses_notretweet)), 2)
        }]

        return HttpResponse(json.dumps({'Code': 1, 'Data': statuses_retweet_list}))
    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_statuses_source(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        all_statuses = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {"all_statuses"})
        all_statuses_df = pd.DataFrame(all_statuses['all_statuses'])
        all_source = len(all_statuses_df)
        statuses_source = all_statuses_df['status_source'].value_counts().to_dict()
        statuses_source_list = []
        for key in statuses_source:
            statuses_source_list.append({'source': key, 'value': round((statuses_source[key]*100 / all_source) ,2)})

        return HttpResponse(json.dumps({'Code': 1, 'Data': statuses_source_list}))
    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_account_overview(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        all_statuses = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {"all_statuses"})
        all_statuses_df = pd.DataFrame(all_statuses['all_statuses'])
        all_statuses_count = len(all_statuses_df)
        statuses_notretweet = len(all_statuses_df[all_statuses_df['is_retweeted'] == False])
        overview_obj = {'原创度': round((statuses_notretweet*100 / all_statuses_count), 1)}
        recently_statuses = list(all_statuses_df[1:]['status_created_at'])
        active_time = [recently_statuses[-1], recently_statuses[1], len(recently_statuses)]
        overview_obj.update({'活跃度': active_time})
        all_fans = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {'master_fans_count'})[
            'master_fans_count']
        alive_fans = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {'fans_info'})['fans_info']
        alive_fans_count = len(alive_fans)
        alive_fans_df = pd.DataFrame(alive_fans)
        fake_fans_count = len(
            alive_fans_df[((alive_fans_df['fan_urank'] < 1) & (alive_fans_df['fan_followers_count'] < 1)
                           & (alive_fans_df['fan_follow_count'] < 3)) | (alive_fans_df['fan_statuses_count'] < 1)])
        true_fans_percent = round(((alive_fans_count - fake_fans_count)*100 / all_fans), 1)
        overview_obj.update({'粉丝质量': true_fans_percent})

        under100 = round((len(alive_fans_df[alive_fans_df['fan_followers_count'] <= 100]) / alive_fans_count), 2)
        under500 = round((len(
            alive_fans_df[(alive_fans_df['fan_followers_count'] <= 500) & (alive_fans_df['fan_followers_count'] > 100)]) / alive_fans_count), 2)
        under1000 = round((len(alive_fans_df[(alive_fans_df['fan_followers_count'] <= 1000) & (
                    alive_fans_df['fan_followers_count'] > 500)]) / alive_fans_count), 2)
        under5000 = round((len(alive_fans_df[(alive_fans_df['fan_followers_count'] <= 5000) & (
                    alive_fans_df['fan_followers_count'] > 1000)]) / alive_fans_count), 2)
        under10000 = round((len(alive_fans_df[(alive_fans_df['fan_followers_count'] <= 10000) & (
                    alive_fans_df['fan_followers_count'] > 5000)]) / alive_fans_count), 2)
        under100000 = round((len(alive_fans_df[(alive_fans_df['fan_followers_count'] <= 100000) & (
                    alive_fans_df['fan_followers_count'] > 10000)]) / alive_fans_count), 2)
        than100000 = round((len(alive_fans_df[alive_fans_df['fan_followers_count'] > 100000]) / alive_fans_count) ,2)

        influence = round(((under100*0.01 + under500*0.02 + under1000*0.05 + under5000*0.1 + under10000*0.15 + under100000*0.2 + than100000*0.47)*100), 1)
        overview_obj.update({'影响力': influence})
        mbrank = alive_fans_df['fan_mbrank'].value_counts()
        novip = mbrank[0]
        vip = round(((alive_fans_count - novip)*100 / alive_fans_count), 1)
        addv_percent = round((len(alive_fans_df[alive_fans_df['fan_verified'] == True])*100 / alive_fans_count), 1)
        verified_type = round((len(alive_fans_df['fan_verified_type'].value_counts())*100 / 12), 1)
        ad_value = round(((vip + addv_percent + verified_type) / 3) ,1)
        overview_obj.update({'广告投放价值': ad_value})

        return HttpResponse(json.dumps({'Code': 1, 'Data': overview_obj}))
    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

'''
def get_fan_area(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        fans_info = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {"fans_info"})
        fans_info_df = pd.DataFrame(fans_info['fans_info'])
        userinfo_list = []
        for index, row in fans_info_df.iterrows():
            userinfo_list.extend(row['fan_userinfo'])
        userinfo_df = pd.DataFrame(userinfo_list)
        fans_area_df = userinfo_df[userinfo_df['item_name'] == '所在地']
        fans_area_df['city'], fans_area_df['area'] = fans_area_df['item_content'].str.split(' ', 1).str
        fans_area_obj = fans_area_df['city'].value_counts().to_dict()
        other = len(fans_info_df) - len(fans_area_df)
        fans_area_obj.update({'未知': other})

        c = (
            Map(init_opts=opts.InitOpts(width="400px", height="300px"))
                .add("省份", [list(z) for z in zip(fans_area_obj.keys(), fans_area_obj.values())], "china", is_roam=False, is_map_symbol_show=False)
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=""),
                    visualmap_opts=opts.VisualMapOpts(
                        item_height=60,
                        item_width=10,
                        pos_left=10,
                        pos_bottom=20
                    ),
                    legend_opts=opts.LegendOpts(
                        is_show=False
                    )
            )
        )
        return HttpResponse(json.dumps({'Code': 1, 'Data': fans_area_obj, 'Map': c.render_embed()}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_follow_area(request):
    if db.account_value.find({"_id": int(request.GET['master_id'])}).count() > 0:
        follow_info = db.account_value.find_one({"_id": int(request.GET['master_id'])}, {"follow_info"})
        follow_info_df = pd.DataFrame(follow_info['follow_info'])
        userinfo_list = []
        for index, row in follow_info_df.iterrows():
            userinfo_list.extend(row['follow_userinfo'])
        userinfo_df = pd.DataFrame(userinfo_list)
        follow_area_df = userinfo_df[userinfo_df['item_name'] == '所在地']
        follow_area_df['city'], follow_area_df['area'] = follow_area_df['item_content'].str.split(' ', 1).str
        follow_area_obj = follow_area_df['city'].value_counts().to_dict()
        other = len(follow_info_df) - len(follow_area_df)
        follow_area_obj.update({'未知': other})

        c = (
            Map(init_opts=opts.InitOpts(width="400px", height="300px"))
                .add("省份", [list(z) for z in zip(follow_area_obj.keys(), follow_area_obj.values())], "china", is_roam=False, is_map_symbol_show=False)
                .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
                .set_global_opts(
                    title_opts=opts.TitleOpts(title=""),
                    visualmap_opts=opts.VisualMapOpts(
                        item_height=60,
                        item_width=10,
                        pos_left=10,
                        pos_bottom=20
                    ),
                    legend_opts=opts.LegendOpts(
                        is_show=False
                    )
            )
        )
        return HttpResponse(json.dumps({'Code': 1, 'Data': follow_area_obj, 'Map': c.render_embed()}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))
'''
