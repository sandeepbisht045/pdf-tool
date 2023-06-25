from django.shortcuts import render
from django.http import HttpResponse
import PyPDF2,filetype
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
        print(file.name)
        file_info = filetype.guess(file.read())
        
        if file_info is None or file_info.mime != 'application/pdf':
            return render(request,"index.html",{'info':'invalid_format'})
        protect_unlock = request.POST.get('protect_unlock')
        password = request.POST.get('password')
        if protect_unlock == "protect":
            protected_file = protect_pdf_with_password(file, password)
            if protected_file == 'already_protected':
                return render(request,"index.html",{'info':'PDF is already protected'})

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] = f'attachment; filename="protected_{file.name}"'
            response['X-Info'] = 'Protected PDF Success'
            response.write(protected_file.getvalue())
        else:
            try:
                unprotected_file = remove_password_from_pdf(file, password)
            except:
                return render(request,"index.html",{'info':'Incorrect Password provided'})

            if unprotected_file == 'already_unlocked':
                return render(request,"index.html",{'info':'PDF is already unlocked'})

            response = HttpResponse(content_type='application/pdf')
            response['Content-Disposition'] =  f'attachment; filename="protected_{file.name}"'
            response['X-Info'] = 'Unlocked PDF Success'
            response.write(unprotected_file.getvalue())
        return response

    return render(request, 'index.html')
