# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm, PasswordForm, RealnameForm
from django.contrib.auth.models import User
from account.models import Profile, PointHistory, Log, Message, MessagePoll
from student.models import Enroll, Work, Assistant
from django.core.exceptions import ObjectDoesNotExist
from account.templatetags import tag 
from django.views.generic import ListView
from django.contrib.auth.models import Group
from django.http import JsonResponse
import sys, os
from django.http import HttpResponse
from mimetypes import MimeTypes
from student.lesson import *
import StringIO
import xlsxwriter
import datetime
from django.utils import timezone
from django.utils.timezone import localtime

# 判斷是否開啟事件記錄
def is_event_open():
        return Profile.objects.get(user=User.objects.get(id=1)).event_open


# 網站首頁
def homepage(request):
    users = User.objects.all()
    return render_to_response('homepage.html', {'user_count':len(users)}, context_instance=RequestContext(request))

# 使用者登入功能
def user_login(request):
        message = None
        test = ""
        if request.method == "POST":
                form = LoginForm(request.POST)
                if form.is_valid():
                        username = request.POST['username']
                        password = request.POST['password']
                        user = authenticate(username=username, password=password)
                        if user is not None:
                                if user.is_active:
                                        if user.id == 1:
                                            if user.first_name == "": 
                                                user.first_name = "管理員"
                                                user.save()
                                        # 登入成功，導到大廳
                                        login(request, user)
                                        # 記錄系統事件
                                        if is_event_open() :
                                            log = Log(user_id=request.user.id, event='登入系統')
                                            log.save()
                                        return redirect('dashboard')
                                else:
                                        message = "Your user is inactive"
                        else:
                            # 記錄系統事件
                            log = Log(user_id=0, event='登入失敗')
                            log.save()                                
                            message = "無效的帳號或密碼!"
        else:
                form = LoginForm()
        return render_to_response('registration/login.html', {'test': test, 'message': message, 'form': form}, context_instance=RequestContext(request))

# 記錄登出
def suss_logout(request, user_id):
    # 記錄系統事件
    if is_event_open() :    
        log = Log(user_id=user_id, event='登出系統')
        log.save()    
    return redirect('/account/login/')

# 大廳
@login_required
def dashboard(request):
    # 記錄系統事件
    if is_event_open() :   
        log = Log(user_id=request.user.id, event='查看訊息')
        log.save()    
    messages = []
    messagepolls = MessagePoll.objects.filter(reader_id=request.user.id)
    for messagepoll in messagepolls:
        messages.append(messagepoll.message)
    return render(request,
                  'account/dashboard.html',
                  {'section': 'dashboard', 
                   'messages': messages})

# 註冊帳號                  
def register(request):
    if request.method == 'POST':
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            # Create a new user object but avoid saving it yet
            new_user = form.save(commit=False)
            # Set the chosen password                 
            new_user.set_password(
                form.cleaned_data['password'])
            # Save the User object
            new_user.save()
            profile = Profile(user=new_user)
            profile.save()
            # 記錄系統事件
            if is_event_open() :   
                log = Log(user_id=new_user.id, event='註冊帳號成功')
                log.save()                
            return render(request,
                          'account/register_done.html',
                          {'new_user': new_user})
    else:
        form = UserRegistrationForm()
    return render(request,
                  'account/register.html',
                  {'form': form})
      
# 顯示個人檔案
def profile(request, user_id):
    user = User.objects.get(id=user_id)
    enrolls = Enroll.objects.filter(student_id=user_id)
    try: 
        profile = Profile.objects.get(user=user)
    except ObjectDoesNotExist:
        profile = Profile(user=user)
        profile.save()

    del lesson_list[:]
    reset()
    works = Work.objects.filter(user_id=user_id)
    for work in works:
        lesson_list[work.index-1].append(work.score)
        lesson_list[work.index-1].append(work.publication_date)
        if work.score > 0 :
            score_name = User.objects.get(id=work.scorer).first_name
            lesson_list[work.index-1].append(score_name)
        else :
            lesson_list[work.index-1].append("null")

    # 計算積分    
    credit = profile.work + profile.assistant + profile.debug + profile.creative
    # 記錄系統事件
    if is_event_open() :       
        log = Log(user_id=request.user.id, event='查看個人檔案')
        log.save()        
    return render_to_response('account/profile.html',{'works':works, 'lesson_list':lesson_list, 'enrolls':enrolls, 'profile': profile,'user_id':user_id, 'credit':credit}, context_instance=RequestContext(request))	

