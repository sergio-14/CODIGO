from django.db import models
from django.utils import timezone
from django.contrib.auth import get_user_model
from datetime import date
from django.conf import settings
from django.core.exceptions import ValidationError  
import inflect 
from num2words import num2words

User = get_user_model()

ESTADO_CHOICES = [
    ('Aprobado', 'Aprobado'),
    ('Pendiente', 'Pendiente'),
    ('Rechazado', 'Rechazado'),
    ('Proceso', 'Proceso'),
]

RESULTADO_CHOICES = [
    ('Suficiente', 'Suficiente'),
    ('Insuficiente', 'Insuficiente'),
]

class Modalidad(models.Model):
    nombre = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    
    class Meta:
        verbose_name_plural = "Modalidades"
        verbose_name = "Modalidad"


    def __str__(self):
        return self.nombre

class Estudiante(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    Ru = models.CharField(max_length=20, null=True, blank=True)
    
class Docente(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    especialidad = models.CharField(max_length=100)
    titulo = models.CharField(max_length=100)
    
    def __str__(self):
        return f'{self.user.nombre}'

class Facultad(models.Model):
    nombre = models.CharField(max_length=150, unique=True)
    
    def __str__(self):
        return self.nombre


# Modelo de Carreras
class Carrera(models.Model):
    nombre_carrera = models.CharField(max_length=150)
    facultad = models.ForeignKey(Facultad, on_delete=models.CASCADE)
    def __str__(self):
        return self.nombre_carrera

# Modelo de Semestre
class Semestre(models.Model):
    S_Semestre=models.CharField(max_length=100,verbose_name='Semestre')
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    
    def __str__(self):
        return self.S_Semestre
    
    
class Area(models.Model):
    nombre_area = models.CharField(max_length=150, unique=True)

    def __str__(self):
        return self.nombre_area

# Modelo de Materia
class Materia(models.Model):
    nombre_materia = models.CharField(max_length=150)
    codigo = models.CharField(max_length=50, unique=True)
    semestre = models.ForeignKey(Semestre, on_delete=models.CASCADE)
    area = models.ForeignKey(Area, on_delete=models.CASCADE, null=True, blank=True)
    
    def __str__(self):
        return self.nombre_materia

# Modelo de Gestión
class Gestion(models.Model):
    anio = models.IntegerField(unique=True)
    
    def __str__(self):
         return str(self.anio)

# Modelo de Periodos
class Periodo(models.Model):
    numero = models.IntegerField()
    gestion = models.ForeignKey(Gestion, on_delete=models.CASCADE)
    
    class Meta:
        ordering = ['-numero','-gestion__anio']  
    
    def __str__(self):
        return f'{self.numero}/{self.gestion.anio}'  


class InvCientifica(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuario relacionado', related_name='name_user')
    user_uno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='Segundo participante', blank=True, null=True, related_name='name_useruno')
    habilitar_users = models.BooleanField(default=False, verbose_name='¡Mas de un Estudiante click aqui!')
    invtitulo = models.CharField(max_length=450, verbose_name='Agregar Título')
    invfecha_creacion = models.DateTimeField(auto_now_add=True)
    invdescripcion = models.TextField(verbose_name='Agregar una Descripción Breve', blank=True)
    invdocumentacion = models.FileField(upload_to='documento/investigacion', verbose_name='Agregar Documentacion', null=True, blank=True)
    investado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Pendiente')
    
    class Meta:
        verbose_name_plural = "Investicaciones cientificas"
        verbose_name = "Investigacion cientifica"


    def __str__(self):
        return self.invtitulo

class ComentarioInvCientifica(models.Model):
    invcomentario = models.TextField(max_length=1000, help_text='', verbose_name='Ingrese Comentario Retroalimentativo')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    invfecha_post = models.DateTimeField(auto_now_add=True)
    invproyecto_relacionado = models.ForeignKey(InvCientifica, on_delete=models.CASCADE)
    invdocorregido = models.FileField(upload_to='documento/investigacion', verbose_name='Agregar Documentacion', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Comentario InvCientifica"
        verbose_name = "Comentario Inv"
        ordering = ['-invfecha_post']

    def __str__(self):
        return self.invcomentario[:15] + '...' if len(self.invcomentario) > 15 else self.invcomentario

class HabilitarSeguimiento(models.Model):
    habilitarInv = models.BooleanField(default=True, verbose_name='Habilitar Formulario')
    
    class Meta:
        verbose_name_plural = "Habilitacion Inv"
        verbose_name = "Habilitar Inv"

    def __str__(self):
        return "Configuración Global"

class PerfilProyecto(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuario relacionado', related_name='perfil_name_user')
    user_uno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='Segundo participante', blank=True, null=True, related_name='perfil_name_useruno')
    habilitar_users = models.BooleanField(default=False, verbose_name='¡Mas de un Estudiante click aqui!')
    pertitulo = models.CharField(max_length=450, verbose_name='Agregar Título Perfil')
    perfecha_creacion = models.DateTimeField(auto_now_add=True)
    perdescripcion = models.TextField(verbose_name='Agregar una Descripción', blank=True)
    perdocumentacion = models.FileField(upload_to='documento/perfil', verbose_name='Agregar Documentación', null=True, blank=True)
    permodalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE, verbose_name='Seleccione Una Modalidad')
    perestado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Pendiente')
    
    class Meta:
        verbose_name_plural = "Perfil de Proyectos"
        verbose_name = "Perfil Proyecto"

    def __str__(self):
        return self.pertitulo

class ComentarioPerfil(models.Model):
    percomentario = models.TextField(max_length=1000, help_text='', verbose_name='Ingrese Comentario Retroalimentativo')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    perfecha_post = models.DateTimeField(auto_now_add=True)
    perproyecto_relacionado = models.ForeignKey(PerfilProyecto, on_delete=models.CASCADE, related_name='comentarios')
    perdocorregido = models.FileField(upload_to='documento/perfil', verbose_name='Agregar Documentacion', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Comentario Perfiles"
        verbose_name = "Comentario Perfil"
        ordering = ['-perfecha_post']

    def __str__(self):
        return self.percomentario[:15] + '...' if len(self.percomentario) > 15 else self.percomentario


class HabilitarTribunalesPerfil(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, verbose_name='Usuario relacionado', related_name='habilitar_user')
    user_uno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='Segundo participante', blank=True, null=True, related_name='habilitar_user_uno')
    pertitulo = models.CharField(max_length=450, verbose_name='Agregar Título Acta')
    permodalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE, verbose_name='Seleccione Una Modalidad')
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='habilitar_tutor', on_delete=models.CASCADE, verbose_name='Tutor')
    jurado_1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='habilitar_jurado_1', on_delete=models.CASCADE, verbose_name='Jurado 1')
    jurado_2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='habilitar_jurado_2', on_delete=models.CASCADE, verbose_name='Jurado 2')
    jurado_3 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='habilitar_jurado_3', on_delete=models.CASCADE, verbose_name='Jurado 3')
    
    class Meta:
        verbose_name_plural = "Habilitar Tribunales Perfil"
        verbose_name = "Habilitar Tribunal Perfil"
    
    def __str__(self):
        return self.pertitulo

