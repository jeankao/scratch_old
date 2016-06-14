# -*- coding: UTF-8 -*-
from django.conf.urls import url
from django.contrib.auth.decorators import login_required
from . import views
from teacher.views import ClassroomListView, ClassroomCreateView
#, ClassroomDetails

urlpatterns = [
    # post views
    url(r'^classroom/$', login_required(ClassroomListView.as_view()), name='classroom-list'),
    #url(r'^classroom/all/$', login_required(ClassroomList.as_view(all_items=True)), name='classroom-list-all'),
    url(r'^classroom/add/$', login_required(ClassroomCreateView.as_view()), name='classroom-add'),
    url(r'^classroom/edit/(?P<classroom_id>\d+)/$', 'teacher.views.classroom_edit', name='classroom-edit'),
    #url(r'^assistant_cancle/(?P<classroom_id>\d+)/(?P<user_id>\d+)/(?P<lesson>\d+)/$', 'teacher.views.assistant_cancle'),  
    # 退選
    url(r'^unenroll/(?P<enroll_id>\d+)/(?P<classroom_id>\d+)/$', 'teacher.views.unenroll'),  	
    
    #url(r'^assistant/(?P<classroom_id>\d+)/(?P<user_id>\d+)/(?P<lesson>\d+)/$', 'teacher.views.assistant'), 
    #url(r'^score_peer/(?P<index>\d+)/(?P<classroom_id>\d+)/(?P<group>\d+)/$', 'teacher.views.score_peer'),     
    #url(r'^scoring/(?P<classroom_id>[^/]+)/(?P<user_id>\d+)/(?P<index>\d+)/$', 'teacher.views.scoring'),     
    #url(r'^score/(?P<classroom_id>\d+)/(?P<index>\d+)/$', 'teacher.views.score'),       
    #url(r'^work/(?P<classroom_id>\d+)/$', 'teacher.views.work'),    
    #url(r'^work/group/(?P<lesson>\d+)/(?P<classroom_id>\d+)/$', 'teacher.views.work_group'),   	
    #url(r'^exam/(?P<classroom_id>\d+)/$', 'teacher.views.exam_list'),
	#url(r'^exam_detail/(?P<student_id>\d+)/(?P<exam_id>\d+)/$', 'teacher.views.exam_detail'), 
    #url(r'^memo/(?P<classroom_id>\d+)/$', 'teacher.views.memo'),	
	#url(r'^check/(?P<user_id>[^/]+)/(?P<unit>[^/]+)/(?P<classroom_id>\d+)/$', 'teacher.views.check'), 	
    #url(r'^grade/(?P<classroom_id>\d+)/$', 'teacher.views.grade'),
    #url(r'^grade1/(?P<classroom_id>\d+)/$', 'teacher.views.grade_unit1'),
    #url(r'^grade2/(?P<classroom_id>\d+)/$', 'teacher.views.grade_unit2'),
    #url(r'^grade3/(?P<classroom_id>\d+)/$', 'teacher.views.grade_unit3'),
    #url(r'^grade4/(?P<classroom_id>\d+)/$', 'teacher.views.grade_unit4'),	
	
]