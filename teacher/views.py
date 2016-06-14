# -*- coding: UTF-8 -*-
#from django.shortcuts import render
from django.shortcuts import render_to_response, redirect
from django.contrib.auth.models import User
#from django.http import HttpResponse
#from django.contrib.auth import authenticate, login
from django.template import RequestContext
#from django.contrib.auth.decorators import login_required
#from django.core.paginator import Paginator, EmptyPage, PageNotAnInteger
from django.views.generic import ListView, DetailView, CreateView
from django.core.exceptions import ObjectDoesNotExist
#from django.contrib.auth.models import Group
from teacher.models import Classroom
from student.models import Enroll
from account.models import Log
from student.models import Enroll, Work, EnrollGroup, Assistant, Exam
from .forms import ClassroomForm, ScoreForm,  CheckForm1, CheckForm2, CheckForm3, CheckForm4
#from django.views.generic.edit import ModelFormMixin
#from django.http import HttpResponseRedirect
from student.lesson import *
from account.avatar import *
from account.models import Profile, PointHistory
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

# 列出班級所有作業
def work(request, classroom_id):
        classroom = Classroom.objects.get(id=classroom_id)
        # 記錄系統事件
        log = Log(user_id=request.user.id, event=u'列出班級所有作業<'+classroom.name+'>')
        log.save()              
        return render_to_response('teacher/work.html', {'lesson_list':lesson_list, 'classroom': classroom}, context_instance=RequestContext(request))

# 列出某作業所有同學名單
def score(request, classroom_id, index):
    enrolls = Enroll.objects.filter(classroom_id=classroom_id)
    classroom_name = Classroom.objects.get(id=classroom_id).name
    classmate_work = []
    scorer_name = ""
    for enroll in enrolls:
        try:    
            work = Work.objects.get(user_id=enroll.student_id, index=index)
            if work.scorer > 0 :
                scorer = User.objects.get(id=work.scorer)
                scorer_name = scorer.first_name
            else :
                scorer_name = "1"
        except ObjectDoesNotExist:
            work = Work(index=index, user_id=1, number="0")
        try:
			group_name = EnrollGroup.objects.get(id=enroll.group).name
        except ObjectDoesNotExist:
			group_name = "沒有組別"
        assistant = Assistant.objects.filter(student_id=enroll.student_id, lesson=index)
        if assistant.exists():
            classmate_work.append([enroll,work,1, scorer_name, group_name])
        else :
            classmate_work.append([enroll,work,0, scorer_name, group_name])            
    lesson = lesson_list[int(index)-1]

    def getKey(custom):
        return custom[0].seat
	
    classmate_work = sorted(classmate_work, key=getKey)
    
    # 記錄系統事件
    log = Log(user_id=request.user.id, event=u'列出某作業所有同學名單<'+classroom_name+'><'+index+'>')
    log.save()          
    return render_to_response('teacher/score.html',{'classmate_work': classmate_work, 'classroom_id':classroom_id, 'lesson':lesson, 'index': index}, context_instance=RequestContext(request))


# 教師評分
def scoring(request, classroom_id, user_id, index):
    user = User.objects.get(id=user_id)
    enroll = Enroll.objects.get(classroom_id=classroom_id, student_id=user_id)
    try:
        assistant = Assistant.objects.get(classroom_id=classroom_id,lesson=index,student_id=request.user.id)
    except ObjectDoesNotExist:            
        if not is_teacher(request.user, classroom_id):
            return render_to_response('message.html', {'message':"您沒有權限"}, context_instance=RequestContext(request))
        
    try:
        work3 = Work.objects.get(user_id=user_id, index=index)
    except ObjectDoesNotExist:
        work3 = Work(index=index, user_id=user_id, number="0")
        
    if request.method == 'POST':
        form = ScoreForm(request.user, request.POST)
        if form.is_valid():
            work = Work.objects.filter(index=index, user_id=user_id)
            if not work.exists():
                work = Work(index=index, user_id=user_id, score=form.cleaned_data['score'], publication_date=timezone.now())
                work.save()
                # 記錄系統事件
                log = Log(user_id=request.user.id, event=u'新增評分<'+user.first_name+'><'+work.score+'分>')
                log.save()                      
            else:
                # 小老師
                if not is_teacher(request.user, classroom_id):
                    if work[0].score < 0 :   			    
				                # credit
                        update_avatar(request, 2, 1)
                        # History
                        history = PointHistory(user_id=request.user.id, kind=2, message='assistant:<'+lesson_list[int(index)-1][2]+'>'+enroll.student.first_name.encode('utf8'), url=request.get_full_path())
                        history.save()				
                work.update(score=form.cleaned_data['score'])
                work.update(scorer=request.user.id)
               # 記錄系統事件
                log = Log(user_id=request.user.id, event=u'更新評分<'+user.first_name+u'><'+str(work[0].score)+u'分>')
                log.save()                    
						
            if is_teacher(request.user, classroom_id):         
                if form.cleaned_data['assistant']:
                    try :
					    assistant = Assistant.objects.get(student_id=user_id, classroom_id=classroom_id, lesson=index)
                    except ObjectDoesNotExist:
                        assistant = Assistant(student_id=user_id, classroom_id=classroom_id, lesson=index)
                        assistant.save()			
                return redirect('/teacher/score/'+classroom_id+'/'+index)
            else: 
                return redirect('/teacher/score_peer/'+index+'/'+classroom_id+'/'+str(enroll.group))

    else:
        work = Work.objects.filter(index=index, user_id=user_id)
        if not work.exists():
            form = ScoreForm(user=request.user)
        else:
            form = ScoreForm(instance=work[0], user=request.user)
    lesson = lesson_list[int(index)-1]
    return render_to_response('teacher/scoring.html', {'form': form,'work':work3, 'student':user, 'classroom_id':classroom_id, 'lesson':lesson}, context_instance=RequestContext(request))

