from django.shortcuts import render
from seg_mod_graduacion.models import RepositorioTitulados, Estudiante, ProyectoFinal, Modalidad, ActaPublica,Periodo

from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils.text import slugify
from django.core.paginator import Paginator, PageNotAnInteger, EmptyPage
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied

from django.urls import reverse
from .forms import TransferirActividadForm, ActividadRepositorioForm

from django.http import HttpResponse
from .utils import render_pdf

#Repositorio publico
from .forms import ActividadFilterForm, AgregarForm
from django.db.models import Q

def permiso_M_G(user, group_name='ADMMGS'):
    if user.is_superuser:
        return True
    elif user.groups.filter(name=group_name).exists():
        return True
    else:
        raise PermissionDenied(f"El usuario no pertenece al grupo '{group_name}' y no es superusuario.")
    
def handle_permission_denied(request, exception):
    return render(request, '403.html', status=403)

class TransferirActividadView(View):
    
    def get(self, request, actividad_id):
      
        actividad = get_object_or_404(ProyectoFinal, id=actividad_id, estado='Aprobado')
     
        ultimo_acta = ActaPublica.objects.filter(estudiante=actividad.estudiante).order_by('-id').first()
        
        if ultimo_acta:
            estudiante = ultimo_acta.estudiante  
            form = TransferirActividadForm(estudiante=estudiante)  
        else:
            form = TransferirActividadForm()  
        
        ultimos_periodos = Periodo.objects.all().order_by('-gestion__anio', '-numero')[:4]
        
        return render(request, 'admrepositorio/transferir_actividad.html', {
            'form': form, 
            'actividad': actividad,
            'ultimos_periodos': ultimos_periodos  
        })
    
    def post(self, request, actividad_id):
        actividad = get_object_or_404(ProyectoFinal, id=actividad_id, estado='Aprobado')
        
     
        ultimo_acta = ActaPublica.objects.filter(estudiante=actividad.estudiante).order_by('-id').first()
        
    
        estudiante = ultimo_acta.estudiante if ultimo_acta else None  
        form = TransferirActividadForm(request.POST, estudiante=estudiante)  
        
        if form.is_valid():
            numero_acta = form.cleaned_data['numero_acta']
            nota_aprobacion = form.cleaned_data['nota_aprobacion']
            actividad.transferir_a_repositorio(
                form.cleaned_data['periodo'],  
                numero_acta,
                nota_aprobacion
            )
            return redirect('listarepositorios')
        
        ultimos_periodos = Periodo.objects.all().order_by('-gestion__anio', '-numero')[:4]
        
        return render(request, 'admrepositorio/transferir_actividad.html', {
            'form': form,
            'actividad': actividad,
            'ultimos_periodos': ultimos_periodos  
        })
        
        
@user_passes_test(lambda u: permiso_M_G(u, 'ADMMGS'))
def listaractividadesaprovadas(request):
    repositorios_existentes = RepositorioTitulados.objects.values_list('estudiante_id', flat=True)
    actividades_aprobadas = ProyectoFinal.objects.filter(
        estado='Aprobado'
    ).exclude(
        estudiante_id__in=repositorios_existentes
    )
    return render(request, 'admrepositorio/listaractividadesaprovadas.html', {'actividades_aprobadas': actividades_aprobadas})

def editar_actividad_repositorio(request, pk):
    actividad = get_object_or_404(RepositorioTitulados, pk=pk)
    ultimos_periodos = Periodo.objects.all().order_by('-gestion__anio', '-numero')[:4]
    
    if request.method == 'POST':
        form = ActividadRepositorioForm(request.POST, request.FILES, instance=actividad)  # Incluye request.FILES
        if form.is_valid():
            form.save()
            return redirect('listarepositorios')
    else:
        form = ActividadRepositorioForm(instance=actividad)
    
    return render(request, 'admrepositorio/editar_actividad_repositorio.html', {
        'form': form, 
        'actividad': actividad,
        'ultimos_periodos': ultimos_periodos 
    })


