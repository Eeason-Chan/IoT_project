"""
URL configuration for XAI Traffic Dashboard.
"""
from django.urls import path, include

urlpatterns = [
    path('api/traffic/', include('traffic.urls')),
    path('api/xai/', include('xai.urls')),
    path('api/system/', include('monitoring.urls')),
]