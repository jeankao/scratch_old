# -*- coding: UTF-8 -*-
from django.conf.urls import url
from . import views

urlpatterns = [
    # post views
    url(r'^$', views.dashboard, name='dashboard'),    
    #登入
    url(r'^login/$', views.user_login, name='login'),
    #登出
    url(r'^logout/$', 'django.contrib.auth.views.logout'),
    url(r'^suss_logout/(?P<user_id>\d+)/$', views.suss_logout),    
    #列出所有帳號
    url(r'^userlist/$', views.UserListView.as_view()),      
    #註冊帳號
    url(r'^register/$', views.register, name='register'),   
    #個人檔案
    url(r'^profile/(?P<user_id>\d+)/$', views.profile),    
    #修改密碼
    url(r'^password-change/$', 'django.contrib.auth.views.password_change', name='password_change'),
    url(r'^password-change/done/$', 'django.contrib.auth.views.password_change_done', name='password_change_done'),    
    url(r'^password/(?P<user_id>\d+)/$', views.password),
    #修改真實姓名
    url(r'^realname/(?P<user_id>\d+)/$', views.adminrealname),    
    url(r'^realname/$', views.realname, name='realname'),   
    #積分記錄
    url(r'^log/(?P<kind>\d+)/(?P<user_id>\d+)/$', views.LogListView.as_view()),	    
    #設定教師
    url(r'^teacher/make/$', views.make, name='make'),    
    #系統事件記錄
    url(r'^event/(?P<user_id>\d+)/$', views.EventListView.as_view()),            
]
