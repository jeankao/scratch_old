# -*- coding: UTF-8 -*-
#from django.shortcuts import render
#from .models import CertificateModel
#from django.http import HttpResponseForbidden
from certificate.forms import ImageUploadForm
from django.shortcuts import render_to_response, redirect
from django.template import RequestContext
from django.core.exceptions import ObjectDoesNotExist
#from django.http import HttpResponse
#from django.contrib.auth.models import User
from account.models import Log
from teacher.models import Classroom
from student.models import Enroll
from certificate.models import Certificate
from PIL import Image,ImageDraw,ImageFont
#from django.conf import settings
#from django.utils.encoding import smart_text
#from django.core.files import File 
import cStringIO as StringIO
#import os
#from django.utils import timezone
#from django.http import JsonResponse
#from blog.models import Message, MessagePoll


# 上傳 Hour of code 證書
def upload_pic(request):
    m = []
    if request.method == 'POST':
        form = ImageUploadForm(request.POST, request.FILES)
        if form.is_valid():
            try:
                m = Certificate.objects.get(student_id=request.user.id)
                m.picture = form.cleaned_data['image']
				
                image_field = form.cleaned_data.get('image')
                image_file = StringIO.StringIO(image_field.read())
                image = Image.open(image_file)
                image = image.resize((800, 600), Image.ANTIALIAS)

                image_file = StringIO.StringIO()
                image.save(image_file, 'JPEG', quality=90)

                image_field.file = image_file
                m.save()
            except ObjectDoesNotExist:
                m = Certificate(picture=form.cleaned_data['image'], student_id=request.user.id)
                m.save()
            classroom_id = Enroll.objects.filter(student_id=request.user.id).order_by('-id')[0].classroom.id
            # 記錄系統事件
            log = Log(user_id=request.user.id, event='上傳Hour of Code證書成功')
            log.save()             
            return redirect('/certificate/classroom/0/'+str(classroom_id))
    else :
        try:
            m = Certificate.objects.get(student_id=request.user.id)   
        except ObjectDoesNotExist:
            pass
        form = ImageUploadForm()
    return render_to_response('certificate/certificate.html', {'form':form, 'certificate': m}, context_instance=RequestContext(request))

# 顯示證書
def show(request, unit, enroll_id):
    enroll = Enroll.objects.get(id=enroll_id)
    if unit == "0" :
	    try:
		    certificate_image = Certificate.objects.get(student_id=enroll.student.id).picture
	    except ObjectDoesNotExist:
			certificate_image = ""
    else :
		certificate_image = "static/certificate/" + unit + "/" + enroll_id + ".jpg"		
    # 記錄系統事件
    log = Log(user_id=request.user.id, event=u'查看證書<'+unit+'><'+enroll.student.first_name+'>')
    log.save() 		
    return render_to_response('certificate/show.html', {'certificate_image': certificate_image}, context_instance=RequestContext(request))
    
# 顯示班級證書    
def classroom(request, unit, classroom_id):
    enrolls = Enroll.objects.filter(classroom_id=classroom_id)
    classroom_name = Classroom.objects.get(id=classroom_id).name
    datas = []
    nodatas = []
    for enroll in enrolls:	
        if unit == "0" :
            try :
                certificate = Certificate.objects.get(student_id=enroll.student_id)
                datas.append([enroll, certificate])
            except ObjectDoesNotExist:
                certificate = []
                nodatas.append([enroll, []])
		
            def getKey(custom):
                return custom[1].publish
            datas = sorted(datas, key=getKey)	
        elif unit == "1" :
                if enroll.certificate1:
	                datas.append(enroll)
                else :
                    nodatas.append(enroll)	
        elif unit == "2" :
                if enroll.certificate2:
	                datas.append(enroll)
                else :
                    nodatas.append(enroll)	
        elif unit == "3" :
                if enroll.certificate3:
	                datas.append(enroll)
                else :
                    nodatas.append(enroll)	
        elif unit == "4" :
                if enroll.certificate4:
	                datas.append(enroll)
                else :
		            nodatas.append(enroll)						
        if unit =="1" :
            def getKey1(custom):
                return custom.certificate1_date
            datas = sorted(datas, key=getKey1)				
        elif unit == "2":
            def getKey2(custom):
                return custom.certificate2_date
            datas = sorted(datas, key=getKey2)	
        elif unit == "3":
            def getKey3(custom):
                return custom.certificate3_date
            datas = sorted(datas, key=getKey3)		
        elif unit == "4":
            def getKey4(custom):
                return custom.certificate4_date
            datas = sorted(datas, key=getKey4)		

        def getKey5(custom):
            if unit=="0" :
                return custom[0].seat
            else :
                return custom.seat
        nodatas = sorted(nodatas, key=getKey5)
    for data in nodatas:
		datas.append(data)
    # 記錄系統事件
    log = Log(user_id=request.user.id, event=u'查看班級證書<'+unit+'><'+classroom_name+'>')
    log.save() 				
    return render_to_response('certificate/classroom.html', {'enrolls':nodatas,'datas': datas, 'unit':unit}, context_instance=RequestContext(request))
