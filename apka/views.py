from django.shortcuts import render
from django.views import generic
from .models import Task, Project
from django.db.models import Sum
from django.urls import reverse_lazy
from django.utils import timezone
import datetime
from django.contrib.auth.models import User
from django.db import connections


# fetch users from a stored procedure
def fetch_users(request):
    cursor = connections['comarch'].cursor()
    try:
        cursor.execute('EXEC Rejestrator_ListaPracownikow')
        result_set = cursor.fetchall()
    finally:
        cursor.close()

    # User.objects.exclude(username='admin').delete()

    for i in range(len(result_set)):
        try:
            q = User(id=result_set[i][0], username=result_set[i][1], is_staff=False,
                 first_name=result_set[i][4] + ' ' + result_set[i][3], last_name=result_set[i][9], email=result_set[i][8])
            q.set_password(result_set[i][2])
        # q.employee.department = result_set[i][9]          # TODO: rozszerzenie wbudowanego modelu User, dodanie dodatkowych pól
        # q.employee.phone = result_set[i][8]
        # q.employee.more = result_set[i][6]
            q.save()
        except:
            pass

    return render(request, 'apka/fetched.html')


# fetch projects from a stored procedure
def fetch_projects(request):
    cursor = connections['comarch'].cursor()
    try:
        cursor.execute('EXEC Rejestrator_ListaProjektow')
        result_set = cursor.fetchall()
    finally:
        cursor.close()

    Project.objects.all().delete()      # delete before update

    for i in range(len(result_set)):
        q = Project(id=result_set[i][0], code=result_set[i][1][:10], full_name=result_set[i][2][:90])
        if result_set[i][4] == 0:           # don't apply archive projects
            q.save()
        else:
            pass
    return render(request, 'apka/fetched_p.html')


# index site
def index(request):
    current_month = timezone.now().month
    current_year = timezone.now().year
    return render(request, 'apka/index.html', {'current_month': current_month, 'current_year': current_year})


# user summary of projects
def summary(request):
    hours_table = []
    attempts_table = []
    advancement_table = []
    project_list = Project.objects.all().order_by('code')
    total_hours = Task.objects.filter(date__month=timezone.now().month,
                                      user=request.user).aggregate(Sum('hours')).get('hours__sum', 0.00)

    for i in project_list:
        hours_table.append(Task.objects.filter(project_id=i, date__month=timezone.now().month,
                                               user=request.user).aggregate(Sum('hours')).get('hours__sum', 0.00))
        attempts_table.append(Task.objects.filter(project_id=i, user=request.user).count())
        try:
            advancement_table.append(Task.objects.filter(project_id=i, user=request.user).latest('date').advancement)
        except:
            advancement_table.append(0)
    zipped_list = zip(project_list, hours_table, attempts_table, advancement_table)

    return render(request, 'apka/projects.html', {'zipped_list': zipped_list, 'total_hours': total_hours})


# historic summary of certain month
def month_summary(request, month, year):
    task_list = Task.objects.filter(date__month=month, date__year=year, user=request.user).order_by('date')
    return render(request, 'apka/month_summary.html', {'task_list': task_list, 'month':month, 'year':year})


# create view and list view of month
class TaskCreate(generic.CreateView):
    template_name = 'apka/registrator.html'
    model = Task
    fields = ['id', 'advancement', 'project_id', 'break_time', 'hour_begin',
              'hour_end', 'date', 'description', 'hours', 'action']

    def form_valid(self, form):
        form.instance.user = self.request.user

        # if the form is valid, update the working hours if there is a difference
        self.object = form.save()
        test = Task.objects.get(id=self.object.id)
        filtered = Task.objects.filter(date=test.date)
        for i in filtered:
            if i.hour_begin != test.hour_begin:
                i.hour_begin = test.hour_begin
            if i.hour_end != test.hour_end:
                i.hour_end = test.hour_end
            if i.break_time != test.break_time:
                i.break_time = test.break_time
            i.save()
        return super().form_valid(form)

    def get_queryset(self):
        return Task.objects.filter(user=self.request.user)

    def get_context_data(self, **kwargs):
        return dict(
            super(TaskCreate, self).get_context_data(**kwargs),
            user=self.request.user,
            project_list=Project.objects.all().order_by('code'),
            task_list=Task.objects.filter(date__month=timezone.now().month, user=self.request.user).order_by('date'),
        )


class TaskUpdate(generic.UpdateView):
    template_name = 'apka/edit_form.html'
    model = Task
    fields = ['project_id', 'hours', 'description', 'hour_begin',
              'hour_end', 'break_time', 'advancement']

    def get_context_data(self, **kwargs):

        test = Task.objects.get(id=self.object.id)
        filtered = Task.objects.filter(date=test.date)
        for i in filtered:
            if i.hour_begin != test.hour_begin:
                i.hour_begin = test.hour_begin
            if i.hour_end != test.hour_end:
                i.hour_end = test.hour_end
            if i.break_time != test.break_time:
                i.break_time = test.break_time
            i.save()

        return dict(
            super(TaskUpdate, self).get_context_data(**kwargs),
            project_list=Project.objects.all().order_by('code'),
            task_list=Task.objects.filter(date__month=timezone.now().month, user=self.request.user).order_by('date'),
            object_id=self.object.id
        )

    def get_success_url(self, **kwargs):
        return reverse_lazy('apka:edit_form', args = {self.object.id})


