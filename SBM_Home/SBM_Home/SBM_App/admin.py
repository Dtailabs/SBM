from django.contrib import admin
from .models import Users,Attendance,StudentLogs
# Register your models here.
admin.site.register(Users)
#admin.site.register(Uploads)
admin.site.register(Attendance)
admin.site.register(StudentLogs)

