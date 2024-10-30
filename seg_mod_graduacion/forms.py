from django import forms
from django.contrib.auth.models import Group
from gestion_usuarios.models import User 
from .models import InvCientifica, ComentarioInvCientifica, HabilitarProyectoFinal,HabilitarSeguimiento,ActaGrado
from .models import PerfilProyecto, ComentarioPerfil, RepositorioTitulados, ProyectoFinal, ComentarioProFinal
from .models import ActaProyectoPerfil,HabilitarProyectoFinal, Modalidad, ActaPublica, ActaPrivada,ActaViaDiplomado, Periodo
from django.utils.text import slugify
from django_select2.forms import ModelSelect2Widget

class ModalidadForm(forms.ModelForm):
    class Meta:
        model = Modalidad
        fields = ['nombre']

    def save(self, commit=True):
        instance = super().save(commit=False)
        instance.slug = slugify(instance.nombre)
        if commit:
            instance.save()
        return instance
  
# área de investigación científica 
class InvCientificaForm(forms.ModelForm):
    class Meta:
        model = InvCientifica
        fields = ['user_uno','habilitar_users','invtitulo', 'invdescripcion', 'invdocumentacion' ]
        widgets = {
            'invdescripcion': forms.Textarea(attrs={'class': 'descripcion-field'}),
        }
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        estudiantes_group = Group.objects.get(name='Estudiantes')
        estudiantes_users = User.objects.filter(groups=estudiantes_group, is_active=True)

        investigaciones_aprobadas = InvCientifica.objects.filter(investado='Aprobado')

        usuarios_con_inv = investigaciones_aprobadas.values_list('user', 'user_uno')
     
        usuarios_con_inv = set(
            usuario for usuarios in usuarios_con_inv for usuario in usuarios if usuario is not None
        )

        estudiantes_users = estudiantes_users.exclude(id__in=usuarios_con_inv)

        if self.request and self.request.user.is_authenticated:
            estudiantes_users = estudiantes_users.exclude(id=self.request.user.id)

        self.fields['user_uno'].queryset = estudiantes_users
      
        self.fields['invtitulo'].required = True
        self.fields['invdescripcion'].required = True
        self.fields['invdocumentacion'].required = True
        
        
class InvComentarioForm(forms.ModelForm):
    class Meta:
        model = ComentarioInvCientifica
        fields = ['invcomentario','invdocorregido'] 
        widgets = {
            'invcomentario': forms.Textarea(attrs={'class': 'comentari-field'}),
        }

class GlobalSettingsForm(forms.ModelForm):
    class Meta:
        model = HabilitarSeguimiento
        fields = ['habilitarInv']

    def __init__(self, *args, **kwargs):
        super(GlobalSettingsForm, self).__init__(*args, **kwargs)
        
# área de perfil de proyecto 
class PerfilForm(forms.ModelForm):
    class Meta:
        model = PerfilProyecto
        fields = ['user_uno','habilitar_users','pertitulo', 'perdescripcion', 'perdocumentacion', 'permodalidad']
        widgets = {
            'perdescripcion': forms.Textarea(attrs={'class': 'descripcion-field'}),
        }
        
    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)

        estudiantes_group = Group.objects.get(name='Estudiantes')
        estudiantes_users = User.objects.filter(groups=estudiantes_group, is_active=True)

        perfiles_aprobadas = PerfilProyecto.objects.filter(perestado='Aprobado')
        inv_aprobadas = InvCientifica.objects.filter(investado='Aprobado')

        usuarios_con_perfil = perfiles_aprobadas.values_list('user', 'user_uno')
        usuarios_con_inv = inv_aprobadas.values_list('user', 'user_uno')
       
        usuarios_con_perfil = set(
            usuario for usuarios in usuarios_con_perfil for usuario in usuarios if usuario is not None
        )
        usuarios_con_inv = set(
            usuario for usuarios in usuarios_con_inv for usuario in usuarios if usuario is not None
        )

        estudiantes_users = estudiantes_users.filter(
            id__in=usuarios_con_inv
            ).exclude(id__in=usuarios_con_perfil
            )

        if self.request and self.request.user.is_authenticated:
            estudiantes_users = estudiantes_users.exclude(id=self.request.user.id)

        self.fields['user_uno'].queryset = estudiantes_users
    
        self.fields['pertitulo'].required = True
        self.fields['perdescripcion'].required = True
        self.fields['perdocumentacion'].required = True
        self.fields['permodalidad'].required = True
        
        INCLUDED_MODALITIES = ['Trabajo Dirigido', 'Proyecto de Grado', 'Tesis de Grado']
        self.fields['permodalidad'].choices = [
            (choice_value, choice_label)
            for choice_value, choice_label in self.fields['permodalidad'].choices
            if choice_label in INCLUDED_MODALITIES
        ]
      
      
class PerComentarioForm(forms.ModelForm):
    class Meta:
        model = ComentarioPerfil
        fields = ['percomentario','perdocorregido'] 
        widgets = {
            'percomentario': forms.Textarea(attrs={'class': 'comentari-field'}),
        }


