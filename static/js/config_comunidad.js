// ? CHEQUEAR URL ACTUAL POR LA CONSOLA
// var currentUrl = window.location.href
// console.log(currentUrl)

// ! *************************
// ! * CONFIGURACION GENERAL *
// ! *************************

// ? MODAL GENERAL - NOMBRE
const btnAbrirModalNombre = document.querySelector("#abrir-modal-nombre");
const modalNombre = document.querySelector("#modal-nombre")
const btnCerrarModalNombre = document.querySelector("#cerrar-modal-nombre");

if (modalNombre != null) {
    btnAbrirModalNombre.addEventListener("click", () => {
        modalNombre.showModal();
    });
    btnCerrarModalNombre.addEventListener("click", () => {
        modalNombre.close();
    });
}


// ? MODAL GENERAL - IMAGEN
const btnAbrirModalImagen = document.querySelector("#abrir-modal-imagen");
const modalImagen = document.querySelector("#modal-imagen");
const btnCerrarModalImagen = document.querySelector("#cerrar-modal-imagen");

if (modalImagen != null) {
    btnAbrirModalImagen.addEventListener("click", () => {
        modalImagen.showModal();
    });

    btnCerrarModalImagen.addEventListener("click", () => {
        modalImagen.close();
    });
}


// ? MODAL GENERAL - MIEMBROS MAXIMOS
const btnAbrirModalMiembros = document.querySelector("#abrir-modal-miembros");
const modalMiembros = document.querySelector("#modal-miembros");
const btnCerrarModalMiembros = document.querySelector("#cerrar-modal-miembros");

if (modalMiembros != null) {
    btnAbrirModalMiembros.addEventListener("click", () => {
        modalMiembros.showModal();
    });

    btnCerrarModalMiembros.addEventListener("click", () => {
        modalMiembros.close();
    });

}

// ! *************************
// ! * CONFIGURACION EQUIPOS *
// ! *************************


// ? MODAL EQUIPOS - JUGADORES MAXIMOS EQUIPO
const btnAbrirModalJugadoresEquipo = document.querySelector("#abrir-modal-jugadores-equipo");
const modalJugadoresEquipo = document.querySelector("#modal-jugadores-equipo");
const btnCerrarModalJugadoresEquipo = document.querySelector("#cerrar-modal-jugadores-equipo");


if (modalJugadoresEquipo != null) {
    btnAbrirModalJugadoresEquipo.addEventListener("click", () => {
        modalJugadoresEquipo.showModal();
    });

    btnCerrarModalJugadoresEquipo.addEventListener("click", () => {
        modalJugadoresEquipo.close();
    });

}


// ? MODAL EQUIPOS - JUGADORES INICIALES
const btnAbrirModalJugadoresIniciales = document.querySelector("#abrir-modal-jugadores-iniciales");
const modalJugadoresIniciales = document.querySelector("#modal-jugadores-iniciales");
const btnCerrarModalJugadoresIniciales = document.querySelector("#cerrar-modal-jugadores-iniciales");


if (modalJugadoresIniciales != null) {
    btnAbrirModalJugadoresIniciales.addEventListener("click", () => {
        modalJugadoresIniciales.showModal();
    });

    btnCerrarModalJugadoresIniciales.addEventListener("click", () => {
        modalJugadoresIniciales.close();
    });
}

// ? MODAL EQUIPOS - COMIENZO TEMPORADAS
const btnAbrirModalComienzoTemporadas = document.querySelector("#abrir-modal-comienzo-temporadas");
const modalComienzoTemporadas = document.querySelector("#modal-comienzo-temporadas");
const btnCerrarModalComienzoTemporadas = document.querySelector("#cerrar-modal-comienzo-temporadas");


if (modalComienzoTemporadas != null) {
    btnAbrirModalComienzoTemporadas.addEventListener("click", () => {
        modalComienzoTemporadas.showModal();
    });

    btnCerrarModalComienzoTemporadas.addEventListener("click", () => {
        modalComienzoTemporadas.close();
    });
}

// ! *************************
// ! * CONFIGURACION MERCADO *
// ! *************************

// ? MODAL MERCADO - DURACIÓN DEL MERCADO
const btnAbrirModalDuracionMercado = document.querySelector("#abrir-modal-duracion-mercado");
const modalDuracionMercado = document.querySelector("#modal-comienzo-mercado");
const btnCerrarModalDuracionMercado = document.querySelector("#cerrar-modal-duracion-mercado");


