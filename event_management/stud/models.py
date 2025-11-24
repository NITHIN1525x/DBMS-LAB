from django.db import models


class Role(models.Model):
    role_id = models.AutoField(primary_key=True)
    role_name = models.CharField(unique=True, max_length=30)
    description = models.CharField(max_length=200, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.role_name

    class Meta:
        managed = False
        db_table = 'roles'


class Department(models.Model):
    dept_id = models.AutoField(primary_key=True)
    dept_name = models.CharField(unique=True, max_length=150)
    dept_code = models.CharField(unique=True, max_length=20)
    hod_name = models.CharField(max_length=150, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.dept_name

    class Meta:
        managed = False
        db_table = 'departments'


class User(models.Model):
    user_id = models.AutoField(primary_key=True)
    roll_no = models.CharField(max_length=20, blank=True, null=True)
    name = models.CharField(max_length=200)
    email = models.CharField(max_length=200, blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    password_hash = models.CharField(max_length=255, blank=True, null=True)
    role = models.ForeignKey(Role, on_delete=models.SET_NULL, blank=True, null=True, db_column='role_id', related_name='users')
    dept = models.ForeignKey(Department, on_delete=models.SET_NULL, blank=True, null=True, db_column='dept_id', related_name='users')
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'users'


class Venue(models.Model):
    venue_id = models.AutoField(primary_key=True)
    name = models.CharField(max_length=150)
    location = models.CharField(max_length=255, blank=True, null=True)
    capacity = models.IntegerField()

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'venues'


class Category(models.Model):
    category_id = models.AutoField(primary_key=True)
    name = models.CharField(unique=True, max_length=80)
    description = models.CharField(max_length=200, blank=True, null=True)
    icon = models.CharField(max_length=50, blank=True, null=True)
    active_status = models.BooleanField(default=True)

    def __str__(self):
        return self.name

    class Meta:
        managed = False
        db_table = 'categories'


class Event(models.Model):
    event_id = models.AutoField(primary_key=True)
    title = models.CharField(max_length=255)
    description = models.TextField(blank=True, null=True)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, blank=True, null=True, db_column='category_id', related_name='events')
    organizer = models.ForeignKey(User, on_delete=models.SET_NULL, blank=True, null=True, db_column='organizer_id', related_name='organized_events')
    venue = models.ForeignKey(Venue, on_delete=models.SET_NULL, blank=True, null=True, db_column='venue_id', related_name='events')
    start_datetime = models.DateTimeField(blank=True, null=True)
    end_datetime = models.DateTimeField(blank=True, null=True)
    capacity = models.IntegerField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)
    created_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return self.title

    class Meta:
        managed = False
        db_table = 'events'


class Registration(models.Model):
    reg_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, db_column='event_id', related_name='registrations')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id', related_name='registrations')
    registered_at = models.DateTimeField(blank=True, null=True)
    status = models.CharField(max_length=20, blank=True, null=True)

    def __str__(self):
        return f"{self.user} -> {self.event}"

    class Meta:
        managed = False
        db_table = 'registrations'
        unique_together = (('event', 'user'),)


class Attendance(models.Model):
    attendance_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, db_column='event_id')
    user = models.ForeignKey(User, on_delete=models.CASCADE, db_column='user_id')
    present = models.BooleanField(default=False)
    checked_at = models.DateTimeField(blank=True, null=True)

    def __str__(self):
        return f"{self.user} @ {self.event}: {self.present}"

    class Meta:
        managed = False
        db_table = 'attendance'
        unique_together = (('event', 'user'),)


class Resource(models.Model):
    resource_id = models.AutoField(primary_key=True)
    resource_name = models.CharField(unique=True, max_length=100)
    total_quantity = models.IntegerField()

    def __str__(self):
        return self.resource_name

    class Meta:
        managed = False
        db_table = 'resources'


class EventResource(models.Model):
    er_id = models.AutoField(primary_key=True)
    event = models.ForeignKey(Event, on_delete=models.CASCADE, db_column='event_id', related_name='event_resources')
    resource = models.ForeignKey(Resource, on_delete=models.CASCADE, db_column='resource_id')
    quantity_required = models.IntegerField()

    def __str__(self):
        return f"{self.event} uses {self.resource} x{self.quantity_required}"

    class Meta:
        managed = False
        db_table = 'event_resources'