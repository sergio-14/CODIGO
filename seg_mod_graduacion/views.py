from django.contrib.auth.models import Group
from django.contrib.auth.decorators import login_required, user_passes_test
from django.shortcuts import render, redirect, get_object_or_404
from django.views import View
from django.utils.text import slugify
from django.core.paginator import Paginator
from django.contrib import messages
from django.utils.decorators import method_decorator
from django.core.exceptions import PermissionDenied

from .forms import InvCientificaForm, InvComentarioForm, GlobalSettingsForm, PerfilForm, PerComentarioForm, ActComentarioForm, ActaPerfilForm
from .models import Estudiante, InvCientifica, ComentarioInvCientifica, HabilitarSeguimiento, PerfilProyecto, ComentarioPerfil, ComentarioProFinal

##############  permisos decoradores  para funciones y clases   ################  

#modalidad de graduación permigroup 
def permiso_M_G(user, ADMMGS):
    try:
        grupo = Group.objects.get(name=ADMMGS)
    except Group.DoesNotExist:
        raise PermissionDenied(f"El grupo '{ADMMGS}' no existe.")
    
    if grupo in user.groups.all():
        return True
    else:
        raise PermissionDenied
    
#permiso para docentes  
def permiso_Docentes(user, Docentes):
    try:
        grupo = Group.objects.get(name=Docentes)
    except Group.DoesNotExist:
        raise PermissionDenied(f"El grupo '{Docentes}' no existe.")
    
    if grupo in user.groups.all():
        return True
    else:
        raise PermissionDenied

#permiso para estudiantes
def permiso_Estudiantes(user, Estudiantes):
    try:
        grupo = Group.objects.get(name=Estudiantes)
    except Group.DoesNotExist:
        raise PermissionDenied(f"El grupo '{Estudiantes}' no existe.")
    
    if grupo in user.groups.all():
        return True
    else:
        raise PermissionDenied
    
def permiso_I_S(user, ADMIIISP):
    try:
        grupo = Group.objects.get(name=ADMIIISP)
    except Group.DoesNotExist:
        raise PermissionDenied(f"El grupo '{ADMIIISP}' no existe.")
    
    if grupo in user.groups.all():
        return True
    else:
        raise PermissionDenied


#vista 403
def handle_permission_denied(request, exception):
    return render(request, '403.html', status=403)

################  vistas modalidad de graduación  ##########################

#vista agregar formulario alcance de proyecto 
@login_required
@user_passes_test(lambda u: permiso_Estudiantes(u, 'Estudiantes')) 
def vista_investigacion(request):
    proyectos_usuario = InvCientifica.objects.filter(
        Q(user=request.user) | 
        Q(user_uno=request.user) | 
        Q(user_dos=request.user)
    ).order_by('-invfecha_creacion').prefetch_related('comentarioinvcientifica_set')
    #proyectos_usuario = InvCientifica.objects.filter(user=request.user).order_by('-invfecha_creacion').prefetch_related('comentarioinvcientifica_set')

    paginator = Paginator(proyectos_usuario, 1)  
    page_number = request.GET.get('page')
    proyectos_paginados = paginator.get_page(page_number)

    return render(request, 'invcientifica/vista_investigacion.html', {'proyectos': proyectos_paginados})

@method_decorator(user_passes_test(lambda u: permiso_M_G(u, 'ADMIIISP')), name='dispatch')
class ProyectosParaAprobar(View):
    def get(self, request):
        # Filtra los proyectos pendientes
        proyectos = InvCientifica.objects.filter(investado='Pendiente')
        
        # Paginación: Muestra solo 1 proyecto por página
        paginator = Paginator(proyectos, 1)
        page_number = request.GET.get('page')
        proyectos_paginados = paginator.get_page(page_number)
        
        # Generar formulario para cada proyecto
        proyectos_con_formulario = {proyecto: InvComentarioForm() for proyecto in proyectos_paginados}
        
        # Contexto para renderizar en la plantilla
        context = {
            'proyectos': proyectos_con_formulario,
            'paginador': proyectos_paginados  # Se pasa el objeto paginado para control de navegación
        }
        
        return render(request, 'invcientifica/ProyectosParaAprobar.html', context)
    
    def post(self, request):
        proyecto_id = request.POST.get('proyecto_id')
        comentario_texto = request.POST.get('invcomentario')
        invdocorregido = request.FILES.get('invdocorregido')
        
        if proyecto_id and comentario_texto:
            proyecto = get_object_or_404(InvCientifica, pk=proyecto_id)
            comentario = ComentarioInvCientifica(
                invcomentario=comentario_texto,
                user=request.user,
                invproyecto_relacionado=proyecto,
                invdocorregido=invdocorregido
            )
            comentario.save()
            messages.success(request, 'Comentario agregado exitosamente.')
        else:
            messages.error(request, 'Hubo un error al agregar el comentario.')
            return redirect('ProyectosParaAprobar')
        
        if 'aprobar' in request.POST:
            return AprobarProyecto().post(request, proyecto_id)
        elif 'rechazar' in request.POST:
            return RechazarProyecto().post(request, proyecto_id)
        else:
            messages.error(request, 'Hubo un error al procesar la solicitud.')
            return redirect('ProyectosParaAprobar')
        

class AprobarProyecto(View):
    def post(self, request, proyecto_id):
        proyecto = get_object_or_404(InvCientifica, pk=proyecto_id)
        proyecto.investado = 'Aprobado'
        proyecto.save()
        messages.success(request, '¡Proyecto aprobado exitosamente!')
        return redirect('ProyectosParaAprobar')

class RechazarProyecto(View):
    def post(self, request, proyecto_id):
        proyecto = get_object_or_404(InvCientifica, pk=proyecto_id)
        proyecto.investado = 'Rechazado'
        proyecto.save()
        messages.error(request, '¡Proyecto rechazado!')
        return redirect('ProyectosParaAprobar')

#@user_passes_test(lambda u: permiso_M_G(u, 'ADMMGS')) 
def global_settings_view(request):
    settings = HabilitarSeguimiento.objects.first()
    if not settings:
        settings = HabilitarSeguimiento()

    if request.method == 'POST':
        form = GlobalSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = GlobalSettingsForm(instance=settings)
    
    return render(request, 'invcientifica/global_settings.html', {'form': form, 'settings': settings})