class ActaProyectoPerfil(models.Model):
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE )
    perperiodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, null=True)
    acta = models.CharField(max_length=30, unique=True )
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_estudiante', on_delete=models.CASCADE)
    estudiante_uno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='Segundo participante', blank=True, null=True, related_name='acta_estudianteuno')
    titulo = models.CharField(max_length=450)
    lugar = models.CharField(max_length=50)
    fechadefensa = models.DateField(default=timezone.now)
    horainicio = models.TimeField()
    horafin = models.TimeField()
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_tutor', on_delete=models.CASCADE)
    jurado_1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_jurado_1', on_delete=models.CASCADE)
    jurado_2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_jurado_2', on_delete=models.CASCADE)
    jurado_3 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_jurado_3', on_delete=models.CASCADE)
    modalidad = models.ForeignKey('Modalidad', on_delete=models.CASCADE, verbose_name='Seleccione Una Modalidad')
    resultado = models.CharField(max_length=15, choices=RESULTADO_CHOICES, default='Suficiente')
    observacion_1 = models.TextField(max_length=200)
    observacion_2 = models.TextField(max_length=200)
    observacion_3 = models.TextField(max_length=200)
    docrespaldo = models.FileField(upload_to='documento/perfil', verbose_name='Agregar Documentación', null=True, blank=True)

    
    class Meta:
        verbose_name_plural = "Actas Perfil"
        verbose_name = "Acta Perfil"
        
    def __str__(self):
        return self.acta
    
    
            
    
