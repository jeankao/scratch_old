# -*- coding: UTF-8 -*-
from django import template
from django.contrib.auth.models import User
from account.models import MessagePoll
from teacher.models import Classroom
from student.models import Enroll
from django.contrib.auth.models import Group
from django.utils import timezone
from django.utils.safestring import mark_safe

register = template.Library()

@register.filter()
def to_int(value):
    return int(value)
    
@register.filter()
def name(user_id):
    if user_id > 0 :
        user = User.objects.get(id=user_id)
        return user.first_name
    else : 
        return "匿名"
    
@register.filter()
def teacher_id(classroom_id):
    if classroom_id > 0 :
        teacher_id = Classroom.objects.get(id=classroom_id).teacher_id
        return teacher_id
    else : 
        return 0
        
@register.filter()
def reader_name(message_id):
    try:
        poll = MessagePoll.objects.get(message_id=message_id)
        user = User.objects.get(id=poll.reader_id)
        if poll.read :
            return user.first_name+u"(已讀)"
        else :
            return user.first_name
    except :
        return "noname"
        
@register.filter()
def show_member(show_id):
    members = Enroll.objects.filter(group_show=show_id)
    name = ""
    for member in members:
        name = name + '<' + member.student.first_name + '>'
    return name
    
@register.filter(name='has_group') 
def has_group(user, group_name):
    group =  Group.objects.get(name=group_name) 
    return group in user.groups.all()
    
@register.filter(name='unread') 
def unread(user_id):
    return MessagePoll.objects.filter(reader_id=user_id, read=False).count()
    
@register.filter(name="img")
def img(title):
    if title.startswith(u'[私訊]'):
        return "line"
    elif title.startswith(u'[公告]'):
        return "announce"
    elif u'擔任小老師' in title:
        return "assistant"
    elif u'設您為教師' in title:
        return "teacher"
    else :
        return ""