if (modalDuracionMercado != null) {
    btnAbrirModalDuracionMercado.addEventListener("click", () => {
        modalDuracionMercado.showModal();
    });

    btnCerrarModalDuracionMercado.addEventListener("click", () => {
        modalDuracionMercado.close();
    });
}

// ? MODAL MERCADO - JUGADORES LIBRES MERCADO
const btnAbrirModalJugadoresLibres = document.querySelector("#abrir-modal-jugadores-libres");
const modalJugadoresLibres = document.querySelector("#modal-jugadores-libres");
const btnCerrarModalJugadoresLibres = document.querySelector("#cerrar-modal-jugadores-libres");

const numeroInputJugadoresLibres = document.getElementById('maximo_jugadores_mercado');
const btnGuardarJugadoresLibres = document.getElementById('boton-guardar-jugadores-libres')

if (modalJugadoresLibres != null) {
    btnAbrirModalJugadoresLibres.addEventListener("click", () => {
        modalJugadoresLibres.showModal();
    });

    btnCerrarModalJugadoresLibres.addEventListener("click", () => {
        modalJugadoresLibres.close();
    });

    numeroInputJugadoresLibres.addEventListener('input', () => {
        const valor = numeroInputJugadoresLibres.value;
        btnGuardarJugadoresLibres.disabled = valor < 0 || valor > 20;
    });
}

// ? MODAL MERCADO - JUGADORES LIBRES MERCADO
const btnAbrirModalJugadoresMiembros = document.querySelector("#abrir-modal-jugadores-miembros");
const modalJugadoresMiembros = document.querySelector("#modal-jugadores-miembros");
const btnCerrarModalJugadoresMiembros = document.querySelector("#cerrar-modal-jugadores-miembros");

const numeroInputJugadoresMiembros = document.getElementById('maximo_jugadores_simultaneo');
const btnGuardarJugadoresMiembros = document.getElementById('boton-guardar-jugadores-miembros')

if (modalJugadoresMiembros != null) {
    btnAbrirModalJugadoresMiembros.addEventListener("click", () => {
        modalJugadoresMiembros.showModal();
    });

    btnCerrarModalJugadoresMiembros.addEventListener("click", () => {
        modalJugadoresMiembros.close();
    });

    numeroInputJugadoresMiembros.addEventListener('input', () => {
        const valor = numeroInputJugadoresMiembros.value;
        btnGuardarJugadoresMiembros.disabled = valor < 0 || valor > 5;
    });
}

// ? MODAL OFERTAS - OFERTAS, PUJAS Y CLÁUSULAS
const btnAbrirModalOfertas = document.querySelector("#abrir-modal-ofertas");
const modalDuracionOfertas = document.querySelector("#modal-ofertas");
const btnCerrarModalOfertas = document.querySelector("#cerrar-modal-ofertas");


if (modalDuracionOfertas != null) {
    btnAbrirModalOfertas.addEventListener("click", () => {
        modalDuracionOfertas.showModal();
    });

    btnCerrarModalOfertas.addEventListener("click", () => {
        modalDuracionOfertas.close();
    });
}

// ? MODAL OFERTAS - COMPRAS MIEMBROS
const btnAbrirModalComprasMiembros = document.querySelector("#abrir-modal-compras-miembros");
const modalComprasMiembros = document.querySelector("#modal-compras-miembros");
const btnCerrarModalComprasMiembros = document.querySelector("#cerrar-modal-compras-miembros");


if (modalComprasMiembros != null) {
    btnAbrirModalComprasMiembros.addEventListener("click", () => {
        modalComprasMiembros.showModal();
    });

    btnCerrarModalComprasMiembros.addEventListener("click", () => {
        modalComprasMiembros.close();
    });
}

// ? MODAL OFERTAS - CLÁUSULAS RECESION
const btnAbrirModalClausulasRecesion = document.querySelector("#abrir-modal-clausulas-recesion");
const modalClausulasRecesion = document.querySelector("#modal-clausulas-recesion");
const btnCerrarModalClausulasRecesion = document.querySelector("#cerrar-modal-clausulas-recesion");


if (modalClausulasRecesion != null) {
    btnAbrirModalClausulasRecesion.addEventListener("click", () => {
        modalClausulasRecesion.showModal();
    });

    btnCerrarModalClausulasRecesion.addEventListener("click", () => {
        modalClausulasRecesion.close();
    });
}

// ? MODAL OFERTAS - CLASULA IMPEDIR FICHAR
const btnAbrirModalClausulasFichado = document.querySelector("#abrir-modal-clausulas-fichado");
const modalClausulasFichado = document.querySelector("#modal-clausulas-fichado");
const btnCerrarModalClausulasFichado = document.querySelector("#cerrar-modal-clausulas-fichado");


