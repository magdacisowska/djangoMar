from django.db import models
from django.utils import timezone
import datetime
from django.contrib.auth.models import User, AbstractUser


def week_day(day_number):
    week = ['Pon', 'Wt', 'Śr', 'Czw', 'Pt', 'Sob', 'Nd']
    return week[day_number]


# zbędne, lecz działa
def increment_id():
    last_task = Task.objects.all().order_by('id').last()
    if not last_task:
        return 1
    task_id = last_task.id
    new_task_id = task_id + 1
    return new_task_id


# Create your models here.
class Project(models.Model):
    id = models.IntegerField(primary_key=True)
    full_name = models.CharField(max_length=100)
    code = models.CharField(max_length=10, unique=True)

    def __str__(self):
        return self.code

    class Meta:
        db_table = 'Project'


class Task(models.Model):
    id = models.IntegerField(primary_key=True, default=increment_id)
    project_id = models.ForeignKey(Project, on_delete=models.CASCADE, db_column='project_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user')

    description = models.CharField(max_length=40, blank=True)
    date = models.DateField(default=timezone.now())

    hours = models.FloatField(default=8)
    hour_begin = models.TimeField(default=datetime.time(hour=7, minute=45))
    hour_end = models.TimeField(default=datetime.time(hour=16, minute=0))
    break_time = models.TimeField(default=datetime.timedelta(hours=0, minutes=30))

    test = models.BooleanField(default=True)
    ACTION_CHOICES = (
        ('P', 'P'),('M', 'M'),('L', 'L'),
        ('I', 'I'),('Z', 'Z'),(' ', ' '))
    action = models.CharField(max_length=13, choices=ACTION_CHOICES, default=' ')

    ADVANCEMENT_CHOICES = ((0, '0'), (25, '25'), (50, '50'), (75, '75'), (100, '100'))
    advancement = models.IntegerField(choices=ADVANCEMENT_CHOICES, default='0')

    approved = models.BooleanField(default=False)

    def __str__(self):
        return self.description

    def get_absolute_url(self):
        return "/add"

    # returns day of the week and full date as a string
    def date_show(self):
        return week_day(self.date.weekday()) + ' ' + self.date.strftime("%d/%m/%Y")

    # returns hours of work as a better readable string
    def time_show(self):
        return self.hour_begin.strftime("%H:%M") + ' - ' + self.hour_end.strftime("%H:%M")

    def was_published_recently(self):
        now_day = timezone.now().day
        now_month = timezone.now().month
        return (now_day - 7 <= self.date.day <= now_day) & (now_month <= self.date.month <= now_month)

    # parity flag for display
    def day_parity(self):
        return self.date.day % 2

    # returns if the day is on weekend
    def is_weekend(self):
        return self.date.weekday() == 6 or self.date.weekday() == 5

    # returns fixed hours depending on weekends, type of action
    def fixed_hours(self):
        if self.date.weekday() == 6 or self.date.weekday() == 5:
            return 0
        else:
            return 8

    # returns break_time as timedelta, instead of time
    def break_time_delta(self):
        return datetime.timedelta(minutes=self.break_time.minute)

    # returns total working hours as time, also a base for following functions
    def hours_calc(self):
        beg = datetime.timedelta(hours=self.hour_begin.hour, minutes=self.hour_begin.minute)
        end = datetime.timedelta(hours=self.hour_end.hour, minutes=self.hour_end.minute)
        br = datetime.timedelta(minutes=self.break_time.minute)
        return end - beg - br + datetime.timedelta(minutes=15)

    # returns total working hours as float
    def hours_calc_hr(self):
        return self.hours_calc().total_seconds()/3600

    # returns total overtime as float
    def overtime_hr(self):
        if self.project_id == 'Zwol.' or self.project_id == 'Urlop':
            return 0.0
        else:
            return round((self.hours_calc() - datetime.timedelta(hours=self.fixed_hours())).total_seconds()/3600, 2)

    class Meta:
        db_table = 'Task'


# na razie nie używane
class Employee(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, db_column='user')
    department = models.CharField(max_length=20, blank=True)
    phone = models.CharField(max_length=15)
    more = models.CharField(max_length=30)

    class Meta:
        db_table = 'Employee'

