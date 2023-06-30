import datetime
import random
import string

from PIL import Image
from apscheduler.schedulers.background import BackgroundScheduler
from django import forms
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.contrib.humanize.templatetags.humanize import intcomma
from django.core.exceptions import ObjectDoesNotExist
from django.db.models import Q
from django.http import Http404, JsonResponse, HttpResponse
from django.shortcuts import redirect, render, get_object_or_404
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView

from EFastMisterApp.models import *
from UsersApp.models import *


@login_required
def crear_comunidad(request):
    if request.method == 'POST':

        if request.user.is_authenticated:
            nombre = request.POST['nombre']
            perfil_imagen = request.FILES.get('profile_image', None)
            miembros = request.POST['miembros']
            privada = request.POST.get("privada", None)
            codigo = ""
            if privada == "1":
                privada = True

                # TODO // GENERAR 5 LETRAS ALEATORIAS
                letras = ''.join(random.choices(string.ascii_uppercase, k=5))

                # TODO // GENERAR 5 NUMEROS ALEATORIOS
                numeros = ''.join(random.choices(string.digits, k=5))

                # TODO // GENERAR CARACTER ESPECIAL ALEATORIO
                caracter_especial = random.choice('!@#$%^&*()')

                # TODO // CONCATENAMOS TODOS LOS CARACTERES GENERADOS Y LO UNIMOS EN EL CODIGO
                codigo = f"{letras}#{numeros}{caracter_especial}"

            else:
                privada = False

            check_comunidad = Comunidad.objects.filter(nombre_comunidad=nombre)

            # ? CHEQUEO PARA VERIFICAR QUE NO EXISTE UNA COMUNIDAD COMO LA QUE SE INTENTA CREAR
            if check_comunidad.exists():
                messages.error(request, 'Ya existe una comunidad con ese nombre')

            else:
                # ? CREACION DE LA NUEVA COMUNIDAD
                nuevaComunidad = Comunidad()
                nuevaComunidad.nombre_comunidad = nombre
                nuevaComunidad.administrador = request.user
                nuevaComunidad.es_privada = privada
                nuevaComunidad.cantidad_miembros = miembros

                # ? CHEQUEO DE LAS MEDIDAS DE LA IMAGEN, PARA EVITAR QUE EL USUARIO AÑADA IMAGENES DEMASIADO GRANDES
                if perfil_imagen:
                    img = Image.open(perfil_imagen)
                    width, height = img.size

                    if width > 720 or height > 720:
                        messages.error(request, 'La imagen seleccionada es demasiado grande')
                        return redirect('vista_crear_comunidad')
                    else:
                        nuevaComunidad.profile_image = perfil_imagen
                else:
                    nuevaComunidad.profile_image = "comunidad_default.png"

                nuevaComunidad.save()

                # ? COMPROBAMOS SI ES PRIVADA PARA CREAR SU CODIGO DE ACCESO/INVITACIÓN
                if codigo != "":
                    # TODO // Como es privada, creamos un nuevo acceso mediante codigo
                    nuevoAcceso = AccesoComunidades()
                    nuevoAcceso.codigoAcceso = codigo
                    nuevoAcceso.comunidad = nuevaComunidad
                    nuevoAcceso.save()

                # ? CREACIÓN DE LA CONFIGURACIÓN BASICA DE LA COMUNIDAD
                nuevaConfig = GestionComunidad()
                nuevaConfig.comunidad = nuevaComunidad
                nuevaConfig.save()

                # ? CREACIÓN DE LOS JUGADORES DE LA COMUNIDAD
                generar_jugadores_comunidad(nuevaComunidad)

                # ? CREACION DE LA CONEXION ENTRE USUARIO Y COMUNIDAD (comunidadUsuario)
                configuracion_comunidad = GestionComunidad.objects.get(comunidad=nuevaComunidad)
                nuevoUsuarioC = ComunidadUsuario()
                nuevoUsuarioC.usuario = request.user
                nuevoUsuarioC.comunidad = Comunidad.objects.get(id=nuevaComunidad.id)
                nuevoUsuarioC.saldo = configuracion_comunidad.presupuesto_inicio
                nuevoUsuarioC.save()

                request.session['comunidad'] = nuevaComunidad.id
                return redirect('pagina_principal_comunidad', id_comunidad=nuevaComunidad.id)

        return render(request, 'crear-comunidad.html')


@login_required
def eliminar_comunidad(request):
    if request.method == 'POST':
        id_comunidad = request.session.get('comunidad')

        if id_comunidad is not None:
            check_comunidad = Comunidad.objects.get(id=id_comunidad)
        else:
            check_comunidad = None

        if check_comunidad is not None:
            if check_comunidad.administrador == request.user:
                check_comunidad.delete()
                messages.info(request, 'Comunidad eliminada correctamente')
                return redirect('vista_elegir_comunidad')
            else:
                messages.error(request, 'No puedes eliminar la comunidad dado que no eres Administrador')
        else:
            messages.error(request, 'No se ha podido eliminar la comunidad especificada')


@login_required
def acceso_comunidad(request):
    if request.method == 'POST':
        codigo = request.POST.get('codigo')
        acceso = AccesoComunidades.objects.filter(codigoAcceso=codigo).first()

        if acceso is not None:

            # ? SACAMOS LA COMUNIDAD A RAIZ DEL ACCESO Y CREAMOS EL ENLACE ENTRE EL USUARIO Y LA COMUNIDAD (NUEVO MIEMBRO)
            comunidad = Comunidad.objects.get(id=acceso.comunidad.id)
            configuracion_comunidad = GestionComunidad.objects.get(comunidad=comunidad)

            # ? VERIFICACIÓN DE MIEMBROS EN LA COMUNIDAD SOLICITADA
            num_miembros = ComunidadUsuario.objects.filter(comunidad=comunidad).count()

            if num_miembros == comunidad.cantidad_miembros:
                messages.error(request,
                               "Está comunidad ya ha está llena, por favor pruebe con otra o espere a que haya")
                return redirect('vista_unirse_comunidad')
            else:
                nuevoUsuarioC = ComunidadUsuario()
                nuevoUsuarioC.usuario = request.user
                nuevoUsuarioC.comunidad = Comunidad.objects.get(id=comunidad.id)
                nuevoUsuarioC.saldo = configuracion_comunidad.presupuesto_inicio

                if ComunidadUsuario.objects.filter(usuario=request.user, comunidad=comunidad):
                    messages.error(request, "Ya eres miembro de la comunidad indicada")
                    return redirect('vista_unirse_comunidad')
                else:
                    nuevoUsuarioC.save()

                # ? CREACIÓN DEL MENSAJE AL UNIRSE UN NUEVO MIEMBRO A LA COMUNIDAD
                nueva_noticia = Noticia()
                nueva_noticia.perfil_usuario = Perfil.objects.get(user=request.user)
                nueva_noticia.descripcion = 'se unió a la comunidad'
                nueva_noticia.fecha_publicacion = datetime.date.today()
                nueva_noticia.comunidad = comunidad
                nueva_noticia.save()

                # ? AÑADIMOS LA COMUNIDAD EN SESIÓN
                request.session['comunidad'] = comunidad.id
                return redirect('pagina_principal_comunidad', id_comunidad=comunidad.id)
        else:
            messages.error(request, 'El codigo que ha introducido no es valido')
            return redirect(reverse('vista_unirse_comunidad'))


