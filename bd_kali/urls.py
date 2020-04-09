"""bd_kali URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/2.2/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import path
from accountvalue import views as av_views
from channel import views as ch_views
from repost import views as re_views
from mblog import views as mb_views

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/masterbaseinfo', av_views.get_master_base_info),
    path('api/fangender/', av_views.get_fan_gender),
    path('api/fanaddv', av_views.get_fan_addv),
    path('api/alivefans', av_views.get_alive_fans),
    path('api/truefans', av_views.get_true_fans),
    path('api/fanmeasure', av_views.get_fan_measure),
    path('api/fanverifiedtype', av_views.get_fan_verified_type),
    path('api/fanmbrank', av_views.get_fan_mbrank),
    #path('api/fanarea', av_views.get_fan_area),
    path('api/followgender', av_views.get_follow_gender),
    path('api/followaddv', av_views.get_follow_addv),
    path('api/followmeasure', av_views.get_follow_measure),
    path('api/followverifiedtype', av_views.get_follow_verified_type),
    path('api/followmbrank', av_views.get_follow_mbrank),
    #path('api/followarea', av_views.get_follow_area),
    path('api/statusestimeline', av_views.get_statuses_timeline),
    path('api/statusesactivetime', av_views.get_statuses_active_time),
    path('api/statusesindex', av_views.get_statuses_index),
    path('api/statusesretweet', av_views.get_statuses_retweet),
    path('api/statusessource', av_views.get_statuses_source),
    path('api/accountoverview', av_views.get_account_overview),

    path('api/hottag', ch_views.get_hottag),

    path('api/repostchart', re_views.get_repost_chart),
    path('api/repostcard', re_views.get_repost_card),

    path('api/mbloginfo', mb_views.get_mblog_info),
    path('api/participantrepostfrom', mb_views.get_participant_repost_from),
    path('api/participantrepostverified', mb_views.get_participant_repost_verified),
    path('api/participantrepostgender', mb_views.get_participant_repost_gender),
    path('api/participantrepostaddv', mb_views.get_participant_repost_addv),
    path('api/participantreposttrue', mb_views.get_participant_repost_true),
    path('api/participantrepostmeasure', mb_views.get_participant_repost_measure),
    path('api/spreadtimeline', mb_views.get_spread_timeline),
    path('api/spreadrepostrelative', mb_views.get_spread_repost_relative),
    path('api/spreadrepostdeep', mb_views.get_spread_repost_deep),
    path('api/spreadrepostkeyuser', mb_views.get_spread_repost_keyuser),
    path('api/spreadrepostkeyuserroad', mb_views.get_spread_repost_keyuser_road),
    path('api/spreadrepostboom', mb_views.get_spread_repost_bomm),
    path('api/spreadoverview', mb_views.get_spread_overview),
    path('api/repostwordcloud', mb_views.get_spread_repost_word),
]
