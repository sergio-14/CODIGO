from django.contrib import admin

# Register your models here.
from .models import T_Fase, T_Tipo, T_Proyectos_IIISP
# Register interacion social
admin.site.register(T_Fase)
admin.site.register(T_Tipo)
admin.site.register(T_Proyectos_IIISP)


