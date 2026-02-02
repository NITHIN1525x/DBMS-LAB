# Event Management System — Comprehensive Presentation Guide

---

## 📋 TABLE OF CONTENTS
1. [System Architecture & How It Works](#system-architecture--how-it-works)
2. [User Flow - Step by Step](#user-flow---step-by-step)
3. [Database Schema Overview](#database-schema-overview)
4. [Stored Procedures Explained](#stored-procedures-explained)
5. [Database Triggers Explained](#database-triggers-explained)
6. [Database Views Explained](#database-views-explained)
7. [Key DBMS Concepts Used](#key-dbms-concepts-used)
8. [Practical Examples](#practical-examples)

---

## System Architecture & How It Works

### **High-Level Architecture Diagram**

```
┌─────────────────────────────────────────────────────────────┐
│                     WEB BROWSER                             │
│                   (Django Templates)                        │
└──────────────────────┬──────────────────────────────────────┘
                       │
                       ↓
┌─────────────────────────────────────────────────────────────┐
│               DJANGO WEB APPLICATION                        │
│          (Python Backend + Business Logic)                  │
│   ┌──────────────────────────────────────────────────────┐  │
│   │  Views Layer (views.py)                             │  │
│   │  - Dashboard, CRUD operations, Form handling        │  │
│   └──────────────────────────────────────────────────────┘  │
│   ┌──────────────────────────────────────────────────────┐  │
│   │  Models Layer (models.py)                           │  │
│   │  - ORM models + DB View proxies                     │  │
│   │  - Stored Procedure callers                         │  │
│   └──────────────────────────────────────────────────────┘  │
└──────────────────────┬──────────────────────────────────────┘
                       │ (SQL Queries / Procedure Calls)
                       ↓
┌─────────────────────────────────────────────────────────────┐
│              MySQL DATABASE (em)                            │
│   ┌──────────────────────────────────────────────────────┐  │
│   │  TABLES (Actual Data)                              │  │
│   │  - roles, departments, users, events, etc.         │  │
│   └──────────────────────────────────────────────────────┘  │
│   ┌──────────────────────────────────────────────────────┐  │
│   │  VIEWS (Read-only Queries)                         │  │
│   │  - vw_event_details, vw_user_registrations, etc.  │  │
│   └──────────────────────────────────────────────────────┘  │
│   ┌──────────────────────────────────────────────────────┐  │
│   │  STORED PROCEDURES (Reusable Logic)               │  │
│   │  - sp_register_user_for_event                      │  │
│   │  - sp_mark_attendance                              │  │
│   └──────────────────────────────────────────────────────┘  │
│   ┌──────────────────────────────────────────────────────┐  │
│   │  TRIGGERS (Automatic Actions)                      │  │
│   │  - trg_before_registration_insert                  │  │
│   │  - trg_after_registration_insert                   │  │
│   └──────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────┘
```

### **Key Components**

| Component | Purpose | Example |
|-----------|---------|---------|
| **Django Views** | Handle HTTP requests, call models, render templates | `dashboard()`, `registration_create()` |
| **Django Models** | Define data structure, interact with database | `Event`, `Registration`, `User` |
| **Database Tables** | Store actual data persistently | `events`, `registrations`, `users` |
| **Database Views** | Pre-computed queries that return data | `vw_event_details` (event + organizer + venue info) |
| **Stored Procedures** | Reusable database logic for complex operations | `sp_register_user_for_event` (with validation) |
| **Triggers** | Automatic actions when data changes | When registering a user, auto-create attendance record |
| **Templates** | HTML pages rendered on server, sent to browser | `dashboard.html`, `users/list.html` |

---

## User Flow — Step by Step

### **SCENARIO 1: Admin Creates an Event**

```
1. Admin opens "Events" page
   └─> Django View: event_list() 
       └─> Queries: Event.objects.all()
           └─> Database: SELECT * FROM events

2. Admin clicks "Add New Event" 
   └─> Django View: event_create() (GET request)
       └─> Renders: events/form.html
           └─> Shows form with dropdowns:
               - Categories (from vw_categories)
               - Organizers (from users table)
               - Venues (from venues table)

3. Admin fills form: Title, Description, Venue, Capacity, Start Date
   └─> Django View: event_create() (POST request)
       └─> Python: Event.objects.create(...)
           └─> Database: INSERT INTO events (title, desc, ...) VALUES (...)

4. Database accepts INSERT
   └─> Django: messages.success() → "Event created successfully!"
       └─> Redirect to event_list

5. New event appears in table
   └─> Next visitor sees it in Event.objects.all()
```

**Key Learning Points:**
- Views are request handlers (GET to show, POST to save)
- Models are ORM (Object-Relational Mapping) wrappers
- Database stores actual data
- Users interact through forms (templates)

---

### **SCENARIO 2: User Registers for an Event (Using Stored Procedure)**

```
1. User opens "Registrations" page
   └─> Django View: registration_list()
       └─> Query: UserRegistrationsView.objects.all()
           └─> Database: SELECT * FROM vw_user_registrations
               (Shows user name, email, event title, date from joined view)

2. Admin clicks "Add New Registration"
   └─> Django View: registration_create() (GET)
       └─> Renders: registrations/form.html
           └─> Shows: Event dropdown + User dropdown
               (Note: Form mentions stored procedure protection)

3. Admin selects Event: "ML Workshop" (capacity: 50)
   └─> Select User: "John (4SF23CS001)"

4. Form POST → Django calls:
   ┌─────────────────────────────────────────────────────────┐
   │ result = call_register_user_for_event(event_id=5, user_id=12) │
   │                                                          │
   │ This calls MYSQL:                                        │
   │   CALL sp_register_user_for_event(@event_id, @user_id)  │
   │                                                          │
   │ Stored Procedure does:                                   │
   │   ✓ Check if event exists                               │
   │   ✓ Check if user already registered (UNIQUE)           │
   │   ✓ Check if event has capacity                         │
   │   ✓ If all OK: INSERT into registrations                │
   │   ✓ Trigger fires → Auto-create attendance record       │
   │   ✓ Return success/error message                        │
   └─────────────────────────────────────────────────────────┘

5. Result returned to Django
   └─> If success: "Registration successful! Attendance auto-marked."
       └─> Redirect to registration_list
   └─> If error: "Event capacity exceeded!" or "User already registered"

6. Check Attendance
   └─> Django View: attendance_list()
       └─> Query: Attendance.objects.all()
           └─> Shows John's attendance for ML Workshop (created by trigger!)
```

**Key Learning Points:**
- Stored procedures encapsulate complex business logic
- Triggers automate related actions (register → auto attendance)
- Validation happens at database level (more secure)
- Errors are returned to Django for user feedback

---

### **SCENARIO 3: Dashboard Shows Event Summary (Using View)**

```
1. Admin opens Dashboard
   └─> Django View: dashboard()
       └─> Queries:
           ├─ event_summaries = EventRegistrationSummaryView.objects.all()
           │  └─> SELECT * FROM vw_event_registration_summary
           │      Returns:
           │      ┌──────────┬─────────────────┬──────────┐
           │      │ Event ID │ Event Title     │ Capacity │ Reg Count │ Remaining │
           │      ├──────────┼─────────────────┼──────────┤
           │      │ 5        │ ML Workshop     │ 50       │ 45        │ 5         │
           │      │ 6        │ Cloud Computing │ 100      │ 98        │ 2         │
           │      └──────────┴─────────────────┴──────────┘
           │
           ├─ upcoming_events = EventDetailsView.objects.filter(start >= now)
           │  └─> SELECT * FROM vw_event_details
           │      Returns: Event title, Category name, Venue name, Organizer name
           │               (All joined from multiple tables in ONE VIEW!)
           │
           └─ recent_registrations = UserRegistrationsView.objects.order_by('-registered_at')[:5]
              └─> SELECT * FROM vw_user_registrations
                  Returns: User name, Roll no, Event, Status, Date

2. Dashboard.html renders with stats:
   ┌────────────────────────────────────────┐
   │  Total Events: 12                      │
   │  Total Users: 150                      │
   │  Total Venues: 5                       │
   │  Total Registrations: 245              │
   └────────────────────────────────────────┘
   
   + Upcoming Events Table (from vw_event_details)
   + Recent Registrations Table (from vw_user_registrations)
   + Event Summary with Capacity Fill Rates (from vw_event_registration_summary)

3. User sees beautiful dashboard with real-time data
   └─> All views are READ-ONLY
   └─> Views are computed on-the-fly or cached
   └─> Very fast because views JOIN tables at DB level (not Python)
```

**Key Learning Points:**
- Views are like "pre-built queries" 
- They JOIN multiple tables at database level (faster than Python loops)
- Perfect for dashboards and reporting
- Read-only, so no INSERT/UPDATE/DELETE via views

---

## Database Schema Overview

### **Core Tables (Actual Data)**

```
ROLES
├─ role_id (PK)
├─ role_name (UNIQUE)
├─ description
└─ created_at

DEPARTMENTS
├─ dept_id (PK)
├─ dept_name (UNIQUE)
├─ dept_code (UNIQUE)
├─ hod_name
└─ created_at

USERS
├─ user_id (PK)
├─ name
├─ roll_no
├─ email
├─ phone
├─ role_id (FK → ROLES)
├─ dept_id (FK → DEPARTMENTS)
└─ created_at

VENUES
├─ venue_id (PK)
├─ name
├─ location
└─ capacity

CATEGORIES
├─ category_id (PK)
├─ name (UNIQUE)
├─ description
├─ icon
└─ active_status

EVENTS
├─ event_id (PK)
├─ title
├─ description
├─ category_id (FK → CATEGORIES)
├─ organizer_id (FK → USERS)
├─ venue_id (FK → VENUES)
├─ start_datetime
├─ end_datetime
├─ capacity
├─ status
└─ created_at

REGISTRATIONS  ⭐ (Important)
├─ reg_id (PK)
├─ event_id (FK → EVENTS) 
├─ user_id (FK → USERS)
├─ registered_at
├─ status
└─ UNIQUE(event_id, user_id) [One user per event]

ATTENDANCE  ⭐ (Auto-created by trigger)
├─ attendance_id (PK)
├─ event_id (FK → EVENTS)
├─ user_id (FK → USERS)
├─ present (BOOLEAN)
├─ checked_at
└─ UNIQUE(event_id, user_id)

RESOURCES
├─ resource_id (PK)
├─ resource_name (UNIQUE)
└─ total_quantity

EVENT_RESOURCES
├─ er_id (PK)
├─ event_id (FK → EVENTS)
├─ resource_id (FK → RESOURCES)
└─ quantity_required
```

### **Entity Relationship Diagram (Simplified)**

```
        ROLES          DEPARTMENTS
          ↑                  ↑
          │                  │
          └────── USERS ─────┘
                    ↑
                    │
    ┌───────────────┼───────────────┐
    │               │               │
    │          REGISTRATIONS    ATTENDANCE
    │      (organizer)              │
    │               │               │
    ↓               ↓               ↓
CATEGORIES ── EVENTS ────────────────┘
             ↗     ↖
          VENUES    EVENT_RESOURCES
                        ↑
                        │
                   RESOURCES
```

---

## Stored Procedures Explained

### **What is a Stored Procedure?**

A stored procedure is a **pre-compiled SQL program stored in the database** that can be called repeatedly without recompiling. It encapsulates complex business logic.

**Benefits:**
- ✅ Centralized logic (easier to maintain)
- ✅ Better performance (compiled once)
- ✅ Security (validate at DB level)
- ✅ Reusable across applications

---

### **Stored Procedure 1: `sp_register_user_for_event`**

**Purpose:** Register a user for an event with validation

**Location in Project:** 
- Called in `models.py` → `call_register_user_for_event()`
- Used in `views.py` → `registration_create()`
- Form template mentions it: `registrations/form.html`

**SQL Definition (Example):**

```sql
DELIMITER $$

CREATE PROCEDURE sp_register_user_for_event(
    IN p_event_id INT,
    IN p_user_id INT
)
BEGIN
    DECLARE v_current_registrations INT;
    DECLARE v_event_capacity INT;
    DECLARE v_error_message VARCHAR(255);
    
    -- Start transaction
    START TRANSACTION;
    
    BEGIN
        -- Check if event exists
        SELECT capacity INTO v_event_capacity 
        FROM events 
        WHERE event_id = p_event_id;
        
        IF v_event_capacity IS NULL THEN
            SET v_error_message = 'Event not found';
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_error_message;
        END IF;
        
        -- Check if user already registered
        IF EXISTS (SELECT 1 FROM registrations 
                   WHERE event_id = p_event_id AND user_id = p_user_id) THEN
            SET v_error_message = 'User already registered for this event';
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_error_message;
        END IF;
        
        -- Check if event has capacity
        SELECT COUNT(*) INTO v_current_registrations
        FROM registrations
        WHERE event_id = p_event_id;
        
        IF v_current_registrations >= v_event_capacity THEN
            SET v_error_message = 'Event is full, no more registrations available';
            SIGNAL SQLSTATE '45000' SET MESSAGE_TEXT = v_error_message;
        END IF;
        
        -- All checks passed, insert registration
        INSERT INTO registrations (event_id, user_id, registered_at, status)
        VALUES (p_event_id, p_user_id, NOW(), 'confirmed');
        
        -- Commit transaction
        COMMIT;
        SELECT 'Registration successful' AS message;
        
    END;
    
END $$

DELIMITER ;
```

**How Django Calls It:**

```python
# In models.py
def call_register_user_for_event(event_id, user_id):
    """Call stored procedure: sp_register_user_for_event"""
    with connection.cursor() as cursor:
        try:
            cursor.callproc('sp_register_user_for_event', [event_id, user_id])
            return {'success': True, 'message': 'User registered successfully'}
        except Exception as e:
            return {'success': False, 'message': str(e)}

# In views.py
def registration_create(request):
    if request.method == 'POST':
        event_id = request.POST.get('event')
        user_id = request.POST.get('user')
        
        # Call stored procedure
        result = call_register_user_for_event(event_id, user_id)
        
        if result['success']:
            messages.success(request, result['message'])
            return redirect('registration_list')
        else:
            messages.error(request, f"Registration failed: {result['message']}")
```

**Why Use This Instead of Django ORM?**
- ✅ Event capacity validation happens at DB level (atomic, safe)
- ✅ Unique constraint prevents double registration
- ✅ All logic in one SQL transaction
- ✅ Faster than multiple Python queries

---

### **Stored Procedure 2: `sp_mark_attendance`**

**Purpose:** Mark or update attendance for a user in an event

**SQL Definition (Example):**

```sql
DELIMITER $$

CREATE PROCEDURE sp_mark_attendance(
    IN p_event_id INT,
    IN p_user_id INT,
    IN p_present BOOLEAN
)
BEGIN
    DECLARE v_attendance_exists INT;
    
    START TRANSACTION;
    
    BEGIN
        -- Check if attendance record exists
        SELECT COUNT(*) INTO v_attendance_exists
        FROM attendance
        WHERE event_id = p_event_id AND user_id = p_user_id;
        
        IF v_attendance_exists > 0 THEN
            -- Update existing record
            UPDATE attendance
            SET present = p_present, checked_at = NOW()
            WHERE event_id = p_event_id AND user_id = p_user_id;
        ELSE
            -- Create new attendance record
            INSERT INTO attendance (event_id, user_id, present, checked_at)
            VALUES (p_event_id, p_user_id, p_present, NOW());
        END IF;
        
        COMMIT;
        SELECT 'Attendance marked successfully' AS message;
        
    END;
    
END $$

DELIMITER ;
```

**How Django Calls It:**

```python
# In views.py
def attendance_create(request):
    if request.method == 'POST':
        event_id = request.POST.get('event')
        user_id = request.POST.get('user')
        present = request.POST.get('present') == 'on'
        
        # Call stored procedure
        result = call_mark_attendance(event_id, user_id, present)
        
        if result['success']:
            messages.success(request, result['message'])
            return redirect('attendance_list')
        else:
            messages.error(request, f"Attendance marking failed: {result['message']}")
```

**Key Insight:** This procedure uses INSERT OR UPDATE logic (upsert), which is complex in ORM but simple in stored procedures.

---

## Database Triggers Explained

### **What is a Trigger?**

A trigger is an **automatic action that fires when a specific event happens** on a table (INSERT, UPDATE, DELETE). It's like an "if-then" rule.

**Syntax:**
```sql
CREATE TRIGGER trigger_name
{BEFORE|AFTER} {INSERT|UPDATE|DELETE} ON table_name
FOR EACH ROW
BEGIN
    -- Your SQL statements here
END;
```

---

### **Trigger 1: `trg_before_registration_insert`**

**Purpose:** Validate event capacity BEFORE a registration is inserted

**When It Fires:** Before INSERT into `registrations` table

**SQL Definition (Example):**

```sql
DELIMITER $$

CREATE TRIGGER trg_before_registration_insert
BEFORE INSERT ON registrations
FOR EACH ROW
BEGIN
    DECLARE v_current_registrations INT;
    DECLARE v_event_capacity INT;
    
    -- Get event capacity
    SELECT capacity INTO v_event_capacity
    FROM events
    WHERE event_id = NEW.event_id;
    
    -- Count current registrations
    SELECT COUNT(*) INTO v_current_registrations
    FROM registrations
    WHERE event_id = NEW.event_id;
    
    -- Check capacity
    IF v_current_registrations >= v_event_capacity THEN
        SIGNAL SQLSTATE '45000' 
        SET MESSAGE_TEXT = 'Event capacity exceeded. Cannot register.';
    END IF;
    
END $$

DELIMITER ;
```

**How It Works:**

```
1. Admin tries to register user (via form)
   └─> Django calls: sp_register_user_for_event()

2. Stored procedure tries: INSERT INTO registrations (event_id, user_id, ...)

3. MySQL Engine: "Wait! There's a BEFORE INSERT trigger on registrations!"
   └─> Trigger executes:
       ├─ Count current registrations
       ├─ Get event capacity
       └─ If count >= capacity: REJECT INSERT with error message

4. If trigger allows (capacity > count):
   └─> INSERT proceeds
   └─> Actual row added to table

5. Error is caught by Django
   └─> messages.error() shows user: "Event capacity exceeded"
```

**Key Points:**
- ✅ Prevents invalid data at database level (not Python)
- ✅ `NEW` keyword refers to the row being inserted
- ✅ Triggers ensure data integrity

---

### **Trigger 2: `trg_after_registration_insert`**

**Purpose:** Automatically create an attendance record when user registers

**When It Fires:** After INSERT into `registrations` table (successfully)

**SQL Definition (Example):**

```sql
DELIMITER $$

CREATE TRIGGER trg_after_registration_insert
AFTER INSERT ON registrations
FOR EACH ROW
BEGIN
    -- Automatically create attendance record
    INSERT INTO attendance (event_id, user_id, present, checked_at)
    VALUES (NEW.event_id, NEW.user_id, FALSE, NOW());
    
    -- Note: When admin marks present later, another stored procedure updates this
    
END $$

DELIMITER ;
```

**How It Works:**

```
Flow:
1. User registers for event (via form)
   └─> Django calls: sp_register_user_for_event(event_id=5, user_id=12)

2. Stored Procedure: INSERT into registrations (event_id=5, user_id=12, ...)

3. MySQL: "Trigger trg_after_registration_insert fires!"
   └─> Automatically executes:
       INSERT INTO attendance (event_id=5, user_id=12, present=FALSE, checked_at=NOW())

4. Result:
   ├─ registrations table: Row added ✓
   └─ attendance table: Row auto-added ✓ (marked as absent initially)

5. Later, admin marks present using sp_mark_attendance()
   └─> Attendance updated to present=TRUE
```

**Why This Is Powerful:**
- ✅ No need to write code to create attendance record
- ✅ Automatic, can't forget
- ✅ Maintains data consistency

---

### **Trigger Visualization**

```
┌───────────────────────────────────────────────────────┐
│ Admin registers user "John" for "ML Workshop"        │
└──────────────────────┬────────────────────────────────┘
                       │ Django calls sp_register_user_for_event()
                       ↓
┌───────────────────────────────────────────────────────┐
│ MySQL: INSERT into registrations                     │
└──────────────────────┬────────────────────────────────┘
                       │
         ┌─────────────┴─────────────┐
         ↓                           ↓
    ┌─────────────┐         ┌─────────────────┐
    │ BEFORE      │         │ AFTER INSERT    │
    │ INSERT      │         │ TRIGGER         │
    │ TRIGGER     │         │ (auto-create    │
    │ (validate   │         │  attendance)    │
    │  capacity)  │         │                 │
    └─────────────┘         └─────────────────┘
         │                           │
         └──────────┬────────────────┘
                    ↓
        ┌──────────────────────────┐
        │ registrations table:      │
        │ - John → ML Workshop ✓   │
        │                          │
        │ attendance table:         │
        │ - John → ML Workshop     │
        │   (absent, to be marked) │
        └──────────────────────────┘
```

---

## Database Views Explained

### **What is a Database View?**

A view is a **virtual table based on a SQL query**. It doesn't store data itself; instead, it dynamically computes results from other tables. Views are read-only.

**Benefits:**
- ✅ Pre-built queries (no need to write complex JOINs in Django)
- ✅ Fast (computed at database level)
- ✅ Cleaner code (just query the view)
- ✅ Reusable across applications

---

### **View 1: `vw_event_details`**

**Purpose:** Get all event details with joined information (category, venue, organizer, department)

**SQL Definition (Example):**

```sql
CREATE VIEW vw_event_details AS
SELECT 
    e.event_id,
    e.title,
    e.description,
    e.start_datetime,
    e.end_datetime,
    e.status,
    e.capacity,
    c.name AS category_name,
    v.name AS venue_name,
    v.location AS venue_location,
    u.name AS organizer_name,
    d.dept_name AS organizer_department
FROM events e
LEFT JOIN categories c ON e.category_id = c.category_id
LEFT JOIN venues v ON e.venue_id = v.venue_id
LEFT JOIN users u ON e.organizer_id = u.user_id
LEFT JOIN departments d ON u.dept_id = d.dept_id;
```

**How Django Uses It:**

```python
# In models.py
class EventDetailsView(models.Model):
    event_id = models.IntegerField(primary_key=True)
    title = models.CharField(max_length=255)
    category_name = models.CharField(max_length=80, blank=True, null=True)
    venue_name = models.CharField(max_length=150, blank=True, null=True)
    organizer_name = models.CharField(max_length=200, blank=True, null=True)
    # ... more fields
    
    class Meta:
        managed = False
        db_table = 'vw_event_details'

# In views.py
def event_list(request):
    events = EventDetailsView.objects.all()  # Query the view!
    return render(request, 'events/list.html', {'events': events})

# In template
{% for event in events %}
    <tr>
        <td>{{ event.title }}</td>
        <td>{{ event.category_name }}</td>
        <td>{{ event.venue_name }}</td>
        <td>{{ event.organizer_name }}</td>
    </tr>
{% endfor %}
```

**Why This Is Better Than Multiple Queries:**

❌ **Without View (Bad Approach):**
```python
# Need multiple queries in Python
for event in Event.objects.all():
    category = event.category.name  # Extra query
    venue = event.venue.name        # Extra query
    organizer = event.organizer.name  # Extra query
    dept = event.organizer.dept.dept_name  # Extra query!
    # This is 4 queries per event! (N+1 problem)
```

✅ **With View (Good Approach):**
```python
# Single query, all info joined at DB level
events = EventDetailsView.objects.all()
# One query returns everything!
```

---

### **View 2: `vw_user_registrations`**

**Purpose:** Show user registrations with user and event details

**SQL Definition (Example):**

```sql
CREATE VIEW vw_user_registrations AS
SELECT 
    r.reg_id,
    u.user_id,
    u.name AS user_name,
    u.roll_no,
    u.email,
    e.event_id,
    e.title AS event_title,
    e.start_datetime,
    e.end_datetime,
    r.status AS registration_status,
    r.registered_at
FROM registrations r
INNER JOIN users u ON r.user_id = u.user_id
INNER JOIN events e ON r.event_id = e.event_id
ORDER BY r.registered_at DESC;
```

**Used In:**

```python
# In views.py - Dashboard
def dashboard(request):
    recent_registrations = UserRegistrationsView.objects.order_by('-registered_at')[:5]
    # Shows: User name, Event title, Status, Date in one query!
    
# In views.py - Registration List
def registration_list(request):
    registrations = UserRegistrationsView.objects.all()
    return render(request, 'registrations/list.html', {'registrations': registrations})
```

**Template Display:**
```html
<table>
    <tr>
        <td>{{ reg.user_name }}</td>
        <td>{{ reg.roll_no }}</td>
        <td>{{ reg.event_title }}</td>
        <td>{{ reg.registration_status }}</td>
    </tr>
</table>
```

---

### **View 3: `vw_event_registration_summary`**

**Purpose:** Show event capacity vs registrations (for dashboard charts)

**SQL Definition (Example):**

```sql
CREATE VIEW vw_event_registration_summary AS
SELECT 
    e.event_id,
    e.title,
    e.capacity,
    COUNT(r.reg_id) AS total_registrations,
    (e.capacity - COUNT(r.reg_id)) AS remaining_seats
FROM events e
LEFT JOIN registrations r ON e.event_id = r.event_id
GROUP BY e.event_id, e.title, e.capacity;
```

**How It Works:**

```
Database:
- Event: ML Workshop (capacity 50)
  - 5 registrations exist

View executes GROUP BY:
- COUNT(registrations) = 5
- remaining = 50 - 5 = 45
- Calculates IN DATABASE (fast!)

Returns to Django:
{
  'title': 'ML Workshop',
  'capacity': 50,
  'total_registrations': 5,
  'remaining_seats': 45
}

Template:
├─ Displays: 5 / 50 (10%)
├─ Shows progress bar
└─ Shows "Available" status
```

**Used In:**

```python
# In views.py - Dashboard
def dashboard(request):
    event_summaries = EventRegistrationSummaryView.objects.all()
    # Perfect for showing event fill rates!
    
# In views.py - Event Summary Page
def event_summary(request):
    summaries = EventRegistrationSummaryView.objects.all()
    return render(request, 'events/summary.html', {'summaries': summaries})
```

---

### **View Comparison Table**

| View Name | Purpose | Data Source | Use Case |
|-----------|---------|-------------|----------|
| `vw_event_details` | Event + related info | events, categories, venues, users, departments | Event listing, Event details page |
| `vw_user_registrations` | Registration + user + event info | registrations, users, events | Registration list, Dashboard recent |
| `vw_event_registration_summary` | Event capacity analysis | events, registrations (with GROUP BY) | Dashboard summary, Event capacity page |

---

## Key DBMS Concepts Used

### **1. Transactions**

A transaction is a **sequence of operations that must all succeed or all fail together** (ACID property).

**In This Project:**
- Stored procedures use `START TRANSACTION` and `COMMIT`
- When registering a user:
  1. Validate capacity (BEFORE trigger)
  2. Insert registration (main operation)
  3. Trigger fires (auto-create attendance)
  4. If any step fails → All rolled back

```sql
START TRANSACTION;
  -- Check 1
  -- Insert 1
  -- Check 2
  -- Insert 2
COMMIT; -- All or nothing
```

---

### **2. Foreign Keys**

Foreign keys maintain **referential integrity** (prevent orphaned records).

```
users.user_id ←──┐
                 │
                 └── registrations.user_id

If you delete a user:
- Option 1 (CASCADE): Delete all their registrations
- Option 2 (SET NULL): Set registrations.user_id to NULL
- Option 3 (RESTRICT): Prevent deletion if registrations exist
```

**In This Project:**
```python
class Registration(models.Model):
    event = models.ForeignKey(Event, on_delete=models.CASCADE)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    # If event or user deleted → registration auto-deleted
```

---

### **3. Unique Constraints**

Prevents duplicate records.

**In This Project:**
```python
class Registration(models.Model):
    # ...
    class Meta:
        unique_together = (('event', 'user'),)
        # One user can register for an event ONLY ONCE
```

Also enforced in stored procedure:
```sql
IF EXISTS (SELECT 1 FROM registrations 
           WHERE event_id = p_event_id AND user_id = p_user_id) THEN
    -- Error: User already registered
END IF;
```

---

### **4. Indexes**

Indexes speed up queries on frequently searched columns.

```
Without Index:
  SELECT * FROM events WHERE status = 'scheduled'
  └─> Scan entire table (slow if millions of records)

With Index on `status` column:
  SELECT * FROM events WHERE status = 'scheduled'
  └─> Look up index (instant!)
```

---

### **5. Aggregation Functions**

Functions like COUNT, SUM, AVG used in views.

```sql
-- In vw_event_registration_summary
COUNT(r.reg_id) AS total_registrations
GROUP BY e.event_id
```

---

## Practical Examples

### **Example 1: Complete Registration Flow**

**Step 1: User fills form and submits**

```
┌─────────────────────────────┐
│ registrations/form.html     │
│ Event: ML Workshop          │
│ User: John (4SF23CS001)     │
│ [Submit]                    │
└──────────────┬──────────────┘
               │
               ↓
        POST /registrations/create/
               │
               ↓
```

**Step 2: Django processes request**

```python
# In views.py
def registration_create(request):
    event_id = request.POST.get('event')  # 5
    user_id = request.POST.get('user')    # 12
    
    result = call_register_user_for_event(event_id, user_id)
```

**Step 3: Python calls stored procedure**

```python
# In models.py
def call_register_user_for_event(event_id, user_id):
    with connection.cursor() as cursor:
        cursor.callproc('sp_register_user_for_event', [5, 12])
```

**Step 4: Stored Procedure executes in MySQL**

```sql
CALL sp_register_user_for_event(5, 12);

-- Procedure does:
1. SELECT capacity FROM events WHERE event_id=5
   └─> capacity = 50

2. Check BEFORE INSERT trigger validates:
   SELECT COUNT(*) FROM registrations WHERE event_id=5
   └─> count = 45
   └─> 45 < 50? YES, proceed

3. START TRANSACTION
   INSERT INTO registrations (event_id=5, user_id=12, status='confirmed', ...)

4. AFTER INSERT trigger fires:
   INSERT INTO attendance (event_id=5, user_id=12, present=FALSE, ...)

5. COMMIT
```

**Step 5: Result returned to Django**

```python
return {'success': True, 'message': 'User registered successfully'}
```

**Step 6: User sees success message**

```
✓ User registered successfully!
Redirecting to registrations list...
```

**Step 7: User checks attendance**

```
Attendance page now shows:
┌──────────┬─────────────┬──────────┐
│ Event    │ Participant │ Status   │
├──────────┼─────────────┼──────────┤
│ ML Wor.  │ John        │ ✗ Absent │  ← Auto-created by trigger!
└──────────┴─────────────┴──────────┘
```

---

### **Example 2: Dashboard Summary Calculation**

**Question:** How does dashboard show event capacities?

**Answer:**

```python
# Django View
def dashboard(request):
    event_summaries = EventRegistrationSummaryView.objects.all()
    # Returns list of event summaries
```

**Behind the scenes, MySQL executes:**

```sql
SELECT 
    e.event_id,
    e.title,
    e.capacity,
    COUNT(r.reg_id) AS total_registrations,
    (e.capacity - COUNT(r.reg_id)) AS remaining_seats
FROM events e
LEFT JOIN registrations r ON e.event_id = r.event_id
GROUP BY e.event_id, e.title, e.capacity;
```

**Result received by Django:**

```python
[
    {
        'event_id': 5,
        'title': 'ML Workshop',
        'capacity': 50,
        'total_registrations': 45,
        'remaining_seats': 5
    },
    {
        'event_id': 6,
        'title': 'Web Dev',
        'capacity': 100,
        'total_registrations': 98,
        'remaining_seats': 2
    }
]
```

**Template renders:**

```html
<table>
    <tr>
        <td>ML Workshop</td>
        <td>50</td>
        <td>45</td>
        <td>5</td>
        <td>90% ████████░</td>
    </tr>
    <tr>
        <td>Web Dev</td>
        <td>100</td>
        <td>98</td>
        <td>2</td>
        <td>98% ██████████</td>
    </tr>
</table>
```

---

### **Example 3: Error Handling**

**Scenario:** User tries to register when event is FULL

**What Happens:**

```
1. Admin submits: Event=5 (capacity 50), User=12
   └─> Already 50 registrations exist

2. Django calls: call_register_user_for_event(5, 12)

3. MySQL Procedure executes:
   - BEFORE INSERT trigger checks:
     SELECT COUNT(*) FROM registrations WHERE event_id=5
     └─> Returns 50
     └─> 50 >= 50? YES, trigger rejects

4. Error raised: "Event capacity exceeded"

5. Python catches exception:
   except Exception as e:
       return {'success': False, 'message': str(e)}
       
6. Django displays error:
   messages.error(request, "Registration failed: Event capacity exceeded")
   
7. User sees:
   ⚠️ Registration failed: Event capacity exceeded
   [← Go Back]
```

**Why This is Better Than Python-Only Validation:**
- ✅ Database validates (multiple apps can use stored procedure)
- ✅ No race condition (database handles concurrency)
- ✅ User can't bypass by editing JavaScript

---

## 📊 Presentation Summary Slide

### **Key Takeaways**

| Layer | Component | Purpose | Example |
|-------|-----------|---------|---------|
| **Frontend** | HTML Templates | Display to user | dashboard.html |
| **Backend** | Django Views | Request handler | registration_create() |
| **ORM** | Django Models | Data abstraction | Registration model |
| **Database** | Tables | Data storage | registrations table |
| **Database** | Views | Pre-built queries | vw_event_details |
| **Database** | Stored Procedures | Complex logic | sp_register_user_for_event |
| **Database** | Triggers | Auto-actions | trg_after_registration_insert |

### **DBMS Concepts Demonstrated**

1. **Stored Procedures** - Encapsulate validation logic (capacity check)
2. **Triggers** - Automate related operations (auto-create attendance)
3. **Views** - Pre-compute complex JOINs (event details with all info)
4. **Transactions** - Ensure atomicity (all or nothing)
5. **Foreign Keys** - Maintain referential integrity
6. **Unique Constraints** - Prevent duplicates (one registration per user)
7. **Indexing** - Improve query performance (search events by status)
8. **Aggregation** - Calculate summaries (remaining seats = capacity - count)

---

## 🎯 Q&A For Your Presentation

**Q: Why use stored procedures instead of Django code?**
A: Database-level validation is atomic, prevents race conditions, and is reusable across applications.

**Q: What happens if a trigger fails?**
A: The entire transaction rolls back. No partial data is saved.

**Q: Can you delete data from a view?**
A: Views are read-only in most cases. You query them but don't modify through them.

**Q: Why are there three views?**
A: Each view serves a different use case:
- `vw_event_details` - Full event info (for listing)
- `vw_user_registrations` - Registration history (for tracking)
- `vw_event_registration_summary` - Capacity analysis (for dashboards)

**Q: What's the difference between triggers and stored procedures?**
A: Triggers fire automatically on events (INSERT/UPDATE/DELETE). Stored procedures are called explicitly.

---

## 📚 Additional Resources

- Database Views location in code: `models.py` (EventDetailsView, UserRegistrationsView, etc.)
- Stored Procedure callers: `models.py` (call_register_user_for_event, call_mark_attendance)
- Trigger references in templates: See comments in `registrations/form.html` and `attendance/form.html`
- Django usage: `views.py` shows all query examples

---

**Created for Presentation on:** December 9, 2025
**Event Management System v1.0**
**Built with:** Django + MySQL + Stored Procedures + Triggers + Views