@login_required
def unirse_comunidad_publica(request, comunidad_id):
    comunidad = Comunidad.objects.get(id=comunidad_id)
    configuracion_comunidad = GestionComunidad.objects.get(comunidad=comunidad)

    # ? CREACION DE LA CONEXIÓN ENTRE USUARIO Y COMUNIDAD
    nuevoUsuarioC = ComunidadUsuario()
    nuevoUsuarioC.usuario = request.user
    nuevoUsuarioC.comunidad = comunidad
    nuevoUsuarioC.saldo = configuracion_comunidad.presupuesto_inicio

    # ? VERIFICA SI EL USUARIO YA ESTÁ DENTRO DE ESA COMUNIDAD, EN TAL CASO LE DARÁ UN ERROR
    if ComunidadUsuario.objects.filter(usuario=request.user, comunidad=comunidad):
        messages.error(request, "Ya eres miembro de la comunidad seleccionada")
        return redirect('vista_elegir_comunidad')
    else:
        nuevoUsuarioC.save()

    # ? CREACIÓN DEL MENSAJE AL UNIRSE UN NUEVO MIEMBRO A LA COMUNIDAD
    nueva_noticia = Noticia()
    nueva_noticia.perfil_usuario = Perfil.objects.get(user=request.user)
    nueva_noticia.descripcion = 'se unió a la comunidad'
    nueva_noticia.fecha_publicacion = datetime.date.today()
    nueva_noticia.comunidad = comunidad
    nueva_noticia.save()

    # ? AÑADIMOS LA COMUNIDAD EN SESIÓN
    request.session['comunidad'] = comunidad.id
    return redirect('pagina_principal_comunidad', id_comunidad=comunidad.id)


@login_required
def abandonar_comunidad(request):
    if request.method == 'POST':
        idComunidad = request.session.get('comunidad')
        comunidad = Comunidad.objects.get(id=idComunidad)
        usuario = request.user
        comunidad_usuario = ComunidadUsuario.objects.get(comunidad=comunidad, usuario=usuario)

        if comunidad_usuario:
            comunidad_usuario.delete()
            comunidades_del_usuario = ComunidadUsuario.objects.filter(usuario=usuario)

            # ? CREACIÓN DEL MENSAJE AL ABANDONAR LA COMUNIDAD
            nueva_noticia = Noticia()
            nueva_noticia.perfil_usuario = Perfil.objects.get(user=request.user)
            nueva_noticia.descripcion = 'ha abandonado la comunidad'
            nueva_noticia.fecha_publicacion = datetime.date.today()
            nueva_noticia.comunidad = comunidad
            nueva_noticia.save()

            if comunidades_del_usuario:
                comunidad_usuario = random.choice(comunidades_del_usuario)
                request.session['comunidad'] = comunidad_usuario.comunidad.id
                messages.info(request, 'Ha abandonado la liga correctamente.')
                return redirect('pagina_principal_comunidad', id_comunidad=comunidad_usuario.comunidad.id)
            else:
                messages.info(request, 'Ha abandonado la liga correctamente.')
                return redirect('vista_elegir_comunidad')


        else:
            messages.error(request, 'Ha habido un error al intentar abandonar la comunidad, intentelo de nuevo por '
                                    'favor')


@login_required
def generar_comunidad_aleatoria(request):
    comunidades_aleatorias = Comunidad.objects.filter(es_privada=0).all()

    for comunidad in comunidades_aleatorias:
        num_usuarios = ComunidadUsuario.objects.filter(comunidad=comunidad).all().count()

        if num_usuarios < comunidad.cantidad_miembros:
            check_comunidad_usuario = ComunidadUsuario.objects.filter(usuario=request.user, comunidad=comunidad)

            if check_comunidad_usuario:
                continue
            else:
                request.session['comunidad'] = comunidad.id

                # ? CREACIÓN DEL VINCULO ENTRE LA COMUNIDAD Y EL USUARIO
                nuevo_comunidad_usuario = ComunidadUsuario()
                nuevo_comunidad_usuario.usuario = request.user
                nuevo_comunidad_usuario.comunidad = comunidad
                nuevo_comunidad_usuario.saldo = GestionComunidad.objects.get(comunidad=comunidad).presupuesto_inicio
                nuevo_comunidad_usuario.save()

                # ? CREACIÓN DEL MENSAJE AL UNIRSE UN NUEVO MIEMBRO A LA COMUNIDAD
                nueva_noticia = Noticia()
                nueva_noticia.perfil_usuario = Perfil.objects.get(user=request.user)
                nueva_noticia.descripcion = 'se unió a la comunidad'
                nueva_noticia.fecha_publicacion = datetime.date.today()
                nueva_noticia.comunidad = comunidad
                nueva_noticia.save()
            break

    return redirect('pagina_principal_comunidad', id_comunidad=0)