class TaskDelete(generic.DeleteView):
    model = Task
    template_name = 'apka/delete_form.html'
    success_url = reverse_lazy('apka:task_form')


class SubmitMonth(generic.ListView):
    model = Task
    template_name = 'apka/submit_month.html'

    def get_context_data(self, **kwargs):

        daily_sum = [31]                    # tablica przechowujaca sumę godzin danego dnia
        monthly_sum = 0                     # suma godzin calego miesiaca
        overtime_sum = 0                    # suma nadgodzin calego miesiaca
        fixed_sum = 0                       # suma stałych godzin całego miesiaca
        task_list = Task.objects.filter(date__month=timezone.now().month, user=self.request.user)

        # search and sum hours through the whole month
        for i in range(1,31):
            daily_sum.append(Task.objects.filter(date__day=i, date__month=timezone.now().month,
                                                 user=self.request.user).aggregate(Sum('hours')).get('hours__sum', 0.00))
            try:
                monthly_sum += Task.objects.filter(date__day=i, date__month=timezone.now().month,
                                                   user=self.request.user)[:1].get().hours_calc_hr()
                overtime_sum += Task.objects.filter(date__day=i, date__month=timezone.now().month,
                                                    user=self.request.user)[:1].get().overtime_hr()
                fixed_sum += Task.objects.filter(date__day=i, date__month=timezone.now().month,
                                                 user=self.request.user)[:1].get().fixed_hours()
            except:
                pass

        # test for hours total
        for task in task_list:
            if task.hours_calc().total_seconds() == datetime.timedelta(hours=daily_sum[task.date.day]).total_seconds():
                task.test = True
            else:
                task.test = False
            task.save()                             # save changes to database

        return dict(
            super(SubmitMonth, self).get_context_data(**kwargs),
            project_list=Project.objects.all().order_by('code'),
            task_list=Task.objects.filter(user=self.request.user, date__month=timezone.now().month).order_by('date'),
            sum_1=Task.objects.filter(date__month=timezone.now().month,
                                      user=self.request.user).aggregate(Sum('hours')).get('hours__sum', 0.00),
            sum_2=monthly_sum, overtime_sum=overtime_sum, fixed_sum=fixed_sum
        )


class VerificationAdmin(generic.ListView):
    model = Task
    template_name = 'apka/verification.html'

    def get_context_data(self, **kwargs):
        if self.request.user.username == 'admin':
            task_list = Task.objects.filter(approved=False)
            user_list = User.objects.all()
        else:
            task_list = Task.objects.filter(approved=False, user__last_name=self.request.user.last_name)
            user_list = User.objects.filter(last_name=self.request.user.last_name)
        return dict(
            super(VerificationAdmin, self).get_context_data(**kwargs),
            user_list=user_list,
            task_list=task_list
        )


class VerificationAdminApproved(generic.ListView):
    model = Task
    template_name = 'apka/verified.html'

    def get_context_data(self, **kwargs):
        cursor = connections['comarch'].cursor()
        if self.request.user.username == 'admin':
            task_list = Task.objects.filter(approved=False)
        else:
            task_list = Task.objects.filter(approved=False, user__last_name=self.request.user.last_name)
        for i in task_list:
            try:
                # cursor.execute('EXEC Rejestrator_GodzinyInsert_proc %s', [i.project_id, i.user, i.action,
                #                                                        str(i.hours), str(i.date),
                #                                                        str(i.description)])
                cursor.execute(             # TODO: procedura zatwierdzania (problemem jest argument Komentarz)
                    '''
                        EXEC Rejestrator_GodzinyInsert_proc
                            @PrjId = ?, -- int
                            @PrcId = ?, -- int
                            @Czynnosc = ?, -- varchar(1)
                            @Godziny = ?, -- decimal(15,2)
                            @Data = ?, -- datetime
                            @Komentarz = ? -- varchar(200)
                    ''',
                    [i.project_id,
                     i.user,
                     i.action,
                     i.hours,
                     i.date,
                     i.description]
                )
                result = cursor.fetchall()
            finally:
                cursor.close()

        for i in task_list:
            i.approved = True
            i.save()
        return dict(super(VerificationAdminApproved, self).get_context_data(**kwargs))


class UsersList(generic.ListView):
    model = User
    template_name = 'apka/users_list.html'

    def get_context_data(self, **kwargs):
        cursor = connections['comarch'].cursor()                    # TODO: rozszerzenie modelu User...
        try:
            cursor.execute('EXEC Rejestrator_ListaPracownikow')
            result_set = cursor.fetchall()
        finally:
            cursor.close()

        return dict(
            super(UsersList, self).get_context_data(**kwargs),
            # user_list=User.objects.all(),                 # TODO: ... i wyświetlanie obiektów modelu User, a nie za każdym razem wyniku wywołania procedury
            user_list=result_set,
            current_month=timezone.now().month,
            current_year=timezone.now().year
        )
