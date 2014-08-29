import xlrd, csv, os.path, dg.settings, StringIO, zipfile, person
from django.views.decorators.csrf import csrf_protect
from django.shortcuts import render_to_response
from django.core.mail import EmailMultiAlternatives
from django.template import RequestContext
from django.http import  HttpResponse
from django.core.management import setup_environ
setup_environ(dg.settings)
from django.contrib.auth.decorators import login_required, user_passes_test
from dg.settings import PERMISSION_DENIED_URL
from django.contrib.auth.models import User
from django.contrib import messages

from xl_import.models import Document
from xl_import.forms import DocumentForm
from geographies.models import  Block
from coco.models import CocoUser

@login_required()
@user_passes_test(lambda u: u.groups.filter(name='CoCo User').count() > 0, login_url=PERMISSION_DENIED_URL)
@csrf_protect

def home(request):# home page 
    form = DocumentForm(request.POST, request.FILES)
    user_id= User.objects.get(username=request.user.username).id
    blocks = CocoUser.objects.filter(user__id=user_id).values_list('villages__block__block_name').distinct() 
    block_names=[]
    for block in blocks:
        block_names.append(str(block[0]))
    return render_to_response(
        'xl_import/netupload.html',
       {'form': form, 'blocks':block_names},
        context_instance=RequestContext(request)
        )
   
def file_upload(request):# Handle file upload
    
    ext_allwd = ['.xls', '.xlsx']
    
    user_id= User.objects.get(username=request.user.username).id
    block_id = Block.objects.get(block_name=request.POST.get("get_block")).id
    
    if request.method == 'POST':
        form = DocumentForm(request.POST, request.FILES)
       
        if form.is_valid():
            
            document = Document(docfile=request.FILES['docfile'])
            
            if (os.path.splitext(document.docfile.name)[1] in ext_allwd):
                document.save()
                converted_document = file_converter(document)
               # messages.add_message(request, messages.INFO, '')                        
                person.add_person(converted_document.name,user_id,block_id)
                         
            elif (os.path.splitext(document.docfile.name)[1] == '.csv'):
                document.save()
                #messages.add_message(request, messages.INFO, 'File is being uploaded, this may take few minutes. Please do not refresh or send another upload request. you will be automatically redirected to another page')
                person.add_person(document.docfile.name,user_id,block_id)
                     
    else:
        form = DocumentForm()  # A empty, unbound form

    if (person.error > 0):
            csv_data = csv_to_html()
            send_mail(request)
            return render_to_response("xl_import/error.html", {'csv_data' : csv_data},
                                  context_instance=RequestContext(request)
                                  )
    else :
            send_mail(request)
            return render_to_response(
                                      'xl_import/success.html',
       
                                      context_instance=RequestContext(request)
                                      )
    
    
def file_converter(document): #converts .xls and .xlsx files to .csv
    try:
        
        document_docfile_name = os.path.join(dg.settings.MEDIA_ROOT, document.docfile.name)

        
        wb = xlrd.open_workbook(document_docfile_name)
        sh = wb.sheet_by_name('Sheet1')
        
        converted_csv_file = open(os.path.splitext(document_docfile_name)[0] +'.csv', 'wb') #saves .csv file with uploaded file name
        
        wr = csv.writer(converted_csv_file, quoting=csv.QUOTE_MINIMAL)# write into .csv file row wise
        for rownum in xrange(sh.nrows):
            wr.writerow(sh.row_values(rownum))

        os.remove(document_docfile_name) #delete the old document
        
        return converted_csv_file

    except Exception, err:
        print err
        
        
def handle_zip_download(request):
    
    buffer= StringIO.StringIO()
    zip_subdir = "error_files"
    zip_filename = "%s.zip" % zip_subdir
    
    zip_file= zipfile.ZipFile( buffer, "w" )
    
    for f in person.error_filenames:
        file = os.path.join(dg.settings.MEDIA_ROOT+r'documents/', f)
        zip_path = os.path.join(str(zip_subdir), str(file)).split('/')[-1]
        zip_file.write(file, zip_path) #Add files to zip
        
    zip_file.close() 
       
    del person.error_filenames[:] #empty the list of files 
    resp = HttpResponse(buffer.getvalue(), mimetype = "application/x-zip-compressed")
    resp['Content-Disposition'] = 'attachment; filename=%s' % zip_filename
    return resp
    
def csv_to_html():
    # enter success file datas from village, shg and person into each list in list of lists
    csv_data = [[] for i in range(3)]
    
    i = 0
    for file in person.success_filenames:
        if i < 3:
            file = os.path.join(dg.settings.MEDIA_ROOT+r'documents/', file)
            
            csv_reader = csv.reader(open(file))
            row_num = 0
            for x in csv_data:
                for row in csv_reader:
                    for column in row:
                        csv_data[i].append(column)
                       
            row_num += 1
            i +=1 
    del person.success_filenames[:]   
    return csv_data

def send_mail(request):
    document = Document(docfile=request.FILES['docfile'])
    subject = 'Status of uploaded file: '+document.docfile.name
    if person.error < 1:
        body = 'All the data in uploaded file has been successfully entered'
    else:
        body = 'Some of the data in uploaded file could not be entered. Please find the attachment containing the error files '
    
    from_email = dg.settings.EMAIL_HOST_USER
    to_email = [request.POST.get("email_id")]
    msg = EmailMultiAlternatives(subject, body, from_email, to_email)
    for file in person.error_filenames:
        file = os.path.join(dg.settings.MEDIA_ROOT+r'documents/', file)
        msg.attach_file(file, 'text/csv' )
    msg.send()
    
    

 