@login_required
@user_passes_test(lambda u: permiso_Estudiantes(u, 'Estudiantes')) 
def agregar_investigacion(request):
    settings = HabilitarSeguimiento.objects.first()

    if not settings:
        messages.error(request, 'No se encontró la configuración global. Por favor, contacta al administrador.')
        return redirect('global_settings')

    # Verifica si el usuario, user_uno o user_dos tienen una investigación aprobada
    tiene_investigacion_aprobada = InvCientifica.objects.filter(
        Q(user=request.user) | Q(user_uno=request.user) | Q(user_dos=request.user),
        investado='Aprobado'
        ).exists()
    # Deshabilitar el formulario si no está habilitado globalmente o si hay una investigación aprobada
    form_disabled = not settings.habilitarInv or tiene_investigacion_aprobada

    if request.method == 'POST' and not form_disabled:
        form = InvCientificaForm(request.POST, request.FILES, request=request)  # Pasa el request aquí
        if form.is_valid():
            proyecto = form.save(commit=False)

            # Generar slug único
            slug = slugify(proyecto.invtitulo)
            counter = 1
            while InvCientifica.objects.filter(slug=slug).exists():
                slug = f"{slug}-{counter}"
                counter += 1
            proyecto.slug = slug

            # Asignar el usuario autenticado al proyecto
            proyecto.user = request.user
            proyecto.save()
            return redirect('dashboard')
    else:
        form = InvCientificaForm(request=request)  # Pasa el request también aquí

    # Si el formulario está deshabilitado, deshabilita los campos
    if form_disabled:
        for field in form.fields.values():
            field.widget.attrs['disabled'] = 'disabled'

    return render(request, 'invcientifica/agregar_investigacion.html', {
        'form': form,
        'form_disabled': form_disabled,
    })
    
    
########  PERFIL DE PROYECTO M. G 2DA PARTE   #########
@login_required
@user_passes_test(lambda u: permiso_Estudiantes(u, 'Estudiantes')) 
def vista_perfil(request):
    proyectos_usuario = PerfilProyecto.objects.filter(
        Q(user=request.user) | 
        Q(user_uno=request.user) | 
        Q(user_dos=request.user)
    ).order_by('-perfecha_creacion').prefetch_related('comentarios')
    paginator = Paginator(proyectos_usuario, 1) 
    page_number = request.GET.get('page')
    proyectos_paginados = paginator.get_page(page_number)

    return render(request, 'perfil/vista_perfil.html', {'proyectos': proyectos_paginados})

@method_decorator(user_passes_test(lambda u: permiso_M_G(u, 'ADMIIISP')), name='dispatch')
class PerfilesParaAprobar(View):
    def get(self, request):
        proyectos = PerfilProyecto.objects.filter(perestado='Pendiente')
        
        # Paginación: Muestra solo 1 proyecto por página
        paginator = Paginator(proyectos, 1)
        page_number = request.GET.get('page')
        proyectos_paginados = paginator.get_page(page_number)
        
        proyectos = PerfilProyecto.objects.filter(perestado='Pendiente')
        proyectos_con_formulario = {proyecto: PerComentarioForm() for proyecto in proyectos_paginados}
        
        context = {
            'proyectos': proyectos_con_formulario,
            'paginador': proyectos_paginados 
        }
        return render(request, 'perfil/PerfilesParaAprobar.html', context)
    
    def post(self, request):
        proyecto_id = request.POST.get('proyecto_id')
        comentario_texto = request.POST.get('comentario_texto')
        perdocorregido = request.FILES.get('perdocorregido')
        if proyecto_id and comentario_texto:
            proyecto = get_object_or_404(PerfilProyecto, pk=proyecto_id)
            ComentarioPerfil.objects.create(
                percomentario=comentario_texto, 
                user=request.user, 
                perproyecto_relacionado=proyecto,
                perdocorregido=perdocorregido
                )
            messages.success(request, 'Comentario agregado exitosamente.')
        else:
            messages.error(request, 'Hubo un error al agregar el comentario.')
        
        if 'aprobar' in request.POST:
            return AprobarPerfil().post(request, proyecto_id)
        elif 'rechazar' in request.POST:
            return RechazarPerfil().post(request, proyecto_id)
        else:
            messages.error(request, 'Hubo un error al procesar la solicitud.')
            return redirect('PerfilesParaAprobar')
    
class AprobarPerfil(View):
    def post(self, request, proyecto_id):
        proyecto = get_object_or_404(PerfilProyecto, pk=proyecto_id)
        proyecto.perestado = 'Aprobado'
        proyecto.save()
        messages.success(request, '¡Perfil aprobado exitosamente!')
        return redirect('PerfilesParaAprobar')

class RechazarPerfil(View):
    def post(self, request, proyecto_id):
        proyecto = get_object_or_404(PerfilProyecto, pk=proyecto_id)
        proyecto.perestado = 'Rechazado'
        proyecto.save()
        messages.error(request, '¡Perfil rechazado!')
        return redirect('PerfilesParaAprobar')

@user_passes_test(lambda u: permiso_Estudiantes(u, 'Estudiantes'))
def agregar_perfil(request):
    # Verificar si el usuario autenticado tiene una investigación aprobada como 'user', 'user_uno' o 'user_dos'
    tiene_investigacion_aprobada = InvCientifica.objects.filter(
        Q(user=request.user) | Q(user_uno=request.user) | Q(user_dos=request.user),
        investado='Aprobado'
        ).exists()
    # Verificar si el usuario tiene un perfil de proyecto aprobado
    
    tiene_perfil_aprobado = PerfilProyecto.objects.filter(
        Q(user=request.user) | Q(user_uno=request.user) | Q(user_dos=request.user),
        perestado='Aprobado'
        ).exists()
    # Deshabilitar el formulario si no tiene investigación aprobada o si tiene un perfil aprobado
    form_disabled = not tiene_investigacion_aprobada or tiene_perfil_aprobado

    if request.method == 'POST' and not form_disabled:
        formp = PerfilForm(request.POST, request.FILES, request=request)
        if formp.is_valid():
            proyecto = formp.save(commit=False)
            
            slug = slugify(proyecto.pertitulo)
            counter = 1
            while PerfilProyecto.objects.filter(slug=slug).exists():
                slug = f"{slug}-{counter}"
                counter += 1
            proyecto.slug = slug
            
            proyecto.user = request.user
            proyecto.save()
            return redirect('dashboard')
        else:
            print("Formulario no es válido:", formp.errors)
    else:
        formp = PerfilForm(request=request)

    if form_disabled:
        for field in formp.fields.values():
            field.widget.attrs['disabled'] = 'disabled'

    return render(request, 'perfil/agregar_perfil.html', {
        'formp': formp,
        'form_disabled': form_disabled,
    })
 
 