# 修改密碼
def password(request, user_id):
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=user_id)
            user.set_password(request.POST['password'])
            user.save()
            # 記錄系統事件
            if is_event_open() :               
                log = Log(user_id=request.user.id, event=u'修改<'+user.first_name+u'>密碼成功')
                log.save()                
            return redirect('homepage')
    else:
        form = PasswordForm()
        user = User.objects.get(id=user_id)

    return render_to_response('account/password.html',{'form': form, 'user':user}, context_instance=RequestContext(request))

# 修改他人的真實姓名
def adminrealname(request, user_id):
    if request.method == 'POST':
        form = RealnameForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=user_id)
            user.first_name =form.cleaned_data['first_name']
            user.save()
            # 記錄系統事件
            if is_event_open() :               
                log = Log(user_id=request.user.id, event=u'修改姓名<'+user.first_name+'>')
                log.save()                
            return redirect('/account/userlist/')
    else:
        user = User.objects.get(id=user_id)
        form = RealnameForm(instance=user)

    return render_to_response('account/realname.html',{'form': form}, context_instance=RequestContext(request))
	
# 修改自己的真實姓名
def realname(request):
    if request.method == 'POST':
        form = RealnameForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=request.user.id)
            user.first_name =form.cleaned_data['first_name']
            user.save()
            # 記錄系統事件
            if is_event_open() :               
                log = Log(user_id=request.user.id, event=u'修改姓名<'+user.first_name+'>')
                log.save()                
            return redirect('/account/profile/'+str(request.user.id))
    else:
        user = User.objects.get(id=request.user.id)
        form = RealnameForm(instance=user)

    return render_to_response('account/realname.html',{'form': form}, context_instance=RequestContext(request))

# 記錄積分項目
class LogListView(ListView):
    context_object_name = 'logs'
    paginate_by = 20
    template_name = 'account/log_list.html'
	
    def get_queryset(self):
        # 記錄系統事件
        if self.kwargs['kind'] == "1" :
            log = Log(user_id=self.kwargs['user_id'], event='查看積分--上傳作品')
        elif  self.kwargs['kind'] == "2" :
            log = Log(user_id=self.kwargs['user_id'], event='查看積分--小老師')      
        elif  self.kwargs['kind'] == "3" :
            log = Log(user_id=self.kwargs['user_id'], event='查看積分--除錯')            
        elif  self.kwargs['kind'] == "4" :
            log = Log(user_id=self.kwargs['user_id'], event='查看積分--創意秀')
        else :
            log = Log(user_id=self.kwargs['user_id'], event='查看全部積分')                        
        if is_event_open() :               
            log.save()                
        if not self.kwargs['kind'] == "0" :
            queryset = PointHistory.objects.filter(user_id=self.kwargs['user_id'],kind=self.kwargs['kind']).order_by('-id')
        else :
            queryset = PointHistory.objects.filter(user_id=self.kwargs['user_id']).order_by('-id')		
        return queryset

    def get_context_data(self, **kwargs):
        context = super(LogListView, self).get_context_data(**kwargs)
        user_name = User.objects.get(id=self.kwargs['user_id']).first_name
        context.update({'user_name': user_name})
        return context		
        
# 超級管理員可以查看所有帳號
class UserListView(ListView):
    context_object_name = 'users'
    paginate_by = 20
    template_name = 'account/user_list.html'
    
    def get_queryset(self):
        # 記錄系統事件
        if is_event_open() :           
            log = Log(user_id=1, event='查看帳號')
            log.save()         
        queryset = User.objects.all().order_by('-id')
        return queryset
    
# Ajax 設為教師、取消教師
def make(request):
    user_id = request.POST.get('userid')
    action = request.POST.get('action')
    if user_id and action :
        user = User.objects.get(id=user_id)           
        try :
            group = Group.objects.get(name="teacher")	
        except ObjectDoesNotExist :
            group = Group(name="teacher")
            group.save()
        if action == 'set':            
            # 記錄系統事件
            if is_event_open() : 
                log = Log(user_id=1, event=u'設為教師<'+user.first_name+'>')
                log.save()                        
            group.user_set.add(user)
            # create Message
            title = "<" + request.user.first_name + u">設您為教師<img src='/static/images/teacher.png'>"
            url = "/teacher/classroom"
            message = Message.create(title=title, url=url, time=timezone.now())
            message.save()                        
                    
            # message for group member
            messagepoll = MessagePoll.create(message_id = message.id,reader_id=user_id)
            messagepoll.save()    
        else : 
            # 記錄系統事件
            if is_event_open() :               
                log = Log(user_id=1, event=u'取消教師<'+user.first_name+'>')
                log.save()              
            group.user_set.remove(user)  
            # create Message
            title = "<"+ request.user.first_name + u">取消您為教師"
            url = "/homepage"
            message = Message.create(title=title, url=url, time=timezone.now())
            message.save()                        
                    
            # message for group member
            messagepoll = MessagePoll.create(message_id = message.id,reader_id=user_id)
            messagepoll.save()               
        return JsonResponse({'status':'ok'}, safe=False)
    else:
        return JsonResponse({'status':user.first_name}, safe=False)        
        