def actividad_list(request):
    actividades = RepositorioTitulados.objects.all()
    form = ActividadFilterForm(request.GET)

    if form.is_valid():
        nombre_completo = form.cleaned_data.get('nombre_completo')
        modalidad = form.cleaned_data.get('modalidad')
        periodo_str = form.cleaned_data.get('periodo')

       
        if nombre_completo:
            nombres = nombre_completo.split()
            if len(nombres) == 2:
                nombre, apellido = nombres
                actividades = actividades.filter(
                    Q(estudiante__nombre__icontains=nombre) & 
                    Q(estudiante__apellido__icontains=apellido) |
                    Q(estudiante_uno__nombre__icontains=nombre) & 
                    Q(estudiante_uno__apellido__icontains=apellido)
                )
            else:
                actividades = actividades.filter(
                    Q(estudiante__nombre__icontains=nombre_completo) |
                    Q(estudiante__apellido__icontains=nombre_completo) |
                    Q(estudiante_uno__nombre__icontains=nombre_completo) |
                    Q(estudiante_uno__apellido__icontains=nombre_completo) 
                )
        
        
        if modalidad:
            actividades = actividades.filter(modalidad=modalidad)
      
        if periodo_str:
            try:
              
                numero, gestion_anio = map(int, periodo_str.split('/'))
                actividades = actividades.filter(periodo__numero=numero, periodo__gestion__anio=gestion_anio)
            except ValueError:
               
                pass  
    paginator = Paginator(actividades, 15)  
    page_number = request.GET.get('page')
    try:
        actividades_paginated = paginator.page(page_number)
    except PageNotAnInteger:
        actividades_paginated = paginator.page(1)
    except EmptyPage:
        actividades_paginated = paginator.page(paginator.num_pages)

    return render(request, 'repositoriopublico/actividad_list.html', {'form': form, 'actividades': actividades_paginated})

def agregar_actividad_repositorio(request):
    ultimos_periodos = Periodo.objects.all().order_by('-gestion__anio', '-numero')[:4]
    if request.method == 'POST':
        form = AgregarForm(request.POST, request.FILES)
        if form.is_valid():
            form.save()
            return redirect(reverse('listarepositorios'))
        else:
            print(form.errors)
    else:
        form = AgregarForm()
    
    return render(request, 'admrepositorio/agregar_actividad_repositorio.html', {
        'form': form,
        'ultimos_periodos': ultimos_periodos 
        })



def listarepositorios(request):
    query = request.GET.get('q', '').strip()
    modalidad_id = request.GET.get('modalidad', None)

    actividades_repositorio = RepositorioTitulados.objects.all()

    if query:
        actividades_repositorio = actividades_repositorio.annotate(
            estudiante_completo=Concat('estudiante__nombre', Value(' '), 'estudiante__apellido'),
            estudiante_uno_completo=Concat('estudiante_uno__nombre', Value(' '), 'estudiante_uno__apellido')
        ).filter(
            Q(estudiante_completo__icontains=query) |
            Q(estudiante_uno_completo__icontains=query)
        )

    if modalidad_id and modalidad_id.isdigit():
        actividades_repositorio = actividades_repositorio.filter(modalidad__id=int(modalidad_id))

    actividades_repositorio = actividades_repositorio.order_by('-id')
    paginator = Paginator(actividades_repositorio, 4)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    modalidades = Modalidad.objects.all()

    context = {
        'page_obj': page_obj,
        'query': query,
        'modalidad': modalidad_id,
        'modalidades': modalidades,
    }
    return render(request, 'admrepositorio/listarepositorios.html', context)


