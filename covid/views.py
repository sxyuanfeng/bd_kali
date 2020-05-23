from django.shortcuts import render
from django.http import HttpResponse
import pandas as pd
import pymongo
import json
from pyecharts.charts import Map
from pyecharts import options as opts
import jieba
import re
import os
from datetime import datetime

client = pymongo.MongoClient(host='localhost', port=27017)
db = client.weibo

positive_word = ['高兴', '好受', '开心', '快活', '快乐', '庆幸', '舒畅', '舒坦', '爽快', '甜美', '甜蜜', '甜丝丝', '喜出望外',
                 '畅快', '喜悦', '喜滋滋', '心花怒放', '心旷神怡', '幸灾乐祸', '愉快', '安宁', '安然', '安详', '安心', '安慰',
                 '如意', '如愿', '顺心', '随心', '随意', '幸福', '圆满', '期待', '向往', '入迷', '入神', '心醉', '敬仰', '敬重',
                 '佩服', '仰慕', '尊敬', '尊重', '赞赏', '赞美', '感动', '宁静', '轻松', '踏实', '坦然', '心安理得', '心静',
                 '心平气和', '镇定', '镇静', '乐观', '惊喜', '受宠若惊', '欣慰', '放心', '冷静', '昂扬', '鼓舞', '激动', '兴奋',
                 '振奋', '振作', '放松', '解气', '欢畅', '欢快', '欢喜', '豁朗', '可喜', '快意', '宽畅', '狂喜', '舒心', '怡然',
                 '愉悦', '倾慕', '崇敬', '景仰', '敬慕', '钦敬', '心悦诚服', '悦服', '尊崇', '赞佩', '可人', '惬意', '遂心', '遂愿',
                 '宜人', '期求', '殷切', '快慰', '虔诚', '清爽', '欣幸']

negative_word = ['愤慨', '愤怒', '恼火', '气愤', '悲哀', '悲伤', '沉痛', '伤感', '伤心', '痛苦', '惨然', '痛心', '心酸', '胆怯',
                 '胆战心惊', '发憷', '害怕', '惊吓', '恐怖', '恐惧', '受惊', '心有余悸', '仇恨', '敌视', '敌意', '妒忌', '反感',
                 '可恨', '可恶', '厌恶', '憎恨', '别扭', '不快', '不爽', '烦闷', '难受', '窝火', '窝囊', '心烦', '厌烦', '担心',
                 '担忧', '发愁', '犯愁', '忧虑', '忧郁', '压抑', '郁闷', '无能感', '得意', '高傲', '狂妄', '优越感', '自大',
                 '自负', '抱屈', '冤枉', '浮躁', '急切', '急躁', '焦急', '焦虑', '心急', '心急火燎', '心切', '发慌', '恐慌',
                 '心慌意乱', '不好意思', '惭愧', '丢脸', '害羞', '亏心', '愧疚', '腼腆', '难堪', '难看', '怕羞', '羞耻', '羞辱',
                 '悔悟', '忏悔', '后悔', '过意不去', '内疚', '警惕', '怀疑', '困惑', '迷茫', '可惜', '藐视', '蔑视', '轻视',
                 '悲观', '沮丧', '失落感', '无望', '心寒', '孤单', '寂寞']

country_chinese_english = {}
country_ce = pd.read_excel('country_ce.xls')
for index, row in country_ce.iterrows():
    country_chinese_english.update({row['中文名称']: row['英文名称']})


def get_covid_timeline(request):
    all_covid = db.covid_19.find({}, {'created_at'})
    all_time = []
    for item in all_covid:
        time_item_list = item['created_at'].split(' ')
        new_time_item_list = [time_item_list[0], time_item_list[1], time_item_list[2], time_item_list[3], time_item_list[5]]
        new_time_item = ' '.join(new_time_item_list)
        all_time.append(datetime.strptime(new_time_item, '%c').strftime('%Y-%m-%d'))
    data = pd.DataFrame({'time': all_time})
    time_serise = data['time'].value_counts()
    time_list = []
    for i in time_serise.index:
        time_list.append({'time': str(i), 'value': int(time_serise[i])})
    return HttpResponse(json.dumps({'Code': 1, 'Data': time_list}))

def get_covid_active_user(request):
    all_covid = db.covid_19.find({}, {'name'})
    all_user = []
    for item in all_covid:
        all_user.append(item['name'])
    data = pd.DataFrame({'name': all_user})
    name_serise = data['name'].value_counts()
    name_list = []
    index = 1
    for i in name_serise.index:
        if index < 21:
            name_list.append({'name': str(i), 'value': int(name_serise[i])})
            index += 1
    return HttpResponse(json.dumps({'Code': 1, 'Data': name_list}))

