from django.urls import path
from .views import W2FormUploadView, W2ReportStatusView
from .callback_views import CallbackView

urlpatterns = [
    path('w2/upload/', W2FormUploadView.as_view(), name='w2-upload'),
    path('w2/status/<uuid:report_id>/', W2ReportStatusView.as_view(), name='w2-status'),
    # New API endpoint to handle the third-party callback
    path('w2/callback/', CallbackView.as_view(), name='w2-callback'),
]