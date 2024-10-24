from django import forms
from django.contrib.auth.forms import UserCreationForm
from django.core.exceptions import ValidationError
from django.utils.translation import gettext_lazy as _
from .models import User
from django.contrib.auth.models import Group, Permission
from django.contrib.auth import authenticate
from django.core.files import File
from seg_mod_graduacion.models import Estudiante, Docente
from gestion_usuarios.models import User

class GroupForm(forms.ModelForm):
    class Meta:
        model = Group
        fields = ['name']

# Validaciones para inicio de sesión
class CustomLoginForm(forms.Form):
    email = forms.EmailField(
        max_length=254,
        widget=forms.TextInput(attrs={'placeholder': 'Correo Electrónico'}),
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'placeholder': 'Contraseña'}),
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.first_attempt = True

    def clean(self):
        cleaned_data = super().clean()
        email = cleaned_data.get('email')
        password = cleaned_data.get('password')

        if email and password:
            user = authenticate(username=email, password=password)
            if user is None:
                self.first_attempt = False
                if not User.objects.filter(email=email).exists():
                    self.add_error('email', "El correo electrónico no existe.")
                else:
                    self.add_error('password', "La contraseña es incorrecta.")
            elif not user.is_active:
                self.first_attempt = False
                raise forms.ValidationError("Esta cuenta está inactiva.")
        return cleaned_data

# Validaciones para registrar nuevo usuario
class CustomUserCreationForm(UserCreationForm):
    groups = forms.ModelMultipleChoiceField(
        queryset=Group.objects.all(),
        required=False,
        widget=forms.CheckboxSelectMultiple
    )
    class Meta:
        model = User
        fields = ('email', 'nombre', 'apellido', 'apellidoM', 'is_active', 'is_staff','is_superuser', 'password1', 'password2', 'groups')
        widgets = {
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input danger-switch', 'role': 'switch', 'id': 'flexSwitchCheckActive'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input danger-switch', 'role': 'switch', 'id': 'flexSwitchCheckStaff'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input danger-switch', 'role': 'switch', 'id': 'flexSwitchCheckSuperuser'}),
            }
        labels = {
            'apellido': 'Apellido Paterno',
            'apellidoM': 'Apellido Materno',
        }
        
        
    def clean_password1(self):
        password1 = self.cleaned_data.get("password1")

        if len(password1) < 8:
            raise ValidationError(_("La contraseña debe tener al menos 8 caracteres."))

        if not any(char.isupper() for char in password1):
            raise ValidationError(_("La contraseña debe contener al menos una mayúscula."))

        if password1.isdigit():
            raise ValidationError(_("La contraseña no puede consistir solo en números."))

        return password1

    def clean_password2(self):
        password1 = self.cleaned_data.get("password1")
        password2 = self.cleaned_data.get("password2")

        if password1 and password2 and password1 != password2:
            raise ValidationError(_("Las contraseñas no coinciden."))

        return password2

    def clean_email(self):
        email = self.cleaned_data.get("email")

        if User.objects.filter(email=email).exists():
            raise ValidationError(_("Ya existe un usuario con este correo electrónico."))

        return email

    def save(self, commit=True):
        user = super().save(commit=False)
        user.imagen = File(open('static/img/SINFOTO.webp', 'rb'))  # Asigna la imagen por defecto
        if commit:
            user.save()
            selected_groups = self.cleaned_data.get('groups')
            if selected_groups:
                user.groups.set(selected_groups)

                # Verifica si el usuario pertenece al grupo "Estudiantes" o "Docentes"
                if 'Estudiantes' in selected_groups.values_list('name', flat=True):
                    # Crea una instancia de Estudiante
                    Estudiante.objects.create(user=user)
                elif 'Docentes' in selected_groups.values_list('name', flat=True):
                    # Crea una instancia de Docente
                    Docente.objects.create(user=user)

        return user
    def get_available_groups(self):
        return Group.objects.exclude(id__in=self.instance.groups.values_list('id', flat=True))

# Formulario para actualizar usuario
class CustomClearableFileInput(forms.ClearableFileInput):
    # Define aquí tu widget personalizado si es necesario
    pass
class CustomUserChangeForm(forms.ModelForm):
    
    class Meta:
        model = User
        fields = ('email', 'nombre', 'apellido', 'apellidoM', 'imagen', 'fecha_nac', 'telefono', 'is_active', 'is_staff','is_superuser', 'groups')
        widgets = {
            'imagen': CustomClearableFileInput(),
            'is_active': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch', 'id': 'flexSwitchCheckActive'}),
            'is_staff': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch', 'id': 'flexSwitchCheckStaff'}),
            'is_superuser': forms.CheckboxInput(attrs={'class': 'form-check-input', 'role': 'switch', 'id': 'flexSwitchCheckSuperuser'}),
        }
        labels = {
            'apellido': 'Apellido Paterno',
            'apellidoM': 'Apellido Materno',
        }
        
    def save(self, commit=True):
        user = super().save(commit=False)

        if commit:
            user.save()

            selected_groups = self.cleaned_data.get('groups')
            current_groups = user.groups.values_list('name', flat=True)

            if selected_groups:
                user.groups.set(selected_groups)

                # Si el usuario pertenece al grupo de Estudiantes
                if 'Estudiantes' in selected_groups.values_list('name', flat=True):
                    # Si ya existe una instancia de Docente, elimínala
                    Docente.objects.filter(user=user).delete()

                    # Si no existe una instancia de Estudiante, créala
                    if not Estudiante.objects.filter(user=user).exists():
                        Estudiante.objects.create(user=user)

                # Si el usuario pertenece al grupo de Docentes
                elif 'Docentes' in selected_groups.values_list('name', flat=True):
                    # Si ya existe una instancia de Estudiante, elimínala
                    Estudiante.objects.filter(user=user).delete()

                    # Si no existe una instancia de Docente, créala
                    if not Docente.objects.filter(user=user).exists():
                        Docente.objects.create(user=user)

            # Eliminar las referencias antiguas si el grupo cambia
            if 'Estudiantes' not in selected_groups.values_list('name', flat=True):
                Estudiante.objects.filter(user=user).delete()

            if 'Docentes' not in selected_groups.values_list('name', flat=True):
                Docente.objects.filter(user=user).delete()

        return user


class UserUpdateForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ['imagen', 'nombre', 'apellido', 'apellidoM', 'fecha_nac', 'telefono']
        widgets = {
            'imagen': CustomClearableFileInput(),
            'fecha_nac': forms.DateInput(attrs={'type': 'date'}),
        }
        labels = {
            'imagen': 'Imagen Del Usuario:',
            'nombre': 'Nombres del usuario',
            'apellido': 'Apellido Paterno',
            'apellidoM': 'Apellido Materno',
            'fecha_nac': 'Fecha de Nacimiento',
            'telefono': 'N° Telefono/Celular',
           
        }
        



class EstudianteUpdateForm(forms.ModelForm):
    class Meta:
        model = Estudiante
        fields = ['dni', 'Ru']
        labels = {
            'dni': 'Carnet de Identidad',
            'Ru': 'R.U.'
        }


class DocenteUpdateForm(forms.ModelForm):
    class Meta:
        model = Docente
        fields = ['dni', 'especialidad', 'titulo']
        labels = {
            'dni': 'Carnet de Identidad',
            'especialidad': 'Título',
            'titulo': 'Abreviación ',
        }