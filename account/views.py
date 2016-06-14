# -*- coding: UTF-8 -*-
from django.shortcuts import render
from django.contrib.auth.decorators import login_required
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.contrib.auth import authenticate, login
from .forms import LoginForm, UserRegistrationForm, PasswordForm, RealnameForm
from django.contrib.auth.models import User
from account.models import Profile, PointHistory, Log
from django.core.exceptions import ObjectDoesNotExist
from account.templatetags import tag 
from django.views.generic import ListView
from django.contrib.auth.models import Group
from django.http import JsonResponse

# 網站首頁
def homepage(request):
    return render_to_response('homepage.html', context_instance=RequestContext(request))

# 使用者登入功能
def user_login(request):
        message = None
        if request.method == "POST":
                form = LoginForm(request.POST)
                if form.is_valid():
                        username = request.POST['username']
                        password = request.POST['password']
                        user = authenticate(username=username, password=password)
                        if user is not None:
                                if user.is_active:
                                        # 登入成功，導到大廳
                                        login(request, user)
                                        # 記錄系統事件
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
        return render_to_response('registration/login.html', {'message': message, 'form': form}, context_instance=RequestContext(request))

# 記錄登出
def suss_logout(request, user_id):
    # 記錄系統事件
    log = Log(user_id=user_id, event='登出系統')
    log.save()    
    return redirect('/account/login/')

# 大廳
@login_required
def dashboard(request):
    # 記錄系統事件
    log = Log(user_id=request.user.id, event='抵達大廳')
    log.save()    
    messages = []
    #for messagepoll in messagepolls:
    #    messages.append(messagepoll.message)
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
            log = Log(user_id=new_user.user.id, event='註冊帳號成功')
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
    try: 
        profile = Profile.objects.get(user=user)
    except ObjectDoesNotExist:
        profile = Profile(user=user)
        profile.save()
    
    # 計算積分    
    credit = profile.work + profile.assistant + profile.debug + profile.creative
    # 記錄系統事件
    log = Log(user_id=request.user.id, event='查看個人檔案')
    log.save()        
    return render_to_response('account/profile.html',{'profile': profile,'user_id':user_id, 'credit':credit}, context_instance=RequestContext(request))	

# 修改密碼
def password(request, user_id):
    if request.method == 'POST':
        form = PasswordForm(request.POST)
        if form.is_valid():
            user = User.objects.get(id=user_id)
            user.set_password(request.POST['password'])
            user.save()
            # 記錄系統事件
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
            log = Log(user_id=request.user.id, event=u'修改姓名<'+user.fist_name+'>')
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
        log = Log(user_id=1, event='查看帳號')
        log.save()         
        queryset = User.objects.all().order_by('-id')
        return queryset
    
# Ajax 設為教師、取消教師
def make(request):
    user_id = request.POST.get('userid')
    user = User.objects.get(id=1)        
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
            log = Log(user_id=1, event=u'設為教師<'+user.first_name+'>')
            log.save()                        
            group.user_set.add(user)
        else : 
            # 記錄系統事件
            log = Log(user_id=1, event=u'取消教師<'+user.first_name+'>')
            log.save()              
            group.user_set.remove(user)               
        return JsonResponse({'status':'ok'}, safe=False)
    else:
        return JsonResponse({'status':user.first_name}, safe=False)        
        
# 記錄系統事件
class EventListView(ListView):
    context_object_name = 'events'
    paginate_by = 20
    template_name = 'account/event_list.html'

    def get_queryset(self):    
        # 記錄系統事件
        log = Log(user_id=1, event='查看事件')
        log.save()        
        queryset = Log.objects.order_by('-id')
        return queryset
	