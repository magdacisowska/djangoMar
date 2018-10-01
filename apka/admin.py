from django.contrib import admin
from .models import Task, Project
from django.contrib.auth.models import User
# Register your models here.


class ProjectAdmin(admin.ModelAdmin):
    list_display = ('full_name','code')


class TaskAdmin(admin.ModelAdmin):
    list_display = ('user', 'project_id','description','hours', 'date', 'hours_calc', 'hour_begin', 'hour_end')
    list_filter = ['user', 'date', 'project_id']


admin.site.register(Project, ProjectAdmin)
admin.site.register(Task, TaskAdmin)