# -*- coding: utf-8 -*-
from django import forms
from teacher.models import Classroom
from student.models import Enroll, EnrollGroup, Work

class EnrollForm(forms.Form):
        password =  forms.CharField()
        seat = forms.CharField()
        
        def __init__(self, *args, **kwargs):
            super(EnrollForm, self).__init__(*args, **kwargs)
            self.fields['password'].label = "選課密碼"
            self.fields['seat'].label = "座號"
        
class GroupForm(forms.ModelForm):
        class Meta:
           model = EnrollGroup
           fields = ['name']
           
        def __init__(self, *args, **kwargs):
            super(GroupForm, self).__init__(*args, **kwargs)
            self.fields['name'].label = "組別名稱"
        
class SubmitForm(forms.ModelForm):
        class Meta:
           model = Work
           fields = ['number','memo']
           
        def __init__(self, *args, **kwargs):
            super(SubmitForm, self).__init__(*args, **kwargs)
            self.fields['number'].label = "作品編號"
            self.fields['memo'].label = "心得感想"

class SeatForm(forms.ModelForm):
        class Meta:
            model = Enroll
            fields = ['seat']
