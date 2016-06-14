# -*- coding: UTF-8 -*-
#from django.shortcuts import render
from django.shortcuts import render_to_response, redirect
#from django.contrib.auth.models import User
#from django.http import HttpResponse
#from django.contrib.auth import authenticate, login
from django.template import RequestContext
#from django.contrib.auth.decorators import login_required
#from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
#from django.views.generic import ListView
from django.core.exceptions import ObjectDoesNotExist
from django.contrib.auth.models import Group
from teacher.models import Classroom
from student.models import Enroll, EnrollGroup, Work, Assistant, Exam
from account.models import Log
from certificate.models import Certificate
from student.forms import EnrollForm, GroupForm, SubmitForm, SeatForm
#from django.utils import timezone
from student.lesson import *
#from account.avatar import *
#from django.db import IntegrityError
#from account.models import Profile, PointHistory
#from django.http import JsonResponse

# 判斷是否為授課教師
def is_teacher(user, classroom_id):
    return  user.groups.filter(name='teacher').exists() and Classroom.objects.filter(teacher_id=user.id, id=classroom_id).exists()


# 查看班級學生
def classmate(request, classroom_id):
        enrolls = Enroll.objects.filter(classroom_id=classroom_id).order_by("seat")
        enroll_group = []
        classroom_name=Classroom.objects.get(id=classroom_id).name
        for enroll in enrolls:
            if enroll.group > 0 :
                enroll_group.append([enroll, EnrollGroup.objects.get(id=enroll.group).name])
            else :
                enroll_group.append([enroll, "沒有組別"])
        # 記錄系統事件
        log = Log(user_id=request.user.id, event=u'查看班級學生<'+classroom_name+'>')
        log.save()                        
        return render_to_response('student/classmate.html', {'classroom_name':classroom_name, 'enroll_group':enroll_group}, context_instance=RequestContext(request))

# 顯示所有組別
def group(request, classroom_id):
        student_groups = []
        classroom_name = Classroom.objects.get(id=classroom_id).name
        group_open = Classroom.objects.get(id=classroom_id).group_open        
        groups = EnrollGroup.objects.filter(classroom_id=classroom_id)
        try:
                student_group = Enroll.objects.get(student_id=request.user.id, classroom_id=classroom_id).group
        except ObjectDoesNotExist :
                student_group = []		
        for group in groups:
            enrolls = Enroll.objects.filter(classroom_id=classroom_id, group=group.id)
            student_groups.append([group, enrolls])
            
        #找出尚未分組的學生
        def getKey(custom):
            return custom.seat	
        enrolls = Enroll.objects.filter(classroom_id=classroom_id)
        nogroup = []
        for enroll in enrolls:
            if enroll.group == 0 :
		        nogroup.append(enroll)		
	    nogroup = sorted(nogroup, key=getKey)

        # 記錄系統事件
        log = Log(user_id=request.user.id, event=u'查看分組<'+classroom_name+'>')
        log.save()        
        return render_to_response('student/group.html', {'nogroup': nogroup, 'group_open': group_open, 'student_groups':student_groups, 'classroom_id':classroom_id, 'student_group':student_group, 'teacher': is_teacher(request.user, classroom_id)}, context_instance=RequestContext(request))

# 新增組別
def group_add(request, classroom_id):
        if request.method == 'POST':
            classroom_name = Classroom.objects.get(id=classroom_id).name            
            form = GroupForm(request.POST)
            if form.is_valid():
                group = EnrollGroup(name=form.cleaned_data['name'],classroom_id=int(classroom_id))
                group.save()
                
                # 記錄系統事
                log = Log(user_id=request.user.id, event=u'新增分組<'+classroom_name+'><'+form.cleaned_data['name']+'>')
                log.save()        
        
                return redirect('/student/group/'+classroom_id)
        else:
            form = GroupForm()
        return render_to_response('student/group_add.html', {'form':form}, context_instance=RequestContext(request))

# 加入組別
def group_enroll(request, classroom_id,  group_id):
        classroom_name = Classroom.objects.get(id=classroom_id).name
        group_name = EnrollGroup.objects.get(id=group_id).name
        enroll = Enroll.objects.filter(student_id=request.user.id, classroom_id=classroom_id)
        enroll.update(group=group_id)
        # 記錄系統事件 
        log = Log(user_id=request.user.id, event=u'加入組別<'+classroom_name+'><'+group_name+'>')
        log.save()         
        return redirect('/student/group/'+classroom_id)

