from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
import logging
from .models import W2Report
from .tasks import upload_pdf_file_task

logger = logging.getLogger(__name__)

class CallbackView(APIView):
    """
    Handles the callback from the third-party API service.
    This view is responsible for triggering the second task to upload the PDF.
    """
    def post(self, request, *args, **kwargs):
        # The third-party API is expected to send back the report_id
        # in the request body, typically as JSON.
        try:
            report_id = request.data.get('report_id')
            if not report_id:
                logger.error("Callback API: No report_id received in callback.")
                return Response({"error": "report_id not found in request body."}, status=status.HTTP_400_BAD_REQUEST)
            
            logger.info(f"Callback API: Received callback for report_id: {report_id}")

            # Trigger the second Celery task to upload the PDF file
            upload_pdf_file_task.delay(report_id)

            return Response({"message": "Callback received, PDF upload task initiated."}, status=status.HTTP_200_OK)
        
        except Exception as e:
            logger.error(f"Callback API: An error occurred: {e}")
            return Response({"error": "An unexpected error occurred."}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