class ActaPerfilForm(forms.ModelForm):
    class Meta:
        model = ActaProyectoPerfil
        fields = [
            'perperiodo', 'acta', 'carrera', 'estudiante', 
            'estudiante_uno', 'titulo', 'lugar', 
            'fechadefensa', 'horainicio', 'horafin', 'tutor', 
            'jurado_1', 'jurado_2', 'jurado_3', 'modalidad', 
            'resultado', 'observacion_1', 'observacion_2', 'observacion_3'
        ]
        labels = {
            'perperiodo': 'Periodo y Gestión',
            'acta': 'Número de Acta',
            'carrera': 'Carrera',
            'estudiante': 'Postulante',
            'estudiante_uno': 'Postulante dos',
          
            'titulo': 'Título del Proyecto',
            'lugar': 'Lugar de Defensa',
            'fechadefensa': 'Fecha de Defensa',
            'horainicio': 'Hora de Inicio',
            'horafin': 'Hora de Finalización',
            'tutor': 'Seleccione al Tutor Designado',
            'jurado_1': 'Primer Tribunal Designado',
            'jurado_2': 'Segundo Tribunal Designado',
            'jurado_3': 'Tercer Tribunal Designado',
            'modalidad': 'Seleccione Modalidad',
            'resultado': 'Resultado de la Defensa',
            'observacion_1': 'Observación del Primer Tribunal',
            'observacion_2': 'Observación del Segundo Tribunal',
            'observacion_3': 'Observación del Tercer Tribunal',
        }
        widgets = {
            'perperiodo': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'acta': forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'readonly': 'readonly'}),
            'carrera': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'estudiante': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'estudiante_uno': forms.Select(attrs={'class': 'form-select'}),
          
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'fechadefensa': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'}),
            'horainicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': 'required'}),
            'horafin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': 'required'}),
            'tutor': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_1': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_2': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_3': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'modalidad': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'resultado': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'observacion_1': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'required': 'required'}),
            'observacion_2': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'required': 'required'}),
            'observacion_3': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'required': 'required'}),
        }

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop('request', None)
        super().__init__(*args, **kwargs)
        
        # Filtrado de estudiantes y asignación a los campos correspondientes
        estudiantes_users = self._get_estudiantes_filtrados()
        
        # Establecer el queryset filtrado para los campos de estudiantes
        self.fields['estudiante_uno'].queryset = estudiantes_users
     
        self.fields['estudiante'].queryset = estudiantes_users
        
        INCLUDED_MODALITIES = ['Trabajo Dirigido', 'Proyecto de Grado', 'Tesis de Grado']
        self.fields['modalidad'].choices = [
            (choice_value, choice_label)
            for choice_value, choice_label in self.fields['modalidad'].choices
            if choice_label in INCLUDED_MODALITIES
        ]
        
        # Filtrar los usuarios de los grupos de docentes
        docentes_group = Group.objects.get(name="Docentes")
        self.fields['tutor'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_1'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_2'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_3'].queryset = User.objects.filter(groups=docentes_group, is_active=True)

        # Limitar las opciones del campo resultado
        self._filter_resultado_choices()
        
        # Asignar el número de acta inicial
        self._set_initial_acta_number()

    def _set_initial_acta_number(self):
        # Busca el último valor de 'acta' en la base de datos
        last_acta = ActaProyectoPerfil.objects.order_by('-id').first()
        
        # Si hay registros, incrementa el número, de lo contrario inicia en '001'
        if last_acta:
            last_value = int(last_acta.acta)  # Convierte el último valor a entero
            new_value = last_value + 1  # Incrementa en 1
        else:
            new_value = 1  # Si no hay registros, comienza con 1

        # Formatea el nuevo valor con ceros a la izquierda
        self.initial['acta'] = str(new_value).zfill(5)  # Por ejemplo, '001', '002', etc.

    def _get_estudiantes_filtrados(self):
        estudiantes_group = Group.objects.get(name='Estudiantes')
        estudiantes_users = User.objects.filter(groups=estudiantes_group, is_active=True)
        
        # Filtrar los usuarios que ya tienen perfilproyecto aprobadas
        usuarios_con_perfil_aprobado = PerfilProyecto.objects.filter(perestado='Aprobado').values_list('user', 'user_uno')
        
        # Aplanar las tuplas para obtener solo los IDs de los usuarios
        usuarios_con_perfil = set(usuario for usuarios in usuarios_con_perfil_aprobado for usuario in usuarios if usuario is not None)

        # Filtrar los usuarios que ya tienen un resultado 'Suficiente' o que están en HabilitarProyectoFinal
        usuarios_con_actividad = HabilitarProyectoFinal.objects.values_list('estudiante', flat=True)
        usuarios_con_resultado_suficiente = ActaProyectoPerfil.objects.filter(resultado='Suficiente').values_list('estudiante', 'estudiante_uno')
        
        # Aplanar las tuplas para obtener solo los IDs de los usuarios
        usuarios_a_excluir = set(usuarios_con_actividad).union(set(usuario for usuarios in usuarios_con_resultado_suficiente for usuario in usuarios if usuario is not None))

        # Excluir los usuarios que ya tienen un perfil aprobado y actividad finalizada
        estudiantes_filtrados = estudiantes_users.exclude(id__in=usuarios_a_excluir).filter(id__in=usuarios_con_perfil)
        return estudiantes_filtrados

    def _filter_resultado_choices(self):
        # Filtra las opciones del campo 'resultado' para incluir solo 'Suficiente' e 'Insuficiente'
        INCLUDED_RESULT = ['Insuficiente', 'Suficiente']
        self.fields['resultado'].choices = [
            (choice_value, choice_label)
            for choice_value, choice_label in self.fields['resultado'].choices
            if choice_label in INCLUDED_RESULT
        ]

    def save(self, commit=True):
        # El campo 'acta' ya se establece en self.initial durante la inicialización
        self.instance.acta = self.initial['acta']  # Asegurarse de que se establezca correctamente

        return super().save(commit)
    
    def clean(self):
        cleaned_data = super().clean()
        horainicio = cleaned_data.get('horainicio')
        horafin = cleaned_data.get('horafin')
        if horainicio and horafin:
            if horainicio >= horafin:
                self.add_error('horainicio', "La hora de inicio no puede ser mayor o igual a la hora de finalización.")
                self.add_error('horafin', "La hora de inicio no puede ser mayor o igual a la hora de finalización.")
                return cleaned_data
    
    
from django.db.models import Q
  
        
#actas defensa privada
class ActaPublicaForm(forms.ModelForm):
    class Meta:
        model = ActaPublica
        fields = [
            'perperiodo','acta', 'carrera', 'estudiante', 'estudiante_uno',  'titulo', 'lugar', 
            'fechadefensa', 'horainicio', 'horafin', 'tutor', 
            'jurado_1', 'jurado_2', 'jurado_3', 'modalidad', 
            'calificacion1', 'calificacion2','notatotal', 'presidenteacta' , 'resultado'
        ]
        labels = {
            'perperiodo': 'Periodo y Gestión',
            'acta': 'Número de Acta',
           
            'carrera': 'Carrera',
            'estudiante': 'Postulante',
            'estudiante_uno': 'Postulante dos',
          
            'titulo': 'Título del Proyecto',
            'lugar': 'Lugar de Defensa',
            'fechadefensa': 'Fecha de Defensa',
            'horainicio': 'Hora de Inicio',
            'horafin': 'Hora de Finalización',
            'tutor': 'Seleccione al Tutor Designado',
            'jurado_1': 'Primer Tribunal Designado',
            'jurado_2': 'Segundo Tribunal Designado',
            'jurado_3': 'Tercer Tribunal Designado',
            'modalidad': 'Seleccione Modalidad',
            'calificacion1': '1er. Valor Cuantitativo',
            'calificacion2': '2do. Valor Cuantitativo',
            'notatotal': 'Calificación Total',
            'presidenteacta': 'Asignar Presidente',
        }
        widgets = {
            'perperiodo': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'acta': forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'readonly': 'readonly'}),
            'carrera': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'estudiante': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'estudiante_uno': forms.Select(attrs={'class': 'form-select'}),
          
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'fechadefensa': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'}),
            'horainicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': 'required'}),
            'horafin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': 'required'}),
            'tutor': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_1': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_2': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_3': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'modalidad': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'calificacion1': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'min': '0', 'max': '30'}),
            'calificacion2': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'min': '0', 'max': '70'}),
            'notatotal': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'min': '0', 'max': '100'}),
            'presidenteacta': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        calificacion1 = cleaned_data.get('calificacion1', 0)
        calificacion2 = cleaned_data.get('calificacion2', 0)
        notatotal = calificacion1 + calificacion2
        cleaned_data['notatotal'] = notatotal
        
        horainicio = cleaned_data.get('horainicio')
        horafin = cleaned_data.get('horafin')
        if horainicio and horafin:
            if horainicio >= horafin:
                self.add_error('horainicio', "La hora de inicio no puede ser mayor o igual a la hora de finalización.")
                self.add_error('horafin', "La hora de inicio no puede ser mayor o igual a la hora de finalización.")
                return cleaned_data
            
    def save(self, commit=True):
        instance = super().save(commit=False)
      
        instance.acta = self.initial.get('acta', instance.acta) 
       
        if not instance.pk:
            instance.notatotal = self.cleaned_data.get('notatotal', 0)
           
            instance.observacion_1 = 'sin observacion'
            instance.observacion_2 = 'sin observacion'
            instance.observacion_3 = 'sin observacion'
          
            if commit:
                instance.save()
                return instance
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['resultado'].widget = forms.HiddenInput()
        self.instance.resultado = 'Suficiente'
        self._set_initial_acta_number()
        estudiantes_group = Group.objects.get(name="Estudiantes")
        docentes_group = Group.objects.get(name="Docentes")
        presidentes_group = Group.objects.get(name="Presidentes Defensas")
        estudiantes_users = User.objects.filter(groups=estudiantes_group, is_active=True)
        
        usuarios_con_repositorio = RepositorioTitulados.objects.values_list('estudiante', flat=True) 
        usuarios_con_resultado_Suficiente = ActaPrivada.objects.filter(resultado='Suficiente').values_list('estudiante', flat=True).distinct() 
        usuarios_con_proyecto_final = ProyectoFinal.objects.filter(estado='Aprobado').values_list('estudiante', flat=True).distinct()
       
        
       
        usuarios_uno_con_resultado_Suficiente = ActaPrivada.objects.filter(resultado='Suficiente').values_list('estudiante_uno', flat=True).distinct() 
        usuarios_uno_con_proyecto_final = ProyectoFinal.objects.filter(estado='Aprobado').values_list('estudiante_uno', flat=True).distinct()
        
        #estudiantes_postergados = ActaPublica.objects.filter(notatotal=50).values_list('estudiante', flat=True)
        #estudiantes_sin_nota = ActaPublica.objects.filter(notatotal__isnull=True).values_list('estudiante', flat=True)    
        
        
        #usuarios_dos_con_actapublica = ActaPublica.objects.filter(resultado='Aprobado').values_list('estudiante_dos', flat=True)
        self.fields['estudiante'].queryset = User.objects.filter(
            groups=estudiantes_group
        ).exclude(
            id__in=usuarios_con_repositorio
        ).filter(
            id__in=estudiantes_users
        ).filter(
            id__in=usuarios_con_resultado_Suficiente
        ).filter(
            id__in=usuarios_con_proyecto_final
        )
        
        self.fields['estudiante_uno'].queryset = User.objects.filter(
            groups=estudiantes_group
        ).filter(
            id__in=estudiantes_users
        ).filter(
            id__in=usuarios_uno_con_resultado_Suficiente
        ).filter(
            id__in=usuarios_uno_con_proyecto_final
        )
        
        INCLUDED_MODALITIES = ['Trabajo Dirigido', 'Proyecto de Grado', 'Tesis de Grado']
        self.fields['modalidad'].choices = [
            (choice_value, choice_label)
            for choice_value, choice_label in self.fields['modalidad'].choices
            if choice_label in INCLUDED_MODALITIES
        ]
       
        self.fields['tutor'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_1'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_2'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_3'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['presidenteacta'].queryset = User.objects.filter(groups=presidentes_group, is_active=True)
        
    def _set_initial_acta_number(self):
   
        last_acta = ActaPublica.objects.order_by('-acta').first()
        if last_acta:
            last_value = int(last_acta.acta)
            new_value = last_value + 1
        else:
            new_value = 1
   
        while ActaPublica.objects.filter(acta=str(new_value).zfill(5)).exists():
            new_value += 1
        self.initial['acta'] = str(new_value).zfill(5)  # Formatea el nuevo valor
        print(f"Valor inicial del acta: {self.initial['acta']}") 


from .models import ActaViaDiplomado,ActaExcelencia

class ActaViaDiplomadoForm(forms.ModelForm):
    class Meta:
        model = ActaViaDiplomado
        fields = [
            'carrera', 'perperiodo', 'acta', 'estudiante', 'titulo', 
            'lugar', 'fechadefensa', 'horainicio', 'horafin','presidente', 'secretario', 'vocal_1', 'vocal_2','modalidad' ,
            'valor_1', 'valor_2', 'valor_3', 'totalnota'
        ]  

        widgets = {
            'perperiodo': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'acta': forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'readonly': 'readonly'}),
            'carrera': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'estudiante': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'fechadefensa': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'}),
            'horainicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': 'required'}),
            'horafin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': 'required'}),
            'presidente': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'secretario': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'vocal_1': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'vocal_2': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'modalidad': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'valor_1': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'min': '0', 'max': '40'}),
            'valor_2': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'min': '0', 'max': '30'}),
            'valor_3': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'min': '0', 'max': '30'}),
            'totalnota': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'min': '0', 'max': '100'}),
            
        }
    def clean(self):
        cleaned_data = super().clean()
       
        
        horainicio = cleaned_data.get('horainicio')
        horafin = cleaned_data.get('horafin')
        if horainicio and horafin:
            if horainicio >= horafin:
                self.add_error('horainicio', "La hora de inicio no puede ser mayor o igual a la hora de finalización.")
                self.add_error('horafin', "La hora de inicio no puede ser mayor o igual a la hora de finalización.")
                return cleaned_data
               
    def save(self, commit=True):

        instance = super().save(commit=False)
        instance.acta = self.initial.get('acta', instance.acta) 
        
        if commit:
            instance.save() 

            transferir_datos_via(
                estudiante=instance.estudiante,
                acta=instance.acta,
                titulo=instance.titulo,  
                modalidad=instance.modalidad,
                fecha=instance.fechadefensa,
                periodo=instance.perperiodo,
                nota=instance.totalnota,
                jurado_1=instance.secretario,
                jurado_2=instance.vocal_1,
                jurado_3=instance.vocal_2
            )
        
        return instance
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_initial_acta_number()
        estudiantes_group = Group.objects.get(name="Estudiantes")
        docentes_group = Group.objects.get(name="Docentes")
        presidentes_group = Group.objects.get(name="Presidentes Defensas")
        estudiantes_users = User.objects.filter(groups=estudiantes_group, is_active=True)
        usuarios_con_repositorio = RepositorioTitulados.objects.values_list('estudiante', flat=True) 
        usuarios_con_inv = InvCientifica.objects.filter(
            investado='Aprobado'
            ).filter(Q(user__isnull=False) | Q(user_uno__isnull=False)
                     ).values_list('user', 'user_uno').distinct()
        usuarios_con_inv = list(set(
                [user_id for pair in usuarios_con_inv for user_id in pair if user_id]
            ))
        
        self.fields['estudiante'].queryset = User.objects.filter(
            groups=estudiantes_group
        ).filter(id__in=estudiantes_users
        ).exclude(id__in=usuarios_con_inv
        ).exclude(id__in=usuarios_con_repositorio)
        
        
        INCLUDED_MODALITIES = ['Vía Diplomado']
        self.fields['modalidad'].choices = [
            (choice_value, choice_label)
            for choice_value, choice_label in self.fields['modalidad'].choices
            if choice_label in INCLUDED_MODALITIES
        ]
    
        self.fields['presidente'].queryset = User.objects.filter(groups=presidentes_group, is_active=True)
        self.fields['secretario'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['vocal_1'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['vocal_2'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        
    def _set_initial_acta_number(self):
   
        last_acta = ActaViaDiplomado.objects.order_by('-acta').first()
        if last_acta:
            last_value = int(last_acta.acta)
            new_value = last_value + 1
        else:
            new_value = 1
  
        while ActaViaDiplomado.objects.filter(acta=str(new_value).zfill(5)).exists():
            new_value += 1
        self.initial['acta'] = str(new_value).zfill(5)  # Formatea el nuevo valor
        print(f"Valor inicial del acta: {self.initial['acta']}") 
       

from .utils import transferir_datos_a_repositorio, transferir_datos_via, transferir_datos_grado
class ActaExcelenciaForm(forms.ModelForm):
    class Meta:
        model = ActaExcelencia
        fields = [
            'carrera', 'perperiodo', 'acta', 'estudiante', 
            'lugar', 'fechadefensa', 'horainicio', 'horafin', 'secretario', 'jurado_1', 'jurado_2', 'jurado_3', 'modalidad', 
            'notatotal', 'presidenteacta'
        ]

        widgets = {
            'perperiodo': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'acta': forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'readonly': 'readonly'}),
            'carrera': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'estudiante': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'fechadefensa': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'}),
            'horainicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': 'required'}),
            'horafin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': 'required'}),
            'presidente': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'secretario': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_1': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_2': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_3': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'modalidad': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'notatotal': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'min': '0', 'max': '100'}),
            'presidenteacta': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        horainicio = cleaned_data.get('horainicio')
        horafin = cleaned_data.get('horafin')
        if horainicio and horafin:
            if horainicio >= horafin:
                self.add_error('horainicio', "La hora de inicio no puede ser mayor o igual a la hora de finalización.")
                self.add_error('horafin', "La hora de inicio no puede ser mayor o igual a la hora de finalización.")
        return cleaned_data

    def save(self, commit=True):
       
        instance = super().save(commit=False)
        instance.acta = self.initial.get('acta', instance.acta) 
        
        if commit:
            instance.save() 

          
            transferir_datos_a_repositorio(
                acta=instance.acta,
                estudiante=instance.estudiante,
                modalidad=instance.modalidad,
                fecha=instance.fechadefensa,
                periodo=instance.perperiodo,
                nota=instance.notatotal,
                tutor=instance.secretario,
                jurado_1=instance.jurado_1,
                jurado_2=instance.jurado_2,
                jurado_3=instance.jurado_3
            )
        
        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_initial_acta_number()
        estudiantes_group = Group.objects.get(name="Estudiantes")
        docentes_group = Group.objects.get(name="Docentes")
        presidentes_group = Group.objects.get(name="Presidentes Defensas")
        estudiantes_users = User.objects.filter(groups=estudiantes_group, is_active=True)
        usuarios_con_repositorio = RepositorioTitulados.objects.values_list('estudiante', flat=True) 
        usuarios_con_inv = InvCientifica.objects.filter(
            investado='Aprobado'
            ).filter(Q(user__isnull=False) | Q(user_uno__isnull=False)
                     ).values_list('user', 'user_uno').distinct()
        usuarios_con_inv = list(set(
                [user_id for pair in usuarios_con_inv for user_id in pair if user_id]
            ))
        
        self.fields['estudiante'].queryset = User.objects.filter(
            groups=estudiantes_group
        ).filter(id__in=estudiantes_users
        ).exclude(id__in=usuarios_con_inv
        ).exclude(id__in=usuarios_con_repositorio)
        
        
        INCLUDED_MODALITIES = ['Excelencia Academica']
        self.fields['modalidad'].choices = [
            (choice_value, choice_label)
            for choice_value, choice_label in self.fields['modalidad'].choices
            if choice_label in INCLUDED_MODALITIES
        ]
       
        self.fields['presidenteacta'].queryset = User.objects.filter(groups=presidentes_group, is_active=True)
        self.fields['secretario'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_1'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_2'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_3'].queryset = User.objects.filter(groups=docentes_group, is_active=True)

    def _set_initial_acta_number(self):
        last_acta = ActaExcelencia.objects.order_by('-acta').first()
        if last_acta:
            last_value = int(last_acta.acta)
            new_value = last_value + 1
        else:
            new_value = 1
      
        while ActaExcelencia.objects.filter(acta=str(new_value).zfill(5)).exists():
            new_value += 1
        self.initial['acta'] = str(new_value).zfill(5)
        
#actas defensa publica
class ActaPrivadaForm(forms.ModelForm):
    class Meta:
        model = ActaPrivada
        fields = [
            'perperiodo','acta', 'carrera', 'estudiante', 'estudiante_uno',  'titulo', 'lugar', 
            'fechadefensa', 'horainicio', 'horafin', 'tutor', 
            'jurado_1', 'jurado_2', 'jurado_3', 'modalidad', 
            'resultado','calificacion1', 'observacion_1', 'observacion_2', 'observacion_3'
        ]
        labels = {
            'perperiodo': 'Periodo y Gestión',
            'acta': 'Número de Acta',
            'carrera': 'Carrera',
            'estudiante': 'Postulante',
            'estudiante_uno': 'Postulante dos',
          
            'titulo': 'Título del Proyecto',
            'lugar': 'Lugar de Defensa',
            'fechadefensa': 'Fecha de Defensa',
            'horainicio': 'Hora de Inicio',
            'horafin': 'Hora de Finalización',
            'tutor': 'Seleccione al Tutor Designado',
            'jurado_1': 'Primer Tribunal Designado',
            'jurado_2': 'Segundo Tribunal Designado',
            'jurado_3': 'Tercer Tribunal Designado',
            'modalidad': 'Seleccione Modalidad',
            'resultado': 'Resultado de la Defensa',
            'calificacion1': 'Calificacion',
            'observacion_1': 'Observación del Primer Tribunal',
            'observacion_2': 'Observación del Segundo Tribunal',
            'observacion_3': 'Observación del Tercer Tribunal',
        }
        widgets = {
            'perperiodo': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'acta': forms.TextInput(attrs={'class': 'form-control', 'required': 'required', 'readonly': 'readonly'}),
            'carrera': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'estudiante': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'estudiante_uno': forms.Select(attrs={'class': 'form-select'}),
           
            'titulo': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'fechadefensa': forms.DateInput(attrs={'type': 'date', 'class': 'form-control', 'required': 'required'}),
            'horainicio': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': 'required'}),
            'horafin': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control', 'required': 'required'}),
            'tutor': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_1': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_2': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'jurado_3': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'modalidad': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'resultado': forms.Select(attrs={'class': 'form-select', 'required': 'required'}),
            'calificacion1': forms.NumberInput(attrs={'class': 'form-control', 'required': 'required', 'min': '0', 'max': '30'}),
            'observacion_1': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'required': 'required'}),
            'observacion_2': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'required': 'required'}),
            'observacion_3': forms.Textarea(attrs={'rows': 3, 'class': 'form-control', 'required': 'required'}),
        }
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_initial_acta_number()
        estudiantes_group = Group.objects.get(name="Estudiantes")
        estudiantes_users = User.objects.filter(groups=estudiantes_group, is_active=True)
        docentes_group = Group.objects.get(name="Docentes")
        
        usuarios_con_repositorio = RepositorioTitulados.objects.values_list('estudiante', flat=True) 
        usuarios_con_resultado_Suficiente = ActaPrivada.objects.filter(resultado='Suficiente').values_list('estudiante', flat=True).distinct() 
        usuarios_con_proyecto_final = ProyectoFinal.objects.filter(estado='Aprobado').values_list('estudiante', flat=True).distinct()
        usuarios_con_resultado_Suficienteperfil = ActaProyectoPerfil.objects.filter(resultado='Suficiente').values_list('estudiante', flat=True).distinct() 
        
        #usuarios_uno_con_repositorio = RepositorioTitulados.objects.values_list('estudiante_uno') 
        #usuarios_uno_con_resultado_Suficiente = ActaPrivada.objects.filter(resultado='Suficiente').values_list('estudiante_uno').distinct() 
        usuarios_uno_con_proyecto_final = ProyectoFinal.objects.filter(estado='Aprobado').values_list('estudiante_uno').distinct()
        usuarios_uno_con_resultado_Suficienteperfil = ActaProyectoPerfil.objects.filter(resultado='Suficiente').values_list('estudiante_uno').distinct() 
        
        #usuarios_dos_con_repositorio = RepositorioTitulados.objects.values_list('estudiante_dos', flat=True) 
        #usuarios_dos_con_resultado_Suficiente = ActaPrivada.objects.filter(resultado='Suficiente').values_list('estudiante_dos', flat=True).distinct() 
        
        self.fields['estudiante'].queryset = User.objects.filter(
            groups=estudiantes_group
        ).exclude(
            id__in=usuarios_con_repositorio
        ).filter(
            id__in=estudiantes_users
        ).exclude(
            id__in=usuarios_con_resultado_Suficiente
        ).filter(
            id__in=usuarios_con_resultado_Suficienteperfil
        ).filter(
            id__in=usuarios_con_proyecto_final
        )
        self.fields['estudiante_uno'].queryset = User.objects.filter(
            groups=estudiantes_group
        ).filter(
            id__in=estudiantes_users
        ).filter(
            id__in=usuarios_uno_con_resultado_Suficienteperfil
        ).filter(
            id__in=usuarios_uno_con_proyecto_final
        )
            
        INCLUDED_MODALITIES = ['Trabajo Dirigido', 'Proyecto de Grado', 'Tesis de Grado']
        self.fields['modalidad'].choices = [
            (choice_value, choice_label)
            for choice_value, choice_label in self.fields['modalidad'].choices
            if choice_label in INCLUDED_MODALITIES
        ]
        
        INCLUDED_RESULT = ['Insuficiente', 'Suficiente']
        self.fields['resultado'].choices = [
            (choice_value, choice_label)
            for choice_value, choice_label in self.fields['resultado'].choices
            if choice_label in INCLUDED_RESULT
        ]
        # Filtra los usuarios del grupo "Docentes"
        self.fields['tutor'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_1'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_2'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_3'].queryset = User.objects.filter(groups=docentes_group)
        
    def _set_initial_acta_number(self):
   
        last_acta = ActaPrivada.objects.order_by('-acta').first()
        if last_acta:
            last_value = int(last_acta.acta)
            new_value = last_value + 1
        else:
            new_value = 1
    
        while ActaPublica.objects.filter(acta=str(new_value).zfill(5)).exists():
            new_value += 1
        self.initial['acta'] = str(new_value).zfill(5)  
        print(f"Valor inicial del acta: {self.initial['acta']}") 
        
    def clean(self):
        cleaned_data = super().clean()
        horainicio = cleaned_data.get('horainicio')
        horafin = cleaned_data.get('horafin')
        if horainicio and horafin:
            if horainicio >= horafin:
                self.add_error('horainicio', "La hora de inicio no puede ser mayor o igual a la hora de finalización.")
                self.add_error('horafin', "La hora de inicio no puede ser mayor o igual a la hora de finalización.")
                return cleaned_data
    
    def save(self, commit=True):
       
        self.instance.acta = self.initial['acta'] 

        return super().save(commit)
    
class ActaGradoForm(forms.ModelForm):
    class Meta:
        model = ActaGrado
        fields = [
            'carrera', 'perperiodo', 'acta', 'estudiante', 'area', 'lugar', 'campus', 'espacio',
            'fechadefensa', 'horainicio', 'horafin', 'nota',
            'area_1', 'lugar_1', 'campus_1', 'espacio_1', 'fechadefensa_1', 'horainicio_1', 'horafin_1', 'nota_1',
            'area_2', 'lugar_2', 'campus_2', 'espacio_2', 'fechadefensa_2', 'horainicio_2', 'horafin_2', 'nota_2',
            'area_3', 'lugar_3', 'campus_3', 'espacio_3', 'fechadefensa_3', 'horainicio_3', 'horafin_3', 'nota_3',
            'presidenteacta', 'jurado_1', 'jurado_2', 'jurado_3', 'modalidad','fecha', 'notatotal'
        ]
        labels = {
            'carrera': 'Carrera',
            'perperiodo': 'Periodo y Gestión',
            'acta': 'Número de Acta',
            'estudiante': 'Estudiante',
            'area': 'Seleccione el Área',
            'lugar': 'Lugar',
            'campus': 'Establecimiento',
            'espacio': 'Sitio de evaluación',
            'fechadefensa': 'Fecha de Defensa',
            'horainicio': 'Hora de Inicio',
            'horafin': 'Hora de Fin',
            'nota': 'Nota',
            'area_1': 'Seleccione el Área ',
            'lugar_1': 'Lugar',
            'campus_1': 'Establecimiento',
            'espacio_1': 'Sitio de evaluación',
            'fechadefensa_1': 'Fecha de Defensa',
            'horainicio_1': 'Hora de Inicio',
            'horafin_1': 'Hora de Fin',
            'nota_1': 'Nota',
            'area_2': 'Seleccione el Área',
            'lugar_2': 'Lugar',
            'campus_2': 'Establecimiento',
            'espacio_2': 'Sitio de evaluación',
            'fechadefensa_2': 'Fecha de Defensa',
            'horainicio_2': 'Hora de Inicio',
            'horafin_2': 'Hora de Fin',
            'nota_2': 'Nota ',
            'area_3': 'Seleccione el Área',
            'lugar_3': 'Lugar',
            'campus_3': 'Establecimiento',
            'espacio_3': 'Sitio de evaluación',
            'fechadefensa_3': 'Fecha de Defensa',
            'horainicio_3': 'Hora de Inicio',
            'horafin_3': 'Hora de Fin',
            'nota_3': 'Nota',
            'presidenteacta': 'Presidente del Acta',
            'jurado_1': '1er. Tribunal',
            'jurado_2': '2do. Tribunal',
            'jurado_3': '3er. Tribunal',
            'modalidad': 'Seleccione Una Modalidad',
            'fecha': 'Fecha de Defensa General',
            'notatotal': 'Nota Total',
        }
        widgets = {
            'carrera': forms.Select(attrs={'class': 'form-control'}),
            'perperiodo': forms.Select(attrs={'class': 'form-control'}),
            'acta': forms.TextInput(attrs={'class': 'form-control', 'required': 'required'}),
            'estudiante': forms.Select(attrs={'class': 'form-control'}),
            'area': forms.Select(attrs={'class': 'form-control'}),
            'lugar': forms.TextInput(attrs={'class': 'form-control'}),
            'campus': forms.TextInput(attrs={'class': 'form-control'}),
            'espacio': forms.TextInput(attrs={'class': 'form-control'}),
            'fechadefensa': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'horainicio': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'horafin': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'nota': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '15'}),
            'area_1': forms.Select(attrs={'class': 'form-control'}),
            'lugar_1': forms.TextInput(attrs={'class': 'form-control'}),
            'campus_1': forms.TextInput(attrs={'class': 'form-control'}),
            'espacio_1': forms.TextInput(attrs={'class': 'form-control'}),
            'fechadefensa_1': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'horainicio_1': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'horafin_1': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'nota_1': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '15'}),
            'area_2': forms.Select(attrs={'class': 'form-control'}),
            'lugar_2': forms.TextInput(attrs={'class': 'form-control'}),
            'campus_2': forms.TextInput(attrs={'class': 'form-control'}),
            'espacio_2': forms.TextInput(attrs={'class': 'form-control'}),
            'fechadefensa_2': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'horainicio_2': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'horafin_2': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'nota_2': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '30'}),
            'area_3': forms.Select(attrs={'class': 'form-control'}),
            'lugar_3': forms.TextInput(attrs={'class': 'form-control'}),
            'campus_3': forms.TextInput(attrs={'class': 'form-control'}),
            'espacio_3': forms.TextInput(attrs={'class': 'form-control'}),
            'fechadefensa_3': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'horainicio_3': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'horafin_3': forms.TimeInput(attrs={'class': 'form-control', 'type': 'time'}),
            'nota_3': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '40'}),
            'presidenteacta': forms.Select(attrs={'class': 'form-control'}),
            'jurado_1': forms.Select(attrs={'class': 'form-control'}),
            'jurado_2': forms.Select(attrs={'class': 'form-control'}),
            'jurado_3': forms.Select(attrs={'class': 'form-control'}),
            'modalidad': forms.Select(attrs={'class': 'form-control'}),
            'fecha': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'notatotal': forms.NumberInput(attrs={'class': 'form-control', 'min': '0', 'max': '100'}),
        }
    def clean(self):
        cleaned_data = super().clean()
        
    
        hora_pairs = [
            ('horainicio', 'horafin'),
            ('horainicio_1', 'horafin_1'),
            ('horainicio_2', 'horafin_2'),
            ('horainicio_3', 'horafin_3'),
        ]

        for start_field, end_field in hora_pairs:
            horainicio = cleaned_data.get(start_field)
            horafin = cleaned_data.get(end_field)
            
            if horainicio and horafin and horainicio >= horafin:
                self.add_error(start_field, "La hora de inicio no puede ser mayor o igual a la hora de finalización.")
                self.add_error(end_field, "La hora de inicio no puede ser mayor o igual a la hora de finalización.")

        return cleaned_data

    def save(self, commit=True):
      
        instance = super().save(commit=False)
        instance.acta = self.initial.get('acta', instance.acta) 
        
        if commit:
            instance.save()  
            
            transferir_datos_grado(
                acta=instance.acta,
                estudiante=instance.estudiante,
                modalidad=instance.modalidad,
                fecha=instance.fecha,
                periodo=instance.perperiodo,
                nota=instance.notatotal,
                jurado_1=instance.jurado_1,
                jurado_2=instance.jurado_2,
                jurado_3=instance.jurado_3
            )
        
        return instance

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_initial_acta_number()
        estudiantes_group = Group.objects.get(name="Estudiantes")
        docentes_group = Group.objects.get(name="Docentes")
        presidentes_group = Group.objects.get(name="Presidentes Defensas")
        estudiantes_users = User.objects.filter(groups=estudiantes_group, is_active=True)
        usuarios_con_repositorio = RepositorioTitulados.objects.values_list('estudiante', flat=True) 
        usuarios_con_inv = InvCientifica.objects.filter(
            investado='Aprobado'
            ).filter(Q(user__isnull=False) | Q(user_uno__isnull=False)
                     ).values_list('user', 'user_uno').distinct()
        usuarios_con_inv = list(set(
                [user_id for pair in usuarios_con_inv for user_id in pair if user_id]
            ))
        
        self.fields['estudiante'].queryset = User.objects.filter(
            groups=estudiantes_group
        ).filter(id__in=estudiantes_users
        ).exclude(id__in=usuarios_con_inv
        ).exclude(id__in=usuarios_con_repositorio)
        
        
        INCLUDED_MODALITIES = ['Examen de Grado']
        self.fields['modalidad'].choices = [
            (choice_value, choice_label)
            for choice_value, choice_label in self.fields['modalidad'].choices
            if choice_label in INCLUDED_MODALITIES
        ]
   
        self.fields['presidenteacta'].queryset = User.objects.filter(groups=presidentes_group, is_active=True)
        self.fields['jurado_1'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_2'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_3'].queryset = User.objects.filter(groups=docentes_group, is_active=True)

    def _set_initial_acta_number(self):
        last_acta = ActaGrado.objects.order_by('-acta').first()
        if last_acta:
            last_value = int(last_acta.acta)
            new_value = last_value + 1
        else:
            new_value = 1
       
        while ActaGrado.objects.filter(acta=str(new_value).zfill(5)).exists():
            new_value += 1
        self.initial['acta'] = str(new_value).zfill(5)
        