# 刪除組別
def group_delete(request, group_id, classroom_id):
    group = EnrollGroup.objects.get(id=group_id)
    group.delete()
    classroom_name = Classroom.objects.get(id=classroom_id).name

    # 記錄系統事件 
    log = Log(user_id=request.user.id, event=u'刪除組別<'+classroom_name+'><'+group.name+'>')
    log.save()       
    return redirect('/student/group/'+classroom_id)  
    
# 是否開放選組
def group_open(request, classroom_id, action):
    classroom = Classroom.objects.get(id=classroom_id)
    if action == "1":
        classroom.group_open=True
        classroom.save()
        # 記錄系統事件 
        log = Log(user_id=request.user.id, event=u'開放選組<'+classroom.name+'>')
        log.save()            
    else :
        classroom.group_open=False
        classroom.save()
        # 記錄系統事件 
        log = Log(user_id=request.user.id, event=u'關閉選組<'+classroom.name+'>')
        log.save()                
    return redirect('/student/group/'+classroom_id)  	
	
# 列出選修的班級
def classroom(request):
        enrolls = Enroll.objects.filter(student_id=request.user.id).order_by("-id")
        # 記錄系統事件 
        log = Log(user_id=request.user.id, event='查看選修班級')
        log.save()          
        return render_to_response('student/classroom.html',{'enrolls': enrolls}, context_instance=RequestContext(request))    
    
# 查看可加入的班級
def classroom_add(request):
        classrooms = Classroom.objects.all().order_by('-id')
        classroom_teachers = []
        for classroom in classrooms:
            enroll = Enroll.objects.filter(student_id=request.user.id, classroom_id=classroom.id)
            if enroll.exists():
                classroom_teachers.append([classroom,classroom.teacher.first_name,1])
            else:
                classroom_teachers.append([classroom,classroom.teacher.first_name,0])   
        # 記錄系統事件 
        log = Log(user_id=request.user.id, event='查看可加入的班級')
        log.save() 
        return render_to_response('student/classroom_add.html', {'classroom_teachers':classroom_teachers}, context_instance=RequestContext(request))
    
# 加入班級
def classroom_enroll(request, classroom_id):
        scores = []
        if request.method == 'POST':
                form = EnrollForm(request.POST)
                if form.is_valid():
                    try:
                        classroom = Classroom.objects.get(id=classroom_id)
                        if classroom.password == form.cleaned_data['password']:
                                enroll = Enroll(classroom_id=classroom_id, student_id=request.user.id, seat=form.cleaned_data['seat'])
                                enroll.save()
                                # 記錄系統事件 
                                log = Log(user_id=request.user.id, event=u'加入班級<'+classroom.name+'>')
                                log.save()                                 
                        else:
                                return render_to_response('message.html', {'message':"選課密碼錯誤"}, context_instance=RequestContext(request))
                      
                    except Classroom.DoesNotExist:
                        pass
                    
                    
                    return redirect('/student/classroom')
        else:
            form = EnrollForm()
        return render_to_response('student/classroom_enroll.html', {'form':form}, context_instance=RequestContext(request))
        
# 修改座號
def seat_edit(request, enroll_id, classroom_id):
    enroll = Enroll.objects.get(id=enroll_id)
    if request.method == 'POST':
        form = SeatForm(request.POST)
        if form.is_valid():
            enroll.seat =form.cleaned_data['seat']
            enroll.save()
            classroon_name = Classroom.objects.get(id=classroom_id).name
            # 記錄系統事件 
            log = Log(user_id=request.user.id, event=u'修改座號<'+classroom_name+'>')
            log.save() 
            return redirect('/student/classroom')
    else:
        form = SeatForm(instance=enroll)

    return render_to_response('form.html',{'form': form}, context_instance=RequestContext(request))  

# 四種課程    
def lessons(request, lesson):
        enrolls = Enroll.objects.filter(student_id=request.user.id)
        if request.user.is_authenticated():
            user_id = request.user.id
        else :
            user_id = 0
        # 記錄系統事件 
        if lesson == "1":
            log = Log(user_id=user_id, event='查看課程頁面<Scratch12堂課>')
        elif lesson == "2":
            log = Log(user_id=user_id, event='查看課程頁面<實戰入門>')          
        elif lesson == "3":
            log = Log(user_id=user_id, event='查看課程頁面<實戰進擊>') 
        elif lesson == "4":
            log = Log(user_id=user_id, event='查看課程頁面<實戰高手>')             
        log.save()         
        return render_to_response('student/lessons.html', {'lesson':lesson, 'enrolls':enrolls}, context_instance=RequestContext(request))

