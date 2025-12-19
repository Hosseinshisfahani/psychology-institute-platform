


# Optimize foreign key lookups (JOIN)
courses = Course.objects.select_related('category', 'instructor')

# Optimize many-to-many lookups (separate query)
posts = Post.objects.prefetch_related('tags')

# Combined optimization
appointments = Appointment.objects.select_related(
    'client', 'therapist', 'appointment_type', 'location'
)
```

**Example from your code** (`app/appointments/api_views.py:59`):
```python
queryset = queryset.select_related('client', 'therapist', 'appointment_type', 'location')
```

#### Filtering and Searching
```python
# Complex filtering
from django.db.models import Q

queryset = Post.objects.filter(
    Q(title__icontains=search) | 
    Q(content__icontains=search) | 
    Q(excerpt__icontains=search)
)
```

**Example from your code** (`app/blog/api_views.py:30-34`):
```python
queryset = queryset.filter(
    Q(title__icontains=search) | 
    Q(content__icontains=search) | 
    Q(excerpt__icontains=search)
)
```

#### Aggregations
```python
from django.db.models import Count, Sum, Avg

# Count related objects
courses_with_enrollments = Course.objects.annotate(
    enrollment_count=Count('enrollments')
)

# Sum values
total_spent = Order.objects.filter(user=user).aggregate(
    total=Sum('total_amount')
)['total']
```

### Real Examples from Your Codebase

#### Example 1: List Appointments (`app/appointments/api_views.py`)
```python
def get_queryset(self):
    user = self.request.user
    if user.user_type == 'therapist':
        queryset = Appointment.objects.filter(therapist=user)
    elif user.user_type == 'client':
        queryset = Appointment.objects.filter(client=user)
    else:
        queryset = Appointment.objects.all()
    
    # Optimize with select_related to avoid N+1 queries
    queryset = queryset.select_related('client', 'therapist', 'appointment_type', 'location')
    
    return queryset
```

#### Example 2: Course List with Filtering (`app/courses/api_views.py`)
```python
def get_queryset(self):
    queryset = Course.objects.filter(status='published').select_related('category', 'instructor')
    
    # Filter by category slug
    category_slug = self.request.query_params.get('category_slug')
    if category_slug:
        queryset = queryset.filter(category__slug=category_slug)
    
    return queryset
```

#### Example 3: Dashboard Stats (`app/dashboard/api_views.py`)
```python
course_purchases = CoursePurchase.objects.filter(user=user)
orders = Order.objects.filter(user=user)
workshop_registrations = WorkshopRegistration.objects.filter(user=user)
package_purchases = PackagePurchase.objects.filter(user=user)
```

---

## 5. Transaction Management

### What are Transactions?
Transactions ensure **atomicity** - either all operations succeed or all fail. This prevents partial data updates.

### Transaction Usage in Your Code

#### Using `@transaction.atomic` Decorator
```python
from django.db import transaction

@transaction.atomic
def create_order(request):
    # All database operations here are atomic
    order = Order.objects.create(...)
    order_item = OrderItem.objects.create(order=order, ...)
    # If any operation fails, all changes are rolled back
```

**Example from your code** (`app/payment/api_views.py:140`):
```python
@transaction.atomic
def add_to_cart(request):
    # Cart operations are atomic
    ...
```

#### Using `with transaction.atomic()` Context Manager
```python
from django.db import transaction

def process_payment(request):
    with transaction.atomic():
        # All operations in this block are atomic
        order = Order.objects.create(...)
        payment = Payment.objects.create(order=order, ...)
        # If payment fails, order creation is rolled back
```

**Example from your code** (`app/appointments/api_views.py:90`):
```python
with transaction.atomic():
    appointment = serializer.save(client=self.request.user)
    # Appointment creation is atomic
```

### Where Transactions Are Used
1. **Payment Processing** (`app/payment/api_views.py`)
   - Order creation
   - Payment processing
   - Cart operations

2. **Appointment Booking** (`app/appointments/api_views.py`)
   - Appointment creation
   - Deposit payment

3. **Workshop Registration** (`app/workshops/api_views.py`)
   - Registration creation
   - Payment processing

---

### How Migrations Work

1. **Create Migration**:
   ```bash
   python manage.py makemigrations
   ```
   - Analyzes model changes
   - Creates migration file in `app_name/migrations/`

2. **Apply Migration**:
   ```bash
   python manage.py migrate
   ```
   - Executes SQL to update database schema
   - Tracks applied migrations in `django_migrations` table

3. **Migration Flow**:
   ```
   Model Change (models.py)
        ↓
   makemigrations
        ↓
   Migration File (0001_initial.py, etc.)
        ↓
   migrate
        ↓
   PostgreSQL Schema Update
   ```

### Example Migration
When you add a field to a model:
```python
# models.py
class User(models.Model):
    new_field = models.CharField(max_length=100)  # New field