class ActaViaDiplomado(models.Model):
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE)
    perperiodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, null=True)
    acta = models.CharField(max_length=30, unique=True )
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_via_estudiante', on_delete=models.CASCADE)
    titulo = models.CharField(max_length=450)
    lugar = models.CharField(max_length=50)
    fechadefensa = models.DateField(default=timezone.now)
    horainicio = models.TimeField()
    horafin = models.TimeField()
    modalidad = models.ForeignKey('Modalidad', on_delete=models.CASCADE, verbose_name='Seleccione Una Modalidad')
    presidente = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_via_presidente', on_delete=models.CASCADE)
    secretario = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_via_secretario', on_delete=models.CASCADE)
    vocal_1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_via_vocal_1', on_delete=models.CASCADE)
    vocal_2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_via_vocal_2', on_delete=models.CASCADE)
    valor_1 = models.IntegerField()
    valor_2 = models.IntegerField()
    valor_3 = models.IntegerField()
    totalnota = models.IntegerField()
    docrespaldo = models.FileField(upload_to='documento/actaviadiplomado', verbose_name='Agregar Documentacion', null=True, blank=True)

    
    def get_valor_1(self):
        
        return num2words(self.valor_1, lang='es')
    def get_valor_2(self):
        
        return num2words(self.valor_2, lang='es')
    def get_valor_3(self):
       
        return num2words(self.valor_3, lang='es')
    def get_totalnota(self):
       
        return num2words(self.totalnota, lang='es')
    
    def get_obse(self):
        if self.totalnota == 65:
            return "REPROBADO, SUJETA A NUEVA FECHA DE DEFENSA"
        elif 66 <= self.totalnota <= 70:
            return "APROBADO"
        elif 71 <= self.totalnota <= 80:
            return "BUENO"
        elif 81 <= self.totalnota <= 90:
            return "APROBADO CON FELICITACIÓN"
        elif 91 <= self.totalnota <= 100:
            return "APROBADO CON RECOMENDACIÓN DE PUBLICACIÓN"
        else:
            return "............."

    # Método para generar valorización basada en la totalnota
    def get_valoriz(self):
        if self.totalnota == 65:
             return "INSUFICIENTE"
        elif 66 <= self.totalnota <= 70:
            return "SUFICIENTE"
        elif 71 <= self.totalnota <= 80:
            return "SUFICIENTE"
        elif 81 <= self.totalnota <= 90:
            return "SOBRESALIENTE"
        elif 91 <= self.totalnota <= 100:
            return "EXCELENTE"
        else:
            return "............."
    
    
   
class ActaPrivada(models.Model):
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE )
    perperiodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, null=True)
    acta = models.CharField(max_length=30, unique=True  )
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_pri_estudiante', on_delete=models.CASCADE)
    estudiante_uno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='Segundo participante', blank=True, null=True, related_name='acta_pri_estudianteuno')
    titulo = models.CharField(max_length=450)
    lugar = models.CharField(max_length=50)
    fechadefensa = models.DateField(default=timezone.now)
    horainicio = models.TimeField()
    horafin = models.TimeField()
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_pri_tutor', on_delete=models.CASCADE)
    jurado_1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_pri_jurado_1', on_delete=models.CASCADE)
    jurado_2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_pri_jurado_2', on_delete=models.CASCADE)
    jurado_3 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_pri_jurado_3', on_delete=models.CASCADE)
    modalidad = models.ForeignKey('Modalidad', on_delete=models.CASCADE, verbose_name='Seleccione Una Modalidad')
    resultado = models.CharField(max_length=15, choices=RESULTADO_CHOICES, default='Suficiente')
    observacion_1 = models.TextField(max_length=200)
    observacion_2 = models.TextField(max_length=200)
    observacion_3 = models.TextField(max_length=200)
    calificacion1 = models.IntegerField()
    docrespaldo = models.FileField(upload_to='documento/actaprivada', verbose_name='Agregar Documentacion', null=True, blank=True)

    
    
    class Meta:
        verbose_name_plural = "Actas defensa Privada"
        verbose_name = "Acta Privada"
    
    def __str__(self):
        return self.acta
    

