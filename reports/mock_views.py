import logging
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import uuid
from .tasks import upload_pdf_file_task
from django.conf import settings

logger = logging.getLogger(__name__)
FINPRO_API_KEY = "FinPro-Secret-Key"
class MockDataCreateView(APIView):
    """
    Mock endpoint to simulate receiving W-2 data from the Celery task.
    It returns a unique third_party_report_id and triggers the callback.
    """
    def post(self, request, *args, **kwargs):
        # Authentication check
        if request.headers.get('X-API-Key') != FINPRO_API_KEY:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
            
        data = request.data
        
        logger.info("Mock API: Received data from process_w2_form_task")
        logger.info(f"Mock API: Data received: {data}")
        
        third_party_report_id = str(uuid.uuid4())
        report_id = data.get('report_id')

        if report_id:
            logger.info(f"Mock API: Directly triggering upload_pdf_file_task for report_id: {report_id}")
            upload_pdf_file_task.delay(report_id)

        return Response({"report_id": third_party_report_id}, status=status.HTTP_201_CREATED)

class MockFileUpdateView(APIView):
    """
    Mock endpoint to simulate receiving the PDF file from the Celery task.
    It returns a unique third_party_file_id.
    """
    def post(self, request, report_id, *args, **kwargs):
        # Authentication check
        if request.headers.get('X-API-Key') != FINPRO_API_KEY:
            return Response({"detail": "Authentication credentials were not provided."}, status=status.HTTP_401_UNAUTHORIZED)
        
        uploaded_file = request.FILES.get('file')
        
        if not uploaded_file:
            logger.error("Mock API: No file received for upload.")
            return Response({"error": "No file was submitted."}, status=status.HTTP_400_BAD_REQUEST)
        
        logger.info(f"Mock API: Received file upload for report_id: {report_id}")
        logger.info(f"Mock API: File name: {uploaded_file.name}, size: {uploaded_file.size} bytes")

        third_party_file_id = str(uuid.uuid4())
        
        return Response({"file_id": third_party_file_id}, status=status.HTTP_200_OK)