@login_required
def actualizar_configuracion_comunidad(request):
    if request.method == 'POST':

        # ? SACAMOS LA COMUNIDAD Y SU CONFIGURACION
        comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))
        gestion_comunidad = GestionComunidad.objects.get(comunidad=comunidad)

        # ? SACAMOS LAS VARIABLES QUE SE PASAN EN LOS MODALES DE LA CONFIGURACION

        # * VARIABLES - GENERALES
        nombre = request.POST.get('nombre')
        imagen = request.FILES.get('profile_image')
        miembros_max = request.POST.get('miembros')

        # * VARIABLES - EQUIPOS
        jugadores_max_equipo = request.POST.get('jugadores_equipo')
        comienzo_temporada = request.POST.get('comienzo_temporada_jd')
        jugadores_iniciales = request.POST.get('jugadores_iniciales')

        # * VARIABLES - MERCADO
        mercado_duracion = request.POST.get('duracion_jugadores')
        maximo_jugadores_mercado = request.POST.get('maximo_jugadores_mercado')
        maximo_jugadores_simultaneo = request.POST.get('maximo_jugadores_simultaneo')

        # * VARIABLES - OFERTAS/PUJAS/CLAUSULAS
        hacer_oferta = request.POST.get('hacer_oferta')
        deuda_maxima = request.POST.get('deuda_maxima')
        oferta_bajo_mercado = request.POST.get('oferta_bajo_mercado')
        chupinazo = request.POST.get('chupinazo')
        horas_antes_de_chupinazo_recien_fichados = request.POST.get('horas_antes_de_chupinazo_recien_fichados')
        maximo_jugadores_horas_chupinazo = request.POST.get('maximo_jugadores_horas_chupinazo')
        horas_antes_jornada_chupinazo = request.POST.get('horas_antes_jornada_chupinazo')

        # * VARIABLES - JORNADAS
        intercambio_jugadores = request.POST.get('intercambio_jugadores')
        maximo_jugadores_intercambio = request.POST.get('maximo_jugadores_intercambio')

        # * VARIABLES - BONIFICACIONES
        bonificacion_por_puntos = request.POST.get('bonificacion_por_puntos')
        bonificacion_fija_jornada = request.POST.get('bonificacion_fija_jornada')

        # ? COMPROBACIÓN DE LOS CAMPOS QUE VIENEN EN EL REQUEST Y ACTUALIZACIÓN DE COMUNIDAD/GESTION EN BBDD
        # * CADA VEZ QUE SE QUIERA AÑADIR UN CAMPO MODAL DE LA CONFIGURACIÓN DE LA COMUNIDAD,
        # * HACER LO MISMO PERO CAMBIANDO LOS NOMBRES DE LAS IDS

        # * GENERAL
        if nombre:
            comunidad.nombre_comunidad = nombre
            comunidad.save()

            messages.success(request, 'Nombre de la comunidad actualizado con éxito')
            return redirect('configuracion_general_comunidad')

        if imagen:

            img = Image.open(imagen)
            width, height = img.size

            if width > 720 or height > 720:
                messages.error(request, 'La imagen seleccionada es demasiado grande')
                return redirect('configuracion_general_comunidad')

            else:

                comunidad.profile_image = imagen
                comunidad.save()

                messages.success(request, 'Imagen de la comunidad actualizada con éxito')
                return redirect('configuracion_general_comunidad')

        if miembros_max:
            comunidad.cantidad_miembros = miembros_max
            comunidad.save()

            messages.success(request, 'Miembros máximos de la comunidad actualizados con éxito')
            return redirect('configuracion_general_comunidad')

        # * EQUIPOS
        if jugadores_max_equipo:
            gestion_comunidad.max_futbolistas_equipo = jugadores_max_equipo
            gestion_comunidad.save()

            messages.success(request, 'Jugadores máximos de la comunidad actualizados con éxito')
            return redirect('configuracion_general_equipos')

        if jugadores_iniciales:

            match jugadores_iniciales:
                case "0":
                    gestion_comunidad.futbolistas_inicio = 22
                    gestion_comunidad.presupuesto_inicio = 15000000
                    gestion_comunidad.save()
                    messages.success(request,
                                     'Jugadores Iniciales y Presupuesto Inicial de la comunidad actualizados con éxito')
                    return redirect('configuracion_general_equipos')
                case "1":
                    gestion_comunidad.futbolistas_inicio = 15
                    gestion_comunidad.presupuesto_inicio = 50000000
                    gestion_comunidad.save()
                    messages.success(request,
                                     'Jugadores Iniciales y Presupuesto Inicial de la comunidad actualizados con éxito')
                    return redirect('configuracion_general_equipos')
                case "2":
                    gestion_comunidad.futbolistas_inicio = 11
                    gestion_comunidad.presupuesto_inicio = 75000000
                    gestion_comunidad.save()
                    messages.success(request,
                                     'Jugadores Iniciales y Presupuesto Inicial de la comunidad actualizados con éxito')
                    return redirect('configuracion_general_equipos')
                case "3":
                    gestion_comunidad.futbolistas_inicio = 0
                    gestion_comunidad.presupuesto_inicio = 150000000
                    gestion_comunidad.save()
                    messages.success(request,
                                     'Jugadores Iniciales y Presupuesto Inicial de la comunidad actualizados con éxito')
                    return redirect('configuracion_general_equipos')

        if comienzo_temporada:

            match comienzo_temporada:
                case "0":
                    gestion_comunidad.jugadores_inicio_temp = 22
                    gestion_comunidad.presupuesto_inicio_temp = 15000000
                    gestion_comunidad.save()
                    messages.success(request,
                                     'Jugadores Iniciales Temporada y Presupuesto Inicial Temporada de la comunidad '
                                     'actualizados con éxito')
                    return redirect('configuracion_general_equipos')
                case "1":
                    gestion_comunidad.jugadores_inicio_temp = 15
                    gestion_comunidad.presupuesto_inicio_temp = 50000000
                    gestion_comunidad.save()
                    messages.success(request,
                                     'Jugadores Iniciales Temporada y Presupuesto Inicial Temporada de la comunidad '
                                     'actualizados con éxito')
                    return redirect('configuracion_general_equipos')
                case "2":
                    gestion_comunidad.jugadores_inicio_temp = 11
                    gestion_comunidad.presupuesto_inicio_temp = 75000000
                    gestion_comunidad.save()
                    messages.success(request,
                                     'Jugadores Iniciales Temporada y Presupuesto Inicial Temporada de la comunidad actualizados con éxito')
                    return redirect('configuracion_general_equipos')
                case "3":
                    gestion_comunidad.jugadores_inicio_temp = 0
                    gestion_comunidad.presupuesto_inicio_temp = 150000000
                    gestion_comunidad.save()
                    messages.success(request,
                                     'Jugadores Iniciales Temporada y Presupuesto Inicial Temporada de la comunidad actualizados con éxito')
                    return redirect('configuracion_general_equipos')

        # * MERCADO
        if mercado_duracion:

            match mercado_duracion:
                case "0":
                    gestion_comunidad.duracion_jugadores_mercado = 8
                    gestion_comunidad.save()
                    messages.success(request,
                                     'Duración máxima de los jugadores del mercado actualizados con éxito')
                    return redirect('configuracion_general_mercado')
                case "1":
                    gestion_comunidad.duracion_jugadores_mercado = 12
                    gestion_comunidad.save()
                    messages.success(request,
                                     'Duración máxima de los jugadores del mercado actualizados con éxito')
                    return redirect('configuracion_general_mercado')
                case "2":
                    gestion_comunidad.duracion_jugadores_mercado = 24
                    gestion_comunidad.save()
                    messages.success(request,
                                     'Duración máxima de los jugadores del mercado actualizados con éxito')
                    return redirect('configuracion_general_mercado')

        if maximo_jugadores_mercado:
            gestion_comunidad.maximo_jugadores_mercado = maximo_jugadores_mercado
            gestion_comunidad.save()

            messages.success(request, 'Jugadores máximos del mercado actualizados con éxito')
            return redirect('configuracion_general_mercado')

        if maximo_jugadores_simultaneo:
            gestion_comunidad.maximo_jugadores_simultaneo = maximo_jugadores_simultaneo
            gestion_comunidad.save()

            messages.success(request, 'Jugadores máximos por miembros simultáneos del mercado actualizados con éxito')
            return redirect('configuracion_general_mercado')

        # * OFERTAS/PUJAS/CLAUSULAS
        if hacer_oferta:
            gestion_comunidad.hacer_oferta = hacer_oferta
            gestion_comunidad.save()

            messages.success(request, 'Hacer ofertas del mercado actualizados con éxito')
            return redirect('configuracion_general_ofertas')

        if deuda_maxima:
            gestion_comunidad.deuda_maxima = deuda_maxima
            gestion_comunidad.save()

            messages.success(request, 'Deuda máxima de la oferta actualizados con éxito')
            return redirect('configuracion_general_ofertas')

        if oferta_bajo_mercado:
            gestion_comunidad.oferta_bajo_mercado = oferta_bajo_mercado
            gestion_comunidad.save()

            messages.success(request, "Ofertar por debajo del valor del mercado actualizada con éxito")
            return redirect('configuracion_general_ofertas')

        if chupinazo:
            gestion_comunidad.chupinazo = chupinazo
            gestion_comunidad.save()

            messages.success(request, "Cláusulas de recisión (Chupinazo) actualizado con éxito")
            return redirect('configuracion_general_ofertas')

        if horas_antes_de_chupinazo_recien_fichados:
            gestion_comunidad.horas_antes_de_chupinazo_recien_fichados = horas_antes_de_chupinazo_recien_fichados
            gestion_comunidad.save()

            messages.success(request,
                             "Tiempo para impedir chupinazo de jugadores recien fichados actualizado con éxito")
            return redirect('configuracion_general_ofertas')

        if maximo_jugadores_horas_chupinazo:
            gestion_comunidad.maximo_jugadores_horas_chupinazo = maximo_jugadores_horas_chupinazo
            gestion_comunidad.save()

            messages.success(request,
                             "Número de jugadores máximos a impedir fichar actualizado con éxito")
            return redirect('configuracion_general_ofertas')

        if horas_antes_jornada_chupinazo:
            gestion_comunidad.horas_antes_jornada_chupinazo = horas_antes_jornada_chupinazo
            gestion_comunidad.save()

            messages.success(request,
                             "Horas previas antes de la jornada actualizado con éxito")
            return redirect('configuracion_general_ofertas')

        # * JORNADAS
        if intercambio_jugadores:
            gestion_comunidad.intercambio_jugadores = intercambio_jugadores
            gestion_comunidad.save()

            messages.success(request,
                             "Intercambio de jugadores durante la jornada actualizado con éxito")
            return redirect('configuracion_general_jornadas')

        if maximo_jugadores_intercambio:
            gestion_comunidad.maximo_jugadores_intercambio = maximo_jugadores_intercambio
            gestion_comunidad.save()

            messages.success(request,
                             "Intercambios máximo de jugadores permitidos durante la jornada actualizado con éxito")
            return redirect('configuracion_general_jornadas')

        # * BONIFICACIONES
        if bonificacion_por_puntos:
            gestion_comunidad.bonificacion_por_puntos = bonificacion_por_puntos
            gestion_comunidad.save()

            messages.success(request,
                             "Bonificación por puntos de la comunidad actualizada con éxito")
            return redirect('configuracion_general_bonificaciones')

        if bonificacion_fija_jornada:
            gestion_comunidad.bonificacion_fija_jornada = bonificacion_fija_jornada
            gestion_comunidad.save()

            messages.success(request,
                             "Bonificación fija por jornada de la comunidad actualizada con éxito")
            return redirect('configuracion_general_bonificaciones')


# ? METODO PARA GENERAR LOS JUGADORES DE LA COMUNIDAD CUANDO SE CREA UNA NUEVA
def generar_jugadores_comunidad(comunidad):
    lista_jugadores = Jugadores.objects.filter().all()

    for jugador in lista_jugadores:
        Jugadores_comunidad.objects.create(
            jugador=jugador,
            comunidad=comunidad
        )


