# -*- coding: UTF-8 -*-
from django.db import models
from django.contrib.auth.models import User

# 班級
class Classroom(models.Model):
    # 班級名稱
    name = models.CharField(max_length=30)
    # 選課密碼
    password = models.CharField(max_length=30)
    # 授課教師
    teacher_id = models.IntegerField(default=0)
    # 是否開放分組
    group_open = models.BooleanField(default=True)
    # 是否開放創意秀分組
    group_show_open = models.BooleanField(default=True)
    
    @property
    def teacher(self):
        return User.objects.get(id=self.teacher_id)  
        
    def __unicode__(self):
        return self.name
        
   
