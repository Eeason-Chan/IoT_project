from django.urls import path
from .views import HealthView, StatsView

urlpatterns = [
    path('health', HealthView.as_view()),
    path('stats', StatsView.as_view()),
]