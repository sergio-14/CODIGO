from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler403
from repositoriotitulados import views
from .views import TransferirActividadView, pdf_reporte_repositorio

#from .views import crear_repositorio

urlpatterns = [   
    #path('', home, name='home'),            
    path('admrepositorio/transferir_actividad/<int:actividad_id>/', TransferirActividadView.as_view(), name='transferir_actividad'),
    path('admrepositorio/listarepositorios/', views.listarepositorios, name='listarepositorios'),
    path('admrepositorio/listar_actividades_aprovadas/', views.listaractividadesaprovadas, name='listaractividadesaprovadas'),
    path('admrepositorio/actividad_repositorio/<int:pk>/editar/', views.editar_actividad_repositorio, name='editar_actividad_repositorio'),
    
    path('repositoriopublico/actividades/', views.actividad_list, name='actividad_list'),
    
    path('agregar-actividad-repositorio/', views.agregar_actividad_repositorio, name='agregar_actividad_repositorio'),
    
    path('admrepositorio/pdf/', pdf_reporte_repositorio.as_view(), name='pdf_reporte_repositorio'),
    
    path('exportar_excel_repositorios/', views.exportar_excel_repositorios, name='exportar_excel_repositorios'),
    
    
]