class ActaPublica(models.Model):
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE )
    perperiodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, null=True)
    acta = models.CharField(max_length=30, unique=True )
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_pub_estudiante', on_delete=models.CASCADE)
    estudiante_uno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='Segundo participante', blank=True, null=True, related_name='acta_pub_estudianteuno')
    titulo = models.CharField(max_length=450)
    lugar = models.CharField(max_length=50)
    fechadefensa = models.DateField(default=timezone.now)
    horainicio = models.TimeField()
    horafin = models.TimeField()
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_pub_tutor', on_delete=models.CASCADE)
    jurado_1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_pub_jurado_1', on_delete=models.CASCADE)
    jurado_2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_pub_jurado_2', on_delete=models.CASCADE)
    jurado_3 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_pub_jurado_3', on_delete=models.CASCADE)
    modalidad = models.ForeignKey('Modalidad', on_delete=models.CASCADE, verbose_name='Seleccione Una Modalidad')
    resultado = models.CharField(max_length=15, choices=RESULTADO_CHOICES, default='Suficiente')
    observacion_1 = models.TextField(max_length=200)
    observacion_2 = models.TextField(max_length=200)
    observacion_3 = models.TextField(max_length=200)
    calificacion1 = models.IntegerField()
    calificacion2 = models.IntegerField()
    notatotal = models.IntegerField()
    presidenteacta = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_presidente_Asig', on_delete=models.CASCADE)
    docrespaldo = models.FileField(upload_to='documento/actapublica', verbose_name='Agregar Documentacion', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Actas Defensa Publica"
        verbose_name = "Acta Publica"
    
    def __str__(self):
        return self.acta
    
    
    def get_notatotal_literal(self):
      
        return num2words(self.notatotal, lang='es')

    def get_observacion(self):
        if self.notatotal == 50:
            return "POSTERGADO Y/O REPROBADO"
        elif 51 <= self.notatotal <= 79:
            return "APROBADO"
        elif 80 <= self.notatotal <= 89:
            return "APROBADO CON FELICITACIONES"
        elif 90 <= self.notatotal <= 100:
            return "APROBADO CON MENCÍON HONORÍFICA Y RECOMENDACIÓN DE PUBLICACIÓN"
        else:
            return "............."

   
    def get_valorizacion(self):
        if self.notatotal == 50:
            return "INSUFICIENTE"
        elif 51 <= self.notatotal <= 79:
            return "BUENA"
        elif 80 <= self.notatotal <= 89:
            return "SOBRESALIENTE"
        elif 90 <= self.notatotal <= 100:
            return "EXCELENTE"
        else:
            return "............"
        

class ActaGrado(models.Model):
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE )
    perperiodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, null=True)
    acta = models.CharField(max_length=30, unique=True )
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_grado_estudiante', on_delete=models.CASCADE)
    area = models.ForeignKey('Area', on_delete=models.CASCADE, verbose_name='Seleccione el Area', related_name='actagrado_area')
    lugar = models.CharField(max_length=50)
    campus = models.CharField(max_length=250, default='Campus Universitario Hernán Melgar Justiniano.')
    espacio = models.CharField(max_length=250)
    fechadefensa = models.DateField()
    horainicio = models.TimeField()
    horafin = models.TimeField()
    nota = models.IntegerField()
    area_1 = models.ForeignKey('Area', on_delete=models.CASCADE, verbose_name='Seleccione el Area', related_name='actagrado_area_1')
    lugar_1 = models.CharField(max_length=50)
    campus_1 = models.CharField(max_length=250, default='Campus Universitario Hernán Melgar Justiniano.')
    espacio_1 = models.CharField(max_length=250)
    fechadefensa_1 = models.DateField()
    horainicio_1 = models.TimeField()
    horafin_1 = models.TimeField()
    nota_1 = models.IntegerField()
    area_2 = models.ForeignKey('Area', on_delete=models.CASCADE, verbose_name='Seleccione el Area', related_name='actagrado_area_2')
    lugar_2 = models.CharField(max_length=50)
    campus_2 = models.CharField(max_length=250, default='Campus Universitario Hernán Melgar Justiniano.')
    espacio_2 = models.CharField(max_length=250)
    fechadefensa_2 = models.DateField()
    horainicio_2 = models.TimeField()
    horafin_2 = models.TimeField()
    nota_2 = models.IntegerField()
    area_3 = models.ForeignKey('Area', on_delete=models.CASCADE, verbose_name='Seleccione el Area', related_name='actagrado_area_3')
    lugar_3 = models.CharField(max_length=50)
    campus_3 = models.CharField(max_length=250, default='Campus Universitario Hernán Melgar Justiniano.')
    espacio_3 = models.CharField(max_length=250)
    fechadefensa_3 = models.DateField()
    horainicio_3 = models.TimeField()
    horafin_3 = models.TimeField()
    nota_3 = models.IntegerField()
    presidenteacta = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_grado_presidente_Asi', on_delete=models.CASCADE)
    jurado_1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_grado_jurado_1', on_delete=models.CASCADE)
    jurado_2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_grado_jurado_2', on_delete=models.CASCADE)
    jurado_3 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_grado_jurado_3', on_delete=models.CASCADE)
    modalidad = models.ForeignKey('Modalidad', on_delete=models.CASCADE, verbose_name='Seleccione Una Modalidad')
    fecha = models.DateField(default=timezone.now)
    docrespaldo = models.FileField(upload_to='documento/perfil', verbose_name='Agregar Documentación', null=True, blank=True)
    notatotal = models.IntegerField()
    
    class Meta:
        verbose_name_plural = "Actas de Grado"
        verbose_name = "Acta Grado"
        
    def __str__(self):
        return self.acta
    def get_notali(self):
      
        return num2words(self.notatotal, lang='es')

    def get_observa(self):
        if self.notatotal == 50:
            return "POSTERGADO Y/O REPROBADO"
        elif 51 <= self.notatotal <= 79:
            return "APROBADO"
        elif 80 <= self.notatotal <= 89:
            return "APROBADO CON FELICITACIONES"
        elif 90 <= self.notatotal <= 100:
            return "APROBADO CON MENCÍON HONORÍFICA Y RECOMENDACIÓN DE PUBLICACIÓN"
        else:
            return "............."

   
    def get_valori(self):
        if self.notatotal == 50:
            return "INSUFICIENTE"
        elif 51 <= self.notatotal <= 79:
            return "BUENA"
        elif 80 <= self.notatotal <= 89:
            return "SOBRESALIENTE"
        elif 90 <= self.notatotal <= 100:
            return "EXCELENTE"
        else:
            return "............"

