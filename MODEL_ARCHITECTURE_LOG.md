# Django ORM Models Architecture Log

## Project Overview
This document provides a comprehensive overview of all ORM models in the Emamy Psychology Institute Django project. The project consists of multiple Django apps, each handling specific aspects of the psychology institute's operations.

**Last Updated**: December 2024 - Updated to reflect current project state after removing therapy_sessions app references.

## Apps and Models Summary

### 1. Admin Panel App (`app.admin_panel`)
**Purpose**: Administrative dashboard and system management

#### Models:
1. **AdminDashboard**
   - Fields: title, description, is_active, created_at, updated_at
   - Purpose: Dashboard configuration management
   - Relationships: One-to-many with AdminWidget

2. **AdminWidget**
   - Fields: dashboard (FK), title, widget_type, position, size, config, is_active, created_at
   - Purpose: Dashboard widgets configuration
   - Relationships: Many-to-one with AdminDashboard

3. **AdminLog**
   - Fields: user (FK), action, model_name, object_id, description, ip_address, user_agent, created_at
   - Purpose: Admin activity logging
   - Relationships: Many-to-one with User

4. **AdminNotification**
   - Fields: title, message, notification_type, is_read, is_global, target_users (M2M), created_at, read_at
   - Purpose: Admin notification system
   - Relationships: Many-to-many with User

5. **AdminSetting**
   - Fields: key, value, setting_type, description, is_encrypted, created_at, updated_at
   - Purpose: System settings management

6. **AdminBackup**
   - Fields: name, backup_type, status, file_path, file_size, created_by (FK), started_at, completed_at, error_message, created_at
   - Purpose: Database backup management
   - Relationships: Many-to-one with User

### 2. Blog App (`app.blog`)
**Purpose**: Content management and blog functionality

#### Models:
1. **Category**
   - Fields: name, slug, description, color, icon, is_active, created_at, updated_at
   - Purpose: Blog post categorization
   - Relationships: One-to-many with Post

2. **Tag**
   - Fields: name, slug, created_at
   - Purpose: Post tagging system
   - Relationships: Many-to-many with Post

3. **Post**
   - Fields: title, slug, excerpt, content, featured_image, category (FK), tags (M2M), author (FK), status, is_featured, allow_comments, view_count, like_count, created_at, updated_at, published_at
   - Purpose: Blog posts and content
   - Relationships: Many-to-one with Category, Many-to-many with Tag, Many-to-one with User

4. **Comment**
   - Fields: post (FK), author (FK), content, is_approved, parent (FK to self), created_at, updated_at
   - Purpose: Post comments with threading
   - Relationships: Many-to-one with Post, Many-to-one with User, Self-referential

5. **PostLike**
   - Fields: post (FK), user (FK), created_at
   - Purpose: Post likes tracking
   - Relationships: Many-to-one with Post, Many-to-one with User

6. **NewsletterSubscription**
   - Fields: email, is_active, subscribed_at, unsubscribed_at
   - Purpose: Newsletter subscription management

### 3. Courses App (`app.courses`)
**Purpose**: Online course management system

#### Models:
1. **CourseCategory**
   - Fields: name, slug, description, icon, color, is_active, created_at
   - Purpose: Course categorization
   - Relationships: One-to-many with Course

2. **Course**
   - Fields: title, slug, description, short_description, category (FK), instructor (FK), difficulty, status, price, discount_price, is_free, duration_hours, language, level, prerequisites, learning_objectives, thumbnail, video_intro, enrollment_count, rating, review_count, created_at, updated_at, published_at
   - Purpose: Online courses
   - Relationships: Many-to-one with CourseCategory, Many-to-one with User (instructor)

3. **CourseModule**
   - Fields: course (FK), title, description, order, is_required, created_at
   - Purpose: Course modules/lessons organization
   - Relationships: Many-to-one with Course

4. **Lesson**
   - Fields: module (FK), title, description, lesson_type, content, video_file, video_url, duration_minutes, order, is_preview, is_required, allow_download, created_at, updated_at
   - Purpose: Individual lessons within modules
   - Relationships: Many-to-one with CourseModule

5. **Enrollment**
   - Fields: user (FK), course (FK), status, enrolled_at, completed_at, progress_percentage, last_accessed
   - Purpose: User course enrollments
   - Relationships: Many-to-one with User, Many-to-one with Course

