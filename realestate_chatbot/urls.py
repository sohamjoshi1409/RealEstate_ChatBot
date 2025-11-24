from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),

    # Analysis API endpoints (upload, query)
    path('api/analysis/', include('analysis.urls')),
]