class ActaExcelencia(models.Model):
    carrera = models.ForeignKey(Carrera, on_delete=models.CASCADE )
    perperiodo = models.ForeignKey(Periodo, on_delete=models.CASCADE, null=True)
    acta = models.CharField(max_length=30, unique=True )
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_exc_estudiante', on_delete=models.CASCADE)
    lugar = models.CharField(max_length=50)
    fechadefensa = models.DateField(default=timezone.now)
    horainicio = models.TimeField()
    horafin = models.TimeField()
    secretario = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_exc_tutor', on_delete=models.CASCADE)
    jurado_1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_exc_jurado_1', on_delete=models.CASCADE)
    jurado_2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_exc_jurado_2', on_delete=models.CASCADE)
    jurado_3 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_exc_jurado_3', on_delete=models.CASCADE)
    modalidad = models.ForeignKey('Modalidad', on_delete=models.CASCADE, verbose_name='Seleccione Una Modalidad')
    notatotal = models.IntegerField()
    presidenteacta = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='acta_presidente_Asi', on_delete=models.CASCADE)
    docrespaldo = models.FileField(upload_to='documento/actaexcelencia', verbose_name='Agregar Documentacion', null=True, blank=True)

    class Meta:
        verbose_name_plural = "Actas Defensa Excelencia"
        verbose_name = "Acta Excelencia"
    
    def __str__(self):
        return self.acta
    
    
    def get_notatotal_literal(self):
        
        return num2words(self.notatotal, lang='es')

  
    def get_observacion(self):
        if self.notatotal == 50:
            return "POSTERGADO Y/O REPROBADO"
        elif 51 <= self.notatotal <= 79:
            return "APROBADO"
        elif 80 <= self.notatotal <= 89:
            return "APROBADO CON FELICITACIONES"
        elif 90 <= self.notatotal <= 100:
            return "APROBADO CON MENCÍON HONORÍFICA Y RECOMENDACIÓN DE PUBLICACIÓN"
        else:
            return "............."
    
    def get_mod(self):
        if self.notatotal == 50:
            return "RECONOCIMIENTO A LA CALIDAD"
        elif 51 <= self.notatotal <= 79:
            return "RECONOCIMIENTO A LA CALIDAD"
        elif 80 <= self.notatotal <= 100:
            return "RENDIMIENTO ACADEMICO"
        else:
            return "............."


    def get_valorizacion(self):
        if self.notatotal == 50:
            return "INSUFICIENTE"
        elif 51 <= self.notatotal <= 79:
            return "BUENA"
        elif 80 <= self.notatotal <= 89:
            return "SOBRESALIENTE"
        elif 90 <= self.notatotal <= 100:
            return "EXCELENTE"
        else:
            return "............"