from django.template.loader import get_template
from xhtml2pdf import pisa   

from .models import Periodo

#### acta de perfil de proyecto #####
def agregar_actaperfil(request):
    # Obtener solo los dos últimos períodos ordenados por 'numero' y 'gestion__anio'
    ultimos_periodos = Periodo.objects.all().order_by('-gestion__anio','-numero')[:2]

    if request.method == 'POST':
        form = ActaPerfilForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Acta de perfil agregada exitosamente.')
            return redirect('actaperfil_list')  
    else:
        form = ActaPerfilForm()

    return render(request, 'actas/agregar_actaperfil.html', {
        'form': form,
        'ultimos_periodos': ultimos_periodos  # Agregar los períodos al contexto
    })

from .forms import ActaPrivadaForm ,ActaPublicaForm

def agregar_actaprivada(request):
    ultimos_periodos = Periodo.objects.all().order_by('-gestion__anio','-numero')[:2]

    if request.method == 'POST':
        form = ActaPrivadaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Acta agregada exitosamente.')
            return redirect('actaprivada_list') 
    else:
        form = ActaPrivadaForm()

    return render(request, 'actas/agregar_actaprivada.html', {
        'form': form,
        'ultimos_periodos': ultimos_periodos 
        })

from django.http import JsonResponse
from .models import ActaProyectoPerfil, ActaPrivada

def buscar_estudiante_privada(request):
    estudiante_id = request.GET.get('id', None)
    if estudiante_id:
        try:
            # Filtra por estudiante_id y resultado='Suficiente'
            acta_proyecto = ActaProyectoPerfil.objects.filter(
                estudiante_id=estudiante_id, 
                resultado='Suficiente'
            ).first()  # Obtén el primer resultado que cumpla la condición

            if acta_proyecto:
                data = {
                    'estudiante_uno': getattr(acta_proyecto.estudiante_uno, 'id', None),
                    'titulo': getattr(acta_proyecto.titulo, 'id', acta_proyecto.titulo) if acta_proyecto.acta else None,
                    'lugar': getattr(acta_proyecto.lugar, 'id', acta_proyecto.lugar) if acta_proyecto.acta else None,
                    'tutor': getattr(acta_proyecto.tutor, 'id', None),
                    'jurado_1': getattr(acta_proyecto.jurado_1, 'id', None),
                    'jurado_2': getattr(acta_proyecto.jurado_2, 'id', None),
                    'jurado_3': getattr(acta_proyecto.jurado_3, 'id', None),
                    'modalidad': getattr(acta_proyecto.modalidad, 'id', None),
                }
            else:
                data = {}
        except ActaProyectoPerfil.DoesNotExist:
            data = {}
    else:
        data = {}

    return JsonResponse(data)

def buscar_estudiante_publica(request):
    estudiante_id = request.GET.get('id', None)
    if estudiante_id:
        try:
            # Filtra por estudiante_id y resultado='Suficiente'
            acta_proyecto = ActaPrivada.objects.filter(
                estudiante_id=estudiante_id, 
                resultado='Suficiente'
            ).first()  # Obtén el primer resultado que cumpla la condición

            if acta_proyecto:
                data = {
                    'estudiante_uno': getattr(acta_proyecto.estudiante_uno, 'id', None),
                    'titulo': getattr(acta_proyecto.titulo, 'id', acta_proyecto.titulo) if acta_proyecto.acta else None,
                    'lugar': getattr(acta_proyecto.lugar, 'id', acta_proyecto.lugar) if acta_proyecto.acta else None,
                    'tutor': getattr(acta_proyecto.tutor, 'id', None),
                    'jurado_1': getattr(acta_proyecto.jurado_1, 'id', None),
                    'jurado_2': getattr(acta_proyecto.jurado_2, 'id', None),
                    'jurado_3': getattr(acta_proyecto.jurado_3, 'id', None),
                    'modalidad': getattr(acta_proyecto.modalidad, 'id', None),
                    'calificacion1': getattr(acta_proyecto.calificacion1, 'id', acta_proyecto.calificacion1) if acta_proyecto.acta else None,
                }
            else:
                data = {}
        except ActaPrivada.DoesNotExist:
            data = {}
    else:
        data = {}

    return JsonResponse(data)

def agregar_actapublica(request):
    ultimos_periodos = Periodo.objects.all().order_by('-gestion__anio','-numero')[:2]
    
    if request.method == 'POST':
        form = ActaPublicaForm(request.POST)
        if form.is_valid():
            form.save()
            messages.success(request, 'Acta agregada exitosamente.')
            return redirect('actapublica_list')  # Assuming you have a list view for actas
    else:
        form = ActaPublicaForm()

    return render(request, 'actas/agregar_actapublica.html', {
        'form': form,
        'ultimos_periodos': ultimos_periodos 
        })

from .models import ActaProyectoPerfil

def actaperfil_list(request):
    query = request.GET.get('q')  
    actas_list = ActaProyectoPerfil.objects.all().order_by('-id')

    if query:
        actas_list = actas_list.filter(
            Q(estudiante__nombre__icontains=query) |
            Q(estudiante__apellido__icontains=query)
        )

    paginator = Paginator(actas_list, 3) 
    page_number = request.GET.get('page')
    actas = paginator.get_page(page_number)
    
    return render(request, 'perfil/actaperfil_list.html', {'actas': actas, 'query': query})

class Pdf_ReporteActa(View):
    def get(self, request, *args, **kwargs):
        acta_id = self.kwargs.get('pk')  
        acta = get_object_or_404(ActaProyectoPerfil, pk=acta_id)  
        
        context = {
            'acta': acta,
            
        }
        
        # Generar el PDF
        pdf = render_pdf('reportes/Pdf_ReporteActa.html', context)
        
        # Retornar el PDF como respuesta
        return HttpResponse(pdf, content_type='application/pdf')
    
