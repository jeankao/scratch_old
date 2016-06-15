from django.conf.urls import url
from . import views
from django.contrib.auth.decorators import login_required
from show.views import ShowUpdateView, ReviewListView, RankListView, TeacherListView, GalleryListView
urlpatterns = [
    # post views
	url(r'^group/delete/(?P<group_id>[^/]+)/(?P<classroom_id>[^/]+)/$', 'show.views.group_delete'), 	
    url(r'^group/enroll/(?P<classroom_id>[^/]+)/(?P<group_id>[^/]+)/$', 'show.views.group_enroll'),   
    url(r'^group/open/(?P<classroom_id>[^/]+)/(?P<action>[^/]+)/$', 'show.views.group_open'), 	
    url(r'^group/add/(?P<classroom_id>[^/]+)/$', 'show.views.group_add'),     
    url(r'^group/(?P<classroom_id>[^/]+)/$', 'show.views.group'),    
    #url(r'^group/nogroup/(?P<classroom_id>[^/]+)/$', 'show.views.group_nogroup'), 
    url(r'^group/submit/(?P<group_show>[^/]+)/(?P<classroom_id>[^/]+)/$', login_required(ShowUpdateView.as_view())), 
    #url(r'^list/(?P<classroom_id>[^/]+)/$', 'show.views.list'),    
    url(r'^detail/(?P<show_id>[^/]+)/$', 'show.views.detail'),  	
    url(r'^score/(?P<show_id>[^/]+)/$', login_required(ReviewListView.as_view())),  	
    url(r'^rank/(?P<rank_id>[^/]+)/(?P<classroom_id>[^/]+)/$', login_required(RankListView.as_view())), 
    url(r'^teacher/(?P<classroom_id>[^/]+)/$', login_required(TeacherListView.as_view())),	
    url(r'^gallery/$', GalleryListView.as_view()),    
    url(r'^gallery/make/$', 'show.views.make', name='make'),   	
    url(r'^gallery/(?P<show_id>[^/]+)/$', 'show.views.GalleryDetail'),  	
]