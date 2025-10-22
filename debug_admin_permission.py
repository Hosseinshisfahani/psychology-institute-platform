#!/usr/bin/env python
"""
Debug script to test AdminPermission
"""
import os
import sys
import django

# Add the project directory to Python path
sys.path.insert(0, '/Users/hossein.sh.isfahani/projects/Emamy project')

# Set up Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_institute.settings')
django.setup()

from app.admin_panel.api_views import AdminPermission
from app.dashboard.models import User
from django.test import RequestFactory
from django.contrib.auth import get_user_model

def test_admin_permission():
    """Test the AdminPermission class"""
    print("Testing AdminPermission...")
    
    # Get an admin user
    admin_user = User.objects.filter(user_type='admin').first()
    if not admin_user:
        print("❌ No admin user found")
        return
    
    print(f"Admin user: {admin_user.email} (user_type: {admin_user.user_type})")
    
    # Create a mock request
    factory = RequestFactory()
    request = factory.get('/api/admin/workshops/')
    request.user = admin_user
    
    # Test the permission
    permission = AdminPermission()
    has_permission = permission.has_permission(request, None)
    
    print(f"Has permission: {has_permission}")
    print(f"User is authenticated: {request.user.is_authenticated}")
    print(f"User type: {request.user.user_type}")
    
    if has_permission:
        print("✅ AdminPermission is working correctly")
    else:
        print("❌ AdminPermission is not working")
        
        # Debug further
        print(f"User.is_authenticated: {request.user.is_authenticated}")
        print(f"User.user_type: {request.user.user_type}")
        print(f"User.user_type == 'admin': {request.user.user_type == 'admin'}")

if __name__ == "__main__":
    test_admin_permission()
