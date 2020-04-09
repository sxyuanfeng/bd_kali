from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import pymongo
from datetime import datetime, timedelta
import json
from pyecharts.charts import Graph
from pyecharts import options as opts
import jieba.analyse

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.weibo

verified_type_dict = {'-1': '普通用户', '0': '名人', '1': '政府', '2': '企业', '3': '媒体', '4': '校园', '5': '网站',
                      '6': '应用', '7': '团体或机构', '10': '微博女郎', '200': '初级达人', '220': '中高级达人'}

def tran_time(created, current):
    if created == '刚刚':
        return str(current).split(' ')[0]
    elif created[-3:] == '分钟前':
        minutes = timedelta(minutes = int(created[0:-3]))
        return (current - minutes).strftime("%Y-%m-%d")
    elif created[-3:] == '小时前':
        hours = timedelta(hours = int(created[0:-3]))
        return (current - hours).strftime("%Y-%m-%d")
    elif created[0:2] == '昨天':
        days = timedelta(days = 1)
        return (current - days).strftime("%Y-%m-%d")
    elif len(created.split('-')) == 2:
        return str(current).split(' ')[0].split('-')[0] + '-' + created
    else:
        return created

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

def get_participant_repost_from(request):
    if db.repost.find({"_id": int(request.GET['mid'])}).count() > 0:
        repost_list = db.repost.find_one({"_id": int(request.GET['mid'])}, {"repost_list"})
        repost_list_df = pd.DataFrame(repost_list['repost_list'])
        repost_list_count = len(repost_list_df)
        participant_repost_from = repost_list_df['phone'].value_counts().to_dict()
        participant_repost_from['其它'] = participant_repost_from.pop('')
        new_participant_repost_from = {'其他': 0}
        for i, (k, v) in enumerate(participant_repost_from.items()):
            if i < 9:
                new_participant_repost_from.update({k: v})
            else:
                new_participant_repost_from['其他'] += v
        participant_repost_from_list = []
        for i, (k, v) in enumerate(new_participant_repost_from.items()):
            participant_repost_from_list.append({'item': k, 'value': v, 'percent': round((v*100 / repost_list_count), 2)})

        return HttpResponse(json.dumps({'Code': 1, 'Data': participant_repost_from_list}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_participant_repost_verified(request):
    if db.repost.find({"_id": int(request.GET['mid'])}).count() > 0:
        repost_list = db.repost.find_one({"_id": int(request.GET['mid'])}, {"repost_list"})
        repost_list_df = pd.DataFrame(repost_list['repost_list'])
        repost_list_count = len(repost_list_df)
        verified_type = repost_list_df['verified_type'].value_counts()
        verified_type_list = []
        for index in verified_type.index:
            verified_type_list.append({'item': verified_type_dict[str(index)],
                                       'percent': round((verified_type[index] * 100 / repost_list_count), 2)})
        return HttpResponse(json.dumps({'Code': 1, 'Data': verified_type_list}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_participant_repost_gender(request):
    if db.repost.find({"_id": int(request.GET['mid'])}).count() > 0:
        repost_list = db.repost.find_one({"_id": int(request.GET['mid'])}, {"repost_list"})
        repost_list_df = pd.DataFrame(repost_list['repost_list'])
        repost_list_count = len(repost_list_df)
        gender = repost_list_df['gender'].value_counts().to_dict()
        gender_obj = {'man': round((gender['m']*100 / repost_list_count), 2),
                      'woman': round((gender['f']*100 / repost_list_count), 2)}
        return HttpResponse(json.dumps({'Code': 1, 'Data': gender_obj}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_participant_repost_addv(request):
    if db.repost.find({"_id": int(request.GET['mid'])}).count() > 0:
        repost_list = db.repost.find_one({"_id": int(request.GET['mid'])}, {"repost_list"})
        repost_list_df = pd.DataFrame(repost_list['repost_list'])
        addv_count = len(repost_list_df[repost_list_df['verified'] == True])
        unaddv_count = len(repost_list_df[repost_list_df['verified'] == False])
        addv_obj = [{"type": '未加V', "value": round((unaddv_count*100 / (addv_count+unaddv_count)), 2)},
                    {"type": '加V', "value": round((addv_count*100 / (addv_count+unaddv_count)), 2)}]

        return HttpResponse(json.dumps({'Code': 1, 'Data': addv_obj}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_participant_repost_true(request):
    if db.repost.find({"_id": int(request.GET['mid'])}).count() > 0:
        repost_list = db.repost.find_one({"_id": int(request.GET['mid'])}, {"repost_list"})
        repost_list_df = pd.DataFrame(repost_list['repost_list'])
        fake_repost_count = len(
            repost_list_df[((repost_list_df['urank'] < 2) & (repost_list_df['followers_count'] < 2))])

        repost_true_list = [{'type': '水军', 'value': round((fake_repost_count*100 / len(repost_list_df)), 2)},
                            {'type': '真粉', 'value': round(((len(repost_list_df) - fake_repost_count)*100 / len(repost_list_df)), 2)}]

        return HttpResponse(json.dumps({'Code': 1, 'Data': repost_true_list}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_participant_repost_measure(request):
    if db.repost.find({"_id": int(request.GET['mid'])}).count() > 0:
        repost_list = db.repost.find_one({"_id": int(request.GET['mid'])}, {'repost_list'})['repost_list']
        repost_list_df = pd.DataFrame(repost_list)
        repost_list_count = len(repost_list_df)
        under100 = len(repost_list_df[repost_list_df['followers_count'] <= 100])
        under500 = len(repost_list_df[(repost_list_df['followers_count'] <= 500) & (repost_list_df['followers_count'] > 100)])
        under1000 = len(repost_list_df[(repost_list_df['followers_count'] <= 1000) & (repost_list_df['followers_count'] > 500)])
        under5000 = len(repost_list_df[(repost_list_df['followers_count'] <= 5000) & (repost_list_df['followers_count'] > 1000)])
        under10000 = len(repost_list_df[(repost_list_df['followers_count'] <= 10000) & (repost_list_df['followers_count'] > 5000)])
        under100000 = len(repost_list_df[(repost_list_df['followers_count'] <= 100000) & (repost_list_df['followers_count'] > 10000)])
        than100000 = len(repost_list_df[repost_list_df['followers_count'] > 100000])
        return HttpResponse(json.dumps({'Code': 1, 'Data': [
            {'amount': '0-100', 'percent': round((under100 * 100 / repost_list_count), 2)},
            {'amount': '100-500', 'percent': round((under500 * 100 / repost_list_count), 2)},
            {'amount': '500-1000', 'percent': round((under1000 * 100 / repost_list_count), 2)},
            {'amount': '1000-5000', 'percent': round((under5000 * 100 / repost_list_count), 2)},
            {'amount': '5000-10000', 'percent': round((under10000 * 100 / repost_list_count), 2)},
            {'amount': '1万-10万', 'percent': round((under100000 * 100 / repost_list_count), 2)},
            {'amount': '10万以上', 'percent': round((than100000 * 100 / repost_list_count), 2)},
        ]}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_spread_timeline(request):
    if db.repost.find({"_id": int(request.GET['mid'])}).count() > 0:
        repost_list = db.repost.find_one({"_id": int(request.GET['mid'])}, {"repost_list", "current_time"})
        repost_list_df = pd.DataFrame(repost_list['repost_list'])
        repost_list_df['created_at'] = repost_list_df.apply(lambda x: tran_time(x['created_at'], repost_list['current_time']), axis=1)
        repost_timeline = repost_list_df['created_at'].value_counts().to_dict()
        repost_timeline_list = []
        for key in repost_timeline:
            repost_timeline_list.append({'time': key, 'value': repost_timeline[key]})

        return HttpResponse(json.dumps({'Code': 1, 'Data': repost_timeline_list}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_spread_repost_relative(request):
    if db.repost.find({"_id": int(request.GET['mid'])}).count() > 0:
        repost_list = db.repost.find_one({"_id": int(request.GET['mid'])}, {"repost_list"})
        author = db.repost.find_one({"_id": int(request.GET['mid'])}, {"author"})['author']
        reposts = db.repost.find_one({"_id": int(request.GET['mid'])}, {"reposts"})['reposts']
        #followers = db.repost.find_one({"_id": int(request.GET['mid'])}, {"followers_count"})['followers_count']
        data = pd.DataFrame(repost_list['repost_list'])
        data = data.drop_duplicates(subset=['name'], keep='first')

        father = []
        for index, row in data.iterrows():
            if row['raw_text'].find('//@') >= 0:
                father.append(row['raw_text'][row['raw_text'].find('//@') + 3:][
                              :row['raw_text'][row['raw_text'].find('//@') + 3:].find(':')].replace(' ', ''))
            else:
                father.append(author)

        data['father'] = pd.DataFrame({'father': father})

        nodes = [{'name': author, 'category': author, 'value': reposts}]
        links = []
        category = []

        for index, row in data.iterrows():
            nodes.append({'name': row['name'], 'category': row['father'], 'value': row['reposts_count']})
            links.append({'source': row['father'], 'target': row['name']})
            category.append(row['father'])

        category = set(category)
        category_set = []
        for i in category:
            category_set.append({'name': i})

        c = (
            Graph(init_opts=opts.InitOpts(width="540px", height="400px"))
                .add(
                    "",
                    nodes,
                    links,
                    category_set,
                    repulsion=8,
                    linestyle_opts=opts.LineStyleOpts(curve=0.2),
                    label_opts=opts.LabelOpts(is_show=False),
                )
                .set_global_opts(
                    legend_opts=opts.LegendOpts(is_show=False),
                )
            )

        return HttpResponse(json.dumps({'Code': 1, 'Data': c.render_embed()}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_spread_repost_deep(request):
    if db.repost.find({"_id": int(request.GET['mid'])}).count() > 0:
        repost_list = db.repost.find_one({"_id": int(request.GET['mid'])}, {"repost_list"})
        repost_list_df = pd.DataFrame(repost_list['repost_list'])
        repost_list_count = len(repost_list_df)
        repost_deep = {}
        for index, row in repost_list_df.iterrows():
            deep = len(row['raw_text'].split('//@'))
            if deep in repost_deep:
                repost_deep[deep] += 1
            else:
                repost_deep[deep] = 1
        repost_deep_sort = sorted(repost_deep)
        repost_deep_list = []
        for key in repost_deep_sort:
            repost_deep_list.append({'item': str(key), 'percent': round((repost_deep[key]*100 / repost_list_count), 2)})

        return HttpResponse(json.dumps({'Code': 1, 'Data': repost_deep_list}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_spread_repost_keyuser(request):
    if db.repost.find({"_id": int(request.GET['mid'])}).count() > 0:
        repost_list = db.repost.find_one({"_id": int(request.GET['mid'])}, {"repost_list", "current_time"})
        repost_list_df = pd.DataFrame(repost_list['repost_list'])
        repost_list_df.sort_index(by=['reposts_count'],ascending=False,inplace=True)
        repost_list_df.reset_index(drop=True, inplace=True)
        for index, row in repost_list_df.iterrows():
            if index == 0:
                repost_keyuser_obj = {'avatar': row['avatar'],
                                      'name': row['name'],
                                      'followers_count': row['followers_count'],
                                      'created_at': tran_time(row['created_at'], repost_list['current_time']),
                                      'reposts_count': row['reposts_count'],
                                      'raw_text': row['raw_text']}
            else:
                pass


        return HttpResponse(json.dumps({'Code': 1, 'Data': repost_keyuser_obj}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_spread_repost_keyuser_road(request):
    if db.repost.find({"_id": int(request.GET['mid'])}).count() > 0:
        repost_list = db.repost.find_one({"_id": int(request.GET['mid'])}, {"repost_list", "author"})
        repost_list_df = pd.DataFrame(repost_list['repost_list'])
        repost_list_df.sort_index(by=['reposts_count'],ascending=False,inplace=True)
        repost_list_df.reset_index(drop=True, inplace=True)
        repost_keyuser_road_list = [repost_list['author']]
        for index, row in repost_list_df.iterrows():
            if index == 0:
                raw_text_list = row['raw_text'].split('//@')
                if len(raw_text_list) > 1:
                    for i in range(len(raw_text_list)-1, 0, -1):
                        repost_keyuser_road_list.append(raw_text_list[i].split(':')[0])
                else:
                    repost_keyuser_road_list.append(row['name'])
            else:
                pass


        return HttpResponse(json.dumps({'Code': 1, 'Data': repost_keyuser_road_list}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_spread_repost_bomm(request):
    if db.repost.find({"_id": int(request.GET['mid'])}).count() > 0:
        repost_list = db.repost.find_one({"_id": int(request.GET['mid'])}, {"repost_list", "current_time"})
        repost_list_df = pd.DataFrame(repost_list['repost_list'])
        repost_list_df.sort_index(by=['reposts_count'], ascending=False, inplace=True)
        repost_list_df.reset_index(drop=True, inplace=True)
        repost_boom_list = []
        for index, row in repost_list_df.iterrows():
            if index < 10:
                repost_boom_list.append({'avatar': row['avatar'],
                                      'name': row['name'],
                                      'followers_count': row['followers_count'],
                                      'created_at': tran_time(row['created_at'], repost_list['current_time']),
                                      'reposts_count': row['reposts_count']})
            else:
                pass

        return HttpResponse(json.dumps({'Code': 1, 'Data': repost_boom_list}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_spread_overview(request):
    if db.repost.find({"_id": int(request.GET['mid'])}).count() > 0:
        repost_list = db.repost.find_one({"_id": int(request.GET['mid'])}, {"repost_list"})
        repost_list_df = pd.DataFrame(repost_list['repost_list'])
        repost_list_count = len(repost_list_df)
        overview_obj = {}
        under100 = round(len(repost_list_df[repost_list_df['followers_count'] <= 100]) / repost_list_count, 2)
        under500 = round(len(repost_list_df[(repost_list_df['followers_count'] <= 500) & (repost_list_df['followers_count'] > 100)]) / repost_list_count, 2)
        under1000 = round(len(repost_list_df[(repost_list_df['followers_count'] <= 1000) & (repost_list_df['followers_count'] > 500)]) / repost_list_count, 2)
        under5000 = round(len(repost_list_df[(repost_list_df['followers_count'] <= 5000) & (repost_list_df['followers_count'] > 1000)]) / repost_list_count, 2)
        under10000 = round(len(repost_list_df[(repost_list_df['followers_count'] <= 10000) & (repost_list_df['followers_count'] > 5000)]) / repost_list_count, 2)
        under100000 = round(len(repost_list_df[(repost_list_df['followers_count'] <= 100000) & (repost_list_df['followers_count'] > 10000)]) / repost_list_count, 2)
        than100000 = round(len(repost_list_df[repost_list_df['followers_count'] > 100000]) / repost_list_count, 2)
        influence = round(((under100 * 0.01 + under500 * 0.02 + under1000 * 0.05 + under5000 * 0.1 + under10000 * 0.15 + under100000 * 0.2 + than100000 * 0.47) * 100), 1)
        overview_obj.update({'用户质量': influence})

        fake_repost_count = len(repost_list_df[((repost_list_df['urank'] < 2) & (repost_list_df['followers_count'] < 2))])
        overview_obj.update({'真实用户': round(((repost_list_count - fake_repost_count) * 100 / repost_list_count), 1)})

        addv_count = len(repost_list_df[repost_list_df['verified'] == True])
        overview_obj.update({"加V": round((addv_count * 100 / repost_list_count), 1)})
        overview_obj.update({'综合评分': round((overview_obj['用户质量'] + overview_obj['真实用户'] + overview_obj['加V']) / 3, 1)})

        return HttpResponse(json.dumps({'Code': 1, 'Data': overview_obj}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

def get_spread_repost_word(request):
    if db.repost.find({"_id": int(request.GET['mid'])}).count() > 0:
        repost_list = db.repost.find_one({"_id": int(request.GET['mid'])}, {"repost_list"})
        repost_list_df = pd.DataFrame(repost_list['repost_list'])
        repost_list_df = repost_list_df[~repost_list_df['raw_text'].isin(['转发微博'])]
        tag_list = []
        for text in repost_list_df['raw_text']:
            tag_line = jieba.analyse.extract_tags(text, topK=2, allowPOS=('n'))
            if len(tag_line) > 0:
                for item in tag_line:
                    tag_list.append(item)
            else:
                pass
        tag_list_df = pd.DataFrame({'word': tag_list})
        tag_list_serise = tag_list_df['word'].value_counts()
        tag_dict_list = []
        for index in tag_list_serise.index:
            tag_dict_list.append({'name': index, 'value': int(tag_list_serise[index])})

        return HttpResponse(json.dumps({'Code': 1, 'Data': tag_dict_list}))

    else:
        return HttpResponse(json.dumps({'Code': 0, 'Msg': ''}))

