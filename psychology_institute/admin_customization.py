from django.contrib import admin

# --- PERIODIC TASKS (django-celery-beat) ---
from django_celery_beat.models import (
    ClockedSchedule, CrontabSchedule, IntervalSchedule,
    PeriodicTask, SolarSchedule,
)

# --- ACCOUNTS (allauth) ---
from allauth.account.models import EmailAddress

# --- SOCIAL ACCOUNTS (allauth) ---
from allauth.socialaccount.models import SocialAccount, SocialApp, SocialToken

# --- SITES ---
from django.contrib.sites.models import Site

# --- GROUPS (optional) ---
from django.contrib.auth.models import Group


MODELS_TO_HIDE = [
    # Periodic tasks
    ClockedSchedule, CrontabSchedule, IntervalSchedule, PeriodicTask, SolarSchedule,
    # Accounts / social
    EmailAddress, SocialAccount, SocialApp, SocialToken,
    # Sites
    Site,
    # Groups (optional)
    Group,
]

def unregister_third_party_models():
    for model in MODELS_TO_HIDE:
        try:
            admin.site.unregister(model)
        except admin.sites.NotRegistered:
            pass