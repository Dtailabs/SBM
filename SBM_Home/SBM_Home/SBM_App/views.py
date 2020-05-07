from django.shortcuts import render
from django.http import JsonResponse,HttpResponse
import os
import base64
import requests,ast
#from . import face_capture
from .models import Users,Attendance,StudentLogs
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponseRedirect,StreamingHttpResponse
from django.conf import settings
import time
import numpy as np
import cv2

#import face_embeddings
import pandas as pd
from matplotlib import pyplot
from datetime import date
from datetime import datetime
import uuid

cascPath = "SBM_App/haarcascade_frontalface_default.xml"                            # To Detect Face in given Frame or Image.
faceCascade = cv2.CascadeClassifier(cascPath)
url_ip = '127.0.0.1'#"34.67.128.207"

def unique_user_check(uid): #>>>>>>>>>>>>>>>>>>>>>>>
	print("check user in existed database")
	try:
		values,_ = Users.objects.get(user_id=uid)
		return values
	except:
		return None

def user_verification_check(thresh):#>>>>>>>>>>>>>>>>>>>>>>>
	users = Users.objects.all()
	print("users: ",users)
	t1 = time.time()
	min_dist = 99
	min_id = 0
	c1=0
	# for i9 in range(100):
	for u1 in users:
		print("u1: ",u1.user_id)
		stored_emb = Users.objects.filter(user_id=int(u1.user_id))
		#print("stored_emb: ",stored_emb)
		ll = stored_emb.values_list()[0][-1]
		ll = np.array(list(map(float,ll[1:-1].split(','))))
		#thresh = np.array(list(map(float,thresh[0].split(','))))
		#print("l1: ",ll,"\nstored_emb: ",thresh[0])
		dist = np.sqrt(np.sum(np.square(np.subtract(ll, thresh[0]))))
		if(dist<0.85 and min_dist>dist):
			min_dist = dist
			min_id = u1.user_id
		print("distance: ",dist)
		print("==================")
		c1+=1
		#assert(False)
	print("min_id: {}, min_dist: {}".format(min_id,min_dist))
	print("total_count: ",c1)
	print("elapsed time: ",time.time()-t1)
	if(min_dist<0.85):
		#print("user_status: {},min_id: {},min_dist: {}".format("Known",min_id,min_dist))
		return "known",min_id,min_dist
	else:
		#print("Unknown User")
		return "unknown",False,False
#user_verification_check(123)

def create_new_sheet():#>>>>>>>>>>>>>>>>>>>>>>>
	today = str(date.today()).replace("-","_")
	print("today: ",today)
	if(not os.path.exists("Attendance_{}.csv".format(today))):
		df = pd.DataFrame(columns=['AttendanceLogId','AttendanceDate','EmployeeId','InTime','OutTime','Duration','Status'])
		users = Users.objects.all()
		df['AttendanceLogId'] = np.array([i for i in range(0,len(users))])
		df['AttendanceDate'] = str(date.today())
		df['EmployeeId'] = np.array([str(u1.user_id) for u1 in users])
		df['Status'] = "Absent"
		#df = df[df.columns[1:]]
		df.to_csv("Attendance_{}.csv".format(today))
	# 	return HttpResponse("Created Successfully!!!") 
	# else:
	# 	return HttpResponse("Already Created!!!")
#create_new_sheet()

def user_DB(uname,uid,dob,addr,parent,sex,mobile_no,email,class_id,section_id,emb):#>>>>>>>>>>>>>>>>>>>>>>>
	print("iam in face_DB")
	print("uname: {},uid: {}".format(uname,uid))
	unix = time.time()
	c_date = str(datetime.fromtimestamp(unix).strftime('%d-%m-%Y'))
	c_time = str(datetime.fromtimestamp(unix).strftime('%H:%M:%S'))
	#try:
	#emb = np.ndarray.tolist(emb)
	#emb = ','.join(str(e) for e in emb)
	print(uname,type(uname),uid,type(uid),c_time,c_date,emb,type(emb))
	train = Users(user_id=int(uid), user_name=uname, dob=dob, addr=addr, parent=parent, c_date=c_date, c_time=c_time, sex=sex, mobile_no=mobile_no, email=email, class_id=class_id, section_id=section_id,emb=emb[0])
	train.save()
	print("values inserted to DB successfully!!!")
	return "success"
	#except:
	#	return "not_inserted"