```

Django generates:
```python
# migrations/0002_add_new_field.py
operations = [
    migrations.AddField(
        model_name='user',
        name='new_field',
        field=models.CharField(max_length=100),
    ),
]
```

Which translates to SQL:
```sql
ALTER TABLE dashboard_user ADD COLUMN new_field VARCHAR(100);
```

---

## 7. Connection Pooling

### Current Configuration

#### Production Settings (`settings.py`)
- **No explicit connection pooling** configured
- Django uses default connection management
- Connections are created on-demand and reused within the same request

#### CI Settings (`settings_ci.py`)
```python
"CONN_MAX_AGE": 0,  # No connection reuse (fresh connection per request)
```

### How Django Manages Connections

1. **Connection Lifecycle**:
   - Connection created on first database query
   - Reused for subsequent queries in same request
   - Closed after request completes (unless `CONN_MAX_AGE` > 0)

2. **Connection Reuse**:
   - If `CONN_MAX_AGE` is set, connections persist across requests
   - Reduces connection overhead
   - Example: `CONN_MAX_AGE = 600` (reuse for 10 minutes)

### Recommended Production Configuration
```python
DATABASES = {
    'default': {
        'ENGINE': 'django.db.backends.postgresql',
        'NAME': config('DB_NAME', default='psychology_institute'),
        'USER': config('DB_USER', default='postgres'),
        'PASSWORD': config('DB_PASSWORD', default=''),
        'HOST': config('DB_HOST', default='localhost'),
        'PORT': config('DB_PORT', default='5432'),
        'CONN_MAX_AGE': 600,  # Reuse connections for 10 minutes
        'OPTIONS': {
            'connect_timeout': 10,
        },
    }
}
```

### External Connection Pooling (pgBouncer)
For high-traffic applications, consider using **pgBouncer**:
- Sits between Django and PostgreSQL
- Manages connection pool at database level
- Reduces connection overhead
- Django connects to pgBouncer, pgBouncer connects to PostgreSQL

---

## 🔍 Query Execution Flow

### Complete Request Flow

```
1. HTTP Request arrives
   ↓
2. Django View is called
   ↓
3. View executes ORM query
   ↓
4. Django ORM translates to SQL
   ↓
5. Database backend (psycopg2) executes SQL
   ↓
6. PostgreSQL processes query
   ↓
7. Results returned to Django
   ↓
8. ORM converts rows to Python objects
   ↓
9. Serializer converts to JSON
   ↓
10. HTTP Response sent
```

### Example: Getting User Appointments

```python
# 1. View code
appointments = Appointment.objects.filter(client=user)

# 2. Django ORM generates SQL
SELECT * FROM appointments_appointment WHERE client_id = 123;

# 3. psycopg2 sends to PostgreSQL
# 4. PostgreSQL executes query
# 5. Results returned as rows
# 6. Django ORM converts to Appointment objects
# 7. Serializer converts to JSON
# 8. Response sent to frontend
```

---

## 📊 Database Schema Overview

### Key Tables and Relationships

```
User (dashboard_user)
  ├── OneToOne → UserProfile
  ├── ForeignKey → Course (instructor)
  ├── ForeignKey → Appointment (client, therapist)
  ├── ForeignKey → Order
  └── ManyToMany → Course (enrollments)

Course (courses_course)
  ├── ForeignKey → CourseCategory
  ├── ForeignKey → User (instructor)
  └── ManyToMany → User (enrollments)

Appointment (appointments_appointment)
  ├── ForeignKey → User (client)
  ├── ForeignKey → User (therapist)
  ├── ForeignKey → AppointmentType
  └── ForeignKey → ClinicLocation

Order (payment_order)
  ├── ForeignKey → User
  └── OneToMany → OrderItem

Payment (payment_payment)
  └── ForeignKey → Order
```

---

## 🛠️ Common Database Operations

### Checking Database Connection
```python
from django.db import connection

# Check if connection is alive
connection.ensure_connection()
print("Database connected!")
```

### Running Raw SQL (when needed)
```python
from django.db import connection

with connection.cursor() as cursor:
    cursor.execute("SELECT COUNT(*) FROM dashboard_user")
    row = cursor.fetchone()
    print(f"Total users: {row[0]}")
```

### Database Query Logging
Add to `settings.py` for development:
```python
LOGGING = {
    'version': 1,
    'handlers': {
        'console': {
            'class': 'logging.StreamHandler',
        },
    },
    'loggers': {
        'django.db.backends': {
            'level': 'DEBUG',
            'handlers': ['console'],
        },
    },
}
```

---

## ⚠️ Best Practices

### ✅ Do's
1. **Use `select_related()` for ForeignKey relationships**
   ```python
   Course.objects.select_related('category', 'instructor')
   ```

2. **Use `prefetch_related()` for ManyToMany relationships**
   ```python
   Post.objects.prefetch_related('tags')
   ```

3. **Use transactions for critical operations**
   ```python
   @transaction.atomic
   def critical_operation():
       ...
   ```

4. **Use `aggregate()` instead of Python loops**
   ```python
   # Good
   total = Order.objects.aggregate(Sum('amount'))
   
   # Bad
   total = sum(order.amount for order in Order.objects.all())
   ```

5. **Filter at database level, not in Python**
   ```python
   # Good
   users = User.objects.filter(is_verified=True)
   
   # Bad
   users = [u for u in User.objects.all() if u.is_verified]
   ```

### ❌ Don'ts
1. **Don't use `.all()` without pagination for large datasets**
2. **Don't update in loops - use `bulk_update()`**
3. **Don't forget indexes on frequently queried fields**
4. **Don't expose raw SQL unless necessary**

