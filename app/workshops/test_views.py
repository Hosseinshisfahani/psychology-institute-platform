from django.shortcuts import render
from django.http import HttpResponse

def test_persian_calendar(request):
    """
    Test view for Persian calendar functionality
    """
    return render(request, 'workshops/test_persian_calendar.html')