def index(request):
	return render(request,'SBM_App/index.html')
def register_here_face(request):
	return render(request,'SBM_App/register_face.html')
def login_here_face(request):
	return render(request,'SBM_App/login_face.html')
def suc_reg(request):
	return render(request,'SBM_App/suc_reg.html')
def suc_log(request):
	return render(request,'SBM_App/suc_log.html')
def report_here_logs(request):
	return render(request,'SBM_App/reports.html')

def embeddings_proc(path):
	image_file_name = path#"face_aligned.jpg"
	url = "http://{}:8080/face_embeddings/".format(url_ip)
	payload = {"image": open(image_file_name, "rb")}
	r = requests.post(url, files=payload).json()
	#print("=================================\nResponse: {}\n=================================".format(r))
	return r

def registration_proc():
	image_file_name = "media/register_img.jpg"
	url = "http://{}:8080/registration/".format(url_ip)
	
	# retval, buffer = cv2.imencode('.jpg', image)
	# jpg_as_text = base64.b64encode(buffer)
	
	payload = {"image": open(image_file_name, "rb")}#image.tolist()}
	r = requests.post(url, files=payload).json()
	return r

def verification_proc():
	image_file_name = "media/verify_img.jpg"
	url = "http://{}:8080/registration/".format(url_ip)
	payload = {"image": open(image_file_name, "rb")}

	r = requests.post(url, files=payload).json()
	return r

def capture_user(uid,case):
	t1 = time.time()
	video_capture = cv2.VideoCapture(0)
	reg_face_emb = []
	while(True):
	    # Capture frame-by-frame
	    ret, frame = video_capture.read()
	    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	    faces = faceCascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(80, 80))
	    # Draw a rectangle around the faces
	    for (x, y, w, h) in faces:
	        cv2.rectangle(frame, (x-2, y-37), (x+w+2, y+h+3), (0, 255, 255), 2)
	    
	    cv2.imshow('Video', frame)  #Display the resulting frame
	    k = cv2.waitKey(1)
	    if((k%256 == 27) or (0xFF == ord('q'))):   # ESC or Q pressed
	        print("Escape hit, closing...")
	        break
	    elif(k%256 == 32):
	        print("faces found: ",len(faces))
	        ret, frame = video_capture.read()
	        
	        #data_rects = face_capture.crop_images_frame(frame)
	        if(case == "TRAIN"):
	        	cv2.imwrite("media/register_img.jpg",frame)
	        	reg_ret = registration_proc()
	        	data_rects = reg_ret[0]['faces_list']
	        	cv2.imwrite("media/aligned_image_reg.jpg",np.array(data_rects[0]))
	        	emb_dict = embeddings_proc("media/aligned_image_reg.jpg")
	        	if(case == "TRAIN" and len(reg_ret) == 1):
	        		# aligned_image = np.array(reg_ret[0]['faces_list'])
	        		# emb_dict = embeddings_proc("aligned_image_reg.jpg")
	        		reg_face_emb.append(emb_dict[0]['embedding'])
	        		break
	        else:
	        	cv2.imwrite("media/verify_img.jpg",frame)
	        	ver_ret = verification_proc()
	        	for reg in range(len(ver_ret)):
	        		aligned_image = np.array(ver_ret[reg]['faces_list'])
	        		cv2.imwrite("media/aligned_image_ver.jpg",aligned_image)
	        		emb_dict = embeddings_proc("media/aligned_image_ver.jpg")
	        		reg_face_emb.append(emb_dict[0]['embedding'])
	        	break
	print("out of whileloop>>>>")
	# if(case == 'TRAIN'):
	#     store_path = "SBM_App/dataset/register/{}.png".format(uid)
	# elif(case == "TEST"):
	#     store_path = "SBM_App/dataset/login/{}.png".format(uid)
	# elif(case == "realtime"):
	#     store_path = "SBM_App/dataset/realtime/{}.png".format(uid)
	# else:
	#     store_path = "SBM_App/dataset/video/{}.png".format(uid)

	# cv2.imwrite(store_path,np.array(data_rects[0]))
	# print("elapsed time: ",time.time()-t1)
	video_capture.release()
	cv2.destroyAllWindows()
	return reg_face_emb

