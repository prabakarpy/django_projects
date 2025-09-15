Project Setup and Installation
Create and activate the virtual environment:

For Windows Command Prompt or PowerShell:

python -m venv myvenv
myvenv\Scripts\activate

For Windows Subsystem for Linux (WSL):

python -m venv myvenv
source myvenv/bin/activate

Install project dependencies:
using single cmd: pip install -r requirements.txt
or install one by one below: 
pip install Django
pip install djangorestframework
pip install celery
pip install redis
pip install PyPDF2

Database and Migrations
Initial database migrations (first run):

python manage.py makemigrations reports
python manage.py migrate

python manage.py createsuperuser
provide superuser and password

Running the Project
Start the Django development server:

python manage.py runserver

Start the Celery worker to process tasks:

celery -A w2_service worker --loglevel=info --pool=solo


Install WSL:
Open PowerShell as an administrator and run:

Bash

wsl --install
This will install WSL and a default Linux distribution (usually Ubuntu). You may need to reboot your computer.


open new bash(terminal) to run WSL(ubuntu) for redis:
make sure to activate virtual env or myvenv prefix available in terminal: 
sudo apt update
sudo apt install redis-server
wsl
sudo service redis-server start
sudo service redis-server status

to Run the service (in new terminal): 
curl.exe -X POST "http://localhost:8000/api/w2/upload/" -H "Content-Type: multipart/form-data" -F "file=@D:\Django_projects\w2_service\sample_w2.pdf"

#for example :(myvenv) PS D:\Django_projects\w2_service> curl.exe -X POST "http://localhost:8000/api/w2/upload/" -H "Content-Type: multipart/form-data" -F "file=@D:\Django_projects\w2_service\sample_w2.pdf"

file=@D:\Django_projects\w2_service\sample_w2.pdf" # path to upload pdf file from your machine kept the sample_w2.pdf in project folder as mentioned in example

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

