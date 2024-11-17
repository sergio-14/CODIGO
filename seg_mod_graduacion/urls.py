from django.urls import path
from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import handler403
from .views import handle_permission_denied
from seg_mod_graduacion import views
from .views import ModalidadCreateView, ModalidadListView, ModalidadUpdateView, Pdf_ReporteActaPrivada, Pdf_ReporteActaPublica,Pdf_ReporteActaGrado
from .views import pdf_reporteinv,Pdf_Reporte_InvFiltrado, Pdf_Reporte_Perfiles, Pdf_ReporteActa,Pdf_ReporteActaViadiplomatico, Pdf_ReporteActaExcelencia

handler403 = handle_permission_denied
urlpatterns = [    
    #segguimiento modalidad de graduacion investigacion cientifica
    path('invcientifica/agregar_investigacion/', views.agregar_investigacion, name='agregar_investigacion'),
    path('invcientifica/vista_investigacion/',views.vista_investigacion, name='vista_investigacion'),
    path('invcientifica/ProyectosParaAprobar/', views.ProyectosParaAprobar.as_view(), name='ProyectosParaAprobar'),
    path('AprobarProyecto/<int:proyecto_id>/', views.AprobarProyecto.as_view(), name='AprobarProyecto'),
    path('RechazarProyecto/<int:proyecto_id>/', views.RechazarProyecto.as_view(), name='RechazarProyecto'),
    path('invcientifica/global_settings/', views.global_settings_view, name='global_settings'),
    path('listarinvcientifica/', views.listarinvcientifica, name='listarinvcientifica'),
    path('pdf_reporteinv/<int:pk>/', pdf_reporteinv.as_view(), name='pdf_reporteinv'),
    path('Pdf_Reporte_InvFiltrado', Pdf_Reporte_InvFiltrado.as_view(), name='Pdf_Reporte_InvFiltrado'),
    
    #seguimiento modalidad de graduacion perfil de proyecto
    path('perfil/agregar_perfil/', views.agregar_perfil, name='agregar_perfil'),
    path('perfil/vista_perfil/',views.vista_perfil, name='vista_perfil'),
    path('perfil/PerfilesParaAprobar/', views.PerfilesParaAprobar.as_view(), name='PerfilesParaAprobar'),
    path('AprobarPerfil/<int:proyecto_id>/', views.AprobarPerfil.as_view(), name='AprobarPerfil'),
    path('RechazarPerfil/<int:proyecto_id>/', views.RechazarPerfil.as_view(), name='RechazarPerfil'),
    path('agregar-acta/', views.agregar_actaperfil, name='agregar_actaperfil'),
    path('listarperfiles/', views.listarperfiles, name='listarperfiles'),
    path('reporte-perfiles-pdf/', Pdf_Reporte_Perfiles.as_view(), name='Pdf_Reporte_Perfiles'),
    path('perfil/astas_list', views.actaperfil_list, name='actaperfil_list'),
    path('acta_doc_perfil/<int:acta_id>/Acta_per_doc/', views.Acta_per_doc, name='Acta_per_doc'),
    path('acta_doc_privada/<int:acta_id>/Acta_priv_doc/', views.Acta_priv_doc, name='Acta_priv_doc'),
    path('acta_doc_publica/<int:acta_id>/Acta_prub_doc/', views.Acta_pub_doc, name='Acta_pub_doc'),
    path('acta_doc_ViaDiplomado/<int:acta_id>/Acta_ViaD_doc/', views.Acta_viadiplo_doc, name='Acta_viadiplo_doc'),
    path('acta_doc_Excelencia/<int:acta_id>/Acta_Excelencia_doc/', views.Acta_excel_doc, name='Acta_excel_doc'),
    path('acta_doc_ExGrado/<int:acta_id>/Acta_Exgrado_doc/', views.Acta_grado_doc, name='Acta_grado_doc'),
    path('reporte_acta/<int:pk>/', Pdf_ReporteActa.as_view(), name='Pdf_ReporteActa'),
    
    #seguimiento modalidad de graduacion proyecto final
    path('controlador/actividad_control/nueva/', views.crear_actividad_control, name='crear_actividad_control'),
    path('controlador/editar_actividad_control/<int:pk>/editar/', views.editar_actividad_control, name='editar_actividad_control'),
    path('controlador/lista_actividad_control/', views.lista_actividad_control, name='lista_actividad_control'),
    
    path('proyectofinal/revision/<int:actividad_id>/', views.revisar_actividad, name='revisar_actividad'),
    path('controlador/revision/<int:actividad_id>/', views.revision, name='revision'),
    
    path('controlador/listaractividades/', views.listaractividades, name='listaractividades'),
    path('controlador/listaactividades/', views.listaactividades, name='listaactividades'),
    
    path('proyectofinal/crear_actividad/nueva/', views.crear_actividad, name='crear_actividad'),
    path('proyectofinal/actividad/', views.lista_actividad, name='lista_actividad'),
    path('agregar-actaprivada/', views.agregar_actaprivada, name='agregar_actaprivada'),
    path('agregar-actapublica/', views.agregar_actapublica, name='agregar_actapublica'),
    path('buscar_estudiante_privada/', views.buscar_estudiante_privada, name='buscar_estudiante_privada'),
    path('buscar_estudiante_publica/', views.buscar_estudiante_publica, name='buscar_estudiante_publica'),
    path('buscar_estudiante_paractivar/', views.buscar_estudiante_paractivar, name='buscar_estudiante_paractivar'),
    path('proyectofinal/astas_list_privada', views.actaprivada_list, name='actaprivada_list'),
    path('proyectofinal/astas_list_publica', views.actapublica_list, name='actapublica_list'),
    path('reporte_acta_privada/<int:pk>/', Pdf_ReporteActaPrivada.as_view(), name='Pdf_ReporteActaPrivada'),
    path('reporte_acta_publica/<int:pk>/', Pdf_ReporteActaPublica.as_view(), name='Pdf_ReporteActaPublica'),
    path('reporte_acta_Via_Diplomado/<int:pk>/', Pdf_ReporteActaViadiplomatico.as_view(), name='Pdf_ReporteActaViadiplomatico'),
    path('reporte_acta_Excelencia/<int:pk>/', Pdf_ReporteActaExcelencia.as_view(), name='Pdf_ReporteActaExcelencia'),
    path('reporte_acta_exgrado/<int:pk>/', Pdf_ReporteActaGrado.as_view(), name='Pdf_ReporteActaGrado'),
    
    path('modalidad/modalidadagregar/', ModalidadCreateView.as_view(), name='modalidadagregar'),
    path('modalidades/', ModalidadListView.as_view(), name='listarmodalidades'),
    path('modalidad/editarmodalidad/<int:pk>/', ModalidadUpdateView.as_view(), name='editarmodalidad'),
    
    path('reportes/home_reporte', views.home_reporte, name='home_reporte'),
    
    #para excel
    path('exportar_excel/', views.exportar_excel, name='exportar_excel'),
    path('exportar_excel_perfiles/', views.exportar_excel_perfiles, name='exportar_excel_perfiles'),
    
    
    path('aprobar_actividad/<int:actividad_id>/', views.aprobar_actividad, name='aprobar_actividad'),
    path('habilitar_perfiles/', views.listar_tribunales_perfiles, name='listar_tribunales_perfiles'),
    path('habilitar_perfiles/agregar/', views.agregar_tribunales_perfil, name='agregar_tribunales_perfil'),
    path('habilitar_perfiles/editar/<int:pk>/', views.editar_tribunales_perfil, name='editar_tribunales_perfil'),
    path('filtrartribunales/', views.filtrartribunales, name='filtrartribunales'),
    path('filtraracta/', views.filtraracta, name='filtraracta'), 
    
    path('agregar_viadiplomado/', views.agregar_viadiplomado, name='agregar_viadiplomado'),
    path('proyectofinal/acta_viadiplomado_list', views.actaviadiplomado_list, name='actaviadiplomado_list'),
    path('agregar_Excelencia/', views.agregar_Excelencia, name='agregar_Excelencia'),
    path('proyectofinal/actaexcelencia_list', views.actaexcelencia_list, name='actaexcelencia_list'),
    path('agregar_ExGrado/', views.agregar_Grado, name='agregar_Grado'),
    path('proyectofinal/actagrado_list', views.actagrado_list, name='actagrado_list'),
]
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