class pdf_reporte_repositorio(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        modalidad_id = request.GET.get('modalidad', '').strip()

        actividades_repositorio = RepositorioTitulados.objects.all()

        if query:
            actividades_repositorio = actividades_repositorio.annotate(
                estudiante_completo=Concat('estudiante__nombre', Value(' '), 'estudiante__apellido'),
                estudiante_uno_completo=Concat('estudiante_uno__nombre', Value(' '), 'estudiante_uno__apellido')
            ).filter(
                Q(estudiante_completo__icontains=query) |
                Q(estudiante_uno_completo__icontains=query) 
            )

        if modalidad_id:
            try:
                modalidad_id = int(modalidad_id)
                actividades_repositorio = actividades_repositorio.filter(modalidad__id=modalidad_id)
            except ValueError:
                actividades_repositorio = RepositorioTitulados.objects.none()

        actividades_repositorio = actividades_repositorio.order_by('-id')
        data = {
            'actividades_repositorio': actividades_repositorio,
            'query': query,
            'modalidad_id': modalidad_id,
        }
        
        pdf = render_pdf('admrepositorio/pdf_reporte_repositorio.html', data)
        return HttpResponse(pdf, content_type='application/pdf')

    
from django.db.models import Q, Value
from django.db.models.functions import Concat
import openpyxl
from django.http import HttpResponse
from django.utils.timezone import make_naive, is_aware
from datetime import datetime

def exportar_excel_repositorios(request):
    query = request.GET.get('q', '').strip()
    modalidad_id = request.GET.get('modalidad', None)

    actividades_repositorio = RepositorioTitulados.objects.all()

    if query:
        actividades_repositorio = actividades_repositorio.annotate(
            estudiante_completo=Concat('estudiante__nombre', Value(' '), 'estudiante__apellido'),
            estudiante_uno_completo=Concat('estudiante_uno__nombre', Value(' '), 'estudiante_uno__apellido')
        ).filter(
            Q(estudiante_completo__icontains=query) |
            Q(estudiante_uno_completo__icontains=query)
        )

    if modalidad_id and modalidad_id.isdigit():
        actividades_repositorio = actividades_repositorio.filter(modalidad__id=int(modalidad_id))

    wb = openpyxl.Workbook()
    hoja = wb.active
    hoja.title = 'Reporte Repositorio Titulados'

    # Escribir los encabezados
    encabezados = [
        'ID', 
        '1er. Estudiante', 
        '2do. Estudiante', 
        'Tutor', 
        '1er. Tribunal', 
        '2do. Tribunal', 
        '3er. Tribunal', 
        'Título Proyecto', 
        'Descripción', 
        'Modalidad', 
        'Fecha de Creación', 
        'Tutor Externo', 
        'Estado', 
        'Periodo',
        'Gestión', 
        'Número de Acta', 
        'Nota'
    ]
    hoja.append(encabezados)

    datos = actividades_repositorio.annotate(
        estudiante_completo=Concat('estudiante__nombre', Value(' '), 'estudiante__apellido', Value(' '), 'estudiante__apellidoM'),
        estudiante_uno_completo=Concat('estudiante_uno__nombre', Value(' '), 'estudiante_uno__apellido', Value(' '), 'estudiante_uno__apellidoM'),
        tutor_completo=Concat('tutor__nombre', Value(' '), 'tutor__apellido', Value(' '), 'tutor__apellidoM'),
        jurado1_completo=Concat('jurado_1__nombre', Value(' '), 'jurado_1__apellido', Value(' '),  'jurado_1__apellidoM'),
        jurado2_completo=Concat('jurado_2__nombre', Value(' '), 'jurado_2__apellido', Value(' '),  'jurado_2__apellidoM'),
        jurado3_completo=Concat('jurado_3__nombre', Value(' '), 'jurado_3__apellido', Value(' '), 'jurado_3__apellidoM'),
    ).values_list(
        'id', 
        'estudiante_completo',  
        'estudiante_uno_completo',  
        'tutor_completo',  
        'jurado1_completo', 
        'jurado2_completo',  
        'jurado3_completo',   
        'titulo',  
        'resumen', 
        'modalidad__nombre', 
        'fecha',  
        'guia_externo',  
        'estado', 
        'periodo__numero',   
        'periodo__gestion__anio',
        'numero_acta',  
        'nota_aprobacion' 
    )

    datos_naive = []
    for dato in datos:
        dato_list = list(dato)
     
        for i, valor in enumerate(dato_list):
            if isinstance(valor, datetime) and is_aware(valor):
                dato_list[i] = make_naive(valor)
        datos_naive.append(dato_list)

    
    for dato in datos_naive:
        hoja.append(dato)

    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=repositorio_titulados.xlsx'

    wb.save(response)
    return response