@login_required
@user_passes_test(lambda u: u.is_superuser)
def crear_noticia(request):
    if request.method == 'POST':
        # ! Creacion de la nueva noticia
        nueva_noticia = Noticia()
        nueva_noticia.titulo = request.POST.get('titulo')
        nueva_noticia.descripcion = request.POST.get('descripcion')
        nueva_noticia.save()

        # ? Mensaje de alerta
        messages.success(request, 'Mensaje enviado a todas las comunidades correctamente.')
        return redirect('panel_administracion')


@login_required
def agregar_eliminar_jugador_favorito(request, nombre):
    id_comunidad = request.session.get('comunidad')

    jugador_seleccionado = Jugadores.objects.get(nombre=nombre)
    comunidad_seleccionada = Comunidad.objects.get(id=id_comunidad)

    try:
        # ? INTENTAMOS ELIMINAR EL FAVORITO, SI NO PUEDE SIGNIFICA QUE NO EXISTE PARA ESA COMUNIDAD

        eliminar_favorito = Favoritos.objects.get(jugador=jugador_seleccionado, comunidad=comunidad_seleccionada,
                                                  usuario=request.user)
        eliminar_favorito.delete()
        return redirect('lista_jugadores_comunidad')

    except Favoritos.DoesNotExist:
        # ? SI NO EXISTE EL FAVORITO, CREA UNO

        nuevo_favorito = Favoritos(
            jugador=jugador_seleccionado,
            comunidad=comunidad_seleccionada,
            usuario=request.user
        )
        nuevo_favorito.save()
        return redirect('lista_jugadores_comunidad')


@login_required
def sacar_favoritos(request):
    comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))
    favoritos = Favoritos.objects.filter(comunidad=comunidad, usuario=request.user)
    favoritos_nombres = []
    # ? RECORRE LOS NOMBRES DE LOS FAVORITOS PARA COMPROBAR QUE JUGADORES DE LA LISTA TIENE EL USUARIO LOGEADO EN FAVORITOS
    for favorito in favoritos:
        favoritos_nombres.append(favorito.jugador.nombre)
    return favoritos_nombres


class CrearPlantillaForm(forms.ModelForm):
    class Meta:
        model = Plantilla
        fields = ['user', 'alineacion']
        widgets = {
            'user': forms.HiddenInput(),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['user'].initial = self.instance.user.username if self.instance.user else ''


class CrearPlantillaView(CreateView):
    template_name = 'crear_plantilla.html'
    form_class = CrearPlantillaForm
    success_url = reverse_lazy('jugadores-plantilla')

    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        comunidad_id = self.request.session.get('comunidad')

        if comunidad_id:
            comunidad = get_object_or_404(Comunidad, id=comunidad_id)
            kwargs['instance'] = Plantilla(comunidad=comunidad, user=self.request.user)
        return kwargs

    def form_valid(self, form):

        comunidad = form.instance.comunidad

        if comunidad is None:
            form.add_error('comunidad', 'Debe seleccionar una comunidad.')
            return self.form_invalid(form)

        formacion = form.cleaned_data['alineacion']  # Obtener la formación seleccionada
        # Aquí puedes hacer lo que necesites con la formación,
        # como guardarlo en la base de datos o realizar alguna otra operación.

        # Buscar si ya existe una plantilla para esta comunidad y este usuario
        plantilla_existente = Plantilla.objects.filter(user=self.request.user, comunidad=comunidad).first()
        if plantilla_existente:
            # Si ya existe una plantilla para esta comunidad y este usuario, redirigir
            # al usuario a la página de su plantilla
            return redirect(reverse_lazy('jugadores-plantilla'))

        jugadores_libres = Jugadores_comunidad.objects.filter(comunidad=comunidad, libre=True)
        jugadores_count = jugadores_libres.count()
        configuracion_comunidad = GestionComunidad.objects.get(comunidad=comunidad)
        if jugadores_count < configuracion_comunidad.futbolistas_inicio:
            raise Http404("La comunidad no tiene suficientes jugadores libres.")
        jugadores_aleatorios = random.sample(list(jugadores_libres), configuracion_comunidad.futbolistas_inicio)

        plantilla_jugador = form.save(commit=False)
        plantilla_jugador.user = self.request.user
        plantilla_jugador.perfil = self.request.user.perfil
        plantilla_jugador.save()

        plantilla_guardada = Plantilla.objects.filter(user=self.request.user, comunidad=comunidad).first()
        if plantilla_guardada.puntosTotales is None:
            plantilla_guardada.puntosTotales = 0
            plantilla_guardada.save()

        if plantilla_guardada is not None:

            for jugador in jugadores_aleatorios:
                plantilla_guardada.jugadores.add(jugador)
                jugador.libre = False
                jugador.save()
            plantilla_guardada.save()

        return redirect(self.success_url)


def jugadoresPlantilla(request):
    comunidad_id = request.session.get('comunidad')
    comunidad = Comunidad.objects.get(id=comunidad_id)

    user = User.objects.get(id=request.user.id)
    perfil = Perfil.objects.get(user=user)

    comunidades_del_usuario = ComunidadUsuario.objects.filter(usuario=request.user)
    usuario_datos_comunidad = ComunidadUsuario.objects.get(usuario=request.user, comunidad=comunidad)
    plantilla_jugador = Plantilla.objects.get(comunidad=comunidad, user=user)
    jornadas_jugadores = {}
    subastas_jugadores = []
    titulares = []
    nombres_titulares = []

    alineaciones = Tipo_alineacion.objects.filter().all()

    # ? POSIBLES JUGADORES EN SUBASTA

    if not comunidad_id:
        messages.error(request, "Debe seleccionar una comunidad.")
        return redirect('jugadores-plantilla')

    try:
        plantilla = Plantilla.objects.filter(user=request.user, comunidad__id=comunidad_id).order_by('-id').first()

        if not plantilla:
            messages.error(request, "No se encontró la plantilla para la comunidad actual.")
            return redirect('jugadores-plantilla')

        jugadores_plantilla = JugadorPlantilla.objects.filter(plantilla__user=request.user,
                                                              plantilla__comunidad=comunidad).order_by(
            'jugador__jugador__posicion')
        for jugador_plantilla in jugadores_plantilla:
            jornadas_jugadores[jugador_plantilla.jugador] = Jornada.objects.filter(
                jugador=jugador_plantilla.jugador.jugador)[:4][::-1]

        posibles_subastas = Subasta.objects.filter(comunidad=comunidad)
        lista_jugadores_plantilla = [jugador_plantilla.jugador.jugador.id for jugador_plantilla in jugadores_plantilla]
        for subasta in posibles_subastas:
            if subasta.JugadoresComunidad.jugador.id in lista_jugadores_plantilla:
                subastas_jugadores.append(subasta.JugadoresComunidad.jugador.id)

        titulares = JugadorPlantilla.objects.filter(plantilla=plantilla, es_titular=True)
        nombres_titulares = [jugador.jugador.jugador.nombre for jugador in titulares]
        # print(subastas_jugadores)
        # print(lista_jugadores_plantilla)


    except IndexError:
        jugadores_plantilla = []

    context = {'comunidad': comunidad, 'perfil': perfil, 'comunidades_del_usuario': comunidades_del_usuario,
               'usuario_datos_comunidad': usuario_datos_comunidad, 'jugadores_plantilla': jugadores_plantilla,
               'comunidad_id': comunidad_id, 'alineaciones': alineaciones, 'plantilla_jugador': plantilla_jugador,
               'titulares': titulares, 'nombres_titulares': nombres_titulares, 'jornadas_jugadores': jornadas_jugadores,
               'subastas_jugadores': subastas_jugadores}
    return render(request, 'jugadores_plantilla.html', context)


def obtener_formacion_por_tipo_alineacion(tipo_alineacion):
    formacion = formacion_maxima.get(tipo_alineacion)
    if formacion:
        return formacion
    else:
        return None


formacion_maxima = {
    '1-4-4-2': {'pt': 1, 'df': 4, 'mc': 4, 'dl': 2},
    '1-5-4-1': {'pt': 1, 'df': 5, 'mc': 4, 'dl': 1},
    '1-4-3-3': {'pt': 1, 'df': 4, 'mc': 3, 'dl': 3},
    '1-3-5-2': {'pt': 1, 'df': 3, 'mc': 4, 'dl': 2},
    # Agrega más formaciones según tus necesidades
}


@login_required
def guardar_plantilla(request):
    if request.method == 'POST':
        comunidad_id = request.session.get('comunidad')
        if not comunidad_id:
            messages.error(request, "Debe seleccionar una comunidad.")
            return redirect('jugadores-plantilla')

        plantilla = Plantilla.objects.filter(user=request.user, comunidad__id=comunidad_id).order_by('-id').first()
        if not plantilla:
            messages.error(request, "No se encontró la plantilla para la comunidad actual.")
            return redirect('jugadores-plantilla')

        jugadores_plantilla = JugadorPlantilla.objects.filter(plantilla=plantilla, jugador__comunidad__id=comunidad_id)

        # Crear objetos JugadorPlantilla si no existen
        for jugador in plantilla.jugadores.all():
            if not jugadores_plantilla.filter(jugador=jugador).exists():
                JugadorPlantilla.objects.create(jugador=jugador, plantilla=plantilla)

        tipo_alineacion = plantilla.alineacion.tipo
        formacion_seleccionada = formacion_maxima.get(tipo_alineacion)

        if not formacion_seleccionada:
            messages.error(request, "Formación inválida.")
            return redirect('jugadores-plantilla')

        titulares_seleccionados = 0
        jugadores_por_posicion = {}  # Diccionario para contar el número de jugadores seleccionados por posición

        for jugador_plantilla in jugadores_plantilla:
            titular = f'titular_{jugador_plantilla.jugador.id}_{comunidad_id}'
            if titular in request.POST:
                posicion_jugador = jugador_plantilla.jugador.jugador.posicion.lower().strip()
                max_jugadores_posicion = formacion_seleccionada.get(posicion_jugador, 0)

                mensaje_posicion_jugador = posicion_jugador.upper()
                if max_jugadores_posicion is None:
                    jugador_plantilla.es_titular = False
                    jugador_plantilla.save()
                    messages.error(request,
                                   f"No puedes seleccionar jugadores para la posición {mensaje_posicion_jugador} en esta formación.")
                    return redirect('jugadores-plantilla')

                if jugadores_por_posicion.get(posicion_jugador, 0) >= max_jugadores_posicion:
                    jugador_plantilla.es_titular = False
                    jugador_plantilla.save()
                    messages.error(request,
                                   f"No puedes seleccionar más de {max_jugadores_posicion} jugadores para la posición {mensaje_posicion_jugador}. Se te han añadido los dos ultimos seleccionados para la posicion {mensaje_posicion_jugador}")
                    return redirect('jugadores-plantilla')

                jugador_plantilla.es_titular = True
                titulares_seleccionados += 1
                jugadores_por_posicion[posicion_jugador] = jugadores_por_posicion.get(posicion_jugador, 0) + 1
            else:
                jugador_plantilla.es_titular = False
            jugador_plantilla.save()

        if titulares_seleccionados > 11:
            messages.error(request, "No puedes seleccionar más de 11 titulares.")
            return redirect('jugadores-plantilla')

        return redirect(reverse('jugadores-plantilla'))


def seleccionar_alineacion(request):
    if request.method == "POST":
        tipo_alineacion_seleccionada = request.POST['alineacion']
        alineacion_seleccionada = Tipo_alineacion.objects.get(tipo=tipo_alineacion_seleccionada)
        comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))
        usuario = User.objects.get(id=request.user.id)

        plantilla_jugador = Plantilla.objects.get(comunidad=comunidad, user=usuario)
        plantilla_jugador.alineacion = alineacion_seleccionada
        plantilla_jugador.save()

        # ? JUGADORES TITULARES PASAN A NO SER TITULARES
        titulares = JugadorPlantilla.objects.filter(plantilla=plantilla_jugador, es_titular=True)
        for titular in titulares:
            titular.es_titular = False
            titular.save()

        return redirect('jugadores-plantilla')


