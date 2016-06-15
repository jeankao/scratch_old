# -*- coding: utf-8 -*-
from __future__ import division
from django.shortcuts import render
from show.models import ShowGroup, ShowReview
from django.core.exceptions import ObjectDoesNotExist
from student.models import Enroll
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from show.forms import GroupForm, ShowForm, ReviewForm
from teacher.models import Classroom
from django.views.generic.edit import UpdateView
from django.views.generic import ListView, DetailView, CreateView
from django.http import HttpResponseRedirect
from django.utils import timezone
from django.db.models import Sum
from account.models import Profile, PointHistory, Log
from account.avatar import *
from django.core.exceptions import ObjectDoesNotExist
from collections import OrderedDict
from django.http import JsonResponse
def is_teacher(user, classroom_id):
    return user.groups.filter(name='teacher').exists() and Classroom.objects.filter(teacher_id=user.id, id=classroom_id).exists()

# 所有組別
def group(request, classroom_id):
        classroom_name = Classroom.objects.get(id=classroom_id).name    
        student_groups = []
        group_show_open = Classroom.objects.get(id=classroom_id).group_show_open
        groups = ShowGroup.objects.filter(classroom_id=classroom_id)
        try:
                student_group = Enroll.objects.get(student_id=request.user.id, classroom_id=classroom_id).group_show
        except ObjectDoesNotExist :
                student_group = []		
        for group in groups:
            enrolls = Enroll.objects.filter(classroom_id=classroom_id, group_show=group.id)
            student_groups.append([group, enrolls])
            
        #找出尚未分組的學生
        def getKey(custom):
            return custom.seat	
        enrolls = Enroll.objects.filter(classroom_id=classroom_id)
        nogroup = []
        for enroll in enrolls:
            if enroll.group_show == 0 :
		        nogroup.append(enroll)		
	    nogroup = sorted(nogroup, key=getKey)            
            
        # 記錄系統事件
        log = Log(user_id=request.user.id, event=u'查看創意秀組別<'+classroom_name+'>')
        log.save()              
        return render_to_response('show/group.html', {'nogroup': nogroup, 'group_show_open':group_show_open, 'teacher':is_teacher(request.user, classroom_id), 'student_groups':student_groups, 'classroom_id':classroom_id, 'student_group':student_group}, context_instance=RequestContext(request))

# 新增組別
def group_add(request, classroom_id):
        classroom_name = Classroom.objects.get(id=classroom_id).name
        if request.method == 'POST':
            form = GroupForm(request.POST)
            if form.is_valid():
                group = ShowGroup(name=form.cleaned_data['name'],classroom_id=int(classroom_id))
                group.save()
                enrolls = Enroll.objects.filter(classroom_id=classroom_id)
                for enroll in enrolls :
                    review = ShowReview(show_id=group.id, student_id=enroll.student_id)
                    review.save()
                    
                # 記錄系統事件
                log = Log(user_id=request.user.id, event=u'新增創意秀組別<'+group.name+'><'+classroom_name+'>')
                log.save()                      
                return redirect('/show/group/'+classroom_id)
        else:
            form = GroupForm()
        return render_to_response('show/group_add.html', {'form':form}, context_instance=RequestContext(request))

# 加入組別
def group_enroll(request, classroom_id,  group_id):
        classroom_name = Classroom.objects.get(id=classroom_id).name    
        group_name = ShowGroup(id=group_id).name
        enroll = Enroll.objects.filter(student_id=request.user.id, classroom_id=classroom_id)
        enroll.update(group_show=group_id)
        # 記錄系統事件
        log = Log(user_id=request.user.id, event=u'加入創意秀組別<'+group_name+'><'+classroom_name+'>')
        log.save()                      
        return redirect('/show/group/'+classroom_id)

# 刪除組別
def group_delete(request, group_id, classroom_id):
        classroom_name = Classroom.objects.get(id=classroom_id).name    
        group_name = ShowGroup(id=group_id).name    
        group = ShowGroup.objects.get(id=group_id)
        group.delete()
        # 記錄系統事件
        log = Log(user_id=request.user.id, event=u'刪除創意秀組別<'+group_name+'><'+classroom_name+'>')
        log.save()     
        return redirect('/show/group/'+classroom_id)    

# 開放選組
def group_open(request, classroom_id, action):
    classroom = Classroom.objects.get(id=classroom_id)
    if action == "1":
        classroom.group_show_open=True
        classroom.save()
        # 記錄系統事件
        log = Log(user_id=request.user.id, event=u'開放創意秀選組<'+classroom.name+'>')
        log.save()         
    else :
        classroom.group_show_open=False
        classroom.save()
        # 記錄系統事件
        log = Log(user_id=request.user.id, event=u'關閉創意秀選組<'+classroom.name+'>')
        log.save()          
    return redirect('/show/group/'+classroom_id)  	
	

