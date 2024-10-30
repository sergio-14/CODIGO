from gestion_usuarios.models import models
from django.contrib.auth.models import Group
from django.shortcuts import render, redirect
from django.contrib.auth.decorators import login_required,permission_required
from django.shortcuts import render, redirect,get_object_or_404
from .forms import T_ProyectosForm, IntSocSettingsForm, FaseProyectoForm,TipoProyectoForm,PeriodoForm
from .forms import FaseProyectoForm, GestionForm, SemestreForm,MateriaForm, EditarT_ProyectosForm
from django.conf import settings
from django.contrib.auth import views as auth_views
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.core.paginator import Paginator
from .models import T_Proyectos_IIISP,HabilitarFechas, T_Tipo, T_Fase
from seg_mod_graduacion.models import Gestion,Periodo,Materia,Semestre
from django.contrib.auth.models import User
from datetime import date

#permisos de grupo
from django.contrib.auth.models import Group
from django.contrib.auth.decorators import user_passes_test
from django.utils.decorators import method_decorator   
from django.core.exceptions import PermissionDenied  

from django.contrib.auth.decorators import user_passes_test
from django.contrib.auth import get_user_model
from django.shortcuts import render, redirect
from datetime import date


User = get_user_model()

#docentes interaccion social permigroup
def permiso_I_S(user, ADMIIISP):
    try:
        grupo = Group.objects.get(name=ADMIIISP)
    except Group.DoesNotExist:
        raise PermissionDenied(f"El grupo '{ADMIIISP}' no existe.")
    
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

#vista 403
def handle_permission_denied(request, exception):
    return render(request, '403.html', status=403)

# vista de acceso publico
def hometrabajos(request):
    return render(request, 'homesocial/hometrabajos.html')

#formulario de agregacion docentes I.S.
@user_passes_test(lambda u: permiso_Docentes(u, 'Docentes')) 
def proyecto_detail(request):
    settings = HabilitarFechas.objects.first()
    hoy = date.today()
    habilitado = settings and (settings.fecha_inicio_habilitacion <= hoy <= settings.fecha_fin_habilitacion)
    tiempo_restante = settings.tiempo_restante() if settings else "0 tiempo"
    
    ultimos_periodos = Periodo.objects.all().order_by('-gestion__anio', '-numero')[:2]
    if request.method == 'POST':
        form = T_ProyectosForm(request.POST, request.FILES)
        if habilitado and form.is_valid():
            proyecto = form.save(commit=False)  
            proyecto.S_persona = User.objects.get(nombre=request.user.nombre)  
            proyecto.save() 
            return redirect('proyectosin_so')  
    else:
        form = T_ProyectosForm()

    return render(request, 'homesocial/proyecto_detail.html', {
        'form': form,
        'habilitado': habilitado,
        'tiempo_restante': tiempo_restante,
        'ultimos_periodos': ultimos_periodos 
    })
#editar proyectos 
@login_required
def editar_proyecto(request, Id_Proyect):
   
    proyecto = get_object_or_404(T_Proyectos_IIISP, Id_Proyect=Id_Proyect)
    
    settings = HabilitarFechas.objects.first()
    hoy = date.today()
    habilitado = settings and (settings.fecha_inicio_habilitacion <= hoy <= settings.fecha_fin_habilitacion)
    ultimos_periodos = Periodo.objects.all().order_by('-gestion__anio', '-numero')[:2]
    if request.method == 'POST':
        form = EditarT_ProyectosForm(request.POST, request.FILES, instance=proyecto)
        if habilitado and form.is_valid():
            form.save()  
            return redirect('proyectosin_so')  
    else:
        form = EditarT_ProyectosForm(instance=proyecto)
    
    return render(request, 'homesocial/editar_proyecto.html', {
        'form': form,
        'habilitado': habilitado,
        'ultimos_periodos': ultimos_periodos ,
        'proyecto': proyecto, 
    })

#clasificacion de enviados y no enviados
@user_passes_test(lambda u: permiso_I_S(u, 'ADMIIISP')) 
def clasificar_proyectos(request):
    gestion_input = request.GET.get('gestion') 
    materias = Materia.objects.all()

    materias_con_proyectos = []
    materias_sin_proyectos = []

    if gestion_input:
        try:
            numero, anio = gestion_input.split('/')
            periodos_filtrados = Periodo.objects.filter(numero=numero, gestion__anio=anio)
        except ValueError:
            periodos_filtrados = None  
    else:
        periodos_filtrados = Periodo.objects.all()

    for materia in materias:
        if gestion_input and periodos_filtrados:
            proyectos = T_Proyectos_IIISP.objects.filter(T_Materia=materia, T_Gestion__in=periodos_filtrados)
        else:
            proyectos = T_Proyectos_IIISP.objects.filter(T_Materia=materia)

        if proyectos.exists():
            for proyecto in proyectos:
                materias_con_proyectos.append({
                    'materia': materia,
                    'persona': proyecto.S_persona,
                    
                })
        else:
            materias_sin_proyectos.append(materia)

    return render(request, 'homesocial/clasificar_proyectos.html', {
        'materias_con_proyectos': materias_con_proyectos,
        'materias_sin_proyectos': materias_sin_proyectos,
        'selected_gestion': gestion_input
    })
    