class HabilitarProyectoFinal(models.Model):
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='actividad_estudiante', on_delete=models.CASCADE)
    estudiante_uno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='Segundo participante', blank=True, null=True, related_name='actividad_estudiante_uno')
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='actividad_tutor', on_delete=models.CASCADE)
    jurado_1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='actividad_jurado_1', on_delete=models.CASCADE)
    jurado_2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='actividad_jurado_2', on_delete=models.CASCADE)
    jurado_3 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='actividad_jurado_3', on_delete=models.CASCADE)
    modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE,  verbose_name='Seleccione Una Modalidad')

    def habilitar_actividad(self):
        actividad, created = ProyectoFinal.objects.get_or_create(
            estudiante=self.estudiante,
            defaults={
                'estudiante_uno': self.estudiante_uno,
                'tutor': self.tutor,
                'jurado_1': self.jurado_1,
                'jurado_2': self.jurado_2,
                'jurado_3': self.jurado_3,
                'modalidad': self.modalidad,
                'habilitada': True
            }
        )
        if not created:
            actividad.estudiante_uno = self.estudiante_uno
            actividad.tutor = self.tutor
            actividad.jurado_1 = self.jurado_1
            actividad.jurado_2 = self.jurado_2
            actividad.jurado_3 = self.jurado_3
            actividad.modalidad = self.modalidad
            actividad.habilitada = True
            actividad.save()
        return actividad
    
    class Meta:
        verbose_name_plural = "Habilitar Proyectos Final"
        verbose_name = "Habilitar Proyecto Final"
    
    def __str__(self):
        return f"HabilitarProyectoFinal for {self.estudiante}"
    