# * VISTAS DEFAULT
@login_required
def paginaPrincipal(request, id_comunidad=None):
    if id_comunidad != 0:
        request.session['comunidad'] = id_comunidad
        comunidad = Comunidad.objects.get(id=id_comunidad)
    else:
        comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))

    comunidades_del_usuario = ComunidadUsuario.objects.filter(usuario=request.user)
    usuario_datos_comunidad = ComunidadUsuario.objects.get(usuario=request.user, comunidad=comunidad)
    user = User.objects.get(id=request.user.id)
    perfil = Perfil.objects.get(user=user)

    mensajes_administracion = Noticia.objects.filter(comunidad=None).order_by('-fecha_publicacion')

    # ? FILTRAR LAS NOTICIAS QUE SON DE LA COMUNIDAD (UNIRSE O ABANDONAR COMUNIDAD)
    noticias_movimientos_usuario_comunidad = Noticia.objects.filter(
        Q(descripcion__contains='se unió a la comunidad') | Q(descripcion__contains='ha abandonado la comunidad'),
        comunidad=comunidad
    ).order_by('-fecha_publicacion')

    mensajes_traspasos = Noticia.objects.filter(
        Q(descripcion__contains='cambia de'),
        comunidad=comunidad
    ).order_by('-fecha_publicacion')

    context = {'comunidad': comunidad, 'perfil': perfil, 'comunidades_del_usuario': comunidades_del_usuario,
               'mensajes_admin': mensajes_administracion,
               'movimientos_usuarios': noticias_movimientos_usuario_comunidad,
               'usuario_datos_comunidad': usuario_datos_comunidad,
               'mensajes_traspasos': mensajes_traspasos}
    return render(request, 'paginaPrincipal.html', context)


@login_required
def elegir_comunidad(request):
    print(request.user.username)
    # ? LISTA DE TODAS LAS LIGAS PUBLICAS
    comunidades_publicas = Comunidad.objects.filter(es_privada=0).all()
    # ? NUMERO DE USUARIOS QUE ESTAN DENTRO DE LA COMUNIDAD
    cantidad_usuarios_por_comunidad = {}

    for comunidad in comunidades_publicas:
        cantidad_usuarios = ComunidadUsuario.objects.filter(comunidad=comunidad).count()
        cantidad_usuarios_por_comunidad[comunidad] = cantidad_usuarios

    context = {'comunidades_publicas': cantidad_usuarios_por_comunidad}
    return render(request, 'elegir-comunidad.html', context)


@login_required
def vista_crear_comunidad(request):
    return render(request, 'crear-comunidad.html')


@login_required
def vista_unirse_comunidad(request):
    return render(request, 'unirse-comunidad.html')


@login_required
def vista_configuracion_comunidad(request):
    comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))
    gestion_comunidad = GestionComunidad.objects.get(comunidad=comunidad)
    context = {'comunidad': comunidad, 'gestion_comunidad': gestion_comunidad}
    return render(request, 'configuracion-comunidad.html', context)


@login_required
def vista_configuracion_comunidad_equipos(request):
    comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))
    gestion_comunidad = GestionComunidad.objects.get(comunidad=comunidad)
    context = {'comunidad': comunidad, 'gestion_comunidad': gestion_comunidad}

    return render(request, 'config-equipos.html', context)


@login_required
def vista_configuracion_comunidad_general(request):
    comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))
    context = {'comunidad': comunidad}
    return render(request, 'config-general.html', context)


@login_required
def vista_configuracion_comunidad_mercado(request):
    comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))
    gestion_comunidad = GestionComunidad.objects.get(comunidad=comunidad)
    context = {'comunidad': comunidad, 'gestion_comunidad': gestion_comunidad}
    return render(request, 'config-mercado.html', context)


@login_required
def vista_configuracion_comunidad_ofertas(request):
    comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))
    gestion_comunidad = GestionComunidad.objects.get(comunidad=comunidad)
    context = {'comunidad': comunidad, 'gestion_comunidad': gestion_comunidad}
    return render(request, 'config-ofertas.html', context)


@login_required
def vista_configuracion_comunidad_jornadas(request):
    comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))
    gestion_comunidad = GestionComunidad.objects.get(comunidad=comunidad)
    context = {'comunidad': comunidad, 'gestion_comunidad': gestion_comunidad}
    return render(request, 'config-jornadas.html', context)


