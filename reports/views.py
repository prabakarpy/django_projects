from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from django.http import HttpResponse
from django.conf import settings
# Corrected import statement
from .tasks import process_w2_form_task
# Corrected model import
from .models import W2Report
import uuid
import os

def health_check(request):
    """
    A simple view to confirm the server is running.
    """
    return HttpResponse("Django web service is running successfully for PDF project..")

class W2FormUploadView(APIView):
    """
    Handles the upload of W-2 forms.
    """
    def post(self, request, *args, **kwargs):
        """
        Processes an uploaded W-2 form.
        """
        uploaded_file = request.FILES.get('file')

        if not uploaded_file:
            return Response({"error": "No file was submitted."}, status=status.HTTP_400_BAD_REQUEST)

        try:
            # Create a new W2Report object with the uploaded file.
            # Django's FileField will handle saving the file to the correct path based on the upload_to parameter.
            report = W2Report.objects.create(pdf_file=uploaded_file)
            report_id = str(report.id)
            
            # Trigger the Celery task to process the file in the background.
            # We only need to pass the report's ID. The task will look up the file path from the database.
            process_w2_form_task.delay(report_id)

            # Return a success response with the new report ID
            return Response(
                {"message": "File uploaded successfully.", "report_id": report_id},
                status=status.HTTP_201_CREATED
            )
        except Exception as e:
            # This will catch any exceptions during the file creation and provide a more informative error.
            return Response(
                {"error": f"An error occurred during file upload: {e}"},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR
            )


class W2ReportStatusView(APIView):
    """
    Handles checking the status of a W-2 form report.
    """
    def get(self, request, report_id, *args, **kwargs):
        """
        Retrieves the status of a specific report by its ID.
        """
        try:
            # Use the correct model name and primary key for lookup
            report = W2Report.objects.get(pk=report_id)
            return Response({"report_id": report.id, "status": report.report_status})
        except W2Report.DoesNotExist:
            return Response({"error": "Report not found."}, status=status.HTTP_404_NOT_FOUND)
