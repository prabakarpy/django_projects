import uuid
from django.db import models

class W2Report(models.Model):
    id = models.AutoField(primary_key=True)
    ein = models.CharField(max_length=15, blank=True, null=True)
    ssn = models.CharField(max_length=15, blank=True, null=True)
    wages = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    federal_tax_withheld = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    pdf_file = models.FileField(upload_to='w2_pdfs/')
    report_status = models.CharField(max_length=50, default='RECEIVED')
    third_party_report_id = models.UUIDField(default=uuid.uuid4, editable=False)
    file_size = models.IntegerField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        if self.ssn:
            return f"W-2 Report for SSN ending in {self.ssn[-4:]}"
        return f"W-2 Report with ID {self.id}"