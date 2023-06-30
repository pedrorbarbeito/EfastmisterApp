from django.contrib.auth.models import User
from django.core.validators import MaxValueValidator, MinValueValidator

from django.db import models
from UsersApp.models import Perfil


# Create your models here.
class Equipo(models.Model):
    nombre = models.CharField(max_length=200, blank=True, null=True)
    imagen = models.CharField(max_length=500, null=True, blank=True)

    class Meta:
        ordering = ['id']


class Jugadores(models.Model):
    nombre = models.CharField(max_length=200, blank=True, null=False)
    posicion = models.CharField(max_length=200, blank=True, null=False)
    puntuacion = models.IntegerField(null=True)
    puntuacion_media = models.FloatField(null=True)
    valor = models.IntegerField(null=True)

    equipoReal = models.ForeignKey(Equipo, on_delete=models.CASCADE)
    imagen = models.CharField(max_length=500, blank=True, null=True)

    def __str__(self):
        return str(self.nombre)

    class Meta:
        ordering = ['id']


class Comunidad(models.Model):
    nombre_comunidad = models.CharField(max_length=200, blank=True, null=True)
    fecha_creacion = models.DateTimeField(auto_now_add=True)
    administrador = models.ForeignKey(User, on_delete=models.CASCADE)
    cantidad_miembros = models.IntegerField(validators=[
        MaxValueValidator(30),
        MinValueValidator(5)
    ], null=False, default=5)
    es_privada = models.BooleanField(default=False)
    profile_image = models.ImageField(null=True, blank=True, upload_to="comunidad/",
                                      default="imagenes/comunidad_default.png")
    jugadores = models.ManyToManyField(Jugadores, through='Jugadores_comunidad')

    def __str__(self):
        return str(self.nombre_comunidad)

    class Meta:
        ordering = ['id']

    @property
    def imageURL(self):
        try:
            url = self.profile_image.url
        except:
            url = ''

        return url


class ComunidadUsuario(models.Model):
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    saldo = models.IntegerField(null=True)

    class Meta:
        ordering = ['id']


# ! METODO PARA ABREVIAR LOS PRESUPUESTOS DE LA GESTION COMUNIDAD
def abreviar(campo_presupuesto):
    if campo_presupuesto < 1000000:
        return str(int(campo_presupuesto))
    elif campo_presupuesto < 1000000000:
        return str(int(round(campo_presupuesto / 1000000, 2))) + "M"
    else:
        return str(int(round(campo_presupuesto / 1000000000, 2))) + "B"


class GestionComunidad(models.Model):
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    futbolistas_mercado = models.IntegerField(validators=[
        MaxValueValidator(20),
        MinValueValidator(0)
    ], null=False, default=10)
    max_futbolistas_equipo = models.IntegerField(validators=[
        MaxValueValidator(22),
        MinValueValidator(11)
    ], null=False, default=22)
    futbolistas_inicio = models.IntegerField(validators=[
        MaxValueValidator(22),
        MinValueValidator(11)
    ], null=False, default=15)
    presupuesto_inicio = models.IntegerField(validators=[
        MaxValueValidator(80000000),
        MinValueValidator(30000000)
    ], null=False, default=50000000)
    jugadores_inicio_temp = models.IntegerField(validators=[
        MaxValueValidator(22),
        MinValueValidator(11)
    ], null=False, default=15)
    presupuesto_inicio_temp = models.IntegerField(validators=[
        MaxValueValidator(80000000),
        MinValueValidator(30000000)
    ], null=False, default=50000000)
    pagos_clausulas = models.BooleanField(default=True)
    duracion_jugadores_mercado = models.IntegerField(validators=[
        MaxValueValidator(24),
        MinValueValidator(8)
    ], null=False, default=24)
    maximo_jugadores_mercado = models.IntegerField(validators=[
        MaxValueValidator(20),
        MinValueValidator(1)
    ], null=False, default=10)
    maximo_jugadores_simultaneo = models.IntegerField(validators=[
        MaxValueValidator(5),
        MinValueValidator(0)
    ], null=False, default=3)
    hacer_oferta = models.BooleanField(default=True)

    # * TENER EN CUENTA QUE EN HACER OFERTA CADA NUMERO HACE UN CALCULO DISTINTO DEL DINERO QUE PUEDE OFRECER
    deuda_maxima = models.IntegerField(validators=[
        MaxValueValidator(3),
        MinValueValidator(0)
    ], null=False, default=1)
    oferta_bajo_mercado = models.BooleanField(default=False)
    chupinazo = models.BooleanField(default=True)
    horas_antes_de_chupinazo_recien_fichados = models.IntegerField(validators=[
        MaxValueValidator(168),
        MinValueValidator(0)
    ], null=False, default=24)

    # * 0 = Desactivado || 1 = Un jugador por día
    # * 2 = Tres jugadores por día || 3 = Un jugador por semana
    # * 4 = Tres jugadores por semana
    maximo_jugadores_horas_chupinazo = models.IntegerField(validators=[
        MaxValueValidator(4),
        MinValueValidator(0)
    ], null=False, default=1)
    horas_antes_jornada_chupinazo = models.IntegerField(validators=[
        MaxValueValidator(72),
        MinValueValidator(0)
    ], null=False, default=24)
    intercambio_jugadores = models.BooleanField(default=True)
    maximo_jugadores_intercambio = models.IntegerField(validators=[
        MaxValueValidator(11),
        MinValueValidator(0)
    ], null=False, default=6)
    bonificacion_por_puntos = models.IntegerField(validators=[
        MaxValueValidator(1000000),
        MinValueValidator(0)
    ], null=False, default=10000)
    bonificacion_fija_jornada = models.IntegerField(validators=[
        MaxValueValidator(100000),
        MinValueValidator(0)
    ], null=False, default=25000)

    def __str__(self):
        return str(self.comunidad)

    class Meta:
        ordering = ['id']

    @property
    def presupuesto_abreviado(self):
        return abreviar(self.presupuesto_inicio)

    @property
    def presupuesto_temporada_abreviado(self):
        return abreviar(self.presupuesto_inicio_temp)