def register_face(request):
	global uname,uid
	print("reached 'register_face' in views")
	fname = request.POST.get('fname')
	lname = request.POST.get('lname')
	uname = str(fname).strip()+" "+str(lname).strip()
	uid = int(request.POST.get('user_id'))
	dob=request.POST.get('dob')
	addr=request.POST.get('addr')
	parent=request.POST.get('parent')
	sex=request.POST.get('sex')
	if(str(sex) == str(1)):
		sex = 'Male'
	else:
		sex = "Female"
	mobile_no=request.POST.get('mobile_no')
	email=request.POST.get('email')
	class_id=request.POST.get('class_id')
	section_id = request.POST.get('section_id')
	print("uname: {},uid: {},dob: {},addr: {},parent: {},sex: {},mobile_no: {},email: {},class_id: {},section_id: {}".format(uname,uid,dob,addr,parent,sex,mobile_no,email,class_id,section_id))
	case = 'TRAIN'
	ret_val = unique_user_check(uid)
	if(ret_val != None):
		print("value: uid")
		print("user:{} already existed".format(uid))
		return HttpResponse("yes")
	else:
		print("No match found in the Database")
		print("\n"*2)
		print("uname: ",uname)
		print("uid: ",uid)
		print("\n"*2)
		
		embs = capture_user(uid,"TRAIN")
		####################done with Face Embeddings####################################
		status = user_DB(uname,uid,dob,addr,parent,sex,mobile_no,email,class_id,section_id,embs[0])
		if(status == 'success'):
			return render(request,'SBM_App/suc_reg.html')
		else:
			return render(request,'SBM_App/unauth_reg.html')

def start_main_model(case,video_file_path=False):
	count=1
	frame_count = 0
	if(case == "video"):
		video_capture = cv2.VideoCapture(video_file_path)
	else:
		video_capture = cv2.VideoCapture(0)
	while(True):
	    # Capture frame-by-frame
	    frame_count +=1
	    ret, frame = video_capture.read()
	    frame1 = frame
	    gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
	    faces = faceCascade.detectMultiScale(gray,scaleFactor=1.1,minNeighbors=5,minSize=(80, 80))
	    # Draw a rectangle around the faces
	    for (x, y, w, h) in faces:
	    	cv2.rectangle(frame, (x-2, y-37), (x+w+2, y+h+3), (0, 255, 255), 2)
	    cv2.imshow('Video', frame)  #Display the resulting frame
	    k = cv2.waitKey(1)
	    if((k%256 == 27) or (0xFF == ord('q'))):   # ESC or Q pressed
	    	print("Escape hit, closing...")
	    	break
	    # elif(k%256 == 32):
	    if((case=="video" and frame_count%5 == 0) or (case=="realtime" and k%256 == 32)):
	    	print("faces found: ",len(faces))
	    	ret, frame = video_capture.read()
	    	#try:
    		# data_rects = face_capture.crop_images_frame(frame)
    		# count+=1

    		# for img1 in data_rects:
    		# 	cv2.imwrite("face_aligned.jpg",img1)
    		# 	path = capture_user(uid,"TEST")
    		# 	print("path(registered): ",path)
    		# 	emb_dict = embeddings_proc(path)
    		# 	reg_face_emb = emb_dict[0]['embedding']
    		# 	#return render(request,'SBM_App/suc_reg.html')
    		# 	print("embeddings are extracted...")
    		# 	print("face_emb",reg_face_emb)
    		# 	#print(embeddings_proc())
    		# 	assert(False)
    			
    		# 	emb_dict = face_embeddings.get_embeddings(img1)
    		# 	log_face_emb = emb_dict[0]['embedding'][0]
    		#embs = capture_user(11,"TEST")
    		cv2.imwrite("media/verify_img.jpg",frame)
    		ver_ret = verification_proc()
	    	try:	#return value of verification should needs to have "faces_list" key in it
	    		print("ver_ret: ",len(ver_ret[0]['faces_list']))
	    		embs = []
	    		print("==============================")
	    		for reg in range(len(ver_ret[0]['faces_list'])):
	    			aligned_image = np.array(ver_ret[0]['faces_list'][reg])
	    			cv2.imwrite("media/aligned_image_ver_{}.jpg".format(reg),aligned_image)
	    			emb_dict = embeddings_proc("media/aligned_image_ver_{}.jpg".format(reg))
	    			#embs.append(emb_dict[0]['embedding'])
	    			user_status,u_id,u_dist = user_verification_check(emb_dict[0]['embedding'])
	    			if(user_status != "unknown"):
	    				Attendance_DB(u_id)
	    			print("Information: \nPerson ID: {}\nPerson Dist: {}".format(user_status,u_id,u_dist))
	    		print("==============================")
	    	except:
	    		pass
	video_capture.release()
	cv2.destroyAllWindows()