@login_required
def vista_configuracion_comunidad_bonificaciones(request):
    comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))
    gestion_comunidad = GestionComunidad.objects.get(comunidad=comunidad)
    context = {'comunidad': comunidad, 'gestion_comunidad': gestion_comunidad}
    return render(request, 'config-bonificaciones.html', context)


@login_required
def lista_jugadores_comunidad(request):
    # ? ORDEN DE LA LISTA DE ORDENAR
    orden_lista = request.GET.get('orden')

    # ? VARIABLES RECOGIDAS
    comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))
    equipos = Equipo.objects.all()
    jugadores = Jugadores.objects.all()
    jornadas_jugadores = {}
    fecha_actual = datetime.datetime.now()
    favoritos = Favoritos.objects.filter(comunidad=comunidad, usuario=request.user).order_by('-jugador__valor')
    favoritos_nombre = []
    opciones_seleccionadas = {
        'posicion': "0",
        'valor': "0",
        'equipo': "0",
        'disponibilidad': "0"
    }

    # ? LISTAR LOS JUGADORES CON SUS JORNADAS + ASIGNARLE EL ORDEN DEPENDIENDO DE QUE ESTÉ SELECCIONADO

    if orden_lista == "1":
        jugadores = Jugadores.objects.filter().all().order_by('-puntuacion_media')
        orden_actual = 1

    elif orden_lista == "2":
        jugadores = Jugadores.objects.filter().all().order_by('-valor')
        orden_actual = 2

    else:
        orden_actual = 0
        pass

    for jugador in jugadores:
        jornadas_jugadores[jugador] = Jornada.objects.filter(jugador=jugador)[:4][::-1]

    for favorito in favoritos:
        jugador_fav = Jugadores.objects.get(nombre=favorito.jugador.nombre)
        favoritos_nombre.append(jugador_fav.nombre)

    context = {'lista_jugadores': jugadores, 'jornadas_jugadores': jornadas_jugadores, 'fecha_actual': fecha_actual,
               'favoritos': favoritos_nombre, 'orden_actual': orden_actual, 'equipos': equipos,
               'opciones_seleccionadas': opciones_seleccionadas, 'comunidad': comunidad}
    return render(request, 'lista_jugadores.html', context)


@login_required
def filtrar_listado_jugadores(request):
    if request.method == "POST":
        # ? VARIABLES
        orden_lista = request.GET.get('orden')
        comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))
        equipos = Equipo.objects.all()
        jornadas_jugadores = {}
        fecha_actual = datetime.datetime.now()
        favoritos = Favoritos.objects.filter(comunidad=comunidad, usuario=request.user).order_by('-jugador__valor')
        favoritos_nombre = []
        opciones_seleccionadas = {
            'posicion': "0",
            'valor': "0",
            'equipo': "0",
            'disponibilidad': "0"
        }

        if "resetear" in request.POST:
            # ? CONSULTA JUGADORES
            resultados = Jugadores_comunidad.objects.filter(comunidad=comunidad).all()

            # ? JORNADAS JUGADORES
            for jugador in resultados:
                jornadas_jugadores[jugador.jugador] = Jornada.objects.filter(jugador=jugador.jugador)[:4][::-1]

            # ? JUGADORES FAVORITOS
            for favorito in favoritos:
                jugador_fav = Jugadores.objects.get(nombre=favorito.jugador.nombre)
                favoritos_nombre.append(jugador_fav.nombre)

        elif "filtrar" in request.POST:
            print("filtro")
            # ? VARIABLES RECOGIDAS PARA EL FILTRO
            posicion_seleccionada = request.POST['position']
            valor_seleccionado = request.POST['valor']
            equipo_seleccionado = request.POST['equipo']
            disponibilidad_seleccionada = request.POST['libre']

            if posicion_seleccionada == "0":
                posicion_seleccionada = None

            if valor_seleccionado == "0":
                valor_seleccionado = None

            if equipo_seleccionado == "0":
                equipo_seleccionado = None

            if disponibilidad_seleccionada == "0":
                disponibilidad_seleccionada = None

            # ? FILTROS PARA LA CONSULTA
            consulta = Q()

            if posicion_seleccionada is not None:
                consulta &= Q(jugador__posicion=posicion_seleccionada)
                opciones_seleccionadas['posicion'] = posicion_seleccionada

            if valor_seleccionado is not None:
                if valor_seleccionado == "1":
                    consulta &= Q(jugador__valor__range=(0, 1000000))

                elif valor_seleccionado == "2":
                    consulta &= Q(jugador__valor__range=(1000001, 5000000))

                elif valor_seleccionado == "3":
                    consulta &= Q(jugador__valor__range=(5000001, 10000000))

                elif valor_seleccionado == "4":
                    consulta &= Q(jugador__valor__gte=10000001)

                opciones_seleccionadas['valor'] = valor_seleccionado

            if equipo_seleccionado is not None:
                equipo_real = Equipo.objects.get(nombre=equipo_seleccionado)
                consulta &= Q(jugador__equipoReal=equipo_real)

                opciones_seleccionadas['equipo'] = equipo_seleccionado

            if disponibilidad_seleccionada is not None:
                if disponibilidad_seleccionada == "1":
                    consulta &= Q(libre=True)

                elif disponibilidad_seleccionada == "2":
                    consulta &= Q(libre=False)

                opciones_seleccionadas['disponibilidad'] = disponibilidad_seleccionada

            # ? CONSULTA CON LOS FILTROS || JUGADORES
            consulta &= Q(comunidad=comunidad)
            resultados = Jugadores_comunidad.objects.filter(consulta).all()

            # ? JORNADAS JUGADORES
            for jugador in resultados:
                jornadas_jugadores[jugador.jugador] = Jornada.objects.filter(jugador=jugador.jugador)[:4][::-1]

            # ? JUGADORES FAVORITOS
            for favorito in favoritos:
                jugador_fav = Jugadores.objects.get(nombre=favorito.jugador.nombre)
                favoritos_nombre.append(jugador_fav.nombre)

        context = {'jornadas_jugadores': jornadas_jugadores, 'fecha_actual': fecha_actual,
                   'favoritos': favoritos_nombre, 'orden_actual': orden_lista, 'equipos': equipos,
                   'opciones_seleccionadas': opciones_seleccionadas, 'comunidad': comunidad}
        return render(request, 'lista_jugadores.html', context)


@login_required
def lista_jugadores_favoritos(request):
    comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))
    jugadores = []
    favoritos_nombres = []
    jornadas_jugadores = {}
    favoritos = Favoritos.objects.filter(comunidad=comunidad, usuario=request.user).order_by('-jugador__valor')
    fecha_actual = datetime.datetime.now()
    opciones_seleccionadas = {
        'posicion': "0",
        'valor': "0",
        'equipo': "0",
        'disponibilidad': "0"
    }

    if len(favoritos) == 0:
        messages.info(request, "Debes asignar jugadores a favoritos para poder filtrarlos.")
        return redirect('lista_jugadores_comunidad')

    else:
        for favorito in favoritos:
            jugador_fav = Jugadores.objects.get(nombre=favorito.jugador.nombre)
            jugadores.append(jugador_fav)
            favoritos_nombres.append(jugador_fav.nombre)

        for jugador in jugadores:
            jornadas_jugadores[jugador] = Jornada.objects.filter(jugador=jugador)[:4][::-1]

        context = {'lista_jugadores': jugadores, 'jornadas_jugadores': jornadas_jugadores, 'fecha_actual': fecha_actual,
                   'favoritos': favoritos_nombres, 'opciones_seleccionadas': opciones_seleccionadas,
                   'comunidad': comunidad}
        return render(request, 'lista_jugadores.html', context)


# ! ####################### ^^^^^ FIN DE LAS LISTAS DE JUGADORES ^^^^^ #######################

@login_required
@user_passes_test(lambda u: u.is_superuser)
def panel_administracion(request):
    return render(request, 'panel_administracion.html')


