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

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/masterbaseinfo', av_views.get_master_base_info),
    path('api/fangender/', av_views.get_fan_gender),
    path('api/followgender', av_views.get_follow_gender),
    path('api/followrank', av_views.get_follow_rank),
    path('api/fanrank', av_views.get_fan_rank),
    path('api/followfollowcount', av_views.get_follow_follow_count),
    path('api/followfollowercount', av_views.get_follow_follower_count),
    path('api/fanfollowcount', av_views.get_fan_follow_count),
    path('api/fanfollowercount', av_views.get_fan_follower_count),
    path('api/followstatuscount', av_views.get_follow_status_count),
    path('api/fanstatuscount', av_views.get_fan_status_count),
    path('api/masterstatusestimeline', av_views.get_master_statuses_timeline),
    path('api/masterstatusesindex', av_views.get_master_statuses_index),

    path('api/hottag', ch_views.get_hottag),

    path('api/repostchart', re_views.get_repost_chart)
]
