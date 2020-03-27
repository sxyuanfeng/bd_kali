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
    path('api/fanaddv', av_views.get_fan_addv),
    path('api/alivefans', av_views.get_alive_fans),
    path('api/truefans', av_views.get_true_fans),
    path('api/fanmeasure', av_views.get_fan_measure),
    path('api/fanverifiedtype', av_views.get_fan_verified_type),
    path('api/followgender', av_views.get_follow_gender),
    path('api/followaddv', av_views.get_follow_addv),
    path('api/followmeasure', av_views.get_follow_measure),
    path('api/followverifiedtype', av_views.get_follow_verified_type),
    path('api/masterstatusestimeline', av_views.get_master_statuses_timeline),

    path('api/hottag', ch_views.get_hottag),

    path('api/repostchart', re_views.get_repost_chart),
    path('api/repostcard', re_views.get_repost_card),
]
