from django.urls import path
from django.conf.urls import url
from . import views
from django.conf import settings
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf.urls.static import static

urlpatterns = [
    
    #Html files
    url(r'^$',views.register_here_face,name="register_here_face"),
    url(r'^register_here_face$',views.register_here_face,name="register_here_face"),
    url(r'^login_here_face$',views.login_here_face,name="login_here_face"),
    url(r'^suc_reg$',views.suc_reg,name="suc_reg"),
    url(r'^suc_log$',views.suc_log,name="suc_log"),

    #url(r'^login_face$',views.login_face,name='login_face'),
    url(r'^login_face_realtime$',views.login_face_realtime,name='login_face_realtime'),
    url(r'^login_face_video$',views.login_face_video,name='login_face_video'),
    url(r'^register_face$',views.register_face,name='register_face'),
    
    #url(r'^take_pictures$',views.take_pictures,name='take_pictures'),
    url(r'^unique_user_check$',views.unique_user_check,name='unique_user_check'),

    url(r'^get_registered_users$',views.get_registered_users,name='get_registered_users'),
    url(r'^get_student_logs$',views.get_student_logs,name='get_student_logs'),
    url(r'^Attendance_DB_init$',views.Attendance_DB_init,name='Attendance_DB_init'),
    url(r'^get_attendance_logs$',views.get_attendance_logs,name='get_attendance_logs'),
    url(r'^get_datewise_logs_home$',views.get_datewise_logs_home,name='get_datewise_logs_home'),
    url(r'^get_datewise_logs$',views.get_datewise_logs,name='get_datewise_logs'),
    url(r'^get_studentwise_logs_home$',views.get_studentwise_logs_home,name='get_studentwise_logs_home'),
    url(r'^get_studentwise_logs$',views.get_studentwise_logs,name='get_studentwise_logs'),
    url(r'^report_here_logs$',views.report_here_logs,name='report_here_logs'),
    url(r'^download$',views.download,name='download'),
    url(r'^get_attendance_download$',views.get_attendance_download,name="get_attendance_download"),
    url(r'^get_studentwise_download$',views.get_studentwise_download,name="get_studentwise_download")
    #url(r'^train_models$',views.train_models,name="train_models"),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL,document_root=settings.MEDIA_ROOT)