6. **LessonProgress**
   - Fields: enrollment (FK), lesson (FK), is_completed, completed_at, time_spent, last_position
   - Purpose: User progress on individual lessons
   - Relationships: Many-to-one with Enrollment, Many-to-one with Lesson

7. **CourseReview**
   - Fields: enrollment (OneToOne), rating, title, content, is_approved, created_at, updated_at
   - Purpose: Course reviews and ratings
   - Relationships: One-to-one with Enrollment

8. **Coupon**
   - Fields: code, title, description, coupon_type, discount_value, min_order_amount, max_discount_amount, usage_limit, used_count, is_active, valid_from, valid_until, applicable_courses (M2M), created_at, updated_at
   - Purpose: Discount coupons for courses
   - Relationships: Many-to-many with Course

9. **CoursePurchase**
   - Fields: user (FK), course (FK), amount_paid, original_price, discount_amount, coupon (FK), purchased_at, payment_method, transaction_id, order (FK)
   - Purpose: Course purchase records
   - Relationships: Many-to-one with User, Many-to-one with Course, Many-to-one with Coupon, Many-to-one with Order

### 4. Dashboard App (`app.dashboard`)
**Purpose**: User dashboard and profile management

#### Models:
1. **User** (Extended AbstractUser)
   - Fields: email (unique), user_type, phone_number, national_id, birth_date, gender, address, city, postal_code, profile_image, bio, is_verified, created_at, updated_at, license_number, specialization, experience_years, hourly_rate, is_available
   - Purpose: Extended user model with psychology institute specific fields
   - Relationships: One-to-one with UserProfile

2. **UserProfile**
   - Fields: user (OneToOne), emergency_contact_name, emergency_contact_phone, medical_conditions, medications, therapy_goals, preferred_language, timezone, notification_preferences, created_at, updated_at
   - Purpose: Additional user profile information
   - Relationships: One-to-one with User

3. **Activity**
   - Fields: user (FK), activity_type, description, ip_address, user_agent, created_at
   - Purpose: User activity tracking
   - Relationships: Many-to-one with User

4. **Notification**
   - Fields: user (FK), title, message, notification_type, is_read, created_at
   - Purpose: User notification system
   - Relationships: Many-to-one with User

### 5. Packages App (`app.packages`)
**Purpose**: Educational package management

#### Models:
1. **PackageCategory**
   - Fields: name, slug, description, icon, color, is_active, created_at
   - Purpose: Package categorization
   - Relationships: One-to-many with Package

2. **Package**
   - Fields: title, slug, description, short_description, category (FK), courses (M2M), status, price, discount_price, is_featured, duration_months, language, prerequisites, learning_objectives, thumbnail, intro_video, purchase_count, rating, review_count, meta_title, meta_description, created_at, updated_at, published_at
   - Purpose: Educational packages containing multiple courses
   - Relationships: Many-to-one with PackageCategory, Many-to-many with Course

3. **PackagePurchase**
   - Fields: user (FK), package (FK), amount_paid, original_price, discount_amount, payment_method, transaction_id, order (FK), purchased_at, expires_at
   - Purpose: Package purchases
   - Relationships: Many-to-one with User, Many-to-one with Package, Many-to-one with Order

4. **PackageEnrollment**
   - Fields: purchase (FK), enrollment (FK), started_at, last_accessed, created_at, updated_at
   - Purpose: Track user progress in package courses
   - Relationships: Many-to-one with PackagePurchase, Many-to-one with Enrollment

5. **PackageProgress**
   - Fields: purchase (OneToOne), overall_progress_percentage, completed_courses, total_time_spent, updated_at
   - Purpose: Overall package progress tracking
   - Relationships: One-to-one with PackagePurchase

6. **PackageReview**
   - Fields: purchase (OneToOne), rating, title, content, value_rating, content_rating, support_rating, is_approved, created_at, updated_at
   - Purpose: Package reviews and ratings
   - Relationships: One-to-one with PackagePurchase

7. **PackageCoupon**
   - Fields: code, title, description, coupon_type, discount_value, min_order_amount, max_discount_amount, usage_limit, used_count, is_active, valid_from, valid_until, applicable_packages (M2M), created_at, updated_at
   - Purpose: Discount coupons for packages
   - Relationships: Many-to-many with Package

