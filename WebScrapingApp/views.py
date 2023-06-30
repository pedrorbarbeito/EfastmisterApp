import time
from datetime import datetime

import requests
from bs4 import BeautifulSoup
from django.contrib import messages
from django.contrib.auth.decorators import login_required, user_passes_test
from django.db import connection
from django.shortcuts import redirect, render
from unidecode import unidecode

from EFastMisterApp.models import Jugadores, Equipo, Jornada

# ! ################ WEB SCRAPING JUGADORES/JORNADAS/EQUIPOS ################

@login_required
@user_passes_test(lambda u: u.is_superuser)
def webscraping(request):
    if request.method == 'POST':
        # Verifica el valor del parámetro 'accion' en la URL
        accion = request.POST.get('accion')
        print(accion)

        if accion == 'jugadores':
            # ? BORRADO DE TODOS LOS JUGADORES
            Jugadores.objects.all().delete()

            for i in range(1, 27):
                contador = 0

                # ? Url de la pagina de los jugadores, usa el rango para recorrer todas las paginas totales
                url = f"https://www.jornadaperfecta.com/jugadores/?pagina={i}"
                timeout = 5
                page = requests.get(url, timeout=timeout)
                soup = BeautifulSoup(page.content, "html.parser")

                # ? Lista con los nombres de los jugadores
                tdNombres = soup.find_all('td', attrs={'itemprop': 'name'})

                # ? Lista con los nombres de los jugadores en base de datos
                jugadoresBBDD = Jugadores.objects.all()
                nombres_jugadores_bbdd = []
                for jugadorBBDD in jugadoresBBDD:
                    nombres_jugadores_bbdd.append(jugadorBBDD.nombre)

                # ! ################ BUCLE PARA SACAR LOS DATOS DE CADA JUGADOR BASANDOSE EN SU NOMBRE ################
                for td in tdNombres:
                    nombre_jugador = td.text

                    # ? Comprueba si el jugador que recorre ya existe, en ese caso para porque significa que la lista de
                    # ? jugadores está completa
                    if td.text in nombres_jugadores_bbdd:
                        contador = 1

                    if contador == 1:
                        break

                    # ? Conexion a la pagina concreta de cada jugador (PAGINA DONDE SE ENCUENTRAS SUS DATOS COMPLETOS)
                    nombreUrl = unidecode(td.text.replace(" ", "-").replace(".", ""))
                    urlJugador = f"https://www.jornadaperfecta.com/jugador/{nombreUrl.lower()}"
                    pageJugador = requests.get(urlJugador)
                    soupJugador = BeautifulSoup(pageJugador.content, "html.parser")
                    divDatos = soupJugador.find('div', class_='jugador-datos-precio')
                    divsDatos = divDatos.findAllNext('div')

                    # * Equipo real del jugador

                    divEquipo = soupJugador.find('div', class_='player-team-shield')
                    imgEquipo = divEquipo.findNext('img')

                    # ! ###### EQUIPOS ######
                    # ? get_or_create se usa para comprobar
                    # ? directamente si existe ese objeto en bbdd,
                    # ? si no existe lo crea automaticamente
                    Equipo.objects.update_or_create(nombre=imgEquipo['title'],
                                                    imagen=imgEquipo['src'])
                    equipoReal_jugador = Equipo.objects.get(nombre=imgEquipo['title'])

                    # * Valor del jugador
                    valor = int(divsDatos[0].text.replace(".", ""))
                    valor_jugador = valor

                    # * Puntuacion del jugador
                    puntuacion = soupJugador.find('div', class_='jugador-datos-cifra')
                    puntuacion_jugador = puntuacion.text

                    # * Puntuacion media del jugador
                    puntuacion_media = soupJugador.find('div', class_='jugador-datos-media').findNext('div',
                                                                                                      class_='jugador-datos-cifra')
                    puntuacion_media_jugador = float(puntuacion_media.text)

                    # * Posicion del jugador
                    posicion = soupJugador.find('div', class_='jp-pos')
                    posicion_jugador = posicion.text.strip()

                    # * Imagen del jugador
                    div_foto = soupJugador.find('div', class_='jugador-foto')
                    imagen = div_foto.find('img')
                    src = imagen['src']
                    imagen_jugador = src

                    # ? CREACION Y GUARDADO DEL NUEVO JUGADOR

                    # # ? PARSEO DE LA PUNTUACION DEL JUGADOR PARA QUE SALGA EL NUMERO SIN PROBLEMAS
                    # # ? (AL SCRAPEAR SACABA EL NUMERO Y UNA ',' CREANDO ASI UNA TUPLA)
                    # puntuacion_str = puntuacion_jugador[0]  # Acceder al primer elemento de la tupla
                    # puntuacion_int = int(puntuacion_str)

                    nuevo_jugador = Jugadores(
                        nombre=nombre_jugador,
                        equipoReal=equipoReal_jugador,
                        valor=valor_jugador,
                        puntuacion=puntuacion_jugador,
                        puntuacion_media=puntuacion_media_jugador,
                        posicion=posicion_jugador,
                        imagen=imagen_jugador
                    )
                    nuevo_jugador.save()

                if contador == 1:
                    break

            num_jugadores = str(Jugadores.objects.all().count())
            messages.success(request, 'Total de jugadores scrapeados: ' + num_jugadores)

            pass

        elif accion == 'jornadas':

            # ? BORRADO DE TODAS LAS JORNADAS
            Jornada.objects.all().delete()

            jugadores = Jugadores.objects.all()
            for jugador in jugadores:
                nombre = jugador.nombre
                nombre_url = unidecode(nombre.replace(" ", "-").replace(".", ""))
                url_jugador = f"https://www.jornadaperfecta.com/jugador/{nombre_url.lower()}"
                pageJugador = requests.get(url_jugador)
                soupJugador = BeautifulSoup(pageJugador.content, "html.parser")

                divsjornadas = soupJugador.find_all('div', class_='jugador-temporada-fila')
                for divjornada in divsjornadas:

                    # * Fecha de la jornada
                    if divjornada.findNext('time'):
                        fecha_str = divjornada.findNext('time')['content']
                        fecha = datetime.strptime(fecha_str, '%Y-%m-%dT%H:%M:%S%z')
                    else:
                        fecha = None

                    # ? Datos hace referencia al resto de datos ya que los scrapea de divs separados, asi que los saco todos
                    # ? en una lista y los voy guardando en variables a cada uno por separado
                    datos = divjornada.find_all_next('div')

                    if not divjornada.has_attr('itemprop') or len(datos) == 4:
                        # * Numero de la Jornada
                        numero_jornada = datos[0].text

                        # * Puntos de la Jornada
                        puntos_jornada = None

                        # * Equipo Local de la Jornada
                        equipo_local = None

                        # * Equipo Visitante de la Jornada
                        equipo_visitante = None

                        # * Resultado de la jornada
                        resultado = ''
                    else:

                        # * Numero de la Jornada
                        numero_jornada = datos[1].text

                        # * Puntos de la Jornada
                        puntos_jornada = datos[2].text
                        if puntos_jornada == '':
                            puntos_jornada = None

                        # * Equipo Local de la Jornada
                        if datos[4].findNext('div', attrs={'itemprop': 'homeTeam'}):
                            divEquipo_local = datos[4].findNext('div', attrs={'itemprop': 'homeTeam'})
                            nombre_equipoL = divEquipo_local.findNext('img')['title']
                            equipo_local = Equipo.objects.get(nombre=nombre_equipoL)
                        else:
                            equipo_local = None

                        # * Equipo Visitante de la Jornada
                        if datos[4].findNext('div', attrs={'itemprop': 'awayTeam'}):
                            divEQuipo_visitante = datos[4].findNext('div', attrs={'itemprop': 'awayTeam'})
                            nombre_equipoV = divEQuipo_visitante.findNext('img')['title']
                            equipo_visitante = Equipo.objects.get(nombre=nombre_equipoV)
                        else:
                            equipo_visitante = None

                        # * Resultado de la jornada
                        resultado = datos[4].findNext('div', class_='resultado').text

                    nueva_jornada = Jornada(
                        num_jornada=numero_jornada,
                        fecha=fecha,
                        puntos=puntos_jornada,
                        equipo_local=equipo_local,
                        equipo_visitante=equipo_visitante,
                        resultado=resultado,
                        jugador=jugador
                    )
                    nueva_jornada.save()

            messages.success(request, 'Total de jornadas scrapeadas: ' + str(Jornada.objects.all().count()))

    return redirect('panel_administracion')