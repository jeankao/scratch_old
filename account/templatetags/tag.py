# -*- coding: UTF-8 -*-
from django import template
from django.contrib.auth.models import User
from student.models import Enroll
from django.contrib.auth.models import Group 

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