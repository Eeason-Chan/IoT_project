from django.urls import path
from .views import SHAPGlobalView, SHAPLocalView, SHAPSummaryView, LIMELocalView, CompareView

urlpatterns = [
    path('shap/global', SHAPGlobalView.as_view()),
    path('shap/local/<int:record_id>', SHAPLocalView.as_view()),
    path('shap/summary', SHAPSummaryView.as_view()),
    path('lime/local/<int:record_id>', LIMELocalView.as_view()),
    path('compare/<int:record_id>', CompareView.as_view()),
]