def generateId():#>>>>>>>>>>>>>>>>>>
    return uuid.uuid1().hex

def login_face_video(request):#>>>>>>>>>>>>>>>>>>
	case = "video"
	if request.method=='POST':
		print('In post')
		if request.FILES['video']:
			print("request: ",request)
			videoId = generateId()
			print("uploaded files: ",videoId)
			#assert(False)
			#Perform your ai model operation with video  here
			video = request.FILES['video']
			print("video: ",video)
			
			fs = FileSystemStorage(location="media/videos/")
			video_name = str(video.name).replace(" ","_").replace(",","").replace("-","_").replace("(","_").replace(")","_")
			filename = fs.save(video_name, video)
			print("filename: ",filename)
			# video_file_name = str(video).split("\\")[-1]
			# print("video_file_name:",video_file_name)
			# #result_video_name = video_file_name
			# model = Uploads(video=video_file_name, videoId= videoId)
			# model.save()

			start_main_model(case,str("media/videos/"+video_name))
			return HttpResponse("Done! with *video*")

def login_face_realtime(request):#>>>>>>>>>>>>>>>>>>
	case = 'realtime'
	start_main_model(case=case)
	return HttpResponse("Done! with *RealTime*") 

def get_registered_users(request):#>>>>>>>>>>>>>>>>>>>>>>>>>>>
	users = Users.objects.all()
	user_ids,user_names,dates,times,dobs,parents,sexs,mobile_nos,emails,class_ids,addrs = [],[],[],[],[],[],[],[],[],[],[]
	df = pd.DataFrame(columns=['User Id', 'User Name','Date','Time','DOB','Gaurdian','Sex','Mobile No','Email','Class No','Addr'])
	for num,user in enumerate(users):
		#print(	user_name	c_date	c_time	emb	user_id	dob	parent	sex	mobile_no	email	class_id	addr)
		user_ids.append(user.user_id)
		user_names.append(user.user_name)
		dates.append(user.c_date)
		times.append(user.c_time)
		dobs.append(user.dob)
		parents.append(user.parent)
		sexs.append(user.sex)
		mobile_nos.append(user.mobile_no)
		emails.append(user.email)
		class_ids.append(user.class_id)
		addrs.append(user.addr)
		df.loc[num] = [str(user.user_id),str(user.user_name),str(user.c_date),str(user.c_time),str(user.dob),str(user.parent),str(user.sex),str(user.mobile_no),str(user.email),str(user.class_id),str(user.addr)]
	
	today = str(date.today()).replace("-","_")
	return render(request,'SBM_App/registered_users.html',{'data':zip(user_ids, user_names,dates,times,dobs,parents,sexs,mobile_nos,emails,class_ids,addrs)})

def get_student_logs(request):#>>>>>>>>>>>>>>>>>>>>>>>>>>>
	logs = StudentLogs.objects.all()
	record_ids,user_ids,user_names,dates,times = [],[],[],[],[]
	df = pd.DataFrame(columns=['Record ID','User ID','User Name','Date','Time'])
	for num,user in enumerate(logs):
		#print(user_id,user_name,c_date,c_time)
		record_ids.append(user.record_id)
		user_ids.append(user.log_id)
		user_names.append(user.log_name)
		dates.append(user.log_date)
		times.append(user.log_time)
		df.loc[num] = [str(user.record_id),str(user.log_id),str(user.log_name),str(user.log_date),str(user.log_time)]
	today = str(date.today()).replace("-","_")
	return render(request,'SBM_App/student_logs.html',{'data':zip(record_ids, user_ids, user_names, dates, times)})

