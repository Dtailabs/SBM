from django.db import models

class Users(models.Model):
	user_id = models.IntegerField(primary_key=True)
	user_name=models.CharField(max_length=20)
	dob = models.CharField(max_length=20)
	parent = models.CharField(max_length=20)
	addr = models.CharField(max_length=150)
	c_date=models.CharField(max_length=20)
	c_time=models.CharField(max_length=20)
	sex = models.CharField(max_length=10)
	mobile_no = models.CharField(max_length=15)
	email= models.CharField(max_length=20)
	class_id = models.CharField(max_length=50)
	section_id = models.CharField(max_length=50)
	# photo = models.CharField(max_length=50000)
	# thresh=models.IntegerField()
	emb=models.TextField(max_length=3000)
	def __str__(self):
		return str(self.user_id)
	class Meta:
		db_table="users"

class StudentLogs(models.Model):
	record_id = models.CharField(max_length=20)
	log_id = models.CharField(max_length=20)
	log_name = models.CharField(max_length=20)
	log_date = models.CharField(max_length=20)
	log_time = models.CharField(max_length=20)
	#log_timestamp = models.CharField(max_length=20)
	# log_date = models.CharField(max_length=20)
	# log_time=models.CharField(max_length=20)
	def __str__(self):
		return str(self.record_id)
	class Meta:
		db_table="student_logs"

class Attendance(models.Model):
	std_id = models.CharField(max_length=20)
	#std_name = models.CharField(max_length=20)
	#class_id = models.CharField(max_length=10)
	#section_id = models.CharField(max_length=10)
	att_date = models.CharField(max_length=20)
	att_day = models.CharField(max_length=20)
	att_month = models.CharField(max_length=20)
	att_year = models.CharField(max_length=20)
	in_time=models.CharField(max_length=20, default="-")
	out_time = models.CharField(max_length=20, default="-")
	duration = models.CharField(max_length=20, default="-")
	summary = models.CharField(max_length=5000,default="-")
	status = models.CharField(max_length=10)
	
	def __str__(self):
		return str(self.std_id)
	class Meta:
		db_table="attendance"

# class Uploads(models.Model):
# 	videoId = models.CharField(primary_key=True, max_length = 32)
# 	video = models.FileField(upload_to = "videos/")
# 	duration = models.IntegerField(null = True)

# 	def __str__(self):
# 		return self.videoId
# 	class Meta:
# 		db_table="video_storage"
