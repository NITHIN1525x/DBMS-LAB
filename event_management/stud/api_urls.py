from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    RoleViewSet, DepartmentViewSet, UserViewSet,
    VenueViewSet, CategoryViewSet, EventViewSet,
    RegistrationViewSet, AttendanceViewSet,
    ResourceViewSet, EventResourceViewSet
)

router = DefaultRouter()
router.register(r'roles', RoleViewSet, basename='role')
router.register(r'departments', DepartmentViewSet, basename='department')
router.register(r'users', UserViewSet, basename='user')
router.register(r'venues', VenueViewSet, basename='venue')
router.register(r'categories', CategoryViewSet, basename='category')
router.register(r'events', EventViewSet, basename='event')
router.register(r'registrations', RegistrationViewSet, basename='registration')
router.register(r'attendance', AttendanceViewSet, basename='attendance')
router.register(r'resources', ResourceViewSet, basename='resource')
router.register(r'event-resources', EventResourceViewSet, basename='eventresource')

urlpatterns = [
    path('', include(router.urls)),
]