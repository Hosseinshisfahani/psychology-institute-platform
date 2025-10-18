from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Cohort, CohortSession, CohortEnrollment

User = get_user_model()


class CohortModelTest(TestCase):
    def setUp(self):
        self.instructor = User.objects.create_user(
            email='instructor@test.com',
            first_name='Test',
            last_name='Instructor',
            user_type='therapist'
        )
        
        self.student = User.objects.create_user(
            email='student@test.com',
            first_name='Test',
            last_name='Student',
            user_type='client'
        )
    
    def test_cohort_creation(self):
        cohort = Cohort.objects.create(
            title='Test Cohort',
            description='Test Description',
            instructor=self.instructor,
            start_date='2024-01-01',
            end_date='2024-03-01',
            class_time='10:00:00',
            duration_minutes=90,
            total_sessions=12,
            full_price=1000000,
            max_students=20
        )
        
        self.assertEqual(cohort.title, 'Test Cohort')
        self.assertEqual(cohort.current_enrollments, 0)
        self.assertFalse(cohort.is_full)
        self.assertEqual(cohort.available_spots, 20)
    
    def test_cohort_enrollment(self):
        cohort = Cohort.objects.create(
            title='Test Cohort',
            description='Test Description',
            instructor=self.instructor,
            start_date='2024-01-01',
            end_date='2024-03-01',
            class_time='10:00:00',
            duration_minutes=90,
            total_sessions=12,
            full_price=1000000,
            max_students=20
        )
        
        enrollment = CohortEnrollment.objects.create(
            student=self.student,
            cohort=cohort,
            payment_type='full',
            total_amount=cohort.full_price
        )
        
        self.assertEqual(enrollment.student, self.student)
        self.assertEqual(enrollment.cohort, cohort)
        self.assertEqual(enrollment.payment_type, 'full')
        self.assertEqual(enrollment.total_amount, 1000000)