def get_attendance_logs(request):#>>>>>>>>>>>>>>>>>>>>>>>>>>>
	logs = Attendance.objects.all()
	user_ids,user_names,class_ids,section_ids,dates,days,months,years,in_times,out_times,durations,summarys,statuses = [],[],[],[],[],[],[],[],[],[],[],[],[]
	df = pd.DataFrame(columns=['User ID','Attendance Date','Att_Day','Att_Month','Att_Year','In Time','Out Time','Duration','Status'])
	for num,user in enumerate(logs):
		#atd_id,att_date,in_time,out_time,duration,status
		user_ids.append(user.std_id)
		#user_names.append(user.std_name)
		#class_ids.append(user.class_id)
		#section_ids.append(user.section_id)
		dates.append(user.att_date)
		days.append(user.att_day)
		months.append(user.att_month)
		years.append(user.att_year)
		in_times.append(user.in_time)
		out_times.append(user.out_time)
		durations.append(user.duration)
		summarys.append(user.summary)
		statuses.append(user.status)
		df.loc[num] = [str(user.std_id),str(user.att_date),str(user.att_day),str(user.att_month),str(user.att_year),str(user.in_time),str(user.out_time),str(user.duration),str(user.status)]
	today = str(date.today()).replace("-","_")
	return render(request,'SBM_App/attendance_users.html',{'data':zip(user_ids,dates,days,months,years,in_times,out_times,durations,summarys,statuses)})
def get_attendance_download(request):
	name = "Reports/Attendance_Report.csv"
	file_path = os.path.join(settings.MEDIA_ROOT, name)
	print("csv_file_path :",file_path)
	if os.path.exists(file_path):
		with open(file_path, 'rb') as fh:
			response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
			response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
		return response
	raise Http404
def get_studentwise_download(request):
	name = "Reports/StudentWise_Report.csv"
	file_path = os.path.join(settings.MEDIA_ROOT, name)
	print("csv_file_path :",file_path)
	if os.path.exists(file_path):
		with open(file_path, 'rb') as fh:
			response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
			response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
		return response
	raise Http404

def time_based_logs(request):#>>>>>>>>>>>>>>>>>>>>>>>>>>>
	logs = Attendance.objects.all()
	user_ids,dates,in_times,out_times,durations,statuses = [],[],[],[],[],[]
	df = pd.DataFrame(columns=['User ID','Attendance Date','In Time','Out Time','Duration','Status'])
	
	for num,user in enumerate(logs):
		#atd_id,att_date,in_time,out_time,duration,status
		if(str(user.in_time)>  str(user.status) == "Present"):
			user_ids.append(user.std_id)
			dates.append(user.att_date)
			in_times.append(user.in_time)
			out_times.append(user.out_time)
			durations.append(user.duration)
			statuses.append(user.status)
			df.loc[num] = [str(user.std_id),str(user.att_date),str(user.in_time),str(user.out_time),str(user.duration),str(user.status)]
	today = str(date.today()).replace("-","_")
	return render(request,'SBM_App/attendance_users.html',{'data':zip(user_ids, dates, in_times,out_times,durations,statuses)})

def get_datewise_logs_home(request):
	return render(request,'SBM_App/datewise_report_home.html')