#asignacion de fechas para subir trabajos
@user_passes_test(lambda u: permiso_I_S(u, 'ADMIIISP')) 
def inv_soc_settings(request):
    settings = HabilitarFechas.objects.first()
    if not settings:
        settings =  HabilitarFechas()

    if request.method == 'POST':
        form = IntSocSettingsForm(request.POST, instance=settings)
        if form.is_valid():
            form.save()
            return redirect('dashboard')
    else:
        form = IntSocSettingsForm(instance=settings)
    
    return render(request, 'homesocial/inv_soc_settings.html', {'form': form})

#vista del proyecto I.S. para docentes
@login_required
@user_passes_test(lambda u: permiso_Docentes(u, 'Docentes')) 
def proyectosin_so(request):
    persona = request.user
    proyectos = T_Proyectos_IIISP.objects.filter(S_persona=persona).order_by('-Id_Proyect')
    
    paginator = Paginator(proyectos, 1)  
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)

    context = {
        'persona': persona,
        'page_obj': page_obj
    }
    return render(request, 'homesocial/proyectosin_so.html', context)

#poryectos interacion social vista general publica
def repoin(request):
    gestion_id = request.GET.get('T_Gestion')  
    semestre_id = request.GET.get('Semestre')

    listaproyectos = T_Proyectos_IIISP.objects.none()  

    if gestion_id or semestre_id:
        listaproyectos = T_Proyectos_IIISP.objects.all()

        if gestion_id:
            listaproyectos = listaproyectos.filter(T_Gestion_id=gestion_id)  

        if semestre_id:
            listaproyectos = listaproyectos.filter(T_Materia__semestre_id=semestre_id)

        listaproyectos = listaproyectos.order_by('Id_Proyect') 

    primer_proyecto = listaproyectos.first() if listaproyectos.exists() else None

    # Obtener solo las últimas tres gestiones
    t_gestiones = Periodo.objects.all().order_by('-gestion__anio', '-numero')[:10]

    context = {
        'primer_proyecto': primer_proyecto,
        't_gestiones': t_gestiones,
        't_semestres': Semestre.objects.all(),
        'listaproyectos': listaproyectos,
        'selected_t_gestion': gestion_id,
        'selected_t_semestre': semestre_id,
    }
    
    return render(request, 'homesocial/repoin.html', context)


######## TAREAS #########

#Tipo croud

def listart(request):
    tipos = T_Tipo.objects.all()
    return render(request, 'Tareas/Tipo/listart.html', {'tipos': tipos})


def creart(request):
    if request.method == "POST":
        form = TipoProyectoForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listart')
    else:
        form = TipoProyectoForm()
    return render(request, 'Tareas/Tipo/creart.html', {'form': form})


def editart(request, pk):
    tipo = get_object_or_404(T_Tipo, pk=pk)
    if request.method == "POST":
        form = TipoProyectoForm(request.POST, instance=tipo)
        if form.is_valid():
            form.save()
            return redirect('listart')
    else:
        form = TipoProyectoForm(instance=tipo)
    return render(request, 'Tareas/Tipo/editart.html', {'form': form})


def eliminart(request, pk):
    tipo = get_object_or_404(T_Tipo, pk=pk)
    if request.method == "POST":
        tipo.delete()
        return redirect('listart')
    return render(request, 'Tareas/Tipo/eliminart.html', {'object': tipo})

#Fase croud

def listarf(request):
    fase = T_Fase.objects.all()
    return render(request, 'Tareas/FaseEtapa/listarf.html', {'fase': fase})


def crearf(request):
    if request.method == "POST":
        formf = FaseProyectoForm(request.POST)
        if formf.is_valid():
            formf.save()
            return redirect('listarf')
    else:
        formf = FaseProyectoForm()
    return render(request, 'Tareas/FaseEtapa/crearf.html', {'formf': formf})

def editarf(request, pk):
    fase = get_object_or_404(T_Fase, pk=pk)
    if request.method == "POST":
        formf = FaseProyectoForm(request.POST, instance=fase)
        if formf.is_valid():
            formf.save()
            return redirect('listarf')
    else:
        formf = FaseProyectoForm(instance=fase)
    return render(request, 'Tareas/FaseEtapa/editarf.html', {'formf': formf})


