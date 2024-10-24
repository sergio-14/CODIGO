from io import BytesIO
from django.http import HttpResponse
from django.template.loader import get_template
from xhtml2pdf import pisa

def render_pdf(template_src, context_dict={}):
    template = get_template(template_src)
    html = template.render(context_dict)
    
    # Definir 'result' como un objeto BytesIO
    result = BytesIO()
    
    # Generar el PDF utilizando UTF-8
    pdf = pisa.pisaDocument(BytesIO(html.encode("UTF-8")), result)
    
    # Si no hay errores, devolver el PDF como respuesta HTTP
    if not pdf.err:
        return HttpResponse(result.getvalue(), content_type='application/pdf')
    
    # En caso de error, devolver None o un mensaje de error
    return None




from .models import RepositorioTitulados  # Importa tu modelo RepositorioTitulados

def transferir_datos_a_repositorio(estudiante, acta, modalidad, fecha, periodo, nota, tutor, jurado_1, jurado_2, jurado_3):
    # Crear o actualizar la instancia de RepositorioTitulados usando estudiante como criterio único
    RepositorioTitulados.objects.update_or_create(
        estudiante=estudiante,  # Usamos 'estudiante' como criterio único
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
    # Crear o actualizar la instancia de RepositorioTitulados usando estudiante como criterio único
    RepositorioTitulados.objects.update_or_create(
        estudiante=estudiante,  # Usamos 'estudiante' como criterio único
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