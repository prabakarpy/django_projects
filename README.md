W-2 Processing Service
This project is a Django-based W-2 processing service that uses a third-party mock API for data and file processing. The workflow is asynchronous, leveraging Celery for background tasks.

Prerequisites
To run this project, you need the following installed on your machine:

Python 3.8+

Git

Redis: The Celery worker uses Redis as its message broker. Make sure Redis is installed and running on your local machine.

Django and Celery (will be installed from requirements.txt).

Setup Instructions
Clone the repository:

git clone [your-repository-url]
cd w2_service

Create a Python virtual environment:

python -m venv myvenv

Activate the virtual environment:

. myvenv\Scripts\activate

Install project dependencies:
using single cmd: 
  pip install -r requirements.txt
or install one by one below: 
pip install Django
pip install djangorestframework
pip install celery
pip install redis
pip install PyPDF2

Run database migrations:

python manage.py makemigrations reports
python manage.py migrate

Start the Redis server. Ensure it is running on the default port (6379).

Start the Celery worker:
Open a new terminal window or tab, activate the virtual environment, and run the following command from the project's root directory:

celery -A w2_service worker --loglevel=info --pool=solo

Start the Django development server:
In your original terminal, run the following from the project's root directory:

python manage.py runserver

How to Test the Workflow
Once both the Django server and the Celery worker are running, you can test the entire asynchronous workflow by uploading a mock PDF file using curl.

From a new terminal, run the following command:

curl.exe -X POST "http://localhost:8000/api/w2/upload/" -H "Content-Type: multipart/form-data" -H "X-API-Key: FinPro-Secret-Key" -F "file=@D:\Django_projects\w2_service\sample_w2.pdf"
Success response : 

#for example :(myvenv) PS D:\Django_projects\w2_service> curl.exe -X POST "http://localhost:8000/api/w2/upload/" -H "Content-Type: multipart/form-data" -F "file=@D:\Django_projects\w2_service\sample_w2.pdf"

NOTE: You may need to update the file path in the -F flag to match the location of the sample_w2.pdf file on your machine.
file=@D:\Django_projects\w2_service\sample_w2.pdf" # path to upload pdf file from your machine kept the sample_w2.pdf in project folder as mentioned in example

If the process is successful, you will see a 201 Created response in the curl terminal, and the logs from both your Django server and Celery worker will show the following sequence:
The server receives the initial upload request.
The Celery worker receives the process_w2_form_task.
The worker logs the data being successfully sent to the mock API.
The worker receives the upload_pdf_file_task from the callback.
The worker logs the file being successfully uploaded to the mock API.
Both tasks report as succeeded in the Celery logs.
Celery response will be as follows: (successfull)
[2025-09-15 13:01:58,362: INFO/MainProcess] celery@LAPTOP-5OP5344D ready.
[2025-09-15 13:02:14,412: INFO/MainProcess] Task reports.tasks.process_w2_form_task[e8bb409f-177f-4322-9fb4-c6fd30ddca01] received
[2025-09-15 13:02:14,414: WARNING/MainProcess] -----------------------Celery task trying-------------------------
[2025-09-15 13:02:14,414: WARNING/MainProcess] ----------------------->pdf file processing starts<-------------------------
[2025-09-15 13:02:14,419: WARNING/MainProcess] filepath--->D:\Django_projects\w2_service\media\w2_pdfs\sample_w2.pdf
[2025-09-15 13:02:16,536: WARNING/MainProcess] Successfully sent data for report_id: 29 to third-party API. Report status: SENT_TO_THIRD_PARTY
[2025-09-15 13:02:16,735: INFO/MainProcess] Task reports.tasks.process_w2_form_task[e8bb409f-177f-4322-9fb4-c6fd30ddca01] succeeded in 2.3289999999979045s: 'Successfully processed report_id: 29 and sent data to third-party API.'
[2025-09-15 13:02:16,738: INFO/MainProcess] Task reports.tasks.upload_pdf_file_task[1a0c5a64-2136-4b66-b160-ce4969d6bd14] received
[2025-09-15 13:02:18,825: WARNING/MainProcess] Successfully uploaded PDF for report 29 to third-party API. file_id:81096829-499f-40bb-98a9-b03b1508591f, Report status: COMPLETED
[2025-09-15 13:02:19,022: INFO/MainProcess] Task reports.tasks.upload_pdf_file_task[1a0c5a64-2136-4b66-b160-ce4969d6bd14] succeeded in 2.2810000000026776s: 'Successfully uploaded PDF for report_id: 29, file_id: 81096829-499f-40bb-98a9-b03b1508591f'

To see Report in UI: 
http://127.0.0.1:8000/admin/reports/w2report/



