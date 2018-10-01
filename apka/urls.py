from django.urls import path
from . import views

app_name = 'apka'
urlpatterns = [
    path('', views.index, name='index'),
    path('add', views.TaskCreate.as_view(), name='task_form'),
    path('edit/<int:pk>', views.TaskUpdate.as_view(), name='edit_form'),
    path('summary', views.summary, name='summary'),
    path('history/<int:month>/<int:year>', views.month_summary, name='month_summary'),
    path('delete/<int:pk>', views.TaskDelete.as_view(), name='delete_form'),
    path('submit', views.SubmitMonth.as_view(), name='submit_month'),
    path('veryfication', views.VerificationAdmin.as_view(), name='verification'),
    path('verified', views.VerificationAdminApproved.as_view(), name='verified'),
    path('fetched', views.fetch_users, name='fetched'),
    path('list', views.UsersList.as_view(), name='users_list'),
    path('fetched_p', views.fetch_projects, name='fetched_p')
]