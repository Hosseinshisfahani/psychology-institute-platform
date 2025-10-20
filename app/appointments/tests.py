from django.test import TestCase
from django.contrib.auth import get_user_model
from .models import Staff, AppointmentType, Appointment, AppointmentRoom

User = get_user_model()

class AppointmentModelTests(TestCase):
    """Test cases for appointment models"""
    
    def setUp(self):
        # Create test user
        self.user = User.objects.create_user(
            username='testuser',
            email='test@example.com',
            password='testpass123'
        )
        
        # Create test staff
        self.staff = Staff.objects.create(
            user=self.user,
            role='counselor',
            title='Senior Counselor',
            is_available=True,
            accepts_appointments=True
        )
        
        # Create test appointment type
        self.appointment_type = AppointmentType.objects.create(
            name='مشاوره عمومی',
            duration_minutes=60,
            price=500000
        )
        
        # Create test room
        self.room = AppointmentRoom.objects.create(
            name='اتاق مشاوره 1',
            room_number='101',
            floor=1,
            capacity=3
        )
    
    def test_staff_creation(self):
        """Test staff model creation"""
        self.assertEqual(self.staff.user, self.user)
        self.assertEqual(self.staff.role, 'counselor')
        self.assertTrue(self.staff.is_available)
        self.assertTrue(self.staff.accepts_appointments)
    
    def test_appointment_type_creation(self):
        """Test appointment type creation"""
        self.assertEqual(self.appointment_type.name, 'مشاوره عمومی')
        self.assertEqual(self.appointment_type.duration_minutes, 60)
        self.assertEqual(self.appointment_type.price, 500000)
    
    def test_appointment_room_creation(self):
        """Test appointment room creation"""
        self.assertEqual(self.room.name, 'اتاق مشاوره 1')
        self.assertEqual(self.room.room_number, '101')
        self.assertEqual(self.room.floor, 1)
        self.assertTrue(self.room.is_available)