class ProyectoFinal(models.Model):
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='actividades_estudiante', on_delete=models.CASCADE)
    estudiante_uno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='Segundo participante', blank=True, null=True, related_name='actividades_estudiante_uno')
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='actividades_tutor', on_delete=models.CASCADE)
    jurado_1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='actividades_jurado_1', on_delete=models.CASCADE)
    jurado_2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='actividades_jurado_2', on_delete=models.CASCADE)
    jurado_3 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='actividades_jurado_3', on_delete=models.CASCADE)
    modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE)
    habilitada = models.BooleanField(default=False)
    titulo = models.CharField(max_length=450)
    resumen = models.TextField(max_length=500)
    fecha = models.DateField(default=timezone.now)
    guia_externo = models.CharField(max_length=250, default='Ninguno')
    documentacion = models.FileField(upload_to='documento/proyectofinal', verbose_name='Agregar Documentacion', null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Pendiente')
    jurado_1_aprobado = models.BooleanField(default=False)
    jurado_2_aprobado = models.BooleanField(default=False)
    jurado_3_aprobado = models.BooleanField(default=False)
    
    class Meta:
        verbose_name_plural = "Proyectos Finales"
        verbose_name = "Proyecto Final"

    def __str__(self):
        return f"ProyectoFinal for {self.estudiante}"
    
    @property
    def latest_comments(self):
        return self.comentarios.order_by('-actfecha_post')[:9]
    
    def save(self, *args, **kwargs):
        if self.estado in ['Aprobada', 'Rechazada']:
            # Verificar que todos los jurados han aprobado
            if not (self.jurado_1_aprobado and self.jurado_2_aprobado and self.jurado_3_aprobado):
                raise ValidationError("No se puede cambiar el estado sin la aprobación de todos los jurados.")
        
        super().save(*args, **kwargs)
    
    def transferir_a_repositorio(self, periodo, numero_acta, nota_aprobacion):
        repo_actividad, created = RepositorioTitulados.objects.get_or_create(
            estudiante=self.estudiante,
            estudiante_uno=self.estudiante_uno,
            tutor=self.tutor,
            jurado_1=self.jurado_1,
            jurado_2=self.jurado_2,
            jurado_3=self.jurado_3,
            titulo=self.titulo,
            resumen=self.resumen,
            modalidad=self.modalidad,
            fecha=self.fecha,
            guia_externo=self.guia_externo,
            documentacion=self.documentacion,
            estado=self.estado,
            jurado_1_aprobado=self.jurado_1_aprobado,
            jurado_2_aprobado=self.jurado_2_aprobado,
            jurado_3_aprobado=self.jurado_3_aprobado,
            periodo=periodo,
            numero_acta=numero_acta,
            nota_aprobacion=nota_aprobacion
        )
        return repo_actividad
    
class ComentarioProFinal(models.Model):
    actcomentario = models.TextField(max_length=1000, help_text='', verbose_name='Ingrese Comentario Retroalimentativo')
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, null=True)
    actfecha_post = models.DateTimeField(auto_now_add=True)
    actproyecto_relacionado = models.ForeignKey(ProyectoFinal, on_delete=models.CASCADE, related_name='comentarios')
    actdocorregido = models.FileField(upload_to='documento/proyectofinal', verbose_name='Agregar Documento', null=True, blank=True)
    
    class Meta:
        verbose_name_plural = "Comentarios Proyecto Final"
        verbose_name = "Comentario Proyecto Final"
        ordering = ['-actfecha_post']

    def __str__(self):
        return self.actcomentario[:15] + '...' if len(self.actcomentario) > 15 else self.actcomentario
   
class RepositorioTitulados(models.Model):
    estudiante = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='repo_estudiante', on_delete=models.CASCADE)
    estudiante_uno = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.SET_NULL, verbose_name='Segundo participante', blank=True, null=True, related_name='repo_estudiante_uno')
    tutor = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='repo_tutor', on_delete=models.CASCADE , blank=True, null=True)
    jurado_1 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='repo_jurado_1', on_delete=models.CASCADE)
    jurado_2 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='repo_jurado_2', on_delete=models.CASCADE)
    jurado_3 = models.ForeignKey(settings.AUTH_USER_MODEL, related_name='repo_jurado_3', on_delete=models.CASCADE)
    habilitada = models.BooleanField(default=False)
    titulo = models.CharField(max_length=450, blank=True, null=True)
    resumen = models.TextField(max_length=500 )
    modalidad = models.ForeignKey(Modalidad, on_delete=models.CASCADE, default=1, verbose_name='Seleccione Una Modalidad')
    fecha = models.DateField(default=timezone.now)
    guia_externo = models.CharField(max_length=250)
    documentacion = models.FileField(upload_to='documento/repositorios', verbose_name='Agregar Documentacion', null=True, blank=True)
    estado = models.CharField(max_length=10, choices=ESTADO_CHOICES, default='Pendiente')
    jurado_1_aprobado = models.BooleanField(default=False)
    jurado_2_aprobado = models.BooleanField(default=False)
    jurado_3_aprobado = models.BooleanField(default=False)
    periodo = models.ForeignKey(Periodo, on_delete=models.CASCADE)
    numero_acta = models.CharField(max_length=50)
    nota_aprobacion = models.IntegerField()
    
    class Meta:
        verbose_name_plural = "Repositorio de Proyectos"
        verbose_name = "Repositorio"

    def __str__(self):
        return f"Repositorio Actividad for {self.estudiante}"

