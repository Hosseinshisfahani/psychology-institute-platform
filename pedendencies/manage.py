#!/usr/bin/env python
"""Django's command-line utility for administrative tasks."""
import os
import sys
from pathlib import Path

# Get the absolute path to this manage.py file
MANAGE_PY_PATH = Path(__file__).resolve()

# Project root is the parent of pedendencies directory
PROJECT_ROOT = MANAGE_PY_PATH.parent.parent

# Add project root to Python path so we can import psychology_institute module
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

# Update sys.argv[0] to absolute path for Django's autoreload
sys.argv[0] = str(MANAGE_PY_PATH)

# Change working directory to project root
# This ensures Django finds templates, static files, etc. with correct relative paths
os.chdir(str(PROJECT_ROOT))


def main():
    """Run administrative tasks."""
    os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'psychology_institute.settings')
    try:
        from django.core.management import execute_from_command_line
    except ImportError as exc:
        raise ImportError(
            "Couldn't import Django. Are you sure it's installed and "
            "available on your PYTHONPATH environment variable? Did you "
            "forget to activate a virtual environment?"
        ) from exc
    execute_from_command_line(sys.argv)


if __name__ == '__main__':
    main()
