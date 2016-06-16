# -*- coding: UTF-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views
from student.views import RankListView

urlpatterns = [
    # 作業進度查詢
    url(r'^progress/(?P<classroom_id>\d+)/(?P<unit>\d+)$', 'student.views.progress'),   

    # 作業上傳
    url(r'^work/(?P<classroom_id>\d+)/$', 'student.views.work'),       
    url(r'^submit/(?P<index>\d+)/$', 'student.views.submit'),       
    url(r'^submitall/(?P<index>\d+)/$', 'student.views.submitall'),      
    # 同學
    url(r'^classmate/(?P<classroom_id>\d+)/$', 'student.views.classmate'), 
    # 分組
    url(r'^group/enroll/(?P<classroom_id>[^/]+)/(?P<group_id>[^/]+)/$', 'student.views.group_enroll'),    
    url(r'^group/add/(?P<classroom_id>[^/]+)/$', 'student.views.group_add'),     
    url(r'^group/(?P<classroom_id>[^/]+)/$', 'student.views.group'),   
    url(r'^group/open/(?P<classroom_id>[^/]+)/(?P<action>[^/]+)/$', 'student.views.group_open'),     
	url(r'^group/delete/(?P<group_id>[^/]+)/(?P<classroom_id>[^/]+)/$', 'student.views.group_delete'), 
    # 選課
    url(r'^classroom/enroll/(?P<classroom_id>[^/]+)/$', 'student.views.classroom_enroll'),      
    url(r'^classroom/add/$', 'student.views.classroom_add'),  
    url(r'^classroom/$', 'student.views.classroom'),
	url(r'^classroom/seat/(?P<enroll_id>\d+)/(?P<classroom_id>\d+)/$', 'student.views.seat_edit', name='seat_edit'),
   
    # 課程  
    url(r'^lesson/(?P<lesson>[^/]+)/$', 'student.views.lesson'),    
    url(r'^lessons/(?P<lesson>[^/]+)/$', 'student.views.lessons'),   
    url(r'^lesson/log/(?P<lesson>[^/]+)/$', 'student.views.lesson_log'),    
    #查詢該作業分組小老師
    url(r'^group/work/(?P<lesson>[^/]+)/(?P<classroom_id>[^/]+)$', 'student.views.work_group'),  
    #查詢該作業所有同學心得
    url(r'^memo/(?P<classroom_id>[^/]+)/(?P<index>[^/]+)/$', 'student.views.memo'),   
    #url(r'^exam/$', 'student.views.exam'),      
    #url(r'^exam_check/$', 'student.views.exam_check'),     
    #url(r'^exam/score/$', 'student.views.exam_score'),  	

    #積分排行榜
    url(r'^rank/(?P<kind>[^/]+)/(?P<classroom_id>[^/]+)/$', views.RankListView.as_view(), name='rank'), 
    
    #查詢某班級所有同學心得		
    url(r'^memo_all/(?P<classroom_id>[^/]+)$', 'student.views.memo_all'),  	
    url(r'^memo_show/(?P<user_id>\d+)/(?P<unit>\d+)/(?P<classroom_id>[^/]+)/(?P<score>[^/]+)/$', 'student.views.memo_show'), 	
]
