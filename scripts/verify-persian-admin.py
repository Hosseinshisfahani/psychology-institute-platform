#!/usr/bin/env python
"""
Script to verify Persian (Farsi) configuration for Django Admin
"""
import os
import sys
import django

# Setup Django environment
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_institute.settings')
django.setup()

from django.conf import settings
from django.apps import apps
from django.contrib import admin
from django.utils.translation import gettext as _


def check_language_settings():
    """Check if language settings are configured for Persian"""
    print("\n" + "="*60)
    print("1. Checking Language Settings")
    print("="*60)
    
    checks = {
        "LANGUAGE_CODE": settings.LANGUAGE_CODE,
        "TIME_ZONE": settings.TIME_ZONE,
        "USE_I18N": settings.USE_I18N,
        "USE_L10N": getattr(settings, 'USE_L10N', None),
        "LANGUAGE_BIDI": getattr(settings, 'LANGUAGE_BIDI', None),
    }
    
    for key, value in checks.items():
        status = "✅" if value else "❌"
        print(f"{status} {key}: {value}")
    
    # Check if locale path exists
    locale_paths = getattr(settings, 'LOCALE_PATHS', [])
    print(f"\n📁 Locale Paths: {list(locale_paths)}")
    
    for locale_path in locale_paths:
        fa_path = os.path.join(locale_path, 'fa', 'LC_MESSAGES')
        po_file = os.path.join(fa_path, 'django.po')
        mo_file = os.path.join(fa_path, 'django.mo')
        
        print(f"\n  PO File: {'✅' if os.path.exists(po_file) else '❌'} {po_file}")
        print(f"  MO File: {'✅' if os.path.exists(mo_file) else '❌'} {mo_file}")
        
        if os.path.exists(mo_file):
            mo_time = os.path.getmtime(mo_file)
            from datetime import datetime
            print(f"  Last Compiled: {datetime.fromtimestamp(mo_time).strftime('%Y-%m-%d %H:%M:%S')}")


def check_admin_site_config():
    """Check admin site titles"""
    print("\n" + "="*60)
    print("2. Checking Admin Site Configuration")
    print("="*60)
    
    print(f"Site Header: {admin.site.site_header}")
    print(f"Site Title: {admin.site.site_title}")
    print(f"Index Title: {admin.site.index_title}")


def check_app_verbose_names():
    """Check verbose names for all apps"""
    print("\n" + "="*60)
    print("3. Checking App Verbose Names")
    print("="*60)
    
    local_apps = [
        'app.blog',
        'app.tests',
        'app.courses',
        'app.dashboard',
        'app.therapy_sessions',
        'app.payment',
        'app.reports',
        'app.sales',
        'app.admin_panel',
        'app.workshops',
        'app.packages',
        'app.cohorts',
    ]
    
    for app_name in local_apps:
        try:
            app_config = apps.get_app_config(app_name.split('.')[-1])
            print(f"\n{app_name}:")
            print(f"  Verbose Name: {app_config.verbose_name}")
        except Exception as e:
            print(f"❌ {app_name}: Error - {str(e)}")


def check_translations():
    """Test some key translations"""
    print("\n" + "="*60)
    print("4. Testing Key Translations")
    print("="*60)
    
    test_strings = [
        "Blog",
        "DASHBOARD",
        "Courses",
        "Packages",
        "Therapy Sessions",
        "Workshops",
        "Admin Panel",
        "Psychology Institute Administration",
    ]
    
    from django.utils import translation
    
    # Activate Persian
    with translation.override('fa'):
        for string in test_strings:
            translated = _(string)
            status = "✅" if translated != string else "⚠️"
            print(f"{status} {string} → {translated}")


def main():
    """Run all checks"""
    print("\n" + "#"*60)
    print("# Persian/Farsi Admin Configuration Verification")
    print("# Psychology Institute Project")
    print("#"*60)
    
    check_language_settings()
    check_admin_site_config()
    check_app_verbose_names()
    check_translations()
    
    print("\n" + "="*60)
    print("Verification Complete!")
    print("="*60)
    print("\n✨ If all checks passed, your admin panel should be in Persian.")
    print("🔄 If admin is still in English, try:")
    print("   1. Clear browser cache (Ctrl+Shift+R)")
    print("   2. Restart Django server")
    print("   3. Run: python manage.py compilemessages")
    print("")


if __name__ == '__main__':
    main()

