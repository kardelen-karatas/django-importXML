import os
from io import BytesIO
from django.shortcuts import render, redirect
from django.conf import settings
from django.core.files.storage import FileSystemStorage
from .lib.rinf_validator.validator import RINFValidator, RINFValidationException
from .lib.rinf_to_sql import rinf_to_sql
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
                config = rinf_to_sql.init_config(
                    input_file=request.FILES['document'].open(),
                    output_dir= os.path.join(settings.RINF_FILE_DIR, str(new_document.id)),
                    create_dir=True
                )
                rinf_to_sql.extract_data(config)
                return redirect('home')                    

            else:
                with open('debug.xml', 'w') as f:
                    f.write(xml)
                raise RINFValidationException('file failed RINF validation!')                
                
    else:
        form = DocumentForm()
    return render(request, 'model_form_upload.html', {
        'form': form
    })
