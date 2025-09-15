from rest_framework import serializers
from .models import W2Report

'''
class W2ReportSerializer(serializers.ModelSerializer):
    class Meta:
        model = W2Report
        fields = ['id', 'ein', 'ssn', 'wages', 'federal_tax_withheld', 'report_status']
        read_only_fields = ['id', 'report_status', 'ein', 'ssn', 'wages', 'federal_tax_withheld']
'''
class W2FileUploadSerializer(serializers.Serializer):
    file = serializers.FileField(help_text="W-2 PDF file.")