from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.db.models import Count, Q
from datetime import datetime
from .models import (
    Role, Department, User, Venue, Category,
    Event, Registration, Attendance, Resource, EventResource
)

# Dashboard View
def dashboard(request):
    context = {
        'total_events': Event.objects.count(),
        'total_users': User.objects.count(),
        'total_venues': Venue.objects.count(),
        'total_registrations': Registration.objects.count(),
        'upcoming_events': Event.objects.filter(
            start_datetime__gte=datetime.now()
        ).order_by('start_datetime')[:5],
        'recent_registrations': Registration.objects.order_by('-registered_at')[:5],
    }
    return render(request, 'dashboard.html', context)

# Role Views
def role_list(request):
    roles = Role.objects.all()
    return render(request, 'roles/list.html', {'roles': roles})

def role_create(request):
    if request.method == 'POST':
        role = Role.objects.create(
            role_name=request.POST['role_name'],
            description=request.POST.get('description', ''),
            created_at=datetime.now()
        )
        messages.success(request, 'Role created successfully!')
        return redirect('role_list')
    return render(request, 'roles/form.html')

def role_delete(request, pk):
    role = get_object_or_404(Role, role_id=pk)
    role.delete()
    messages.success(request, 'Role deleted successfully!')
    return redirect('role_list')

# Department Views
def department_list(request):
    departments = Department.objects.all()
    return render(request, 'departments/list.html', {'departments': departments})

def department_create(request):
    if request.method == 'POST':
        department = Department.objects.create(
            dept_name=request.POST['dept_name'],
            dept_code=request.POST['dept_code'],
            hod_name=request.POST.get('hod_name', ''),
            created_at=datetime.now()
        )
        messages.success(request, 'Department created successfully!')
        return redirect('department_list')
    return render(request, 'departments/form.html')

def department_delete(request, pk):
    department = get_object_or_404(Department, dept_id=pk)
    department.delete()
    messages.success(request, 'Department deleted successfully!')
    return redirect('department_list')

# User Views
def user_list(request):
    users = User.objects.all().select_related('role', 'dept')
    return render(request, 'users/list.html', {'users': users})

def user_create(request):
    if request.method == 'POST':
        user = User.objects.create(
            name=request.POST['name'],
            roll_no=request.POST.get('roll_no', ''),
            email=request.POST.get('email', ''),
            phone=request.POST.get('phone', ''),
            role_id=request.POST.get('role'),
            dept_id=request.POST.get('dept'),
            created_at=datetime.now()
        )
        messages.success(request, 'User created successfully!')
        return redirect('user_list')
    
    roles = Role.objects.all()
    departments = Department.objects.all()
    return render(request, 'users/form.html', {
        'roles': roles,
        'departments': departments
    })

def user_delete(request, pk):
    user = get_object_or_404(User, user_id=pk)
    user.delete()
    messages.success(request, 'User deleted successfully!')
    return redirect('user_list')

# Venue Views
def venue_list(request):
    venues = Venue.objects.all()
    return render(request, 'venues/list.html', {'venues': venues})

def venue_create(request):
    if request.method == 'POST':
        venue = Venue.objects.create(
            name=request.POST['name'],
            location=request.POST.get('location', ''),
            capacity=request.POST['capacity']
        )
        messages.success(request, 'Venue created successfully!')
        return redirect('venue_list')
    return render(request, 'venues/form.html')

def venue_delete(request, pk):
    venue = get_object_or_404(Venue, venue_id=pk)
    venue.delete()
    messages.success(request, 'Venue deleted successfully!')
    return redirect('venue_list')

# Category Views
def category_list(request):
    categories = Category.objects.all()
    return render(request, 'categories/list.html', {'categories': categories})

def category_create(request):
    if request.method == 'POST':
        category = Category.objects.create(
            name=request.POST['name'],
            description=request.POST.get('description', ''),
            icon=request.POST.get('icon', ''),
            active_status=request.POST.get('active_status') == 'on'
        )
        messages.success(request, 'Category created successfully!')
        return redirect('category_list')
    return render(request, 'categories/form.html')

def category_delete(request, pk):
    category = get_object_or_404(Category, category_id=pk)
    category.delete()
    messages.success(request, 'Category deleted successfully!')
    return redirect('category_list')

# Event Views
def event_list(request):
    events = Event.objects.all().select_related('category', 'organizer', 'venue')
    return render(request, 'events/list.html', {'events': events})