# 記錄系統事件
class EventListView(ListView):
    context_object_name = 'events'
    paginate_by = 50
    template_name = 'account/event_list.html'

    def get_queryset(self):    
        # 記錄系統事件
        if is_event_open() :           
            log = Log(user_id=self.request.user.id, event='查看事件')
            log.save()       
        if self.kwargs['user_id'] == "0":
            if self.request.GET.get('q') != None:
                queryset = Log.objects.filter(event__icontains=self.request.GET.get('q')).order_by('-id')
            else :
                queryset = Log.objects.order_by('-id')
        else :
            if self.request.GET.get('q') != None:
                queryset = Log.objects.filter(user_id=self.kwargs['user_id'],event__icontains=self.request.GET.get('q')).order_by('-id')
            else : 
                queryset = Log.objects.filter(user_id=self.kwargs['user_id']).order_by('-id')
        return queryset
        

    def get_context_data(self, **kwargs):
        context = super(EventListView, self).get_context_data(**kwargs)
        q = self.request.GET.get('q')
        context.update({'q': q})
        context['is_event_open'] = Profile.objects.get(user=User.objects.get(id=1)).event_open
        return context	
	
# 下載檔案
def download(request, filename):
    #down_file = File.objects.get(name = filename)
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DOWNLOAD_URL = BASE_DIR+"/download/"
    file_path = DOWNLOAD_URL + filename
    file_name = filename
    fp = open(file_path, 'rb')
    response = HttpResponse(fp.read())
    fp.close()
    mime = MimeTypes()
    type, encoding = mime.guess_type(file_name)
    if type is None:
        type = 'application/octet-stream'
    response['Content-Type'] = type
    response['Content-Length'] = str(os.stat(file_path).st_size)
    if encoding is not None:
        response['Content-Encoding'] = encoding
    if u'WebKit' in request.META['HTTP_USER_AGENT']:
        filename_header = 'filename=%s' % file_name.encode('utf-8')
    elif u'MSIE' in request.META['HTTP_USER_AGENT']:
        filename_header = ''
    else:
        filename_header = 'filename*=UTF-8\'\'%s' % urllib.quote(file_name.encode('utf-8'))
    response['Content-Disposition'] = 'attachment; ' + filename_header
    # 記錄系統事件
    if is_event_open() :       
        log = Log(user_id=request.user.id, event=u'下載檔案<'+filename+'>')
        log.save()     
    return response

def avatar(request):
    profile = Profile.objects.get(user = request.user)
    # 記錄系統事件
    if is_event_open() :       
        log = Log(user_id=request.user.id, event=u'查看個人圖像')
        log.save()        
    return render_to_response('account/avatar.html', {'avatar':profile.avatar}, context_instance=RequestContext(request))
    
def clear(request):
    Log.objects.all().delete()
    # 記錄系統事件
    if is_event_open() :       
        log = Log(user_id=request.user.id, event=u'清除所有事件')
        log.save()            
    return redirect("/account/event/0")
    
def event_excel(request):
    # 記錄系統事件
    if is_event_open() :       
        log = Log(user_id=request.user.id, event=u'下載事件到Excel')
        log.save()        
    output = StringIO.StringIO()
    workbook = xlsxwriter.Workbook(output)    
    #workbook = xlsxwriter.Workbook('hello.xlsx')
    worksheet = workbook.add_worksheet()
    date_format = workbook.add_format({'num_format': 'dd/mm/yy hh:mm:ss'})
    events = Log.objects.all().order_by('-id')
    index = 1
    for event in events:
        if event.user_id > 0 :
            worksheet.write('A'+str(index), event.user.first_name)
        else: 
            worksheet.write('A'+str(index), u'匿名')
        worksheet.write('B'+str(index), event.event)
        worksheet.write('C'+str(index), str(localtime(event.publish)))
        index = index + 1

    workbook.close()
    # xlsx_data contains the Excel file
    response = HttpResponse(content_type='application/vnd.ms-excel')
    response['Content-Disposition'] = 'attachment; filename=Report'+str(datetime.datetime.now().date())+'.xlsx'
    xlsx_data = output.getvalue()
    response.write(xlsx_data)
    return response

def event_make(request):
    action = request.POST.get('action')
    if action :
            profile = Profile.objects.get(user=User.objects.get(id=1))
            if action == 'open':
                profile.event_open = True
            else :
                profile.event_open = False
            profile.save()
            return JsonResponse({'status':'ok'}, safe=False)
    else:
            return JsonResponse({'status':'ko'}, safe=False)