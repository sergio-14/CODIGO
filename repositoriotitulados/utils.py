from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    
    # Definir 'result' como un objeto BytesIO
    result = BytesIO()
    
    # Generar el PDF
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    # Si no hay errores, devolver el PDF como respuesta HTTP
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    
    # En caso de error, devolver None o un mensaje de error
    return None