# 上傳創意秀
class ShowUpdateView(UpdateView):
    #model = ShowGroup
    #fields = ['name', 'title','number']
    form_class = ShowForm
    #template_name_suffix = '_update_form'
    #success_url = "/show/group/2"

    def get(self, request, **kwargs):
        self.object = ShowGroup.objects.get(id=self.kwargs['group_show'])
        members = Enroll.objects.filter(group_show=self.kwargs['group_show'])
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(object=self.object, form=form, members=members)
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        obj = ShowGroup.objects.get(id=self.kwargs['group_show'])
        return obj
		
    def form_valid(self, form):
        obj = form.save(commit=False)
        
        # 限制小組成員才能上傳
        members = Enroll.objects.filter(group_show=self.kwargs['group_show'])
        is_member = False
        for member in members :
            if self.request.user.id == member.student_id:
                is_member = True
        
        if is_member :        
            if obj.done == False:
                for member in members:			
			        # credit
                    update_avatar(member, 4, 3)
                    # History
                    history = PointHistory(user_id=member.student_id, kind=4, message=u'3分--繳交創意秀<'+obj.title+'>', url='/show/detail/'+str(obj.id))
                    history.save()
            #save object
            obj.publish = timezone.now()
            obj.done = True
            obj.save()
        
            # 記錄系統事件
            log = Log(user_id=self.request.user.id, event=u'上傳創意秀<'+obj.name+'>')
            log.save()
            return redirect('/show/group/'+self.kwargs['classroom_id'])
        else :
            return redirect('homepage')

# 評分
class ReviewUpdateView(UpdateView):
    model = ShowReview
    form_class = ReviewForm
    template_name_suffix = '_review'

    def get(self, request, **kwargs):
        show = ShowGroup.objects.get(id=self.kwargs['show_id'])
        self.object = ShowReview.objects.get(show_id=self.kwargs['show_id'], student_id=self.request.user.id)
        reviews = ShowReview.objects.filter(show_id=self.kwargs['show_id'], done=True)
        score1 = reviews.aggregate(Sum('score1')).values()[0]
        score2 = reviews.aggregate(Sum('score2')).values()[0]
        score3 = reviews.aggregate(Sum('score3')).values()[0]
        score = [self.object.score1, self.object.score2,self.object.score3]
        if reviews.count() > 0 :
            scores = [score1/ reviews.count(), score2/ reviews.count(), score3/ reviews.count(),  reviews.count()]
        else :
            scores = [0,0,0,0]
        members = Enroll.objects.filter(group_show=self.kwargs['show_id'])
        form_class = self.get_form_class()
        form = self.get_form(form_class)
        context = self.get_context_data(show=show, form=form, members=members, review=self.object, scores=scores, score=score, reviews=reviews)
        return self.render_to_response(context)

    def get_object(self, queryset=None):
        obj = ShowReview.objects.get(show_id=self.kwargs['show_id'], student_id=self.request.user.id)
        return obj
	
    def form_valid(self, form):
        show = ShowGroup.objects.get(id=self.kwargs['show_id'])        
        #save object
        obj = form.save(commit=False)
        if obj.done == False:
            classroom_id = ShowGroup.objects.get(id=self.kwargs['show_id']).classroom_id
            member = Enroll.objects.get(classroom_id=classroom_id, student_id=self.request.user.id)
            # credit
            update_avatar(member, 4, 1)
            # History
            show = ShowGroup.objects.get(id=self.kwargs['show_id'])			
            history = PointHistory(user_id=member.student_id, kind=4, message=u'1分--評分創意秀<'+show.title+'>', url='/show/detail/'+str(show.id))
            history.save()
        obj.publish = timezone.now()
        obj.done = True
        obj.save()
        # 記錄系統事件
        log = Log(user_id=self.request.user.id, event=u'評分創意秀<'+show.name+'>')
        log.save()        
        return redirect('/show/detail/'+self.kwargs['show_id'])

# 所有同學的評分		
class ReviewListView(ListView):
    context_object_name = 'reviews'
    template_name = 'show/reviewlist.html'
    def get_queryset(self):
        show = ShowGroup.objects.get(id=self.kwargs['show_id'])        
        # 記錄系統事件
        log = Log(user_id=self.request.user.id, event=u'查看創意秀所有評分<'+show.name+'>')
        log.save()  
        return ShowReview.objects.filter(show_id=self.kwargs['show_id'])  		

