from django.urls import path

from . import views

urlpatterns = [
    path('inicio/<int:id_comunidad>/', views.paginaPrincipal, name='pagina_principal_comunidad'),
    path('elegir_comunidad/', views.elegir_comunidad, name="vista_elegir_comunidad"),
    path('unirse_comunidad/', views.vista_unirse_comunidad, name="vista_unirse_comunidad"),
    path('unirse_comunidad/join', views.acceso_comunidad, name="acceso_comunidad"),
    path('unirse_comunidad/buscador/<int:comunidad_id>/', views.unirse_comunidad_publica, name="acceso_comunidad_publica"),
    path('crear_comunidad/', views.vista_crear_comunidad, name="vista_crear_comunidad"),
    path('comunidad_aleatoria/', views.generar_comunidad_aleatoria, name="comunidad_aleatoria"),
    path('nueva_comunidad/', views.crear_comunidad, name="nueva_comunidad"),
    path('eliminar_comunidad/', views.eliminar_comunidad, name="eliminar_comunidad"),
    path('abandonar_comunidad/', views.abandonar_comunidad, name="abandonar_comunidad"),
    path('configuracion/', views.vista_configuracion_comunidad, name="configuracion_comunidad"),
    path('configuracion/general', views.vista_configuracion_comunidad_general, name="configuracion_general_comunidad"),
    path('configuracion/equipos', views.vista_configuracion_comunidad_equipos, name="configuracion_general_equipos"),
    path('configuracion/comunidad', views.vista_configuracion_comunidad_mercado, name="configuracion_general_mercado"),
    path('configuracion/ofertas', views.vista_configuracion_comunidad_ofertas, name="configuracion_general_ofertas"),
    path('configuracion/actualizar', views.actualizar_configuracion_comunidad,
         name="actualizar_configuracion_comunidad"),
    path('configuracion/jornadas', views.vista_configuracion_comunidad_jornadas, name="configuracion_general_jornadas"),
    path('configuracion/bonificaciones', views.vista_configuracion_comunidad_bonificaciones,
         name="configuracion_general_bonificaciones"),
    path('clasificacion', views.clasificacion, name="clasificacion"),
    path('jugadores/', views.lista_jugadores_comunidad, name="lista_jugadores_comunidad"),
    path('jugadores/favoritos', views.lista_jugadores_favoritos, name="filtrar_favoritos"),
    path('jugadores/filtrar', views.filtrar_listado_jugadores, name="filtrar_jugadores"),
    path('noticia/guardar', views.crear_noticia, name="crear_nueva_noticia"),
    path('mercado/', views.mercado, name="mercado"),
    path('clasificacion/', views.clasificacion, name="clasificacion"),
    path('favoritos/guardar/<str:nombre>/', views.agregar_eliminar_jugador_favorito, name="agregar_favorito"),
    path('crear-plantilla/', views.CrearPlantillaView.as_view(), name='crear_plantilla'),
    path('jugadores-plantilla/', views.jugadoresPlantilla, name='jugadores-plantilla'),
    #?VISTA PARA OBTENER LA PLANTILLA EXISTENTE
    path('obtener-plantilla-existente/', views.obtener_plantilla_existente, name='obtener-plantilla-existente'),
    path('guardar_plantilla/', views.guardar_plantilla, name='guardar_plantilla'),
    path('more/', views.more, name='more'),
    path('plantilla/', views.vista_plantilla, name='plantilla'),
    path('hacer_oferta/<int:id_jugador>/', views.hacer_oferta, name="hacer_oferta"),
    path('agregar_subasta_jugador/<int:id_jugador>/', views.agregar_subasta_jugador, name="agregar_subasta_jugador"),
    path('seleccionar_alineacion/', views.seleccionar_alineacion, name="seleccionar_alineacion"),
    path('generar_jugadores_subasta/', views.generar_jugadores_subasta, name="generar_jugadores_subasta"),
    path('chequeo_fin_subasta/', views.chequeo_fin_subasta, name="chequeo_fin_subasta"),

]
