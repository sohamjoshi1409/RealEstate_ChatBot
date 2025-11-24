from django.urls import path
from .views import UploadDatasetView, QueryAnalysisView

urlpatterns = [
    path('upload/', UploadDatasetView.as_view(), name='analysis-upload'),
    path('query/', QueryAnalysisView.as_view(), name='analysis-query'),
]