### 6. Payment App (`app.payment`)
**Purpose**: Payment processing and order management

#### Models:
1. **PaymentMethod**
   - Fields: name, payment_type, is_active, config, created_at
   - Purpose: Available payment methods
   - Relationships: One-to-many with Payment

2. **Cart**
   - Fields: user (OneToOne), created_at, updated_at
   - Purpose: Shopping cart for users
   - Relationships: One-to-one with User, One-to-many with CartItem

3. **CartItem**
   - Fields: cart (FK), item_type, item_id, quantity, unit_price, added_at
   - Purpose: Items in shopping cart
   - Relationships: Many-to-one with Cart

4. **Order**
   - Fields: user (FK), order_number, status, subtotal, tax_amount, discount_amount, total_amount, payment_method (FK), payment_status, transaction_id, created_at, updated_at, paid_at
   - Purpose: Orders placed by users
   - Relationships: Many-to-one with User, Many-to-one with PaymentMethod, One-to-many with OrderItem, One-to-many with Payment

5. **OrderItem**
   - Fields: order (FK), item_type, item_id, item_title, quantity, unit_price, total_price
   - Purpose: Items in an order
   - Relationships: Many-to-one with Order

6. **Payment**
   - Fields: order (FK), payment_method (FK), amount, status, gateway_transaction_id, gateway_response, created_at, updated_at, completed_at
   - Purpose: Payment records
   - Relationships: Many-to-one with Order, Many-to-one with PaymentMethod

7. **InstallmentSchedule**
   - Fields: order (OneToOne), total_installments, current_installment, next_due_date, created_at, updated_at
   - Purpose: Installment schedule for orders
   - Relationships: One-to-one with Order

### 7. Reports App (`app.reports`)
**Purpose**: Analytics and reporting system

#### Models:
1. **Report**
   - Fields: name, report_type, description, data, filters, generated_by (FK), generated_at, period_start, period_end
   - Purpose: Financial and analytics reports
   - Relationships: Many-to-one with User

2. **DashboardWidget**
   - Fields: name, widget_type, title, description, config, position_x, position_y, width, height, is_active, created_at, updated_at
   - Purpose: Dashboard widgets for admin panel

3. **AnalyticsEvent**
   - Fields: user (FK), event_type, event_data, ip_address, user_agent, created_at
   - Purpose: Analytics events tracking
   - Relationships: Many-to-one with User

### 8. Sales App (`app.sales`)
**Purpose**: Institution sales and B2B management

#### Models:
1. **Institution**
   - Fields: name, institution_type, contact_person, email, phone, address, city, website, description, is_verified, created_at, updated_at
   - Purpose: Institutions that can purchase services
   - Relationships: One-to-many with InstitutionSubscription, One-to-many with InstitutionUser, One-to-many with InstitutionOrder

2. **ServicePackage**
   - Fields: name, package_type, description, price, duration_months, max_users, max_tests, max_courses, max_sessions, features, is_active, created_at, updated_at
   - Purpose: Service packages for institutions
   - Relationships: One-to-many with InstitutionSubscription, One-to-many with InstitutionOrder

3. **InstitutionSubscription**
   - Fields: institution (FK), package (FK), status, start_date, end_date, price_paid, current_users, tests_used, courses_used, sessions_used, created_at, updated_at
   - Purpose: Institution subscriptions to service packages
   - Relationships: Many-to-one with Institution, Many-to-one with ServicePackage

4. **InstitutionUser**
   - Fields: institution (FK), user (FK), role, is_active, joined_at
   - Purpose: Users associated with institutions
   - Relationships: Many-to-one with Institution, Many-to-one with User

5. **InstitutionOrder**
   - Fields: institution (FK), package (FK), status, quantity, unit_price, total_amount, approved_by (FK), approved_at, notes, created_at, updated_at
   - Purpose: Orders placed by institutions
   - Relationships: Many-to-one with Institution, Many-to-one with ServicePackage, Many-to-one with User

6. **InstitutionPayment**
   - Fields: institution (FK), order (FK), amount, status, payment_method, transaction_id, created_at, updated_at, completed_at
   - Purpose: Payments from institutions
   - Relationships: Many-to-one with Institution, Many-to-one with InstitutionOrder

