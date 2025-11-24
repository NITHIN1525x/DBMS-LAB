from django.urls import path
from . import views

urlpatterns = [
    # Dashboard
    path('', views.dashboard, name='dashboard'),
    
    # Roles
    path('roles/', views.role_list, name='role_list'),
    path('roles/create/', views.role_create, name='role_create'),
    path('roles/delete/<int:pk>/', views.role_delete, name='role_delete'),
    
    # Departments
    path('departments/', views.department_list, name='department_list'),
    path('departments/create/', views.department_create, name='department_create'),
    path('departments/delete/<int:pk>/', views.department_delete, name='department_delete'),
    
    # Users
    path('users/', views.user_list, name='user_list'),
    path('users/create/', views.user_create, name='user_create'),
    path('users/delete/<int:pk>/', views.user_delete, name='user_delete'),
    
    # Venues
    path('venues/', views.venue_list, name='venue_list'),
    path('venues/create/', views.venue_create, name='venue_create'),
    path('venues/delete/<int:pk>/', views.venue_delete, name='venue_delete'),
    
    # Categories
    path('categories/', views.category_list, name='category_list'),
    path('categories/create/', views.category_create, name='category_create'),
    path('categories/delete/<int:pk>/', views.category_delete, name='category_delete'),
    
    # Events
    path('events/', views.event_list, name='event_list'),
    path('events/create/', views.event_create, name='event_create'),
    path('events/delete/<int:pk>/', views.event_delete, name='event_delete'),
    
    # Registrations
    path('registrations/', views.registration_list, name='registration_list'),
    path('registrations/create/', views.registration_create, name='registration_create'),
    path('registrations/delete/<int:pk>/', views.registration_delete, name='registration_delete'),
    
    # Attendance
    path('attendance/', views.attendance_list, name='attendance_list'),
    path('attendance/create/', views.attendance_create, name='attendance_create'),
    path('attendance/delete/<int:pk>/', views.attendance_delete, name='attendance_delete'),
    
    # Resources
    path('resources/', views.resource_list, name='resource_list'),
    path('resources/create/', views.resource_create, name='resource_create'),
    path('resources/delete/<int:pk>/', views.resource_delete, name='resource_delete'),
    
    # Event Resources
    path('event-resources/', views.event_resource_list, name='event_resource_list'),
    path('event-resources/create/', views.event_resource_create, name='event_resource_create'),
    path('event-resources/delete/<int:pk>/', views.event_resource_delete, name='event_resource_delete'),
]