def get_covid_oversea_country(request):
    file = open("country.txt", encoding='UTF-8')
    country_list = []
    while 1:
        line = file.readline()
        if not line:
            break
        else:
            country_list.append(line.replace("\n", ""))
    file.close()
    all_covid = db.covid_oversea.find({}, {'text'}).limit(500)
    all_text = ''
    for item in all_covid:
        all_text = all_text + item['text']
    jieba.load_userdict('country.txt')
    all_text = re.sub("[A-Za-z0-9\!\%\[\]\,\。\<\>\#\@\&\/\-\=\"\:\?\'\;\.\➕\_\～\，\·\！\）\（\？\{\}\【\】\°\(\)]", "", all_text)
    words = jieba.cut(all_text)
    word_list = []
    for word in words:
        if word in country_list:
            word_list.append(word)
    data = pd.DataFrame({'country': word_list})
    country_serise = data['country'].value_counts()
    country_name_list = []
    country_value_list = []
    for i in country_serise.index:
        country_name_list.append(country_chinese_english[str(i)])
        country_value_list.append(int(country_serise[i]))

    c = (
        Map(init_opts=opts.InitOpts(width="1000px", height="580px"))
            .add("国家", [list(z) for z in zip(country_name_list, country_value_list)], "world", is_roam=False,
                 is_map_symbol_show=False)
            .set_series_opts(label_opts=opts.LabelOpts(is_show=False))
            .set_global_opts(
            title_opts=opts.TitleOpts(title=""),
            visualmap_opts=opts.VisualMapOpts(
                item_height=150,
                item_width=20,
                pos_left=100,
                pos_bottom=50
            ),
            legend_opts=opts.LegendOpts(
                is_show=False
            )
        )
    )

    return HttpResponse(json.dumps({'Code': 1, 'Data': c.render_embed()}))

def get_covid_world_hot(request):
    all_covid = db.covid_oversea_diary.find({}, {'text'}).limit(500)
    all_text = ''
    for item in all_covid:
        all_text = all_text + item['text']
    new_all_text = ''
    for n in range(0, len(all_text) - 1):
        if '\u4e00' <= all_text[n] <= '\u9fff':
            new_all_text += all_text[n]
    words = jieba.cut(new_all_text)
    word_list = []
    for word in words:
        word_list.append(word)
    word_list_df = pd.DataFrame({'word': word_list})
    stopwords = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/stopword.txt'), index_col=False,
                            quoting=3, sep='，', names=['stopword'],
                            encoding="utf-8")
    word_list_df = word_list_df[~word_list_df['word'].isin(stopwords.stopword)]
    wordcloud_list = []
    word_serise = word_list_df['word'].value_counts()
    for index in word_serise.index:
        wordcloud_list.append({'name': index, 'value': int(word_serise[index])})
    return HttpResponse(json.dumps({'Code': 1, 'Data': wordcloud_list}))

def get_wuhan_hot(request):
    all_covid = db.covid_wuhan_diary.find({}, {'text'}).limit(500)
    all_text = ''
    for item in all_covid:
        all_text = all_text + item['text']
    new_all_text = ''
    for n in range(0, len(all_text) - 1):
        if '\u4e00' <= all_text[n] <= '\u9fff':
            new_all_text += all_text[n]
    words = jieba.cut(new_all_text)
    word_list = []
    for word in words:
        word_list.append(word)
    word_list_df = pd.DataFrame({'word': word_list})
    stopwords = pd.read_csv(os.path.join(os.path.dirname(os.path.abspath(__file__)) + '/stopword.txt'), index_col=False,
                            quoting=3, sep='，', names=['stopword'],
                            encoding="utf-8")
    word_list_df = word_list_df[~word_list_df['word'].isin(stopwords.stopword)]
    wordcloud_list = []
    word_serise = word_list_df['word'].value_counts()
    for index in word_serise.index:
        wordcloud_list.append({'name': index, 'value': int(word_serise[index])})
    return HttpResponse(json.dumps({'Code': 1, 'Data': wordcloud_list}))

def get_oversea_emotion(request):
    all_covid = db.covid_oversea_diary.find({}, {'text'}).limit(500)
    all_text = ''
    for item in all_covid:
        all_text = all_text + item['text']
    new_all_text = ''
    for n in range(0, len(all_text) - 1):
        if '\u4e00' <= all_text[n] <= '\u9fff':
            new_all_text += all_text[n]
    jieba.load_userdict('emotion.txt')
    words = jieba.cut(new_all_text)
    positive_word_list = []
    negative_word_list = []
    for word in words:
        if word in positive_word:
            positive_word_list.append(word)
        elif word in negative_word:
            negative_word_list.append(word)
    wordcloud_list = [{'item': '积极', 'percent': round((len(positive_word_list)*100 / (len(positive_word_list) + len(negative_word_list))), 2)},
                      {'item': '消极', 'percent': round((len(negative_word_list)*100 / (len(positive_word_list) + len(negative_word_list))), 2)}]
    return HttpResponse(json.dumps({'Code': 1, 'Data': wordcloud_list}))

def get_wuhan_emotion(request):
    all_covid = db.covid_wuhan_diary.find({}, {'text'}).limit(500)
    all_text = ''
    for item in all_covid:
        all_text = all_text + item['text']
    new_all_text = ''
    for n in range(0, len(all_text) - 1):
        if '\u4e00' <= all_text[n] <= '\u9fff':
            new_all_text += all_text[n]
    jieba.load_userdict('emotion.txt')
    words = jieba.cut(new_all_text)
    positive_word_list = []
    negative_word_list = []
    for word in words:
        if word in positive_word:
            positive_word_list.append(word)
        elif word in negative_word:
            negative_word_list.append(word)
    wordcloud_list = [{'item': '积极', 'percent': round((len(positive_word_list)*100 / (len(positive_word_list) + len(negative_word_list))), 2)},
                      {'item': '消极', 'percent': round((len(negative_word_list)*100 / (len(positive_word_list) + len(negative_word_list))), 2)}]
    return HttpResponse(json.dumps({'Code': 1, 'Data': wordcloud_list}))

