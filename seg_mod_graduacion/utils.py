from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
  
    result = BytesIO()
    
    
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
   
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    
    
    return None




from .models import RepositorioTitulados  

def transferir_datos_a_repositorio(estudiante, acta, modalidad, fecha, periodo, nota, tutor, jurado_1, jurado_2, jurado_3):
   
    RepositorioTitulados.objects.update_or_create(
        estudiante=estudiante,  
        defaults={
            'numero_acta': acta,
            'modalidad': modalidad,
            'fecha': fecha,
            'periodo': periodo,
            'nota_aprobacion': nota,
            'tutor': tutor,
            'jurado_1': jurado_1,
            'jurado_2': jurado_2,
            'jurado_3': jurado_3,
            'habilitada': True,  
            'estado': 'Aprobado',  
            'guia_externo': 'Ninguno', 
            
        }
    )
    
def transferir_datos_via(estudiante, acta,  titulo, modalidad, fecha, periodo, nota, jurado_1, jurado_2, jurado_3):
   
    RepositorioTitulados.objects.update_or_create(
        estudiante=estudiante,  
        defaults={
            'numero_acta': acta,
            'titulo': titulo,
            'modalidad': modalidad,
            'fecha': fecha,
            'periodo': periodo,
            'nota_aprobacion': nota,
            'jurado_1': jurado_1,
            'jurado_2': jurado_2,
            'jurado_3': jurado_3,
            'habilitada': True,  
            'estado': 'Aprobado',  
            'guia_externo': 'Ninguno', 
            
        }
    )

def transferir_datos_grado(estudiante, acta, modalidad, fecha, periodo, nota, jurado_1, jurado_2, jurado_3):
   
    RepositorioTitulados.objects.update_or_create(
        estudiante=estudiante,  
        defaults={
            'numero_acta': acta,
            'modalidad': modalidad,
            'fecha': fecha,
            'periodo': periodo,
            'nota_aprobacion': nota,
            'jurado_1': jurado_1,
            'jurado_2': jurado_2,
            'jurado_3': jurado_3,
            'habilitada': True,  
            'estado': 'Aprobado',  
            'guia_externo': 'Ninguno', 
            
        }
    )