if (modalClausulasFichado != null) {
    btnAbrirModalClausulasFichado.addEventListener("click", () => {
        modalClausulasFichado.showModal();
    });

    btnCerrarModalClausulasFichado.addEventListener("click", () => {
        modalClausulasFichado.close();
    });
}

// ? MODAL OFERTAS - CLASULA IMPEDIR FICHAR A MÁS DE
const btnAbrirModalClausulasImpedir = document.querySelector("#abrir-modal-clausulas-impedir");
const modalClausulasImpedir = document.querySelector("#modal-clausulas-impedir");
const btnCerrarModalClausulasImpedir = document.querySelector("#cerrar-modal-clausulas-impedir");


if (modalClausulasImpedir != null) {
    btnAbrirModalClausulasImpedir.addEventListener("click", () => {
        modalClausulasImpedir.showModal();
    });

    btnCerrarModalClausulasImpedir.addEventListener("click", () => {
        modalClausulasImpedir.close();
    });
}

// ? MODAL OFERTAS - CLASULA ANTES DE LAS JORNADAS
const btnAbrirModalClausulasJornadas = document.querySelector("#abrir-modal-clausulas-jornadas");
const modalClausulasJornada = document.querySelector("#modal-clausulas-jornadas");
const btnCerrarModalClausulasJornadas = document.querySelector("#cerrar-modal-clausulas-jornadas");


if (modalClausulasJornada != null) {
    btnAbrirModalClausulasJornadas.addEventListener("click", () => {
        modalClausulasJornada.showModal();
    });

    btnCerrarModalClausulasJornadas.addEventListener("click", () => {
        modalClausulasJornada.close();
    });
}

// ! **************************
// ! * CONFIGURACION JORNADAS *
// ! **************************

// ? MODAL JORNADAS - PERMITIR CAMBIOS DURANTES LAS JORNADAS
const btnAbrirModalCambiosJornadas = document.querySelector("#abrir-modal-cambios-jornadas");
const modalCambiosJornada = document.querySelector("#modal-cambios-jornadas");
const btnCerrarModalCambiosJornadas = document.querySelector("#cerrar-modal-cambios-jornadas");


if (modalCambiosJornada != null) {
    btnAbrirModalCambiosJornadas.addEventListener("click", () => {
        modalCambiosJornada.showModal();
    });

    btnCerrarModalCambiosJornadas.addEventListener("click", () => {
        modalCambiosJornada.close();
    });
}


// ? MODAL JORNADAS - Nº MÁXIMO DE CAMBIOS DURANTES LAS JORNADAS
const btnAbrirModalCambiosMaximoJornadas = document.querySelector("#abrir-modal-cambios-maximo-jornadas");
const modalCambiosMaximoJornada = document.querySelector("#modal-cambios-maximo-jornadas");
const btnCerrarModalCambiosMaximoJornadas = document.querySelector("#cerrar-modal-cambios-maximo-jornadas");


if (modalCambiosMaximoJornada != null) {
    btnAbrirModalCambiosMaximoJornadas.addEventListener("click", () => {
        modalCambiosMaximoJornada.showModal();
    });

    btnCerrarModalCambiosMaximoJornadas.addEventListener("click", () => {
        modalCambiosMaximoJornada.close();
    });
}

// ! ********************************
// ! * CONFIGURACION BONIFICACIONES *
// ! ********************************

// ? MODAL BONIFICACIONES - BONIFICAR POR PUNTO DE LA JORNADA
const btnAbrirModalBonificarPuntos = document.querySelector("#abrir-modal-bonificar-puntos");
const modalBonificarPuntos = document.querySelector("#modal-bonificar-puntos");
const btnCerrarModalBonificarPuntos = document.querySelector("#cerrar-modal-bonificar-puntos");

if (modalBonificarPuntos != null) {
    btnAbrirModalBonificarPuntos.addEventListener("click", () => {
       modalBonificarPuntos.showModal();
    });

    btnCerrarModalBonificarPuntos.addEventListener("click", () => {
        modalBonificarPuntos.close();
    });

}


// ? MODAL BONIFICACIONES - BONIFICACION FIJA POR JORNADA
const btnAbrirModalBonificarJornadas = document.querySelector("#abrir-modal-bonificar-fija");
const modalBonificarJornadas = document.querySelector("#modal-bonificar-fija");
const btnCerrarModalBonificarJornadas = document.querySelector("#cerrar-modal-bonificar-fija");

