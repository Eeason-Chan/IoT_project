from django.urls import path
from .views import SummaryView, DistributionView, TimeseriesView, ZoneStatsView, RecordsView

urlpatterns = [
    path('summary', SummaryView.as_view()),
    path('distribution', DistributionView.as_view()),
    path('timeseries', TimeseriesView.as_view()),
    path('zone-stats', ZoneStatsView.as_view()),
    path('records', RecordsView.as_view()),
]