### 9. Tests App (`app.tests`)
**Purpose**: Psychological testing system

#### Models:
1. **TestCategory**
   - Fields: name, slug, description, icon, color, is_active, created_at
   - Purpose: Categories for psychological tests
   - Relationships: One-to-many with PsychologicalTest

2. **PsychologicalTest**
   - Fields: title, description, category (FK), test_type, difficulty, estimated_duration, instructions, is_free, price, is_active, requires_therapist, min_age, max_age, created_by (FK), created_at, updated_at
   - Purpose: Psychological tests available for users
   - Relationships: Many-to-one with TestCategory, Many-to-one with User

3. **Question**
   - Fields: test (FK), question_text, question_type, order, is_required, created_at
   - Purpose: Questions for psychological tests
   - Relationships: Many-to-one with PsychologicalTest

4. **Choice**
   - Fields: question (FK), choice_text, value, order, score
   - Purpose: Answer choices for questions
   - Relationships: Many-to-one with Question

5. **TestSession**
   - Fields: user (FK), test (FK), status, started_at, completed_at, current_question (FK)
   - Purpose: User test sessions
   - Relationships: Many-to-one with User, Many-to-one with PsychologicalTest, Many-to-one with Question

6. **Answer**
   - Fields: session (FK), question (FK), selected_choices (M2M), text_answer, number_answer, answered_at
   - Purpose: User answers to test questions
   - Relationships: Many-to-one with TestSession, Many-to-one with Question, Many-to-many with Choice

7. **TestResult**
   - Fields: session (OneToOne), total_score, max_score, percentage, interpretation, recommendations, generated_at
   - Purpose: Results of completed tests
   - Relationships: One-to-one with TestSession

8. **TestPurchase**
   - Fields: user (FK), test (FK), amount_paid, purchased_at, payment_method, transaction_id
   - Purpose: Purchases of paid tests
   - Relationships: Many-to-one with User, Many-to-one with PsychologicalTest

### 10. Workshops App (`app.workshops`)
**Purpose**: Educational workshop management

#### Models:
1. **WorkshopCategory**
   - Fields: name, slug, description, icon, color, is_active, created_at
   - Purpose: Categories for workshops
   - Relationships: One-to-many with Workshop

2. **Workshop**
   - Fields: title, slug, description, short_description, category (FK), instructor (FK), status, difficulty, start_date, end_date, registration_deadline, max_participants, current_participants, price, discount_price, payment_type, installment_months, total_hours, language, prerequisites, learning_objectives, thumbnail, intro_video, rating, review_count, created_at, updated_at, published_at
   - Purpose: Educational workshops with multiple sessions
   - Relationships: Many-to-one with WorkshopCategory, Many-to-one with User (instructor)

3. **WorkshopSession**
   - Fields: workshop (FK), session_number, title, description, scheduled_datetime, duration_minutes, meeting_link, meeting_id, meeting_password, recording_url, materials, homework, is_completed, completed_at, created_at, updated_at
   - Purpose: Individual sessions within a workshop
   - Relationships: Many-to-one with Workshop

4. **WorkshopRegistration**
   - Fields: user (FK), workshop (FK), status, payment_type, amount_paid, total_amount, registered_at, completed_at, last_accessed, progress_percentage
   - Purpose: User registrations for workshops
   - Relationships: Many-to-one with User, Many-to-one with Workshop

5. **WorkshopSessionAttendance**
   - Fields: registration (FK), session (FK), attended, attendance_marked_at, join_time, leave_time, duration_minutes, notes, created_at, updated_at
   - Purpose: Track user attendance for workshop sessions
   - Relationships: Many-to-one with WorkshopRegistration, Many-to-one with WorkshopSession

6. **InstallmentPlan**
   - Fields: registration (OneToOne), total_amount, number_of_installments, installment_amount, created_at, updated_at
   - Purpose: Installment plan for a workshop registration
   - Relationships: One-to-one with WorkshopRegistration

7. **InstallmentPayment**
   - Fields: plan (FK), installment_number, amount, due_date, status, paid_at, payment_method, transaction_id, order (FK), reminder_sent, reminder_sent_at, created_at, updated_at
   - Purpose: Individual installment payments
   - Relationships: Many-to-one with InstallmentPlan, Many-to-one with Order

