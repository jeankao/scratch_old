# -*- coding: UTF-8 -*-
#from django.shortcuts import render
from django.shortcuts import render_to_response, redirect
#from django.contrib.auth.models import User
#from django.http import HttpResponse
#from django.contrib.auth import authenticate, login
from django.template import RequestContext
#from django.contrib.auth.decorators import login_required
#from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView, CreateView
#from django.core.exceptions import ObjectDoesNotExist
#from django.contrib.auth.models import Group
from teacher.models import Classroom
from student.models import Enroll
from account.models import Log
#from student.models import Enroll, Work, EnrollGroup, Assistant, Exam
from .forms import ClassroomForm
#, ScoreForm,  CheckForm1, CheckForm2, CheckForm3, CheckForm4
#from django.views.generic.edit import ModelFormMixin
#from django.http import HttpResponseRedirect
#from student.lesson import *
#from account.avatar import *
#from account.models import Profile, PointHistory
#from django.contrib.auth.decorators import login_required, user_passes_test

# 判斷是否為授課教師
def is_teacher(user, classroom_id):
    return user.groups.filter(name='teacher').exists() and Classroom.objects.filter(teacher_id=user.id, id=classroom_id).exists()

# 列出所有課程
class ClassroomListView(ListView):
    model = Classroom
    context_object_name = 'classrooms'
    paginate_by = 20
    def get_queryset(self):
        # 記錄系統事件
        log = Log(user_id=self.request.user.id, event='查看任課班級')
        log.save()        
        queryset = Classroom.objects.filter(teacher_id=self.request.user.id).order_by("-id")
        return queryset
        
#新增一個課程
class ClassroomCreateView(CreateView):
    model = Classroom
    form_class = ClassroomForm
    def form_valid(self, form):
        self.object = form.save(commit=False)
        self.object.teacher_id = self.request.user.id
        self.object.save()
        # 將教師設為0號學生
        enroll = Enroll(classroom_id=self.object.id, student_id=self.request.user.id, seat=0)
        enroll.save()     
        # 記錄系統事件
        log = Log(user_id=self.request.user.id, event=u'新增任課班級<'+self.object.name+'>')
        log.save()                
        return redirect("/teacher/classroom")        
        
# 修改選課密碼
def classroom_edit(request, classroom_id):
    # 限本班任課教師
    if not is_teacher(request.user, classroom_id):
        return redirect("homepage")
    classroom = Classroom.objects.get(id=classroom_id)
    if request.method == 'POST':
        form = ClassroomForm(request.POST)
        if form.is_valid():
            classroom.name =form.cleaned_data['name']
            classroom.password = form.cleaned_data['password']
            classroom.save()
            # 記錄系統事件
            log = Log(user_id=request.user.id, event=u'修改選課密碼<'+classroom.name+'>')
            log.save()                    
            return redirect('/teacher/classroom')
    else:
        form = ClassroomForm(instance=classroom)

    return render_to_response('form.html',{'form': form}, context_instance=RequestContext(request))        
    
# 退選
def unenroll(request, enroll_id, classroom_id):
    enroll = Enroll.objects.get(id=enroll_id)
    enroll.delete()
    classroom_name = Classroom.objects.get(id=classroom_id).name
    # 記錄系統事件
    log = Log(user_id=request.user.id, event=u'退選<'+classroom_name+'>')
    log.save()       
    return redirect('/student/classmate/'+classroom_id)  
    