def eliminarf(request, pk):
    fase = get_object_or_404(T_Fase, pk=pk)
    if request.method == "POST":
        fase.delete()
        return redirect('listarf')
    return render(request, 'Tareas/FaseEtapa/eliminarf.html', {'object': fase})

#Gestion croud

def listarg(request):
    gestion_list = Gestion.objects.all().order_by('-id')
    paginator = Paginator(gestion_list, 5) 
    page_number = request.GET.get('page')
    gestion = paginator.get_page(page_number)
    return render(request, 'Tareas/Gestion/listarg.html', {'gestion': gestion})


def crearg(request):
    if request.method == "POST":
        formg = GestionForm(request.POST)
        if formg.is_valid():
            formg.save()
            return redirect('listarg')
    else:
        formg = GestionForm()
    return render(request, 'Tareas/Gestion/crearg.html', {'formg': formg})

def editarg(request, pk):
    gestion = get_object_or_404(Gestion, pk=pk)
    if request.method == "POST":
        formg = GestionForm(request.POST, instance=gestion)
        if formg.is_valid():
            formg.save()
            return redirect('listarg')
    else:
        formg = GestionForm(instance=gestion)
    return render(request, 'Tareas/Gestion/editarg.html', {'formg': formg})

def eliminarg(request, pk):
    gestion = get_object_or_404(Gestion, pk=pk)
    if request.method == "POST":
        gestion.delete()
        return redirect('listarg')
    return render(request, 'Tareas/Gestion/eliminarg.html', {'object': gestion})

#Periodo croud

def listarper(request):
    periodo_list = Periodo.objects.all().order_by('-id')
    paginator = Paginator(periodo_list, 5) 
    page_number = request.GET.get('page')
    periodo = paginator.get_page(page_number)
    return render(request, 'Tareas/Periodo/listarper.html', {'periodo': periodo})


def crearper(request):
    if request.method == "POST":
        formper = PeriodoForm(request.POST)
        if formper.is_valid():
            formper.save()
            return redirect('listarper')
    else:
        formper = PeriodoForm()
    return render(request, 'Tareas/Periodo/crearper.html', {'formper': formper})

def editarper(request, pk):
    periodo = get_object_or_404(Periodo, pk=pk)
    if request.method == "POST":
        formper = PeriodoForm(request.POST, instance=periodo)
        if formper.is_valid():
            formper.save()
            return redirect('listarpér')
    else:
        formper = PeriodoForm(instance=periodo)
    return render(request, 'Tareas/Periodo/editarper.html', {'formper': formper})



#Semestre croud

def listars(request):
    semestre = Semestre.objects.all()
    return render(request, 'Tareas/Semestre/listars.html', {'semestre': semestre})

def crears(request):
    if request.method == "POST":
        forms = SemestreForm(request.POST)
        if forms.is_valid():
            forms.save()
            return redirect('listars')
    else:
        forms = SemestreForm()
    return render(request, 'Tareas/Semestre/crears.html', {'forms': forms})

def editars(request, pk):
    semestre = get_object_or_404(Semestre, pk=pk)
    if request.method == "POST":
        forms = SemestreForm(request.POST, instance=semestre)
        if forms.is_valid():
            forms.save()
            return redirect('listars')
    else:
        forms = SemestreForm(instance=semestre)
    return render(request, 'Tareas/Semestre/editars.html', {'forms': forms})

def eliminars(request, pk):
    semestre = get_object_or_404(Semestre, pk=pk)
    if request.method == "POST":
        semestre.delete()
        return redirect('listars')
    return render(request, 'Tareas/Semestre/eliminars.html', {'object': semestre})

#Materia cruod

def listarm(request):
    materia = Materia.objects.all()
    return render(request, 'Tareas/Materia/listarm.html', {'materia': materia})

def crearm(request):
    if request.method == 'POST':
        formm = MateriaForm(request.POST)
        if formm.is_valid():
            formm.save()
            return redirect('listarm')
    else:
        formm = MateriaForm()
    return render(request, 'Tareas/Materia/crearm.html', {'formm': formm})

def editarm(request, pk):
    materia = get_object_or_404(Materia, pk=pk)
    if request.method == 'POST':
        formm = MateriaForm(request.POST, instance=materia)
        if formm.is_valid():
            formm.save()
            return redirect('listarm')
    else:
        formm = MateriaForm(instance=materia)
    return render(request, 'Tareas/Materia/editarm.html', {'formm': formm})

def eliminarm(request, pk):
    materia = get_object_or_404(Materia, pk=pk)
    if request.method == 'POST':
        materia.delete()
        return redirect('listarm')
    return render(request, 'Tareas/Materia/eliminarm.html', {'materia': materia})