# 排行榜
class RankListView(ListView):
    context_object_name = 'lists'
    template_name = 'show/ranklist.html'
    def get_queryset(self):
        def getKey(custom):
            return custom[3]	
        lists = []
        rank = 0
        shows = ShowGroup.objects.filter(classroom_id=self.kwargs['classroom_id'])
        for show in shows :
            rank = rank + 1
            students = Enroll.objects.filter(group_show=show.id)
            reviews = ShowReview.objects.filter(show_id=show.id, done=True)	
            if reviews.count() > 0 :			
                score = reviews.aggregate(Sum('score'+self.kwargs['rank_id'])).values()[0]/reviews.count()
            else :
                score = 0
            lists.append([rank, show, students, score, reviews.count(), self.kwargs['rank_id']])
            lists= sorted(lists, key=getKey, reverse=True)
        # 記錄系統事件
        log = Log(user_id=self.request.user.id, event=u'查看創意秀排行榜<'+self.kwargs['rank_id']+'>')
        log.save()  
        return lists

# 教師查看創意秀評分情況
class TeacherListView(ListView):
    context_object_name = 'lists'
    template_name = 'show/teacherlist.html'
    def get_queryset(self):
        lists = {}
        counter = 0
        enrolls = Enroll.objects.filter(classroom_id=self.kwargs['classroom_id']).order_by('seat')
        classroom_name = Classroom.objects.get(id=self.kwargs['classroom_id']).name
        for enroll in enrolls:			
            lists[enroll.id] = []		
            shows = ShowGroup.objects.filter(classroom_id=self.kwargs['classroom_id'])
            for show in shows:
                members = Enroll.objects.filter(group_show=show.id)
                try: 
                    review = ShowReview.objects.get(show_id=show.id, student_id=enroll.student_id)
                    #lists[enroll.id].append([enroll, review, show, members])
                    lists[enroll.id].append([enroll, review, show, members])
                except ObjectDoesNotExist:
                    pass			
		lists = OrderedDict(sorted(lists.items(), key=lambda x: x[1][0][0].seat))
        # 記錄系統事件
        log = Log(user_id=self.request.user.id, event=u'查看創意秀評分狀況<'+classroom_name+'>')
        log.save()  
		
        return lists		

# 藝廊                  
class GalleryListView(ListView):
    context_object_name = 'lists'
    paginate_by = 3
    template_name = 'show/gallerylist.html'
    def get_queryset(self):
        # 記錄系統事件
        log = Log(user_id=self.request.user.id, event=u'查看藝廊')
        log.save() 

        return ShowGroup.objects.filter(open=True).order_by('-publish')
		
# 查看藝郎某項目
def GalleryDetail(request, show_id):
    show = ShowGroup.objects.get(id=show_id)
    reviews = ShowReview.objects.filter(show_id=show_id, done=True)
    score1 = reviews.aggregate(Sum('score1')).values()[0]
    score2 = reviews.aggregate(Sum('score2')).values()[0]
    score3 = reviews.aggregate(Sum('score3')).values()[0]
    if reviews.count() > 0 :
        scores = [score1/ reviews.count(), score2/ reviews.count(), score3/ reviews.count(),  reviews.count()]
    else :
        scores = [0,0,0,0]
    members = Enroll.objects.filter(group_show=show_id)
    #context = self.get_context_data(show=show, form=form, members=members, review=self.object, scores=scores, score=score, reviews=reviews)
    # 記錄系統事件
    log = Log(user_id=self.request.user.id, event=u'查看藝廊<'+show.name+'>')
    log.save() 
    
    return render(request, 'show/gallerydetail.html', {'show': show, 'members':members, 'scores':scores, 'reviews':reviews, 'teacher':is_teacher(request.user, show.classroom_id)})

# 將創意秀開放到藝廊
def make(request):
    show_id = request.POST.get('showid')
    action = request.POST.get('action')
    if show_id and action :
        try :
            show = ShowGroup.objects.get(id=show_id)	
            if action == 'open':
                show.open = True
                # 記錄系統事件
                log = Log(user_id=request.user.id, event=u'藝廊上架<'+show.name+'>')
                log.save()                 
            else:
                show.open = False		
                # 記錄系統事件
                log = Log(user_id=request.user.id, event=u'藝廊下架<'+show.name+'>')
                log.save()                          
            show.save()
        except ObjectDoesNotExist :
            pass
        return JsonResponse({'status':'ok'}, safe=False)
    else:
        return JsonResponse({'status':'ko'}, safe=False)	