###########acta privada ###########################
def actaprivada_list(request):
    query = request.GET.get('q')  
    actas_list = ActaPrivada.objects.all().order_by('-id')

    if query:
        actas_list = actas_list.filter(
            Q(estudiante__nombre__icontains=query) |
            Q(estudiante__apellido__icontains=query)
        )

    paginator = Paginator(actas_list, 3) 
    page_number = request.GET.get('page')
    actas = paginator.get_page(page_number)
    
    return render(request, 'proyectofinal/actaprivada_list.html', {'actas': actas, 'query': query})

class Pdf_ReporteActaPrivada(View):
    def get(self, request, *args, **kwargs):
        acta_id = self.kwargs.get('pk')  # Obtener el id desde la URL
        acta = get_object_or_404(ActaPrivada, pk=acta_id)  # Recuperar la instancia ActaPerfil
        
        # Construir URLs absolutas para las firmas
        context = {
            'acta': acta,
        }
        
        # Generar el PDF
        pdf = render_pdf('reportes/Pdf_ReporteActaPrivada.html', context)
        
        # Retornar el PDF como respuesta
        return HttpResponse(pdf, content_type='application/pdf')
    

###########acta privada ###########################
def actapublica_list(request):
    query = request.GET.get('q')  
    actas_list = ActaPublica.objects.all().order_by('-id')

    if query:
        actas_list = actas_list.filter(
            Q(estudiante__nombre__icontains=query) |
            Q(estudiante__apellido__icontains=query)
        )

    paginator = Paginator(actas_list, 3) 
    page_number = request.GET.get('page')
    actas = paginator.get_page(page_number)
    
    return render(request, 'proyectofinal/actapublica_list.html', {'actas': actas, 'query': query})

class Pdf_ReporteActaPublica(View):
    def get(self, request, *args, **kwargs):
        acta_id = self.kwargs.get('pk')  
        acta = get_object_or_404(ActaPublica, pk=acta_id)  
        logo_url = request.build_absolute_uri('/static/img/logouab.png')
        context = {
            'acta': acta,
            'logo_url': logo_url,
            
        }
        
        # Generar el PDF
        pdf = render_pdf('reportes/Pdf_ReporteActaPublica.html', context)
        
        # Retornar el PDF como respuesta
        return HttpResponse(pdf, content_type='application/pdf')
  
  
from django.db import transaction   
from .forms import ActaViaDiplomadoForm
def agregar_viadiplomado(request):
    ultimos_periodos = Periodo.objects.all().order_by('-gestion__anio', '-numero')[:2]
    
    if request.method == 'POST':
        form = ActaViaDiplomadoForm(request.POST)
        if form.is_valid():
            try:
                acta = form.save(commit=True) 
                print(f"Instancia antes de guardar: {acta}")
                return redirect('actaviadiplomado_list')
            except Exception as e:
                print(f"Error al guardar la instancia: {e}")
        else:
            print(f"Errores del formulario: {form.errors}")
    else:
        form = ActaViaDiplomadoForm()

    return render(request, 'actas/agregar_viadiplomado.html', {
        'form': form,
        'ultimos_periodos': ultimos_periodos,
    })

class Pdf_ReporteActaViadiplomatico(View):
    def get(self, request, *args, **kwargs):
        acta_id = self.kwargs.get('pk')  
        acta = get_object_or_404(ActaViaDiplomado, pk=acta_id)  
        logo_url = request.build_absolute_uri('/static/img/logouab.png')
        logopg_url = request.build_absolute_uri('/static/img/pg.png')
        context = {
            'acta': acta,
            'logo_url': logo_url,
            'logopg_url': logopg_url,
            
        }
        
        # Generar el PDF
        pdf = render_pdf('reportes/Pdf_ReporteActaViadiplomatico.html', context)
        
        # Retornar el PDF como respuesta
        return HttpResponse(pdf, content_type='application/pdf')
  
    
from .models import ActaViaDiplomado
from .forms import ActaExcelenciaForm
def actaviadiplomado_list(request):
    query = request.GET.get('q')  
    actas_list = ActaViaDiplomado.objects.all().order_by('-id')

    if query:
        actas_list = actas_list.filter(
            Q(estudiante__nombre__icontains=query) |
            Q(estudiante__apellido__icontains=query)
        )

    paginator = Paginator(actas_list, 3) 
    page_number = request.GET.get('page')
    actas = paginator.get_page(page_number)
    
    return render(request, 'proyectofinal/actaviadiplomado_list.html', {'actas': actas, 'query': query})
    
def agregar_Excelencia(request):
    ultimos_periodos = Periodo.objects.all().order_by('-gestion__anio', '-numero')[:2]
    
    if request.method == 'POST':
        form = ActaExcelenciaForm(request.POST)
        if form.is_valid():
            try:
                acta = form.save(commit=True) 
                print(f"Instancia antes de guardar: {acta}")
                return redirect('actaexcelencia_list')
            except Exception as e:
                print(f"Error al guardar la instancia: {e}")
        else:
            print(f"Errores del formulario: {form.errors}")
    else:
        form = ActaExcelenciaForm()

    return render(request, 'actas/agregar_Excelencia.html', {
        'form': form,
        'ultimos_periodos': ultimos_periodos,
    })

from .models import ActaExcelencia
class Pdf_ReporteActaExcelencia(View):
    def get(self, request, *args, **kwargs):
        acta_id = self.kwargs.get('pk')  
        acta = get_object_or_404(ActaExcelencia, pk=acta_id)  
        logo_url = request.build_absolute_uri('/static/img/logouab.png')
        context = {
            'acta': acta,
            'logo_url': logo_url,
        }
        
        # Generar el PDF
        pdf = render_pdf('reportes/Pdf_ReporteActaExcelencia.html', context)
        
        # Retornar el PDF como respuesta
        return HttpResponse(pdf, content_type='application/pdf')
  
    
