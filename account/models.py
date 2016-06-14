# -*- coding: UTF-8 -*-
from django.db import models
from django.conf import settings
from django.utils import timezone
from django.contrib.auth.models import User


# 個人檔案資料
class Profile(models.Model):
	user = models.OneToOneField(settings.AUTH_USER_MODEL,related_name="profile")
	#user_id = models.IntegerField(default=0)
	# 積分：上傳作業
	work = models.IntegerField(default=0)
	# 積分：擔任小老師
	assistant = models.IntegerField(default=0)
	# 積分：除錯
	debug = models.IntegerField(default=0)
	# 積分：創意秀
	creative = models.IntegerField(default=0)
	# 大頭貼等級
	avatar = models.IntegerField(default=0)

	def __unicode__(self):
		return str(self.user_id)
	
# 積分記錄 
class PointHistory(models.Model):
    # 使用者序號
	user_id = models.IntegerField(default=0)
	# 積分類別 1:上傳作業 2:小老師 3:除錯 4:創意秀
	kind = models.IntegerField(default=0)
	# 積分項目
	message = models.CharField(max_length=100)
	# 將積分項目超連結到某個頁面
	url = models.CharField(max_length=100)
	# 記載時間 
	publish = models.DateTimeField(default=timezone.now)

	def __unicode__(self):
		return str(self.user_id)
		
class Log(models.Model):
    # 使用者序號
	user_id = models.IntegerField(default=0)
	# 事件內容
	event = models.CharField(max_length=100)
	# 發生時間 
	publish = models.DateTimeField(default=timezone.now)	
	
	def __unicode__(self):
		return str(self.user_id)+'--'.self.event	
	