@login_required
def mercado(request):
    comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))
    comunidades_del_usuario = ComunidadUsuario.objects.filter(usuario=request.user)
    usuario_datos_comunidad = ComunidadUsuario.objects.get(usuario=request.user, comunidad=comunidad)
    user = User.objects.get(id=request.user.id)
    perfil = Perfil.objects.get(user=user)
    subastas = Subasta.objects.filter(comunidad=comunidad)
    plantilla = Plantilla()
    listaJugadores = []
    ofertas_subastas = {}
    jornadas_jugadores = {}
    ofertas_jugadores = []
    oferta_jugadores_completa = []

    try:
        plantilla = Plantilla.objects.get(user=request.user, comunidad=comunidad)
    except ObjectDoesNotExist:
        messages.info(request, 'Por favor, asegurese de tener equipo antes de acceder al Mercado.')
        return redirect('crear_plantilla')

    ofertas_realizadas = Oferta.objects.filter(plantilla=plantilla, estado=True)

    for subasta in subastas:
        jugadores = subasta.JugadoresComunidad.jugador
        listaJugadores.append(jugadores)

        for jugador in listaJugadores:
            jornadas_jugadores[jugador] = Jornada.objects.filter(jugador=jugador)[:4][::-1]

        # if subasta.JugadoresComunidad.jugador.id in listaJugadores:
        #    subastas_jugadores.append(subasta.JugadoresComunidad.jugador.id)

    lista_jugadores_subasta = [jugador.id for jugador in listaJugadores]
    for oferta in ofertas_realizadas:
        if oferta.JugadoresComunidad.jugador.id in lista_jugadores_subasta:
            ofertas_jugadores.append(oferta.JugadoresComunidad.jugador.id)
            # oferta_jugadores_completa.append(oferta)

    # for oJugadores in ofertas_jugadores:
    #    oferta = Oferta.objects.filter(JugadoresComunidad__jugador__id=oJugadores).values('oferta').first()
    #    if oferta:
    #        valor_formateado = intcomma(oferta['oferta'])
    #        ofertas_subastas[oJugadores] = valor_formateado
    #    else:
    #        ofertas_subastas[oJugadores] = None
    #
    # print(ofertas_subastas.values())
    messages.get_messages(request)
    subastas = Subasta.objects.filter(comunidad=comunidad)
    context = {'comunidad': comunidad, 'perfil': perfil, 'subastas': subastas, 'listaJugadores': listaJugadores,
               'jornadas_jugadores': jornadas_jugadores,
               'comunidades_del_usuario': comunidades_del_usuario,
               'usuario_datos_comunidad': usuario_datos_comunidad, 'ofertas_jugadores': ofertas_jugadores,
               'ofertas_subastas': ofertas_subastas}

    return render(request, 'mercado.html', context)


@login_required
def clasificacion(request):
    comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))
    list_plantillas = []
    list_perfilUsuarios = []
    if comunidad is not None:
        plantillas_comunidad = Plantilla.objects.filter(comunidad=comunidad).order_by('-puntosTotales')

        if plantillas_comunidad is not None:

            list_plantillas = list(plantillas_comunidad)
            for plantilla in list_plantillas:
                usuario = User.objects.get(id=plantilla.user.id)
                list_perfilUsuarios.append(Perfil.objects.get(user_id=usuario.id))

        else:
            messages.error(request, "Aun no hay plantillas en esta comunidad")

    else:
        messages.error(request, "No existe esta comunidad")

    comunidades_del_usuario = ComunidadUsuario.objects.filter(usuario=request.user)
    usuario_datos_comunidad = ComunidadUsuario.objects.get(usuario=request.user, comunidad=comunidad)
    user = User.objects.get(id=request.user.id)
    perfil = Perfil.objects.get(user=user)
    context = {'comunidad': comunidad, 'perfil': perfil, 'perfilesClasi': list_perfilUsuarios,
               'clasificacion': list_plantillas,
               'comunidades_del_usuario': comunidades_del_usuario, 'usuario_datos_comunidad': usuario_datos_comunidad}
    return render(request, 'clasificacion.html', context)


def error_403(request):
    return render(request, 'pagina-error-autenticacion.html')


@login_required
def hacer_oferta(request, id_jugador):
    ofertaEntero = 0
    comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))
    jugador = Jugadores_comunidad.objects.get(jugador_id=id_jugador, comunidad=comunidad)
    plantilla = Plantilla.objects.get(user=request.user, comunidad=comunidad)
    comunidadUsuario = ComunidadUsuario.objects.get(comunidad=comunidad, usuario=request.user)
    saldo = comunidadUsuario.saldo
    # Verificar si el usuario ya ha hecho una oferta en esta subasta

    oferta_anterior = Oferta.objects.filter(JugadoresComunidad=jugador, plantilla=plantilla).first()

    if request.method == 'POST':

        oferta_form = request.POST.get('maximo_jugadores_pujas_mercado')

        try:
            ofertaEntero = int(oferta_form)

        except ValueError:
            messages.error(request, 'La oferta debe ser un número.')

        if ofertaEntero <= jugador.jugador.valor:
            messages.error(request, 'La oferta debe ser mayor que el precio actual.')
            return redirect('mercado')
        # Crear la oferta y actualizar el producto
        elif oferta_anterior is not None:
            saldoNuevo = saldo + oferta_anterior.oferta
            if ofertaEntero > saldoNuevo:
                messages.error(request, 'Está intentando realizar una oferta superior a su saldo restante')
                return redirect('mercado')
        elif ofertaEntero > saldo:
            messages.error(request, 'Está intentando realizar una oferta superior a su saldo restante')
            return redirect('mercado')

        if oferta_anterior is not None:
            saldo = comunidadUsuario.saldo + oferta_anterior.oferta
            comunidadUsuario.saldo = saldo
            comunidadUsuario.save()
            oferta_anterior.delete()

        oferta = Oferta(JugadoresComunidad=jugador, plantilla=plantilla, oferta=ofertaEntero)
        oferta.save()
        comunidadUsuario.saldo = comunidadUsuario.saldo - ofertaEntero
        comunidadUsuario.save()
        ofertaFormateada = intcomma(ofertaEntero)
        messages.success(request,
                         'Has hecho una oferta de {} por {}.'.format(ofertaFormateada, jugador.jugador.nombre))
    return redirect('mercado')


def generar_jugadores_subasta():
    comunidades = Comunidad.objects.all()
    listaComunidades = list(comunidades)
    for comunidad in listaComunidades:
        gestion_comunidad = GestionComunidad.objects.get(comunidad=comunidad)
        futbolistasMercado = gestion_comunidad.futbolistas_mercado
        jugadoresComunidad = Jugadores_comunidad.objects.filter(comunidad=comunidad, libre=True)

        if jugadoresComunidad:
            for _ in range(futbolistasMercado):
                jugador_aleatorio = random.choice(jugadoresComunidad)

                subasta = Subasta()
                subasta.JugadoresComunidad = jugador_aleatorio
                subasta.comunidad = comunidad
                subasta.save()


@login_required
def agregar_subasta_jugador(request, id_jugador):
    comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))
    plantilla = Plantilla.objects.get(user=request.user, comunidad=comunidad)
    jugador = Jugadores.objects.get(id=id_jugador)
    jugadorComunidad = get_object_or_404(Jugadores_comunidad, jugador=jugador, comunidad=comunidad)
    jugadorPlantilla = JugadorPlantilla.objects.get(jugador=jugadorComunidad, plantilla=plantilla)
    jugadorFinal = jugadorPlantilla.jugador.jugador

    if request.method == 'POST':

        jugadorComunidadPlantilla = get_object_or_404(Jugadores_comunidad, jugador=jugadorFinal,
                                                      comunidad=comunidad)
        subasta_existente = Subasta.objects.filter(JugadoresComunidad=jugadorComunidadPlantilla, comunidad=comunidad)

        if subasta_existente.exists():
            messages.error(request, 'El jugador ya ha sido puesto en venta')
            return redirect('jugadores-plantilla')
        else:
            subasta = Subasta(JugadoresComunidad=jugadorComunidadPlantilla, comunidad=comunidad)
            subasta.save()
            messages.success(request, 'El jugador ha sido puesto en venta correctamente')
            return redirect('jugadores-plantilla')

    else:
        return HttpResponse('Método no válido para esta vista')