class AccesoComunidades(models.Model):
    codigoAcceso = models.CharField(max_length=200, blank=True, null=True)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.codigoAcceso)

    class Meta:
        ordering = ['id']


class Favoritos(models.Model):
    jugador = models.ForeignKey(Jugadores, on_delete=models.CASCADE)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']


class Jugadores_comunidad(models.Model):
    jugador = models.ForeignKey(Jugadores, on_delete=models.CASCADE)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    libre = models.BooleanField(default=True)

    class Meta:
        ordering = ['id']


class Tipo_alineacion(models.Model):
    tipo = models.CharField(max_length=100, blank=True, null=True)
    num_portero = models.IntegerField(null=True)
    num_defensas = models.IntegerField(null=True)
    num_centrocampistas = models.IntegerField(null=True)
    num_delanteros = models.IntegerField(null=True)

    class Meta:
        ordering = ['id']

    def __str__(self):
        return str(self.tipo)


class Plantilla(models.Model):
    nombre = models.CharField(max_length=200, blank=True, null=True)
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    perfil = models.ForeignKey(Perfil, on_delete=models.CASCADE, null=True)
    puntosTotales = models.IntegerField(null=True)
    valor_plantilla = models.IntegerField(null=True)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)
    alineacion = models.ForeignKey(Tipo_alineacion, on_delete=models.CASCADE, default='')
    jugadores = models.ManyToManyField(Jugadores_comunidad)

    def __str__(self):
        return str(self.nombre)

    class Meta:
        ordering = ['id']


class Partido(models.Model):  # Partido de equipos de una comunidad
    equipo_local = models.ForeignKey(Plantilla, related_name='equipo_local', on_delete=models.CASCADE)
    equipo_visitante = models.ForeignKey(Plantilla, related_name='equipo_visitante', on_delete=models.CASCADE)
    resultado = models.IntegerField(null=False)
    fecha = models.DateTimeField(null=False)

    class Meta:
        ordering = ['id']


class Jornada(models.Model):  # Jornada de partidos reales de los equipos
    num_jornada = models.IntegerField(null=False)
    puntos = models.IntegerField(null=True)
    equipo_local = models.ForeignKey(Equipo, related_name='equipo_local', on_delete=models.CASCADE, null=True)
    equipo_visitante = models.ForeignKey(Equipo, related_name='equipo_visitante', on_delete=models.CASCADE, null=True)
    resultado = models.CharField(max_length=200, blank=True, null=True)
    fecha = models.DateTimeField(null=True)
    jugador = models.ForeignKey(Jugadores, null=True, on_delete=models.CASCADE)

    class Meta:
        ordering = ['id']


class JugadorPlantilla(models.Model):  # para ver si es titular o no cada jugador de una plantilla de usuario
    jugador = models.ForeignKey(Jugadores_comunidad, on_delete=models.CASCADE)
    plantilla = models.ForeignKey(Plantilla, on_delete=models.CASCADE)
    es_titular = models.BooleanField(default=False)

    class Meta:
        unique_together = ('jugador', 'plantilla')


class jugadores_favoritos(models.Model):
    jugador = models.ForeignKey(Jugadores, on_delete=models.CASCADE)
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.jugador.nombre)

    class Meta:
        unique_together = ('jugador', 'usuario', 'comunidad')


class Transaccion(models.Model):
    usuario_origen = models.ForeignKey(User, related_name='usuario_origen', on_delete=models.CASCADE)
    usuario_destino = models.ForeignKey(User, related_name='usuario_destino', on_delete=models.CASCADE)
    jugador = models.ForeignKey(Jugadores, on_delete=models.CASCADE)
    precio = models.FloatField(null=True)
    fecha = models.DateTimeField(null=True)

    class Meta:
        ordering = ['id']


class Oferta(models.Model):
    JugadoresComunidad = models.ForeignKey(
        Jugadores_comunidad,
        on_delete=models.CASCADE,
        null=True
    )
    plantilla = models.ForeignKey(
        Plantilla,
        on_delete=models.CASCADE, null=True)
    oferta = models.IntegerField(null=True)
    estado = models.BooleanField(default=True, null=False)
    fecha_hora = models.DateTimeField(auto_now_add=True)


class Noticia(models.Model):
    titulo = models.CharField(max_length=100, blank=True, null=True)
    descripcion = models.CharField(max_length=250, blank=True, null=True)
    comunidad = models.ForeignKey(Comunidad, on_delete=models.CASCADE, null=True)
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
    perfil_usuario = models.ForeignKey(Perfil, on_delete=models.CASCADE, null=True)
    oferta = models.ForeignKey(Oferta, on_delete=models.CASCADE, null=True)
    plantillaVendedor = models.ForeignKey(
        Plantilla,
        on_delete=models.CASCADE,
        null=True
    )

    class Meta:
        ordering = ['id']




class Subasta(models.Model):
    JugadoresComunidad = models.ForeignKey(
        Jugadores_comunidad,
        on_delete=models.CASCADE,
        null=True
    )
    comunidad = models.ForeignKey(
        Comunidad,
        on_delete=models.CASCADE,
        null=True
    )
    fecha_publicacion = models.DateTimeField(auto_now_add=True)
