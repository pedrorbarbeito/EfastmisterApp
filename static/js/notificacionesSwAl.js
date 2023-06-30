const notificacionSwAl = (titletext = '', text, icon, confirmButtonText, tipo, url = '') => {

    if (tipo === 'exitoso') {
        Swal.fire({
            title: titletext,
            text: text,
            icon: icon,
            confirmButtonText: confirmButtonText,
        }).then((result) => {
            if (result.isConfirmed) {
                window.location.href = url;
            }
        });
    } else if (tipo === 'eliminar') {
        Swal.fire({
            title: titletext,
            text: text,
            icon: icon,
            confirmButtonText: confirmButtonText,
        }).then((result) => {
            if (result.isConfirmed) {
                document.getElementById("formularioEliminar").submit();
            }
        });
    } else if (tipo === 'info' || tipo === 'error') {
        Swal.fire({
            title: titletext,
            text: text,
            icon: icon,
            confirmButtonText:confirmButtonText
        })
    } else {
        Swal.fire({
            titleText: titletext,
            text: text,
            icon: icon,
            confirmButtonText: confirmButtonText
        });
    }


};