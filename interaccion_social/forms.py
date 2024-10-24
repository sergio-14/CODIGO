from django import forms
from .models import T_Proyectos_IIISP, HabilitarFechas, T_Tipo, T_Fase
from seg_mod_graduacion.models import Gestion,Periodo,Materia,Semestre
from datetime import date
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Layout, Row, Column
from datetime import date
        
#proyectos de interaccion social 
class T_ProyectosForm(forms.ModelForm):
    class Meta:
        model = T_Proyectos_IIISP
        fields = [
            'S_Titulo', 'Fecha_Inicio', 'Fecha_Finalizacion', 'S_Descripcion', 
            'S_Documentacion', 'S_Imagen', 'T_Fase_proyecto', 'T_Gestion', 
            'T_Tipo_Proyecto', 'T_Materia'
        ]
        widgets = {
            'Fecha_Inicio': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'Fecha_Finalizacion': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(T_ProyectosForm, self).__init__(*args, **kwargs)
        
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'S_Titulo',
            Row(
                Column('Fecha_Inicio', css_class='form-group col-md-6 mb-0'),
                Column('Fecha_Finalizacion', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'S_Descripcion',
            'S_Documentacion',
            'S_Imagen',
            Row(
                Column('T_Fase_proyecto', css_class='form-group col-md-6 mb-0'),
                Column('T_Gestion', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('T_Tipo_Proyecto', css_class='form-group col-md-6 mb-0'),
                Column('T_Materia', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
        )

        # Asegurar que todos los campos sean requeridos
        for field in self.fields:
            self.fields[field].required = True
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        # Deshabilitar los campos si la fecha no está dentro del rango permitido
        settings = HabilitarFechas.objects.first()
        if settings:
            hoy = date.today()
            if not (settings.fecha_inicio_habilitacion <= hoy <= settings.fecha_fin_habilitacion):
                for field in self.fields:
                    self.fields[field].disabled = True

#editar proyecto IIISP                  
class EditarT_ProyectosForm(forms.ModelForm):
    class Meta:
        model = T_Proyectos_IIISP
        fields = [
            'S_Titulo', 'Fecha_Inicio', 'Fecha_Finalizacion', 'S_Descripcion', 
            'S_Documentacion', 'S_Imagen', 'T_Fase_proyecto', 'T_Gestion', 
            'T_Tipo_Proyecto', 'T_Materia'
        ]
        widgets = {
            'Fecha_Inicio': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
            'Fecha_Finalizacion': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date', 'class': 'form-control'}),
        }

    def __init__(self, *args, **kwargs):
        super(EditarT_ProyectosForm, self).__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.layout = Layout(
            'S_Titulo',
            Row(
                Column('Fecha_Inicio', css_class='form-group col-md-6 mb-0'),
                Column('Fecha_Finalizacion', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            'S_Descripcion',
            'S_Documentacion',
            'S_Imagen',
            Row(
                Column('T_Fase_proyecto', css_class='form-group col-md-6 mb-0'),
                Column('T_Gestion', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
            Row(
                Column('T_Tipo_Proyecto', css_class='form-group col-md-6 mb-0'),
                Column('T_Materia', css_class='form-group col-md-6 mb-0'),
                css_class='form-row'
            ),
        )

        for field in self.fields:
            self.fields[field].required = True
            self.fields[field].widget.attrs.update({'class': 'form-control'})

        settings = HabilitarFechas.objects.first()
        if settings:
            hoy = date.today()
            if not (settings.fecha_inicio_habilitacion <= hoy <= settings.fecha_fin_habilitacion):
                for field in self.fields:
                    self.fields[field].disabled = True
                
#Habilitacion de fechas 
class IntSocSettingsForm(forms.ModelForm):
    class Meta:
        model = HabilitarFechas
        fields = ['fecha_inicio_habilitacion', 'fecha_fin_habilitacion']
        widgets = {
            'fecha_inicio_habilitacion': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
            'fecha_fin_habilitacion': forms.DateInput(format='%Y-%m-%d', attrs={'type': 'date'}),
        }

    def __init__(self, *args, **kwargs):
        super(IntSocSettingsForm, self).__init__(*args, **kwargs)
        self.fields['fecha_inicio_habilitacion'].input_formats = ['%Y-%m-%d']
        self.fields['fecha_fin_habilitacion'].input_formats = ['%Y-%m-%d']
        
#tipo 
class TipoProyectoForm(forms.ModelForm):
    class Meta:
        model = T_Tipo
        fields = ['S_Tipo']
#fase 
class FaseProyectoForm(forms.ModelForm):
    class Meta:
        model = T_Fase
        fields = ['S_Fase']
#gestion
class GestionForm(forms.ModelForm):
    class Meta:
        model = Gestion
        fields = ['anio']
        labels = {
            'anio': 'Agregar Año',
            }
    def clean_anio(self):
        anio = self.cleaned_data.get('anio')
        if anio < 0:
            raise forms.ValidationError("El año no puede ser negativo.")
        return anio
  
import datetime
  
class PeriodoForm(forms.ModelForm):
    class Meta:
        model = Periodo
        fields = ['numero','gestion']
        labels = {
            'numero': 'periodo',
            'gestion': 'gestion',
            }   
    def clean_numero(self):
        numero = self.cleaned_data.get('numero')
        if numero not in [1, 2]:
            raise forms.ValidationError("Solo se permiten los valores 1 y 2.")
        return numero

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Limitar el queryset de gestion a los últimos 6 años
        current_year = datetime.datetime.today().year
        last_six_years = list(range(current_year, current_year - 6, -1))  # Ajuste a los últimos 6 años
        self.fields['gestion'].queryset = Gestion.objects.filter(anio__in=last_six_years)
        
#semestre
class SemestreForm(forms.ModelForm):
    class Meta:
        model = Semestre
        fields = ['S_Semestre','carrera']
#materia
class MateriaForm(forms.ModelForm):
    class Meta:
        model = Materia
        fields = ['nombre_materia','codigo','semestre','carrera']