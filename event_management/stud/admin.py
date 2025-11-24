from django.contrib import admin
from .models import (
    Role, Department, User, Venue, Category, 
    Event, Registration, Attendance, Resource, EventResource
)

@admin.register(Role)
class RoleAdmin(admin.ModelAdmin):
    list_display = ['role_id', 'role_name', 'description', 'created_at']
    search_fields = ['role_name']

@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ['dept_id', 'dept_name', 'dept_code', 'hod_name', 'created_at']
    search_fields = ['dept_name', 'dept_code']

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ['user_id', 'name', 'email', 'roll_no', 'role', 'dept', 'created_at']
    list_filter = ['role', 'dept']
    search_fields = ['name', 'email', 'roll_no']

@admin.register(Venue)
class VenueAdmin(admin.ModelAdmin):
    list_display = ['venue_id', 'name', 'location', 'capacity']
    search_fields = ['name', 'location']

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['category_id', 'name', 'description', 'active_status']
    list_filter = ['active_status']
    search_fields = ['name']

@admin.register(Event)
class EventAdmin(admin.ModelAdmin):
    list_display = ['event_id', 'title', 'category', 'organizer', 'venue', 'start_datetime', 'status']
    list_filter = ['status', 'category', 'venue']
    search_fields = ['title', 'description']
    date_hierarchy = 'start_datetime'

@admin.register(Registration)
class RegistrationAdmin(admin.ModelAdmin):
    list_display = ['reg_id', 'event', 'user', 'registered_at', 'status']
    list_filter = ['status', 'event']
    search_fields = ['user__name', 'event__title']

@admin.register(Attendance)
class AttendanceAdmin(admin.ModelAdmin):
    list_display = ['attendance_id', 'event', 'user', 'present', 'checked_at']
    list_filter = ['present', 'event']
    search_fields = ['user__name', 'event__title']

@admin.register(Resource)
class ResourceAdmin(admin.ModelAdmin):
    list_display = ['resource_id', 'resource_name', 'total_quantity']
    search_fields = ['resource_name']

@admin.register(EventResource)
class EventResourceAdmin(admin.ModelAdmin):
    list_display = ['er_id', 'event', 'resource', 'quantity_required']
    list_filter = ['event', 'resource']
    search_fields = ['event__title', 'resource__resource_name']