import logging
from celery import shared_task
from django.db import transaction
from .models import W2Report
import PyPDF2
import os
import requests
import json
from django.conf import settings

logger = logging.getLogger(__name__)

# The third-party API base URL is our local mock service
THIRD_PARTY_API_BASE_URL = "http://localhost:8000/mock_api/"

# The secret key for authentication. This is explicitly defined here to
# ensure the tasks have access to it. In a real-world scenario, it would be
# loaded from a secure environment variable.
FINPRO_API_KEY = "FinPro-Secret-Key"

@shared_task(bind=True)
def process_w2_form_task(self, report_id):
    """
    Asynchronously processes a W-2 form, extracts data, and sends it to a
    third-party API.
    """
    logger.warning("-----------------------Celery task trying-------------------------")
    logger.warning("----------------------->pdf file processing starts<-------------------------")
    
    try:
        with transaction.atomic():
            report = W2Report.objects.select_for_update().get(pk=report_id)
            file_path = report.pdf_file.path
            logger.warning(f"filepath--->{file_path}")

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")
            pdf_file_size = os.path.getsize(file_path)
            with open(file_path, 'rb') as f:
                reader = PyPDF2.PdfReader(f)
                text = ""
                for page in reader.pages:
                    text += page.extract_text() or ""
            
            extracted_ein = None
            extracted_ssn = None
            extracted_wages = None
            extracted_federal_tax = None

            extracted_data_list = text.split('|')
            if len(extracted_data_list) > 3:
                extracted_ein = extracted_data_list[0].strip()
                extracted_ssn = extracted_data_list[1].strip()
                extracted_wages = extracted_data_list[2].strip()
                extracted_federal_tax = extracted_data_list[3].strip()
            
            # Prepare data to be sent to the third-party API
            data_payload = {
                "report_id": report_id,
                "ein": extracted_ein,
                "ssn": extracted_ssn,
                "wages": extracted_wages,
                "federal_tax_withheld": extracted_federal_tax
            }

            # Headers for authentication
            headers = {
                'Content-Type': 'application/json',
                'X-API-Key': FINPRO_API_KEY # The authentication header
            }

            # Send the data to the third-party API
            api_endpoint = f"{THIRD_PARTY_API_BASE_URL}create/"
            response = requests.post(api_endpoint, data=json.dumps(data_payload), headers=headers)
            response.raise_for_status() # Raise an exception for bad status codes

            report.ein = extracted_ein
            report.ssn = extracted_ssn
            if extracted_wages:
                report.wages = float(extracted_wages)
            if extracted_federal_tax:
                report.federal_tax_withheld = float(extracted_federal_tax)

            report.report_status = 'SENT_TO_THIRD_PARTY'
            report.file_size = pdf_file_size
            report.save()

            logger.warning(f"Successfully sent data for report_id: {report_id} to third-party API. Report status: {report.report_status}")
            return f"Successfully processed report_id: {report_id} and sent data to third-party API."

    except (requests.exceptions.RequestException, ValueError) as e:
        logger.error(f"API request or data type conversion error for report {report_id}: {e}")
        with transaction.atomic():
            report = W2Report.objects.get(pk=report_id)
            report.report_status = 'FAILED'
            report.save()
        return f"Report {report_id} processing failed due to API or data conversion error."
    
    except W2Report.DoesNotExist:
        logger.error(f"W2Report with id {report_id} does not exist.")
        return f"Report {report_id} not found."
    
    except Exception as e:
        logger.error(f"An unexpected error occurred while processing report {report_id}: {e}")
        try:
            with transaction.atomic():
                report = W2Report.objects.get(pk=report_id)
                report.report_status = 'FAILED'
                report.save()
        except W2Report.DoesNotExist:
            pass
        return f"An unexpected error occurred for report {report_id}."

@shared_task(bind=True)
def upload_pdf_file_task(self, report_id):
    """
    Uploads the PDF file to the third-party API. This task is triggered by
    the callback from the third-party service.
    """
    try:
        with transaction.atomic():
            report = W2Report.objects.select_for_update().get(pk=report_id)
            file_path = report.pdf_file.path

            if not os.path.exists(file_path):
                raise FileNotFoundError(f"File not found: {file_path}")

            # Prepare the file for upload
            with open(file_path, 'rb') as f:
                files = {'file': (os.path.basename(file_path), f, 'application/pdf')}
                
                # Headers for authentication
                headers = {
                    'X-API-Key': FINPRO_API_KEY # The authentication header
                }

                # Send the file to the third-party API, using the correct third_party_report_id
                api_endpoint = f"{THIRD_PARTY_API_BASE_URL}{report.third_party_report_id}/upload_file/"
                response = requests.post(api_endpoint, files=files, headers=headers)
                response.raise_for_status()

            # Update the report status to COMPLETED
            report.report_status = 'COMPLETED'
            report.save()

            logger.warning(f"Successfully uploaded PDF for report {report_id} to third-party API. file_id:{report.third_party_report_id}, Report status: {report.report_status}")
            return f"Successfully uploaded PDF for report_id: {report_id}, file_id: {report.third_party_report_id}"

    except (requests.exceptions.RequestException, W2Report.DoesNotExist, FileNotFoundError) as e:
        logger.error(f"Error uploading PDF for report {report_id}: {e}")
        with transaction.atomic():
            report = W2Report.objects.get(pk=report_id)
            report.report_status = 'FAILED'
            report.save()
        return f"Report {report_id} processing failed during PDF upload."
    
    except Exception as e:
        logger.error(f"An unexpected error occurred during PDF upload for report {report_id}: {e}")
        try:
            with transaction.atomic():
                report = W2Report.objects.get(pk=report_id)
                report.report_status = 'FAILED'
                report.save()
        except W2Report.DoesNotExist:
            pass
        return f"An unexpected error occurred for report {report_id}."