# def get_datewise_logs(request):
# 	t1 = time.time()
# 	class_id = request.POST.get('class').strip()
# 	section_id = request.POST.get('section').strip()
# 	date = request.POST.get('date').strip()
# 	print(f"class_id: {class_id}, Section: {section_id}, Date: {date}")
# 	roll_no,name,time_in,time_out,dur,summary = [],[],[],[],[],[]
# 	class_users = Attendance.objects.filter(class_id=class_id,section_id=section_id,att_date=date)
# 	class_users = list(class_users.values_list())
# 	print("class_users: ",class_users)
# 	df = pd.DataFrame(columns=['Roll Number','Name','Time In','Time Out','Duration(H:M)','Summary'])
# 	for num in range(len(class_users)):
# 		roll_no.append(class_users[num][0])
# 		name.append(class_users[num][1])
# 		time_in.append(class_users[num][8])
# 		time_out.append(class_users[num][9])
# 		dur.append(class_users[num][10])
# 		summary.append(class_users[num][11])
# 		df.loc[num] = [str(class_users[num][0]),str(class_users[num][1]),str(class_users[num][8]),str(class_users[num][9]),str(class_users[num][10]),str(class_users[num][11])]
# 	print("elapsed time: ",time.time()-t1)
# 	df.to_csv("media/Reports/Attendance_Report.csv")
# 	return render(request,'SBM_App/datewise_report.html',{'class_id':class_id,'section_id':section_id,'date':date,'data':zip(roll_no,name,time_in,time_out,dur,summary)})

def get_datewise_logs(request):
	t1 = time.time()
	class_id = request.POST.get('class').strip()
	section_id = request.POST.get('section').strip()
	date = request.POST.get('date').strip()
	print(f"class_id: {class_id}, Section: {section_id}, Date: {date}")
	roll_no,name,time_in,time_out,dur,summary = [],[],[],[],[],[]
	class_users = Users.objects.filter(class_id=class_id,section_id=section_id)  # to get User_IDs of respective query params
	print(f"len of class_users: {len(class_users)}")
	df = pd.DataFrame(columns=['Roll Number','Name','Time In','Time Out','Duration(H:M)','Summary'])
	
	if(len(class_users)>0):
		id_names = list(zip(*class_users.values_list()))
		res_users_ids = id_names[0]
		res_users_names = id_names[1]
		print(f"class_users: {res_users_names}")            # Unique User_IDs who are satisfied with above Query
		num=0
		for user_id,user_name in zip(res_users_ids,res_users_names):
			class_users = Attendance.objects.filter(std_id=user_id,att_date=date)
			if(len(class_users)==0):
				break
			class_users = class_users.values_list()[0]
			print(f"class_users:{class_users}")
			roll_no.append(user_id)
			name.append(user_name)
			time_in.append(class_users[6])
			time_out.append(class_users[7])
			dur.append(class_users[8])
			summary.append(class_users[9])
			df.loc[num] = [str(user_id),str(user_name),str(class_users[6]),str(class_users[7]),str(class_users[8]),str(class_users[9])]
			num+=1
		print("elapsed time: ",time.time()-t1)
	#df.to_csv("media/Reports/{}_{}_{}.csv".format(class_id,section_id,date))	
	df.to_csv("media/Reports/Attendance_Report.csv")
	return render(request,'SBM_App/datewise_report.html',{"class_id":class_id,"section_id":section_id,"date":date,'data':zip(roll_no,name,time_in,time_out,dur,summary)})

def get_studentwise_logs_home(request):
	return render(request,'SBM_App/studentwise_report_home.html')

def get_studentwise_logs(request):
	t1 = time.time()
	user_id = request.POST.get('roll_no').strip()
	month_id = request.POST.get('month').strip()
	year_id = request.POST.get('year').strip()
	print(f"class_id: {user_id}, Section: {month_id}, Date: {year_id}")
	dates,time_in,time_out,dur,summary,status = [],[],[],[],[],[]
	user_records = Users.objects.filter(user_id=user_id)  # to get User_IDs of respective query params

	id_names = user_records.values_list()
	if(len(id_names)>0):
		user_name,user_class,user_section = id_names[0][1],id_names[0][10],id_names[0][11]
		print(f"UserName: {user_name}, UserClass: {user_class}, UserSection: {user_section}")
		
		att_records = Attendance.objects.filter(std_id=user_id,att_month=month_id,att_year=year_id)  # to get User_IDs of respective query params
		print(f"len of class_users: {len(att_records)}, values_list: {list(att_records.values_list())}")
		df = pd.DataFrame(columns=['Date','Time In','Time Out','Duration(H:M)','Summary','Status'])
		att_records = list(att_records.values_list())
		for num in range(len(att_records)):
			dates.append(att_records[num][2])
			time_in.append(att_records[num][6])
			time_out.append(att_records[num][7])
			dur.append(att_records[num][8])
			summary.append(att_records[num][9])
			status.append(att_records[num][10])
			df.loc[num] = [str(att_records[num][2]),str(att_records[num][6]),str(att_records[num][7]),str(att_records[num][8]),str(att_records[num][9]),str(att_records[num][10])]
			#num+=1
		print("elapsed time: ",time.time()-t1)
		df.to_csv("media/Reports/StudentWise_Report.csv")
		return render(request,'SBM_App/studentwise_report.html',{'user_id':user_id,'user_name':user_name,'user_class':user_class,'user_section':user_section,'user_month':month_id,'user_year':year_id,'data':zip(dates,time_in,time_out,dur,summary,status)})
	else:
		return render(request,'SBM_App/studentwise_report.html',{'user_id':user_id,'user_name':'-','user_class':"-",'user_section':'-','user_month':month_id,'user_year':year_id,'data':zip(dates,time_in,time_out,dur,summary,status)})

