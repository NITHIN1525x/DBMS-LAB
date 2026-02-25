from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('stud', '0001_initial'),
    ]

    operations = [
        migrations.RunSQL(
            sql="""
                CREATE OR REPLACE VIEW vw_event_details AS
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

                CREATE OR REPLACE VIEW vw_user_registrations AS
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
                JOIN users u ON r.user_id = u.user_id
                JOIN events e ON r.event_id = e.event_id;

                CREATE OR REPLACE VIEW vw_event_registration_summary AS
                SELECT
                    e.event_id,
                    e.title,
                    e.capacity,
                    COUNT(r.reg_id) AS total_registrations,
                    COALESCE(e.capacity - COUNT(r.reg_id), 0) AS remaining_seats
                FROM events e
                LEFT JOIN registrations r ON e.event_id = r.event_id
                GROUP BY e.event_id, e.title, e.capacity;
            """,
            reverse_sql="""
                DROP VIEW IF EXISTS vw_event_details;
                DROP VIEW IF EXISTS vw_user_registrations;
                DROP VIEW IF EXISTS vw_event_registration_summary;
            """,
        ),
    ]