def chequeo_fin_subasta():
    comunidades = Comunidad.objects.all()
    listaComunidades = list(comunidades)
    for comunidad in listaComunidades:
        subasta = Subasta.objects.filter(comunidad=comunidad)
        lista_subasta = list(subasta)
        listaOfertas = []

        for subasta in lista_subasta:
            jugador = subasta.JugadoresComunidad
            ofertas_jugadores = Oferta.objects.filter(JugadoresComunidad=jugador, plantilla__comunidad=comunidad,
                                                      estado=True)
            mejor_oferta = Oferta.objects.filter(JugadoresComunidad=jugador, plantilla__comunidad=comunidad,
                                                 estado=True).order_by(
                '-oferta').first()

            if ofertas_jugadores is not None and mejor_oferta is not None and jugador.libre == True:
                # Restar a ese usuario lo que pujó por el jugador
                # Pasar el jugador a su plantilla
                fichaje_jugador = JugadorPlantilla(jugador=jugador, plantilla=mejor_oferta.plantilla)
                plantilla = fichaje_jugador.plantilla
                plantilla.jugadores.add(fichaje_jugador.jugador)
                fichaje_jugador.save()

                # Si la subasta la hizo un usuario, se le añade el dinero y se le quita el jugador de la plantilla (se le quita aqui, una vez lo vende)
                comunidadUsuario = ComunidadUsuario.objects.get(usuario=mejor_oferta.plantilla.user,
                                                                comunidad=comunidad)

                comunidadUsuario.saldo = comunidadUsuario.saldo - mejor_oferta.oferta
                jugador.libre = False
                jugador.save()
                comunidadUsuario.save()

                # Comprado al mercado
                nueva_noticia = Noticia()
                nueva_noticia.perfil_usuario = Perfil.objects.get(user=mejor_oferta.plantilla.user)
                nueva_noticia.descripcion = fichaje_jugador.jugador.jugador.nombre + ' cambia de EfastMister a  ' + mejor_oferta.plantilla.user.username
                nueva_noticia.fecha_publicacion = datetime.date.today()
                nueva_noticia.comunidad = comunidad
                nueva_noticia.oferta = Oferta.objects.get(id=mejor_oferta.id)
                nueva_noticia.save()


            # El mercado se lleva al jugador porque no recibe ofertas.
            elif jugador.libre == False and len(ofertas_jugadores) == 0:
                plantilla = Plantilla.objects.get(jugadores=jugador)
                usuario = plantilla.user
                comunidadUsuarioSinOfertas = ComunidadUsuario.objects.get(usuario=usuario, comunidad=comunidad)
                comunidadUsuarioSinOfertas.saldo += jugador.jugador.valor
                comunidadUsuarioSinOfertas.save()
                ofertaMercado = Oferta(oferta=jugador.jugador.valor, JugadoresComunidad=jugador)
                ofertaMercado.save()

                # Vendido al mercado
                nueva_noticia = Noticia()
                nueva_noticia.plantillaVendedor = plantilla
                nueva_noticia.descripcion = jugador.jugador.nombre + ' cambia de ' + plantilla.user.username + ' a EfastMister'
                nueva_noticia.fecha_publicacion = datetime.date.today()
                nueva_noticia.comunidad = comunidad
                nueva_noticia.oferta = ofertaMercado
                nueva_noticia.save()

                plantilla.jugadores.remove(jugador)  # Eliminar jugador de la relación
                jugador.libre = True
                jugadorPlantilla = JugadorPlantilla.objects.get(jugador=jugador, plantilla=plantilla)
                jugadorPlantilla.delete()
                plantilla.save()
                jugador.save()




            elif len(ofertas_jugadores) != 0 and jugador.libre == False:
                jugadoresPlantillas = JugadorPlantilla.objects.filter(jugador=jugador)
                for jugadoresPlantilla in jugadoresPlantillas:
                    plantilla = jugadoresPlantilla.plantilla
                    comunidadUsuarioConOfertasVendedor = ComunidadUsuario.objects.get(usuario=plantilla.user,
                                                                                      comunidad=comunidad)
                    comunidadUsuarioConOfertasVendedor.saldo = comunidadUsuarioConOfertasVendedor.saldo + mejor_oferta.oferta
                    comunidadUsuarioConOfertasVendedor.save()

                    plantillaDestino = mejor_oferta.plantilla
                    comunidadUsuarioConOfertasComprador = ComunidadUsuario.objects.get(usuario=plantillaDestino.user,
                                                                                       comunidad=comunidad)
                    comunidadUsuarioConOfertasComprador.saldo = comunidadUsuarioConOfertasComprador.saldo - mejor_oferta.oferta
                    comunidadUsuarioConOfertasComprador.save()

                    # tabla plantillaJugadores
                    plantilla.jugadores.remove(jugador)
                    plantillaDestino.jugadores.add(jugador)
                    jugadoresPlantillaSalida = JugadorPlantilla.objects.get(jugador=jugadoresPlantilla.jugador,
                                                                            plantilla=plantilla)
                    jugadoresPlantillaSalida.delete()
                    jugadorPlantillaDestino = JugadorPlantilla(jugador=jugadoresPlantilla.jugador,
                                                               plantilla=plantillaDestino, es_titular=False)
                    jugadorPlantillaDestino.save()
                    plantillaDestino.es_titular = False

                    plantillaDestino.save()

                    nueva_noticia = Noticia()
                    nueva_noticia.plantillaVendedor = plantilla
                    nueva_noticia.perfil_usuario = Perfil.objects.get(user=plantillaDestino.user)
                    nueva_noticia.descripcion = jugador.jugador.nombre + ' cambia de ' + plantilla.user.username + ' a ' + plantillaDestino.user.username
                    nueva_noticia.fecha_publicacion = datetime.date.today()
                    nueva_noticia.comunidad = comunidad
                    nueva_noticia.oferta = mejor_oferta
                    nueva_noticia.save()

            listaOfertas = list(ofertas_jugadores)
            for oferta in listaOfertas:
                usuarioOferta = oferta.plantilla.user
                comunidadUsuarioSumaSaldo = ComunidadUsuario.objects.get(usuario=usuarioOferta, comunidad=comunidad)
                comunidadUsuarioSumaSaldo.saldo = comunidadUsuarioSumaSaldo.saldo + oferta.oferta
                comunidadUsuarioSumaSaldo.save()
                oferta.estado = False
                oferta.save()

            subasta.delete()


@login_required
def more(request):
    comunidad = Comunidad.objects.get(id=request.session.get('comunidad'))

    if comunidad.es_privada:
        acceso_comunidad = AccesoComunidades.objects.get(comunidad=comunidad)
    else:
        acceso_comunidad = None

    user = User.objects.get(id=request.user.id)
    perfil = Perfil.objects.get(user=user)

    comunidades_del_usuario = ComunidadUsuario.objects.filter(usuario=request.user)
    usuario_datos_comunidad = ComunidadUsuario.objects.get(usuario=request.user, comunidad=comunidad)

    context = {'comunidad': comunidad, 'perfil': perfil, 'acceso_comunidad': acceso_comunidad,
               'comunidades_del_usuario': comunidades_del_usuario, 'usuario_datos_comunidad': usuario_datos_comunidad}
    return render(request, 'more.html', context)


@login_required
def vista_plantilla(request):
    return render(request, 'plantilla.html')


##VISTA PARA OBTENER LA PLANTILLA EXISTENTE
def obtener_plantilla_existente(request):
    comunidad = request.session.get('comunidad')
    plantilla_existente = Plantilla.objects.filter(user=request.user, comunidad=comunidad).exists()

    data = {
        'plantillaExistente': plantilla_existente,
    }
    return JsonResponse(data)


def iniciar_programador():
    scheduler = BackgroundScheduler()
    scheduler.add_job(chequeo_fin_subasta, 'cron', hour=3)  # Ejecutar cada 5 minutos
    scheduler.add_job(generar_jugadores_subasta, 'cron', hour=3, minute=5)  # Ejecutar cada 5 minutos
    scheduler.start()