def Attendance_DB_init(request):#>>>>>>>>>>>>>>>>>>
	users = Users.objects.all()
	unix = time.time()
	c_date = str(datetime.fromtimestamp(unix).strftime('%d-%m-%Y'))
	day,month,year = c_date.split("-")
	#c_time = str(datetime.fromtimestamp(unix).strftime('%H:%M:%S'))
	for user in users:
		att = Attendance(std_id=str(user.user_id),att_date=str(c_date),att_day=day,att_month=month,att_year=year,in_time="-",out_time="-",duration="-",summary="-",status="Absent")
		att.save()
	
	return render(request,'SBM_App/register_face.html')

def student_log_db(student_id):#>>>>>>>>>>>>>>>>>>
	att = Users.objects.get(user_id=student_id)
	student_name = att.user_name
	unix = time.time()
	c_date = str(datetime.fromtimestamp(unix).strftime('%d-%m-%Y'))
	c_time = str(datetime.fromtimestamp(unix).strftime('%H:%M:%S'))
	today = str(date.today())
	
	#logs = StudentLogs(log_id=student_id,log_name=student_name,log_date=str(date.today()),log_time=current_time)
	rec_id = len(StudentLogs.objects.all())+1
	print("record {} is inserted!!!".format(rec_id))
	logs = StudentLogs(record_id=rec_id,log_id=student_id,log_name=student_name,log_date=c_date,log_time=c_time)
	logs.save()

def Attendance_DB(obj_id):#>>>>>>>>>>>>>>>>>>
	unix = time.time()
	c_date = str(datetime.fromtimestamp(unix).strftime('%d-%m-%Y'))#current Date
	c_time = str(datetime.fromtimestamp(unix).strftime('%H:%M:%S'))#current Time
	att = Attendance.objects.get(std_id=obj_id,att_date=c_date) # object to update
	if(att.status == "Absent"):
		att.in_time = c_time
		att.status = "Present"
		att.summary = c_time
	else:
		att.out_time = c_time
		t1 = str(att.in_time)
		t2 = str(att.out_time)
		ftr = [3600,60,1]
		t1 = sum([a*b for a,b in zip(ftr, map(int,t1.split(':')))])
		t2 = sum([a*b for a,b in zip(ftr, map(int,t2.split(':')))])
		att.duration = str(time.strftime('%H:%M:%S', time.gmtime(t2-t1)))
		att.summary = str(att.summary)+","+str(c_time)
	att.save() #save the object
	student_log_db(obj_id)

def download(request):#>>>>>>>>>>>>>>>>>>>>>>>>>>>
    name = "Reports/{}/Attendance_Sheet.csv".format(today)
    file_path = os.path.join(settings.MEDIA_ROOT, csv_file)
    print("csv_file_path :",file_path)
    if os.path.exists(file_path):
        with open(file_path, 'rb') as fh:
            response = HttpResponse(fh.read(), content_type="application/vnd.ms-excel")
            response['Content-Disposition'] = 'inline; filename=' + os.path.basename(file_path)
            return response
    raise Http404