# 課程內容
def lesson(request, lesson):
        # 限登入者
        if not request.user.is_authenticated():
            return redirect("/account/login/")    
        else :
            # 記錄系統事件 
            log = Log(user_id=request.user.id, event=u'查看課程內容<'+lesson+'>')
            log.save()     
            return render_to_response('student/lesson.html', {'lesson':lesson}, context_instance=RequestContext(request))

# 上傳作業  
def submit(request, index):
        scores = []
        if request.method == 'POST':
            form = SubmitForm(request.POST)
            work = Work.objects.filter(index=index, user_id=request.user.id)
            if not work.exists():
                if form.is_valid():
                    work2 = Work(index=index, user_id=request.user.id, number=form.cleaned_data['number'], memo=form.cleaned_data['memo'], publication_date=timezone.now())
                    work2.save()
					# credit
                    update_avatar(request, 1, 3)
                    # History
                    history = PointHistory(user_id=request.user.id, kind=1, message='繳交作業<'+lesson_list[int(index)-1][2]+'>', url=request.get_full_path().replace("submit", "submitall"))
                    history.save()
            else:
                if form.is_valid():
                    work.update(number=form.cleaned_data['number'], memo=form.cleaned_data['memo'])
                else :
                    work.update(memo=form.cleaned_data['memo'])           
                return redirect('/student/submit/'+index)
        else:
            work = Work.objects.filter(index=index, user_id=request.user.id)
            if not work.exists():
                form = SubmitForm()
            else:
                form = SubmitForm(instance=work[0])
                if work[0].scorer>0: 
                    score_name = User.objects.get(id=work[0].scorer).first_name
                    scores = [work[0].score, score_name]
        lesson = lesson_list[int(index)-1]							
        return render_to_response('student/submit.html', {'form':form, 'scores':scores, 'index':index, 'lesson':lesson}, context_instance=RequestContext(request))

# 上傳作業    
def submitall(request, index):
        scores = []
        if request.method == 'POST':
            form = SubmitForm(request.POST)
            work = Work.objects.filter(index=index, user_id=request.user.id)
            if not work.exists():
                if form.is_valid():
                    work2 = Work(index=index, user_id=request.user.id, number=form.cleaned_data['number'], memo=form.cleaned_data['memo'], publication_date=timezone.now())
                    work2.save()
					# credit
                    update_avatar(request, 1, 3)
                    # History
                    history = PointHistory(user_id=request.user.id, kind=1, message='繳交作業<'+lesson_list[int(index)-1][2]+'>', url=request.get_full_path())
                    history.save()					
            else:
                if form.is_valid():
                    work.update(number=form.cleaned_data['number'], memo=form.cleaned_data['memo'])
                else :
                    work.update(memo=form.cleaned_data['memo'])           
                return redirect('/student/submitall/'+index)
        else:
            work = Work.objects.filter(index=index, user_id=request.user.id)
            if not work.exists():
                form = SubmitForm()
            else:
                form = SubmitForm(instance=work[0])
                if work[0].scorer>0: 
                    score_name = User.objects.get(id=work[0].scorer).first_name
                    scores = [work[0].score, score_name]
        lesson = lesson_list[int(index)-1]					
        return render_to_response('student/submitall.html', {'form':form, 'scores':scores, 'index':index, 'lesson':lesson}, context_instance=RequestContext(request))
    
# 列出所有作業        
def work(request, classroom_id):
    del lesson_list[:]
    reset()
    works = Work.objects.filter(user_id=request.user.id)
    for work in works:
        lesson_list[work.index-1].append(work.score)
        lesson_list[work.index-1].append(work.publication_date)
        if work.score > 0 :
            score_name = User.objects.get(id=work.scorer).first_name
            lesson_list[work.index-1].append(score_name)
        else :
            lesson_list[work.index-1].append("尚未評分!")
    c = 0
    for lesson in lesson_list:
        assistant = Assistant.objects.filter(student_id=request.user.id, lesson=c+1, classroom_id=classroom_id)
        if assistant.exists() :
            lesson.append(1)
        else :
            lesson.append("")
        c = c + 1
        enroll_group = Enroll.objects.get(classroom_id=classroom_id, student_id=request.user.id).group
    return render_to_response('student/work.html', {'works':works, 'lesson_list':lesson_list, 'user_id': request.user.id, 'classroom_id':classroom_id, 'group': enroll_group}, context_instance=RequestContext(request))


def lesson_log(request, lesson):
    # 記錄系統事件
    tabname = request.POST.get('tabname')
    log = Log(user_id=request.user.id, event=u'查看課程內容<'+lesson+'> | '+tabname)
    log.save()