def actaexcelencia_list(request):
    query = request.GET.get('q')  
    actas_list = ActaExcelencia.objects.all().order_by('-id')

    if query:
        actas_list = actas_list.filter(
            Q(estudiante__nombre__icontains=query) |
            Q(estudiante__apellido__icontains=query)
        )

    paginator = Paginator(actas_list, 3) 
    page_number = request.GET.get('page')
    actas = paginator.get_page(page_number)
    
    return render(request, 'proyectofinal/actaexcelencia_list.html', {'actas': actas, 'query': query})
    
### VISTA PARA EL ESTUDIANTE ###
###############################################################

from .models import HabilitarProyectoFinal, ActaPublica
from .forms import ActividadControlForm, EditarActividadControlForm

#controlador de proyecto final
def crear_actividad_control(request):
    if request.method == 'POST':
        form = ActividadControlForm(request.POST)
        if form.is_valid():
            actividad_control = form.save()
            actividad_control.habilitar_actividad()
            return redirect('dashboard') 
    else:
        form = ActividadControlForm()
    
    return render(request, 'controlador/crear_actividad_control.html', {'form': form})

def buscar_estudiante_paractivar(request):
    estudiante_id = request.GET.get('id', None)
    if estudiante_id:
        try:
            # Filtra por estudiante_id y resultado='Suficiente'
            activar_estudiante = ActaProyectoPerfil.objects.filter(
                estudiante_id=estudiante_id, 
                resultado='Suficiente'
            ).first()  # Obtén el primer resultado que cumpla la condición

            if activar_estudiante:
                data = {
                    'estudiante_uno': activar_estudiante.estudiante_uno.id if activar_estudiante.estudiante_uno else None,
                    'tutor': activar_estudiante.tutor.id if activar_estudiante.tutor else None,
                    'jurado_1': activar_estudiante.jurado_1.id if activar_estudiante.jurado_1 else None,
                    'jurado_2': activar_estudiante.jurado_2.id if activar_estudiante.jurado_2 else None,
                    'jurado_3': activar_estudiante.jurado_3.id if activar_estudiante.jurado_3 else None,
                    'modalidad': activar_estudiante.modalidad.id if activar_estudiante.modalidad else None,
                }
            else:
                data = {}
        except ActaProyectoPerfil.DoesNotExist:
            data = {}
    else:
        data = {}

    return JsonResponse(data)

#lista de agregacion y proyectos finales
@login_required
def lista_actividad_control(request):
    actividades_control = HabilitarProyectoFinal.objects.all().order_by('-id').distinct()

    paginator = Paginator(actividades_control, 3) 
    page_number = request.GET.get('page') 
    page_obj = paginator.get_page(page_number) 

    return render(request, 'controlador/lista_actividad_control.html', {'page_obj': page_obj})


@login_required
def editar_actividad_control(request, pk):
    actividad_control = get_object_or_404(HabilitarProyectoFinal, pk=pk)

    if request.method == 'POST':
        form = EditarActividadControlForm(request.POST, instance=actividad_control)
        if form.is_valid():
            form.save()
            return redirect('lista_actividad_control')
    else:
        form = EditarActividadControlForm(instance=actividad_control)

    return render(request, 'controlador/editar_actividad_control.html', {'form': form})


from .models import ProyectoFinal, RepositorioTitulados
from django.utils import timezone
from .forms import ActividadForm

@login_required
def crear_actividad(request):
    estudiante = request.user
    actividad = None
    form = None

    try:
        actividad = ProyectoFinal.objects.get(estudiante=estudiante)
    except ProyectoFinal.DoesNotExist:
        actividad = None

    # Verificar si el estudiante ya tiene un RepositorioTitulados asignado
    repositorio_asignado = ActaPublica.objects.filter(
        Q(estudiante=estudiante) | Q(estudiante_uno=estudiante)
    ).first()

    if repositorio_asignado:
        # Si ya tiene un repositorio asignado, deshabilitar el formulario
        form = ActividadForm(instance=actividad)
        for field in form.fields.values():
            field.widget.attrs['disabled'] = True
    elif actividad and actividad.habilitada:
        if request.method == 'POST':
            form = ActividadForm(request.POST, request.FILES, instance=actividad)
            if form.is_valid():
                actividad = form.save(commit=False)
                actividad.fecha = timezone.now()
                #actividad.estado = 'Pendiente' 
                actividad.save()
                return redirect('lista_actividad')
        else:
            form = ActividadForm(instance=actividad)
    else:
        form = ActividadForm()

    return render(request, 'proyectofinal/crear_actividad.html', {
        'form': form,
        'actividad': actividad,
        'repositorio_asignado': repositorio_asignado
    })



def lista_actividad(request):
    user = request.user
    # Filtrar actividades donde el usuario sea estudiante, estudiante_uno o estudiante_dos
    actividades = ProyectoFinal.objects.filter(
        Q(estudiante=user) | Q(estudiante_uno=user) | Q(estudiante_dos=user)
    ).prefetch_related('comentarios').order_by('-fecha')
    
    return render(request, 'proyectofinal/lista_actividad.html', {'actividades': actividades})


from .models import ComentarioProFinal

@login_required
def revisar_actividad(request, actividad_id):
    actividad = get_object_or_404(ProyectoFinal, pk=actividad_id)
    user = request.user

    if request.method == 'POST':
        # Procesar el formulario de revisión y comentarios
        if user == actividad.jurado_1 and 'jurado_1_aprobado' in request.POST:
            actividad.jurado_1_aprobado = request.POST.get('jurado_1_aprobado') == 'on'

        if user == actividad.jurado_2 and 'jurado_2_aprobado' in request.POST:
            actividad.jurado_2_aprobado = request.POST.get('jurado_2_aprobado') == 'on'

        if user == actividad.jurado_3 and 'jurado_3_aprobado' in request.POST:
            actividad.jurado_3_aprobado = request.POST.get('jurado_3_aprobado') == 'on'

        # Guardar la actividad después de la revisión
        actividad.save()

        # Crear comentario si existe
        comentario_texto = request.POST.get('comentario_texto', '')
        actdocorregido = request.FILES.get('actdocorregido')
        if comentario_texto:
            comentario = ComentarioProFinal(
                actcomentario=comentario_texto,
                user=request.user,
                actproyecto_relacionado=actividad,
                actdocorregido=actdocorregido
            )
            comentario.save()

        messages.success(request, 'Revisión de actividad y comentario guardados correctamente.')
        return redirect('listaactividades')

    return render(request, 'proyectofinal/revisar_actividad.html', {'actividad': actividad})