if (modalBonificarJornadas != null) {
    btnAbrirModalBonificarJornadas.addEventListener("click", () => {
       modalBonificarJornadas.showModal();
    });

    btnCerrarModalBonificarJornadas.addEventListener("click", () => {
        modalBonificarJornadas.close();
       });
}


// ! **************************
// ! * CONFIGURACION LISTA JUGADORES *
// ! **************************

// ? MODAL JUGADORES FILTRAR
const btnAbrirModalFiltrarJugadores = document.querySelector("#abrir-modal-filtrar-jugadores");
const modalFiltrarJugadores = document.querySelector("#modal-filtar-jugadores");
const btnCerrarModalFiltrarJugadores = document.querySelector("#cerrar-modal-filtrar-jugadores");


if (modalFiltrarJugadores != null) {
    btnAbrirModalFiltrarJugadores.addEventListener("click", () => {
        modalFiltrarJugadores.showModal();
    });

    btnCerrarModalFiltrarJugadores.addEventListener("click", () => {
        modalFiltrarJugadores.close();
    });
}

// ! **************************
// ! * PANEL DE ADMINISTRACIÓN *
// ! **************************

// ? MODAL CREACIÓN MENSAJES COMUNIDAD
const btnAbrirModalCreacionMensaje = document.querySelector("#abrir-modal-creacion-mensaje");
const modalCreacionMensaje = document.querySelector("#modal-creacion-mensaje");
const btnCerrarModalCreacionMensaje = document.querySelector("#cerrar-modal-creacion-mensaje");


if (modalCreacionMensaje != null) {
    btnAbrirModalCreacionMensaje.addEventListener("click", () => {
        modalCreacionMensaje.showModal();
    });

    btnCerrarModalCreacionMensaje.addEventListener("click", () => {
        modalCreacionMensaje.close();
    });
}

// ! **************************
// ! * JUGADORES MERCADO *
// ! **************************

// ? MODAL JUGADORES Mercado
const btnAbrirModalJugadoresMercado = document.querySelector("#abrir-modal-jugadores-mercado");
const modalJugadoresMercado = document.querySelector("#modal-jugadores-mercado");
const btnCerrarModalJugadoresMercado = document.querySelector("#cerrar-modal-jugadores-mercado");


if (modalJugadoresMercado != null) {
    btnAbrirModalJugadoresMercado.addEventListener("click", () => {
        modalJugadoresMercado.showModal();
    });

    btnCerrarModalJugadoresMercado.addEventListener("click", () => {
        modalJugadoresMercado.close();
    });
}
// ! **************************
// ! * JUGADORES PUJA MERCADO *
// ! **************************


// ? MODAL JUGADORES PUJA MERCADO



// ! **************************
// ! * VENTA JUGADORES *
// ! **************************

const btnAbrirModalVentaJugadores = document.querySelector("#abrir-modal-jugadores-venta");
const modalVentaJugadores = document.querySelector("#modal-jugadores-venta");
const btnCerrarModalVentaJugadores = document.querySelector("#cerrar-modal-jugadores-venta");


if (modalVentaJugadores != null) {
    btnAbrirModalVentaJugadores.addEventListener("click", () => {
        modalVentaJugadores.showModal();
    });

    btnCerrarModalVentaJugadores.addEventListener("click", () => {
        modalVentaJugadores.close();
    });
}


// ! **************************
// ! * FORMACION PLANTILLA *
// ! **************************

const btnAbrirModalFormacionPlantilla = document.querySelector("#abrir-modal-formacion-plantilla");
const modalFormacionPlantilla = document.querySelector("#modal-formacion-plantilla");
const btnCerrarModalFormacionPlantilla = document.querySelector("#cerrar-modal-formacion-plantilla");


if (modalFormacionPlantilla != null) {
    btnAbrirModalFormacionPlantilla.addEventListener("click", () => {
        modalFormacionPlantilla.showModal();
    });

    btnCerrarModalFormacionPlantilla.addEventListener("click", () => {
        modalFormacionPlantilla.close();
    });
}


// ! **************************
// ! * REEMPLAZAR JUGADORES*
// ! **************************

const btnAbrirModalReemplazarJugador = document.querySelector("#abrir-modal-reemplazar-jugador");
const modalReemplazarJugador = document.querySelector("#modal-reemplazar-jugador");
const btnCerrarModalReemplazarJugador = document.querySelector("#cerrar-modal-reemplazar-jugador");


if (modalReemplazarJugador != null) {
    btnAbrirModalReemplazarJugador.addEventListener("click", () => {
        modalReemplazarJugador.showModal();
    });

    btnCerrarModalReemplazarJugador.addEventListener("click", () => {
        modalReemplazarJugador.close();
    });
}

