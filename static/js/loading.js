function cargarDatos() {
    $('#loading-overlay').show();  // Mostrar el div de carga

    $.ajax({
        url: 'scrapeo/',
        type: 'POST',
        success: function (response) {
            // Ocultar el div de carga
            $('#loading-overlay').hide();
            // Hacer algo con los datos obtenidos
            console.log(response.result);
        },
        error: function (xhr) {
            // Mostrar un mensaje de error si ocurrió alguno
            console.error('Error en la solicitud:', xhr.status);
        }
    });
}