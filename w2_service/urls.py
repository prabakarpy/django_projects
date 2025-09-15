from django.contrib import admin
from django.urls import path, include

# Import the new view from your reports app
from reports.views import health_check

urlpatterns = [
    # Health check at the root of the site
    path('', health_check, name='health-check'),
    
    # Standard admin URL
    path('admin/', admin.site.urls),
    
    # Route all API endpoints from the reports app under the /api/ prefix
    path('api/', include('reports.urls')),
    
    # Route all mock API endpoints under the /mock_api/ prefix
    path('mock_api/', include('reports.mock_urls')),
]