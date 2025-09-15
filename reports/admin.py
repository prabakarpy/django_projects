from django.contrib import admin
from .models import W2Report

@admin.register(W2Report)
class W2ReportAdmin(admin.ModelAdmin):
    """
    Django Admin configuration for the W2Report model.
    """
    list_display = ('id', 'ein', 'ssn', 'wages', 'federal_tax_withheld', 'pdf_file', 'third_party_report_id', 'file_size', 'report_status', 'created_at')
    list_filter = ('report_status', 'created_at')
    search_fields = ('id', 'ein', 'ssn')
    readonly_fields = ('id', 'created_at')