def event_create(request):
    if request.method == 'POST':
        event = Event.objects.create(
            title=request.POST['title'],
            description=request.POST.get('description', ''),
            category_id=request.POST.get('category'),
            organizer_id=request.POST.get('organizer'),
            venue_id=request.POST.get('venue'),
            start_datetime=request.POST.get('start_datetime'),
            end_datetime=request.POST.get('end_datetime'),
            capacity=request.POST.get('capacity'),
            status=request.POST.get('status', 'scheduled'),
            created_at=datetime.now()
        )
        messages.success(request, 'Event created successfully!')
        return redirect('event_list')
    
    categories = Category.objects.all()
    users = User.objects.all()
    venues = Venue.objects.all()
    return render(request, 'events/form.html', {
        'categories': categories,
        'users': users,
        'venues': venues
    })

def event_delete(request, pk):
    event = get_object_or_404(Event, event_id=pk)
    event.delete()
    messages.success(request, 'Event deleted successfully!')
    return redirect('event_list')

# Registration Views
def registration_list(request):
    registrations = Registration.objects.all().select_related('event', 'user')
    return render(request, 'registrations/list.html', {'registrations': registrations})

def registration_create(request):
    if request.method == 'POST':
        registration = Registration.objects.create(
            event_id=request.POST['event'],
            user_id=request.POST['user'],
            registered_at=datetime.now(),
            status=request.POST.get('status', 'confirmed')
        )
        messages.success(request, 'Registration created successfully!')
        return redirect('registration_list')
    
    events = Event.objects.all()
    users = User.objects.all()
    return render(request, 'registrations/form.html', {
        'events': events,
        'users': users
    })

def registration_delete(request, pk):
    registration = get_object_or_404(Registration, reg_id=pk)
    registration.delete()
    messages.success(request, 'Registration deleted successfully!')
    return redirect('registration_list')

# Attendance Views
def attendance_list(request):
    attendances = Attendance.objects.all().select_related('event', 'user')
    return render(request, 'attendance/list.html', {'attendances': attendances})

def attendance_create(request):
    if request.method == 'POST':
        attendance = Attendance.objects.create(
            event_id=request.POST['event'],
            user_id=request.POST['user'],
            present=request.POST.get('present') == 'on',
            checked_at=datetime.now()
        )
        messages.success(request, 'Attendance marked successfully!')
        return redirect('attendance_list')
    
    events = Event.objects.all()
    users = User.objects.all()
    return render(request, 'attendance/form.html', {
        'events': events,
        'users': users
    })

def attendance_delete(request, pk):
    attendance = get_object_or_404(Attendance, attendance_id=pk)
    attendance.delete()
    messages.success(request, 'Attendance deleted successfully!')
    return redirect('attendance_list')

# Resource Views
def resource_list(request):
    resources = Resource.objects.all()
    return render(request, 'resources/list.html', {'resources': resources})

def resource_create(request):
    if request.method == 'POST':
        resource = Resource.objects.create(
            resource_name=request.POST['resource_name'],
            total_quantity=request.POST['total_quantity']
        )
        messages.success(request, 'Resource created successfully!')
        return redirect('resource_list')
    return render(request, 'resources/form.html')

def resource_delete(request, pk):
    resource = get_object_or_404(Resource, resource_id=pk)
    resource.delete()
    messages.success(request, 'Resource deleted successfully!')
    return redirect('resource_list')

# Event Resource Views
def event_resource_list(request):
    event_resources = EventResource.objects.all().select_related('event', 'resource')
    return render(request, 'event_resources/list.html', {'event_resources': event_resources})

def event_resource_create(request):
    if request.method == 'POST':
        event_resource = EventResource.objects.create(
            event_id=request.POST['event'],
            resource_id=request.POST['resource'],
            quantity_required=request.POST['quantity_required']
        )
        messages.success(request, 'Event Resource created successfully!')
        return redirect('event_resource_list')
    
    events = Event.objects.all()
    resources = Resource.objects.all()
    return render(request, 'event_resources/form.html', {
        'events': events,
        'resources': resources
    })

def event_resource_delete(request, pk):
    event_resource = get_object_or_404(EventResource, er_id=pk)
    event_resource.delete()
    messages.success(request, 'Event Resource deleted successfully!')
    return redirect('event_resource_list')