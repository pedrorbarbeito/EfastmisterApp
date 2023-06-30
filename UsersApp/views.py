import random
from datetime import datetime

from PIL import Image
from django import forms
from django.contrib import messages
from django.contrib.auth import login, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib.auth.hashers import make_password
from django.contrib.auth.models import User
from django.http import Http404, HttpResponseBadRequest
from django.shortcuts import render, redirect, get_object_or_404
from django.urls import reverse_lazy, reverse
from django.views.generic import CreateView, UpdateView

from EFastMisterApp.models import ComunidadUsuario, Plantilla, Jugadores_comunidad, GestionComunidad, JugadorPlantilla, \
    Comunidad
from UsersApp.models import Perfil

# Create your views here.
def loginUser(request):
    if request.method == 'POST':

        username = request.POST['username']
        password = request.POST['password']

        user = authenticate(request, username=username, password=password)

        if user is None:
            messages.error(request, 'El nombre del usuario o contraseña es incorrecto')
        else:
            login(request, user)
            comunidades_del_usuario = ComunidadUsuario.objects.filter(usuario=request.user)

            if comunidades_del_usuario.count() != 0:
                comunidad_usuario = comunidades_del_usuario[0]
                request.session['comunidad'] = comunidad_usuario.comunidad.id
                return redirect('pagina_principal_comunidad', id_comunidad=comunidad_usuario.comunidad.id)
            else:
                usuario = User.objects.get(username=username)
                if usuario.is_superuser:
                    return redirect('panel_administracion')
                else:
                    return redirect('vista_elegir_comunidad')

    return render(request, 'login.html')


@login_required
def perfil(request):
    comunidad_id = request.session.get('comunidad')
    comunidad = None

    if comunidad_id:
        try:
            comunidad = Comunidad.objects.get(id=comunidad_id)
        except Comunidad.DoesNotExist:
            pass #mensahe de que no hay comunidad

    try:
        perfil = Perfil.objects.get(user=request.user)
    except Perfil.DoesNotExist:
        perfil = None

    context = {'perfil': perfil, 'comunidad': comunidad}
    return render(request, 'perfil.html', context)


@login_required
def editar_perfil(request):
    id_ultima_comunidad_visitada = request.session.get('comunidad')
    comunidad = Comunidad.objects.get(id = id_ultima_comunidad_visitada)

    try:
        perfil = Perfil.objects.get(user=request.user)
    except Perfil.DoesNotExist:
        perfil = Perfil.objects.create(user=request.user)

    if request.method == 'POST':
        # Obtener los datos del formulario
        username = request.POST.get('username')
        password = request.POST.get('password')
        email = request.POST.get('email')


        if not username:
            messages.error(request, 'El nombre es obligatorio')
            return redirect('editar_perfil')

        user = request.user

        if password:
            user.set_password(password)
            request.session['comunidad'] = id_ultima_comunidad_visitada
            user.save()
            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)
            messages.success(request, 'Su contraseña se ha actualizado correctamente')

            # Redireccionar a la página principal de la comunidad
            id_comunidad = request.session.get('comunidad')
            if id_comunidad:
                url = reverse('perfil')
                return redirect(url)

        user.username = username
        user.email = email
        request.session['comunidad'] = id_ultima_comunidad_visitada
        user.save()

        perfil_image = request.FILES.get('profile_image', None)

        if perfil_image:
            img = Image.open(perfil_image)
            width, height = img.size

            if width > 720 or height > 720:
                messages.error(request, 'La imagen seleccionada es demasiado grande')
                return redirect('editar_perfil')

            perfil.profile_image = perfil_image
            request.session['comunidad'] = id_ultima_comunidad_visitada
            perfil.save()

            user = authenticate(username=username, password=password)
            if user is not None:
                login(request, user)

            request.session['comunidad'] = id_ultima_comunidad_visitada

        messages.success(request, 'Su perfil se ha actualizado correctamente')

        # Redireccionar a la página principal de la comunidad
        id_comunidad = request.session.get('comunidad')
        if id_comunidad:
            url = reverse('perfil')
            return redirect(url)

    context = {'perfil': perfil, 'comunidad': comunidad}
    return render(request, 'editar_perfil.html', context)

@login_required
def eliminar_perfil(request):
    if request.user.is_authenticated:
        perfil = Perfil.objects.filter(user=request.user).first()
        print('Perfil antes de eliminar:', perfil)  # mensaje de depuración
        if perfil:
            perfil.user.delete()
            messages.info(request, 'El perfil y el usuario han sido eliminados correctamente')
            print('Perfil después de eliminar:', perfil)  # mensaje de depuración
            return redirect('registerpage')
        else:
            messages.error(request, 'El perfil no existe')
    else:
        messages.error(request, 'Debes estar autenticado para eliminar el perfil')
    return render(request, 'error_perfil.html')


def register(request):
    if request.method == 'POST':
        username = request.POST['username']
        correo = request.POST['correo']
        password1 = request.POST['password1']
        password2 = request.POST['password2']

        if password1 != password2:
            messages.error(request, "Las contraseñas no coinciden.")

        elif User.objects.filter(username=username).exists() or User.objects.filter(email=correo).exists():
            messages.error(request, "Ya existe un usuario con ese correo/nombre.")

        else:
            user = User()
            user.username = username.lower()
            user.email = correo
            user.password = make_password(password1)
            user.save()
            perfil = Perfil()
            perfil.user = user
            perfil.profile_image = "user-default.png"
            perfil.created = datetime.now
            perfil.save()
            messages.success(request, 'Ha creado la cuenta satisfactoriamente.')

    return render(request, 'register.html')


# * Vistas Default
def vistaRegister(request):
    return render(request, "register.html")


def vistaLogin(request):
    return render(request, "login.html")