8. **WorkshopReview**
   - Fields: registration (OneToOne), rating, title, content, instructor_rating, content_rating, interaction_rating, is_approved, created_at, updated_at
   - Purpose: Workshop reviews and ratings
   - Relationships: One-to-one with WorkshopRegistration

### 11. Appointments App (`app.appointments`)
**Purpose**: Appointment booking system for in-person therapy sessions

#### Models:
1. **ClinicLocation**
   - Fields: name, address, city, phone, capacity, facilities (JSON), is_active, created_at, updated_at
   - Purpose: Central clinic locations where sessions occur
   - Relationships: One-to-many with TherapistSchedule, One-to-many with Appointment

2. **AppointmentType**
   - Fields: name, description, default_duration_minutes, price, color, is_active, created_at, updated_at
   - Purpose: Define different types of therapy appointments with both fixed and custom durations
   - Relationships: One-to-many with Appointment

3. **TherapistSchedule**
   - Fields: therapist (FK), day_of_week, start_time, end_time, location (FK), is_active, created_at, updated_at
   - Purpose: System-wide working hours and therapist availability patterns
   - Relationships: Many-to-one with User (therapist), Many-to-one with ClinicLocation

4. **TherapistTimeOff**
   - Fields: therapist (FK), start_date, end_date, reason, is_approved, created_at, updated_at
   - Purpose: Exceptions to regular schedule (vacations, breaks)
   - Relationships: Many-to-one with User (therapist)

5. **Appointment**
   - Fields: client (FK), therapist (FK), appointment_type (FK), location (FK), scheduled_datetime, duration_minutes, status, notes, created_at, updated_at
   - Purpose: Main booking model for therapy sessions
   - Relationships: Many-to-one with User (client), Many-to-one with User (therapist), Many-to-one with AppointmentType, Many-to-one with ClinicLocation
   - Status choices: scheduled, confirmed, completed, cancelled, no_show, rescheduled

6. **AppointmentCancellation**
   - Fields: appointment (OneToOne), cancelled_by (FK), cancelled_at, reason, cancellation_fee, refund_amount, policy_applied
   - Purpose: Track cancellations with time-based policies and fee calculations
   - Relationships: One-to-one with Appointment, Many-to-one with User

7. **AppointmentReschedule**
   - Fields: original_appointment (FK), new_appointment (FK), rescheduled_by (FK), rescheduled_at, reason, reschedule_fee
   - Purpose: Track rescheduling history and maintain appointment chain
   - Relationships: Many-to-one with Appointment (original), Many-to-one with Appointment (new), Many-to-one with User

8. **CancellationPolicy**
   - Fields: name, hours_before_appointment, cancellation_fee_percentage, description, is_active, created_at, updated_at
   - Purpose: Define cancellation rules with time-based fee structures
   - Example policies: 24hrs+ = 0%, 12-24hrs = 25%, <12hrs = 50%

9. **AppointmentReminder**
   - Fields: appointment (FK), reminder_type, scheduled_time, sent_at, status, created_at
   - Purpose: Automated reminders via email, SMS, or push notifications
   - Relationships: Many-to-one with Appointment

## Database Architecture Summary

### Key Relationships:
1. **User Model**: Central to the system, extended with psychology-specific fields
2. **Content Management**: Blog posts, courses, packages, workshops
3. **Learning Management**: Enrollments, progress tracking, assessments
4. **Payment System**: Orders, payments, installments, coupons
5. **Analytics**: Reports, events, dashboard widgets
6. **Institution Management**: B2B sales and subscriptions

### Foreign Key Relationships:
- Most models have relationships with the User model
- Content models (courses, packages, workshops) have category relationships
- Payment models are interconnected through Order and Payment relationships

### Many-to-Many Relationships:
- Post-Tag relationships in blog
- Course-Package relationships
- User-Notification relationships in admin panel
- Course-User relationships through enrollments

### Unique Constraints:
- User email uniqueness
- Order number uniqueness
- Various unique_together constraints for business logic

## Current Project State
**Total Apps**: 11 Django apps
**Total Models**: 70+ ORM models
**Status**: All therapy_sessions app references have been removed from the codebase. New appointments app added for in-person therapy session booking.

This architecture supports a comprehensive psychology institute platform with learning management, content management, business operations, and appointment booking system.