class ActividadControlForm(forms.ModelForm):
    class Meta:
        model = HabilitarProyectoFinal
        fields = ['estudiante','estudiante_uno', 'tutor', 'jurado_1', 'jurado_2', 'jurado_3', 'modalidad']
        labels = {
            'estudiante': 'Seleccionar Postulante',
            'estudiante_uno': 'Postulante dos',
            'tutor': 'Seleccione al Tutor Designado',
            'jurado_1': 'Primero Tribunal Designado',
            'jurado_2': 'Segundo Tribunal Designado',
            'jurado_3': 'Tercer Tribunal Designado',
            'modalidad': 'Seleccione modalidad ',
        }
        widgets = {
            'estudiante': forms.Select(attrs={'class': 'form-select'}),
            'estudiante_uno': forms.Select(attrs={'class': 'form-select'}),
            'tutor': forms.Select(attrs={'class': 'form-select'}),
            'jurado_1': forms.Select(attrs={'class': 'form-select'}),
            'jurado_2': forms.Select(attrs={'class': 'form-select'}),
            'jurado_3': forms.Select(attrs={'class': 'form-select'}),
            'modalidad': forms.Select(attrs={'class': 'form-select'})
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        estudiantes_group = Group.objects.get(name="Estudiantes")
        docentes_group = Group.objects.get(name="Docentes")
        usuarios_con_actividad = HabilitarProyectoFinal.objects.values_list('estudiante', flat=True)
        usuarios_con_perfil_aprobado = ActaProyectoPerfil.objects.filter(resultado='Suficiente').values_list('estudiante', flat=True).distinct()
        self.fields['estudiante'].queryset = User.objects.filter(
        groups=estudiantes_group,
        is_active=True  
        ).exclude(id__in=usuarios_con_actividad).filter(id__in=usuarios_con_perfil_aprobado)
       
        self.fields['estudiante_uno'].queryset = User.objects.filter(
            groups=estudiantes_group,
            is_active=True  
            ).exclude(id__in=usuarios_con_actividad)#.filter(id__in=usuarios_con_perfil_aprobado)
      
        self.fields['tutor'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_1'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_2'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_3'].queryset = User.objects.filter(groups=docentes_group)
          
class EditarActividadControlForm(forms.ModelForm):
    class Meta:
        model = HabilitarProyectoFinal
        fields = ['estudiante', 'estudiante_uno', 'tutor', 'jurado_1', 'jurado_2', 'jurado_3','modalidad']
        labels = {
            'estudiante': 'Postulante',
            'estudiante_uno': 'Postulante dos',
            'tutor': 'Seleccione al Tutor Designado',
            'jurado_1': 'Primero Tribumal Designado',
            'jurado_2': 'Segundo Tribumal Designado',
            'jurado_3': 'Tercer Tribumal Designado',
            'modalidad': 'Seleccione modalidad ',
        }
        widgets = {
            'estudiante': forms.Select(attrs={'class': 'form-select'}),
            'estudiante_uno': forms.Select(attrs={'class': 'form-select'}),
            'tutor': forms.Select(attrs={'class': 'form-select'}),
            'jurado_1': forms.Select(attrs={'class': 'form-select'}),
            'jurado_2': forms.Select(attrs={'class': 'form-select'}),
            'jurado_3': forms.Select(attrs={'class': 'form-select'}),
            'modalidad': forms.Select(attrs={'class': 'form-select'})
        }
        
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        docentes_group = Group.objects.get(name="Docentes")
        self.fields['tutor'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_1'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_2'].queryset = User.objects.filter(groups=docentes_group)
        self.fields['jurado_3'].queryset = User.objects.filter(groups=docentes_group)
        
      
        if self.instance and self.instance.pk:
          self.fields['estudiante'].disabled = True
          self.fields['estudiante_uno'].disabled = True
             
class ActividadForm(forms.ModelForm):
    class Meta:
        model = ProyectoFinal
        fields = ['estudiante', 'estudiante_uno', 'tutor', 'jurado_1', 'jurado_2', 'jurado_3', 'titulo', 'resumen', 'modalidad', 'guia_externo', 'documentacion']
        widgets = {
            'estudiante': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'estudiante_uno': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'tutor': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'jurado_1': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'jurado_2': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'jurado_3': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'modalidad': forms.Select(attrs={'class': 'form-control', 'disabled': 'disabled'}),
            'titulo': forms.TextInput(attrs={'class': 'form-control'}),
            'resumen': forms.Textarea(attrs={'class': 'form-control', 'rows': 4}),
            'guia_externo': forms.TextInput(attrs={'class': 'form-control'}),
            'documentacion': forms.FileInput(attrs={'class': 'form-control-file'}),
        }

class ActComentarioForm(forms.ModelForm):
    class Meta:
        model = ComentarioProFinal
        fields = ['actcomentario','actdocorregido'] 
        widgets = {
            'actcomentario': forms.Textarea(attrs={'class': 'comentari-field'}),
        }
        

from .models import HabilitarTribunalesPerfil

class HabilitarTribunalesPerfilForm(forms.ModelForm):
    class Meta:
        model = HabilitarTribunalesPerfil
        fields = ['user', 'user_uno', 'pertitulo', 'permodalidad', 'tutor', 'jurado_1', 'jurado_2', 'jurado_3']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control', 'id': 'id_user'}),
            'user_uno': forms.Select(attrs={'class': 'form-control', 'id': 'id_user_uno'}),
            'pertitulo': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_pertitulo'}),
            'permodalidad': forms.Select(attrs={'class': 'form-control', 'id': 'id_permodalidad'}),
            'tutor': forms.Select(attrs={'class': 'form-control'}),
            'jurado_1': forms.Select(attrs={'class': 'form-control'}),
            'jurado_2': forms.Select(attrs={'class': 'form-control'}),
            'jurado_3': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'user': 'Seleccione el Postulante Principal ',
            'user_uno': 'Postulante dos',
            'pertitulo': 'Titulo del PRoyecto',
            'tutor': 'Seleccione al Tutor',
            'jurado_1': 'Primero Tribumal',
            'jurado_2': 'Segundo Tribumal',
            'jurado_3': 'Tercer Tribumal',
            'permodalidad': 'Modalidad ',
        }
     
    def __init__(self, *args, **kwargs):
        super(HabilitarTribunalesPerfilForm, self).__init__(*args, **kwargs)
        estudiantes_group = Group.objects.get(name='Estudiantes')
        
        INCLUDED_MODALITIES = ['Trabajo Dirigido', 'Proyecto de Grado', 'Tesis de Grado']
        self.fields['permodalidad'].choices = [
            (choice_value, choice_label)
            for choice_value, choice_label in self.fields['permodalidad'].choices
            if choice_label in INCLUDED_MODALITIES
        ]
    
        docentes_group = Group.objects.get(name="Docentes")
        self.fields['tutor'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_1'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_2'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_3'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
       
        activo_users = HabilitarTribunalesPerfil.objects.values_list('user')
        aprobados = PerfilProyecto.objects.filter(perestado='Aprobado').values_list('user', flat=True)
        aprobados_uno = PerfilProyecto.objects.filter(perestado='Aprobado').values_list('user_uno', flat=True)
        
        acta_users = ActaProyectoPerfil.objects.values_list('estudiante')
        

        self.fields['user'].queryset = User.objects.filter(
        groups=estudiantes_group,
        ).filter(id__in=aprobados,
        ).exclude(id__in=acta_users,
        ).exclude(id__in=activo_users)
        
        self.fields['user_uno'].queryset = User.objects.filter(
        groups=estudiantes_group,
        ).filter(id__in=aprobados_uno
        )
        
        
        
class EditarHabilitarTribunalesPerfilForm(forms.ModelForm):
    class Meta:
        model = HabilitarTribunalesPerfil
        fields = ['user', 'user_uno', 'pertitulo', 'permodalidad', 'tutor', 'jurado_1', 'jurado_2', 'jurado_3']
        widgets = {
            'user': forms.Select(attrs={'class': 'form-control', 'id': 'id_user'}),
            'user_uno': forms.Select(attrs={'class': 'form-control', 'id': 'id_user_uno'}),
            'pertitulo': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_pertitulo'}),
            'permodalidad': forms.Select(attrs={'class': 'form-control', 'id': 'id_permodalidad'}),
            'tutor': forms.Select(attrs={'class': 'form-control'}),
            'jurado_1': forms.Select(attrs={'class': 'form-control'}),
            'jurado_2': forms.Select(attrs={'class': 'form-control'}),
            'jurado_3': forms.Select(attrs={'class': 'form-control'}),
        }
        labels = {
            'user': 'Seleccione el Postulante Principal ',
            'user_uno': 'Postulante dos',
            'pertitulo': 'Titulo del PRoyecto',
            'tutor': 'Seleccione al Tutor',
            'jurado_1': 'Primero Tribumal',
            'jurado_2': 'Segundo Tribumal',
            'jurado_3': 'Tercer Tribumal',
            'permodalidad': 'Modalidad ',
        }
     
    def __init__(self, *args, **kwargs):
        super(EditarHabilitarTribunalesPerfilForm, self).__init__(*args, **kwargs)

        estudiantes_group = Group.objects.get(name='Estudiantes')
        
        INCLUDED_MODALITIES = ['Trabajo Dirigido', 'Proyecto de Grado', 'Tesis de Grado']
        self.fields['permodalidad'].choices = [
            (choice_value, choice_label)
            for choice_value, choice_label in self.fields['permodalidad'].choices
            if choice_label in INCLUDED_MODALITIES
        ]
       
        docentes_group = Group.objects.get(name="Docentes")
        self.fields['tutor'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_1'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_2'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
        self.fields['jurado_3'].queryset = User.objects.filter(groups=docentes_group, is_active=True)
      
        aprobados = PerfilProyecto.objects.filter(perestado='Aprobado').values_list('user', flat=True)
        
        acta_users = ActaProyectoPerfil.objects.values_list('estudiante')
        
        self.fields['user'].queryset = User.objects.filter(
        groups=estudiantes_group,
        ).filter(id__in=aprobados)
        
       
        
class ActaPerForm(forms.ModelForm):
    class Meta:
        model = ActaProyectoPerfil
        fields = ['docrespaldo']
        widgets = {
            'docrespaldo': forms.FileInput(attrs={'class': 'form-control'})
        }
      
class ActaPrivForm(forms.ModelForm):
    class Meta:
        model = ActaPrivada
        fields = ['docrespaldo']
        widgets = {
            'docrespaldo': forms.FileInput(attrs={'class': 'form-control'})
        }
      
class ActaPubForm(forms.ModelForm):
    class Meta:
        model = ActaPublica
        fields = ['docrespaldo']
        widgets = {
            'docrespaldo': forms.FileInput(attrs={'class': 'form-control'})
        }
      
class ActaViadiploForm(forms.ModelForm):
    class Meta:
        model = ActaViaDiplomado
        fields = ['docrespaldo']
        widgets = {
            'docrespaldo': forms.FileInput(attrs={'class': 'form-control'})
        }
      
class ActaExcelenForm(forms.ModelForm):
    class Meta:
        model = ActaExcelencia
        fields = ['docrespaldo']
        widgets = {
            'docrespaldo': forms.FileInput(attrs={'class': 'form-control'})
        }
   
class ActaGraForm(forms.ModelForm):
    class Meta:
        model = ActaGrado
        fields = ['docrespaldo']
        widgets = {
            'docrespaldo': forms.FileInput(attrs={'class': 'form-control'})
        }
   