def listaractividades(request):
    actividades_list = ProyectoFinal.objects.exclude(estado='Aprobado').order_by('-fecha')
    
    paginator = Paginator(actividades_list, 1) 
    page_number = request.GET.get('page') 
    actividades = paginator.get_page(page_number) 

    return render(request, 'controlador/listaractividades.html', {'actividades': actividades})


from django.db.models import Q
@login_required
def listaactividades(request):
    usuario = request.user
    
    # Filtra las actividades que tienen el estado 'Preapro' y que no son 'Aprobado' ni 'Pendiente'
    actividades = ProyectoFinal.objects.filter(
        Q(tutor=usuario) | Q(jurado_1=usuario) | Q(jurado_2=usuario) | Q(jurado_3=usuario),
        estado='Proceso'  # Filtra solo las actividades con estado 'Preapro'
    ).exclude(
        Q(estado='Aprobado') | Q(estado='Pendiente')  # Excluye las actividades con estado 'Aprobado' o 'Pendiente'
    ).order_by('-fecha')

    # Paginación
    paginator = Paginator(actividades, 1)  # 1 actividad por página
    page_number = request.GET.get('page')
    actividades = paginator.get_page(page_number)

    return render(request, 'controlador/listaactividades.html', {'actividades': actividades})

@user_passes_test(lambda u: permiso_M_G(u, 'ADMMGS'))
def revision(request, actividad_id):
    actividad = get_object_or_404(ProyectoFinal, pk=actividad_id)
    user = request.user
    todos_aprobados = actividad.jurado_1_aprobado and actividad.jurado_2_aprobado and actividad.jurado_3_aprobado

    if request.method == 'POST':
        if 'cambiar_estado' in request.POST:
            if todos_aprobados:
                actividad.estado = 'Aprobado'
                actividad.save()
                messages.success(request, 'Estado de la actividad cambiado a Aprobado.')
            else:
                messages.error(request, 'Necesita que los 3 jurados aprueben la documentación para poder cambiar el estado.')
                
            return redirect('listaactividades')

    return render(request, 'controlador/revision.html', {'actividad': actividad, 'todos_aprobados': todos_aprobados})


from django import forms
class AprobarProyectoForm(forms.Form):
    actcomentario = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),  
        required=False,
        label='Comentario Retroalimentativo'
    )
    actdocorregido = forms.FileField(
        widget=forms.ClearableFileInput(attrs={'class': 'form-control'}),  
        required=False,
        label='Adjuntar Documento'
    )
    aprobar = forms.BooleanField(
        required=False,
        label='Aprobar Documento para Revisión de Tribunales',
        widget=forms.CheckboxInput(attrs={'class': 'form-check-input'}) 
    )
    
    

def aprobar_actividad(request, actividad_id):
    # Obtén la actividad que se desea aprobar
    actividad = get_object_or_404(ProyectoFinal, id=actividad_id)
    user = request.user  # Captura el usuario logueado

    # Crea una instancia del formulario
    if request.method == 'POST':
        form = AprobarProyectoForm(request.POST, request.FILES)
        if form.is_valid():
            # Cambiar el estado a 'Preapro' si el checkbox está marcado y la actividad está en estado 'Pendiente'
            if form.cleaned_data['aprobar'] and actividad.estado == 'Pendiente':
                actividad.estado = 'Proceso'
                actividad.save()
                messages.success(request, 'Actividad aprobada exitosamente.')

            # Procesar el comentario y documento
            comentario_texto = form.cleaned_data.get('actcomentario')
            actdocorregido = form.cleaned_data.get('actdocorregido')

            if comentario_texto or actdocorregido:
                comentario = ComentarioProFinal(
                    actcomentario=comentario_texto,
                    user=user,
                    actproyecto_relacionado=actividad,
                    actdocorregido=actdocorregido
                )
                comentario.save()
                messages.success(request, 'Comentario y documento guardados correctamente.')

            return redirect('listaractividades')
    else:
        form = AprobarProyectoForm()  # Asegúrate de que el formulario se instancia aquí

    # Renderiza la plantilla con el formulario
    return render(request, 'controlador/aprobar_actividad.html', {'form': form, 'actividad': actividad})



from django.views.generic.edit import CreateView, UpdateView
from django.views.generic.list import ListView
from django.urls import reverse_lazy
from .models import Modalidad
from .forms import ModalidadForm

class ModalidadCreateView(CreateView):
    model = Modalidad
    form_class = ModalidadForm
    template_name = 'modalidad/modalidadagregar.html'
    success_url = reverse_lazy('listarmodalidades')

class ModalidadListView(ListView):
    model = Modalidad
    template_name = 'modalidad/listarmodalidades.html'
    context_object_name = 'modalidades'

class ModalidadUpdateView(UpdateView):
    model = Modalidad
    form_class = ModalidadForm
    template_name = 'modalidad/editarmodalidad.html'
    success_url = reverse_lazy('listarmodalidades')
    
def home_reporte(request):
   return render(request, "reportes/home_reporte.html")

# session de reportes

from django.http import HttpResponse
from .utils import render_pdf

class pdf_reporteinv(View):
    def get(self, request, *args, **kwargs):
        # Obtener la actividad específica
        actividad_id = self.kwargs.get('pk')  # Obtener el id desde la URL
        actividad = get_object_or_404(InvCientifica, pk=actividad_id)
        
        # Obtener los comentarios relacionados con la actividad
        comentarios = ComentarioInvCientifica.objects.filter(invproyecto_relacionado=actividad)
        data = {
            'actividad': actividad,
            'comentarios': comentarios  # Incluir los comentarios en el contexto
        }
        
        # Generar el PDF
        pdf = render_pdf('reportes/pdf_reporteinv.html', data)
        
        # Devolver el PDF como respuesta
        return HttpResponse(pdf, content_type='application/pdf')
 
from django.db import models

def listarinvcientifica(request):
    # Filtrado por nombre del usuario
    query = request.GET.get('q')
    if query:
        cientifica = InvCientifica.objects.filter(
            models.Q(user__nombre__icontains=query) |
            models.Q(user__apellido__icontains=query)
        )
    else:
        cientifica = InvCientifica.objects.all()

    # Ordenar por fecha de creación o id
    cientifica = cientifica.order_by('-id')

    # Paginación - Muestra 10 registros por página
    paginator = Paginator(cientifica, 2)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'page_obj': page_obj,
        'query': query,
    }
    return render(request, 'invcientifica/listarinvcientifica.html', context)

