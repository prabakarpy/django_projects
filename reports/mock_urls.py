from django.urls import path
from .mock_views import MockDataCreateView, MockFileUpdateView

urlpatterns = [
    # Mock endpoint for creating a report and returning a unique ID
    path('create/', MockDataCreateView.as_view(), name='mock-api-create'),
    
    # Mock endpoint for uploading the file using the unique ID
    path('<uuid:report_id>/upload_file/', MockFileUpdateView.as_view(), name='mock-api-upload-file'),
]
