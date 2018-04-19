import os
from io import BytesIO
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .lib.rinf_validator.validator import RINFValidator, RINFValidationException
from .lib.rinf_to_sql import rinf_to_sql
from .lib.rinf_to_sql.rinf_to_postgres import RINFExtractor,RINFExtractorConfig  
from .models import Document
from .forms import DocumentForm


def home(request):
    documents = Document.objects.all()
    return render(request, 'home.html', { 'documents': documents })


def model_form_upload(request):
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
        if form.is_valid():
            validator = RINFValidator()
            xml = request.FILES['document'].read().decode('utf-8')

            if validator.validate(xml):               
                new_document = form.save()
                input_file = request.FILES['document'].open()
                config = RINFExtractorConfig(
                    'localhost',
                    '5433',
                    'postgres',
                    '12345678',
                    'xmlexporter'
                )
                rinf_extractor = RINFExtractor(config)
                rinf_extractor.parse_xml(input_file)
                rinf_extractor.close()                  
            else:
                with open('debug.xml', 'w') as f:
                    f.write(xml)
                raise RINFValidationException('file failed RINF validation!')                
                
    else:
        form = DocumentForm()
    return render(request, 'model_form_upload.html', {
        'form': form
    })