class Pdf_Reporte_InvFiltrado(View):
    def get(self, request, *args, **kwargs):
        # Filtrar por nombre y apellido
        query = request.GET.get('q')
        if query:
            cientifica = InvCientifica.objects.filter(
                models.Q(user__nombre__icontains=query) |
                models.Q(user__apellido__icontains=query)
            )
        else:
            cientifica = InvCientifica.objects.all()

        # Añadir la URL completa de la firma al contexto para cada comentario
        for actividad in cientifica:
            comentarios = ComentarioInvCientifica.objects.filter(invproyecto_relacionado=actividad)
            
            actividad.comentarios = comentarios  # Agregar comentarios al objeto de actividad

        # Preparar los datos para pasar al template
        data = {
            'cientifica': cientifica,
        }
        
        # Generar el PDF
        pdf = render_pdf('reportes/Pdf_Reporte_InvFiltrado.html', data)
        
        # Devolver el PDF como respuesta
        return HttpResponse(pdf, content_type='application/pdf')
      
#reportes perfil de proyecto 
def listarperfiles(request):
    query = request.GET.get('q', '').strip()
    modalidad_id = request.GET.get('modalidad', None)

    perfiles = PerfilProyecto.objects.all()

    if query:
        perfiles = perfiles.filter(
            Q(user__nombre__icontains=query) |
            Q(user__apellido__icontains=query)
        )

    if modalidad_id and modalidad_id.isdigit():
        perfiles = perfiles.filter(permodalidad__id=int(modalidad_id))
    else:
        modalidad_id = None

    perfiles = perfiles.order_by('-id')
    paginator = Paginator(perfiles, 3)  # Paginación ajustada a 10 por página
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    modalidades = Modalidad.objects.all()

    context = {
        'page_obj': page_obj,
        'query': query,
        'modalidad': modalidad_id,
        'modalidades': modalidades,
    }
    return render(request, 'perfil/listarperfiles.html', context)

from django.template.loader import render_to_string

class Pdf_Reporte_Perfiles(View):
    def get(self, request, *args, **kwargs):
        query = request.GET.get('q', '').strip()
        modalidad_id = request.GET.get('modalidad', '').strip()

        perfiles = PerfilProyecto.objects.all()

        if query:
            perfiles = perfiles.filter(
                Q(user__nombre__icontains=query) |
                Q(user__apellido__icontains=query)
            )

        if modalidad_id:
            try:
                modalidad_id = int(modalidad_id)
                perfiles = perfiles.filter(permodalidad__id=modalidad_id)
            except ValueError:
                perfiles = PerfilProyecto.objects.none()

        perfiles = perfiles.order_by('-id')

        for perfil in perfiles:
            comentarios = ComentarioPerfil.objects.filter(perproyecto_relacionado=perfil)
            
            perfil.comentarios_list = comentarios

        data = {
            'perfiles': perfiles,
            'query': query,
            'modalidad_id': modalidad_id,
        }
        
        pdf = render_pdf('reportes/Pdf_Reporte_Perfiles.html', data)
        
        # Devolver el PDF como respuesta
        return HttpResponse(pdf, content_type='application/pdf')
 



#import excel 

from django.db.models import Value
from django.db.models.functions import Concat
import openpyxl
from django.http import HttpResponse
from .models import InvCientifica

from django.utils.timezone import make_naive, is_aware
from datetime import datetime

def exportar_excel(request):
    # Crear un libro de trabajo
    wb = openpyxl.Workbook()
    hoja = wb.active
    hoja.title = 'Reporte Alcanze Investigación Cientifica'

    # Escribir los encabezados
    encabezados = [
        'ID', 
        '1er. Estudiante', 
        '2do. Estudiante', 
        '3er. Estudiante', 
        'Título del Proyecto', 
        'Fecha de Creación', 
        'Descripción del Proyecto', 
        'El Documento fue'
    ]
    hoja.append(encabezados)

    # Obtener los datos del modelo InvCientifica
    datos = InvCientifica.objects.annotate(
        estudiante1=Concat('user__nombre', Value(' '), 'user__apellido', Value(' '),'user__apellidoM'),
        estudiante2=Concat('user_uno__nombre', Value(' '), 'user_uno__apellido', Value(' '),'user_uno__apellidoM'),
        estudiante3=Concat('user_dos__nombre', Value(' '), 'user_dos__apellido', Value(' '), 'user_dos__apellidoM')
    ).values_list(
        'id', 
        'estudiante1',  # Primer participante
        'estudiante2',  # Segundo participante
        'estudiante3',  # Tercer participante
        'invtitulo', 
        'invfecha_creacion', 
        'invdescripcion', 
        'investado'
    )

    # Convertir fechas con zona horaria a naive (sin tzinfo)
    datos_naive = []
    for dato in datos:
        dato_list = list(dato)
        # Si el campo de fecha tiene zona horaria, convertirlo a naive
        for i, valor in enumerate(dato_list):
            if isinstance(valor, datetime) and is_aware(valor):
                dato_list[i] = make_naive(valor)
        datos_naive.append(dato_list)

    # Agregar los datos al archivo
    for dato in datos_naive:
        hoja.append(dato)

    # Preparar la respuesta HTTP para descargar el archivo
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=proyectos_investigacion.xlsx'

    # Guardar el archivo en la respuesta
    wb.save(response)
    return response



