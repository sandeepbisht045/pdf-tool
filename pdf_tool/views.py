from django.shortcuts import render
from django.http import HttpResponse
import PyPDF2,filetype,base64
from io import BytesIO


def protect_pdf_with_password(file, password):
    pdf_reader = PyPDF2.PdfReader(file)
    if pdf_reader.is_encrypted:
        return 'already_protected'
    pdf_writer = PyPDF2.PdfWriter()
    for page_num in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_num]
        pdf_writer.add_page(page)

    pdf_writer.encrypt(password)

    output_pdf = BytesIO()
    pdf_writer.write(output_pdf)
    output_pdf.seek(0)
    return output_pdf

def remove_password_from_pdf(file, password):
    pdf_reader = PyPDF2.PdfReader(file)
    if pdf_reader.is_encrypted:
        try:
            pdf_reader.decrypt(password)
        except:
            return 'wrong_password'
    else:
        return 'already_unlocked'

    pdf_writer = PyPDF2.PdfWriter()

    for page_number in range(len(pdf_reader.pages)):
        page = pdf_reader.pages[page_number]
        pdf_writer.add_page(page)

    output_pdf = BytesIO()
    pdf_writer.write(output_pdf)
    output_pdf.seek(0)
    return output_pdf

def pdf_tool(request):
    if request.method == 'POST':
        file = request.FILES['import']
        file_info = filetype.guess(file.read())
        
        if file_info is None or file_info.mime != 'application/pdf':
            return render(request,"index.html",{'info':'invalid_format'})
        protect_unlock = request.POST.get('protect_unlock')
        password = request.POST.get('password')
        if protect_unlock == "protect":
            type_ ='protect'
            protected_file = protect_pdf_with_password(file, password)
            if protected_file == 'already_protected':
                return render(request,"index.html",{'info':'PDF is already protected','type':type_})

            response = HttpResponse(content_type='application/pdf')
            file_name = f'protected_{file.name}'
            response.write(protected_file.getvalue())
        else:
            type_ ='unlock'
            try:
                unprotected_file = remove_password_from_pdf(file, password)
            except:
                return render(request,"index.html",{'info':'Incorrect Password provided','type':type_})

            if unprotected_file == 'already_unlocked':
                return render(request,"index.html",{'info':'PDF is already unlocked','type':type_})

            response = HttpResponse(content_type='application/pdf')
            file_name = f'unlocked_{file.name}'
            response.write(unprotected_file.getvalue())
        
        pdf_content_base64 = base64.b64encode(response.content).decode('utf-8')

        return render(request,"index.html",{'pdf_content': pdf_content_base64, 'success': 'success','file_name':file_name,'type':type_})


    return render(request, 'index.html')
