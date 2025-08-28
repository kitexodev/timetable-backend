# In timetable_project/urls.py

from django.contrib import admin
from django.urls import path, include # Make sure 'include' is imported

urlpatterns = [
    path('admin/', admin.site.urls),
    # This line tells Django that all API routes should start with 'api/'
    # and are defined in the 'core.urls' file.
    path('api/', include('core.urls')),
]