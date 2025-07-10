from django.urls import path
from . import views

app_name = 'ljudski_resursi'

urlpatterns = [
    path('', views.home, name='home'),
    path('employees/', views.employee_list, name='employee_list'),
    path('employees/create/', views.employee_form, name='employee_create'),
    path('employees/update/<int:pk>/', views.employee_form, name='employee_update'),
    path('employees/delete/<int:pk>/', views.employee_delete, name='employee_delete'),
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.DepartmentCreateView.as_view(), name='department_create'),
    path('positions/', views.position_list, name='position_list'),
    path('evaluacije/', views.evaluacija_list, name='evaluacija_list'),
    path('evaluacije/create/', views.evaluacija_create, name='evaluacija_create'),
    path('evaluacije/update/<int:pk>/', views.evaluacija_update, name='evaluacija_update'),
    path('evaluacije/delete/<int:pk>/', views.evaluacija_delete, name='evaluacija_delete'),
]