def exportar_excel_perfiles(request):
    query = request.GET.get('q', '').strip()
    modalidad_id = request.GET.get('modalidad', None)

    # Obtener los datos del modelo PerfilProyecto con filtrado aplicado
    perfiles = PerfilProyecto.objects.all()

    if query:
        perfiles = perfiles.filter(
            Q(user__nombre__icontains=query) |
            Q(user__apellido__icontains=query)
        )

    if modalidad_id and modalidad_id.isdigit():
        perfiles = perfiles.filter(permodalidad__id=int(modalidad_id))

    # Crear un libro de trabajo
    wb = openpyxl.Workbook()
    hoja = wb.active
    hoja.title = 'Reporte Perfiles de Proyecto'

    # Escribir los encabezados
    encabezados = [
        'ID', 
        '1er. Estudiante', 
        '2do. Estudiante', 
        '3er. Estudiante', 
        'Título del Proyecto', 
        'Fecha de Creación', 
        'Modalidad',  # Modalidad agregada
        'Descripción del Proyecto', 
        'El Documento fue'
    ]
    hoja.append(encabezados)

    # Anotar los nombres completos y obtener los datos con el filtrado
    datos = perfiles.annotate(
        estudiante1=Concat('user__nombre', Value(' '), 'user__apellido', Value(' '),'user__apellidoM'),
        estudiante2=Concat('user_uno__nombre', Value(' '), 'user_uno__apellido', Value(' '), 'user_uno__apellidoM'),
        estudiante3=Concat('user_dos__nombre', Value(' '), 'user_dos__apellido', Value(' '), 'user_dos__apellidoM')
    ).values_list(
        'id', 
        'estudiante1',  # Primer participante
        'estudiante2',  # Segundo participante
        'estudiante3',  # Tercer participante
        'pertitulo', 
        'perfecha_creacion', 
        'permodalidad__nombre',  # Obtener el nombre de la modalidad
        'perdescripcion', 
        'perestado'
    )

    # Convertir fechas con zona horaria a naive (sin tzinfo)
    datos_naive = []
    for dato in datos:
        dato_list = list(dato)
        # Si el campo de fecha tiene zona horaria, convertirlo a naive
        for i, valor in enumerate(dato_list):
            if isinstance(valor, datetime) and is_aware(valor):
                dato_list[i] = make_naive(valor)
        datos_naive.append(dato_list)

    # Agregar los datos al archivo
    for dato in datos_naive:
        hoja.append(dato)

    # Preparar la respuesta HTTP para descargar el archivo
    response = HttpResponse(content_type='application/vnd.openxmlformats-officedocument.spreadsheetml.sheet')
    response['Content-Disposition'] = 'attachment; filename=perfiles_proyecto.xlsx'

    # Guardar el archivo en la respuesta
    wb.save(response)
    return response


from .models import HabilitarTribunalesPerfil
from .forms import HabilitarTribunalesPerfilForm, EditarHabilitarTribunalesPerfilForm


def listar_tribunales_perfiles(request):
    perfiles_list = HabilitarTribunalesPerfil.objects.all()

    paginator = Paginator(perfiles_list, 8)  
    page_number = request.GET.get('page')
    perfiles = paginator.get_page(page_number)

    return render(request, 'perfil/listar__tribunales_perfiles.html', {'perfiles': perfiles})


def agregar_tribunales_perfil(request):
    if request.method == 'POST':
        form = HabilitarTribunalesPerfilForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_tribunales_perfiles')
    else:
        form = HabilitarTribunalesPerfilForm()
    return render(request, 'perfil/agregar_tribunales_perfil.html', {'form': form})

def editar_tribunales_perfil(request, pk):
    perfil = get_object_or_404(HabilitarTribunalesPerfil, pk=pk)
    if request.method == 'POST':
        form = EditarHabilitarTribunalesPerfilForm(request.POST, instance=perfil)
        if form.is_valid():
            form.save()
            return redirect('listar_tribunales_perfiles')
    else:
        form = EditarHabilitarTribunalesPerfilForm(instance=perfil)

        
        form.fields['user'].widget.attrs['disabled'] = 'disabled'
        form.fields['user_uno'].widget.attrs['disabled'] = 'disabled'

    return render(request, 'perfil/editar_tribunales_perfil.html', {'form': form, 'perfil': perfil})

def filtrartribunales(request):
    user_id = request.GET.get('user_id', None)
    
    if user_id:
        # Intenta obtener el PerfilProyecto del usuario seleccionado
        try:
            perfil = PerfilProyecto.objects.get(user_id=user_id, perestado='Aprobado')  # Solo perfiles aprobados
            data = {
                'user_uno': perfil.user_uno.id if perfil.user_uno else '',  # Si user_uno existe
                'pertitulo': perfil.pertitulo,
                'permodalidad': perfil.permodalidad.id,  # Si es una ForeignKey, pasamos el ID
            }
        except PerfilProyecto.DoesNotExist:
            data = {
                'error': 'No se encontró ningún Perfil Proyecto aprobado para este usuario.'
            }
    else:
        data = {
            'error': 'No se proporcionó un usuario válido.'
        }

    return JsonResponse(data)

from django.core.exceptions import ObjectDoesNotExist
def filtraracta(request):
    user_id = request.GET.get('user_id', None)  # Obtenemos el ID del estudiante seleccionado
    
    if user_id and user_id.isdigit():  # Verifica si el ID del usuario es un número válido
        try:
            # Obtenemos el perfil de habilitación del estudiante con los datos relevantes
            habilitar_perfil = HabilitarTribunalesPerfil.objects.get(user_id=user_id)
            
            # Construimos los datos que vamos a pasar
            data = {
                'titulo': habilitar_perfil.pertitulo,
                'modalidad': habilitar_perfil.permodalidad.id,  # Pasamos el ID de la modalidad
                'tutor': habilitar_perfil.tutor.id if habilitar_perfil.tutor else '',  # Verificamos si tutor existe
                'jurado_1': habilitar_perfil.jurado_1.id if habilitar_perfil.jurado_1 else '',  # Verificamos si jurado_1 existe
                'jurado_2': habilitar_perfil.jurado_2.id if habilitar_perfil.jurado_2 else '',  # Verificamos si jurado_2 existe
                'jurado_3': habilitar_perfil.jurado_3.id if habilitar_perfil.jurado_3 else '',  # Verificamos si jurado_3 existe
                'estudiante_uno': habilitar_perfil.user_uno.id if habilitar_perfil.user_uno else '',  # Verificamos si estudiante_uno existe
            }
        except ObjectDoesNotExist:
            data = {
                'error': 'necesita seleccionar al primer postulante para pasar los campos pregrabados.'
            }
        except Exception as e:
            data = {
                'error': f'Ocurrió un error inesperado: {str(e)}'
            }
    else:
        data = {
            'error': 'No se proporcionó un usuario válido o el ID no es un número.'
        }

    return JsonResponse(data)
