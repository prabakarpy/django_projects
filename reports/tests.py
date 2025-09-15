import io
import uuid
import json
from unittest import mock
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from .models import W2Report
from .pdf_parser import extract_w2_data
from tempfile import NamedTemporaryFile
from django.core.files.uploadedfile import SimpleUploadedFile
from unittest.mock import patch, MagicMock

from .models import W2Report

# Mock data for a valid W-2
MOCK_W2_PDF_CONTENT = b"Fake PDF Content for Box 1 - Wages, tips, other compensation $12,345.67 " \
                     b"Employee's Social Security Number 123-45-6789 " \
                     b"Employer Identification Number 98-7654321 " \
                     b"Box 2 - Federal income tax withheld $1,234.56"

# A valid W-2 data dictionary
VALID_W2_DATA = {
    'ein': '98-7654321',
    'ssn': '123-45-6789',
    'wages': 12345.67,
    'federal_tax_withheld': 1234.56,
}

class PDFParserTests(TestCase):
    def test_extract_w2_data_success(self):
        """
        Test that all required fields are correctly extracted from a valid mock PDF.
        """
        with NamedTemporaryFile(suffix=".pdf", delete=True) as temp_file:
            temp_file.write(MOCK_W2_PDF_CONTENT)
            temp_file.seek(0)
            extracted_data = extract_w2_data(temp_file.name)
        
        self.assertIsNotNone(extracted_data)
        self.assertEqual(extracted_data, VALID_W2_DATA)

    def test_extract_w2_data_failure(self):
        """
        Test that extraction fails gracefully for an invalid PDF.
        """
        with NamedTemporaryFile(suffix=".pdf", delete=True) as temp_file:
            temp_file.write(b"This is not a W-2 form.")
            temp_file.seek(0)
            extracted_data = extract_w2_data(temp_file.name)
            
        self.assertIsNone(extracted_data)

class W2ViewTests(TestCase):
    def setUp(self):
        self.client = self.client
        self.upload_url = reverse('w2-upload')
        self.mock_file = SimpleUploadedFile(
            "w2_form.pdf",
            MOCK_W2_PDF_CONTENT,
            content_type="application/pdf"
        )
        self.report = W2Report.objects.create(
            pdf_file=self.mock_file
        )

    @patch('reports.tasks.process_w2_form_task.delay')
    def test_w2_form_upload_success(self, mock_task_delay):
        """
        Test that a valid PDF upload creates a report and triggers the task.
        """
        mock_file_stream = io.BytesIO(MOCK_W2_PDF_CONTENT)
        mock_file = SimpleUploadedFile("w2_form.pdf", mock_file_stream.getvalue(), content_type="application/pdf")

        response = self.client.post(self.upload_url, {'file': mock_file}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_202_ACCEPTED)
        self.assertIn('report_id', response.json())
        self.assertIn('status', response.json())
        self.assertEqual(response.json()['status'], 'PENDING')
        
        # Check if a new W2Report object was created
        self.assertEqual(W2Report.objects.count(), 2)

        # Check if the Celery task was called with the correct ID
        created_report_id = response.json()['report_id']
        mock_task_delay.assert_called_once_with(created_report_id)

    def test_w2_form_upload_invalid(self):
        """
        Test that an invalid request returns a 400 Bad Request.
        """
        response = self.client.post(self.upload_url, {}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertIn('file', response.json())
        self.assertEqual(W2Report.objects.count(), 1) # Only the setup report exists

    def test_w2_report_status_success(self):
        """
        Test that a valid report status can be retrieved.
        """
        url = reverse('w2-status', args=[self.report.id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(str(response.json()['id']), str(self.report.id))
        self.assertEqual(response.json()['report_status'], 'PENDING_PROCESSING')

    def test_w2_report_status_not_found(self):
        """
        Test that a non-existent report ID returns a 404 Not Found.
        """
        non_existent_id = uuid.uuid4()
        url = reverse('w2-status', args=[non_existent_id])
        response = self.client.get(url)

        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertEqual(response.json()['error'], 'Report not found.')