# 小老師評分名單
def score_peer(request, index, classroom_id, group):
    enrolls = Enroll.objects.filter(classroom_id=classroom_id, group=group)
    lesson = ""
    classmate_work = []
    for enroll in enrolls:
        if not enroll.student_id == request.user.id : 
            scorer_name = ""
            try:    
                work = Work.objects.get(user_id=enroll.student.id, index=index)
                if work.scorer > 0 :
                    scorer = User.objects.get(id=work.scorer)
                    scorer_name = scorer.first_name
            except ObjectDoesNotExist:
                work = Work(index=index, user_id=1, number="0")        
            classmate_work.append([enroll.student,work,1, scorer_name])
        lesson = lesson_list[int(index)-1]
    # 記錄系統事件
    log = Log(user_id=request.user.id, event=u'小老師評分名單<'+index+'><'+group+'>')
    log.save()    
    return render_to_response('teacher/score_peer.html',{'enrolls':enrolls, 'classmate_work': classmate_work, 'classroom_id':classroom_id, 'lesson':lesson, 'index': index}, context_instance=RequestContext(request))

# 設定為小老師
def assistant(request, classroom_id, user_id, lesson):
    user = User.objects.get(id=user_id)
    assistant = Assistant(student_id=user_id, classroom_id=classroom_id, lesson=lesson)
    assistant.save()
    # 記錄系統事件
    log = Log(user_id=request.user.id, event=u'設為小老師<'+user.first_name+'>')
    log.save()    
    return redirect('/teacher/score/'+str(assistant.classroom_id)+"/"+lesson)    
    
# 取消小老師
def assistant_cancle(request, classroom_id, user_id, lesson):
    user = User.objects.get(id=user_id)   
    assistant = Assistant.objects.get(student_id=user_id, classroom_id=classroom_id, lesson=lesson)
    assistant.delete()
    # 記錄系統事件
    log = Log(user_id=request.user.id, event=u'取消小老師<'+user.first_name+'>')
    log.save()     

    return redirect('/teacher/score/'+str(assistant.classroom_id)+"/"+lesson)    
    
# 以分組顯示作業
def work_group(request, lesson, classroom_id):
        classroom_name = Classroom.objects.get(id=classroom_id).name
        student_groups = []
        groups = EnrollGroup.objects.filter(classroom_id=classroom_id)
        try:
                student_group = Enroll.objects.get(student_id=request.user.id, classroom_id=classroom_id).group
        except ObjectDoesNotExist :
                student_group = []		
        for group in groups:
            enrolls = Enroll.objects.filter(classroom_id=classroom_id, group=group.id)
            group_assistants = []
            works = []
            scorer_name = ""
            for enroll in enrolls: 
                try:    
                    work = Work.objects.get(user_id=enroll.student_id, index=lesson)
                    if work.scorer > 0 :
                        scorer = User.objects.get(id=work.scorer)
                        scorer_name = scorer.first_name
                    else :
                        scorer_name = "X"
                except ObjectDoesNotExist:
                    work = Work(index=lesson, user_id=1, number="0")
                works.append([enroll, work.score, scorer_name, work.number])
                try :
                    assistant = Assistant.objects.get(student_id=enroll.student.id, classroom_id=classroom_id, lesson=lesson)
                    group_assistants.append(enroll)
                except ObjectDoesNotExist:
				    pass
            student_groups.append([group, works, group_assistants])
        lesson_data = lesson_list[int(lesson)-1]		
        # 記錄系統事件
        log = Log(user_id=request.user.id, event=u'以分組顯示作業<'+lesson+'><'+classroom_name+'>')
        log.save()         
        return render_to_response('teacher/work_group.html', {'lesson':lesson, 'lesson_data':lesson_data, 'student_groups':student_groups, 'classroom_id':classroom_id, 'student_group':student_group}, context_instance=RequestContext(request))

